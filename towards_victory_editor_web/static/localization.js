// WP-07: localization editor tab. Read-only consumer of the `editor.localization` contract
// (Editor_Web_Work_Plan.md 6.2, implemented by WP-06); this module never changes that shape.
//
// The design is driven by two facts about that resource:
//   * One physical file is one payload entry, and each pair file repeats the whole group's EN/ZH
//     arrays, so the GET payload is large (the 11-language Engineering Department groups repeat their
//     rows once per file). The payload is therefore indexed into per-group maps and never stored in
//     the resource state, and the table renders a bounded window of rows instead of the whole group.
//   * Only `english` / `simp_chinese` are editable; generated outputs and other languages are shown
//     read-only with the "edit the registered data source" hint from `read_only_reason`/`source_data`.
//
// Saving reuses the shared preview → confirm → commit flow (static/editor_panel.js) and the resource
// state (static/resource_state.js). The draft holds only the edited keys, never a copy of the loaded
// values, so the resource state stays cheap to clone and the dirty flag is exactly "some key differs
// from the loaded file".

import { createEditorPanel } from "./editor_panel.js";
import { renderLocalizationText, localizationTextWarnings } from "./localization_text.js";
import { ResourceState, resourceBase, setControlsBusy, setToolDirty } from "./resource_state.js";

const PAGE_SIZE = 200;
const EDITABLE_LANGUAGES = ["english", "simp_chinese"];
const LANGUAGE_LABELS = { english: "English", simp_chinese: "简体中文" };
// Contract 6.2: keys match [A-Za-z0-9_.-]+; values must not contain a physical CR/LF or NUL.
const KEY_PATTERN = /^[A-Za-z0-9_.-]+$/;
export const LOCALIZATION_FILTERS = { all: "全部", missing: "仅缺译", edited: "仅已改动" };
const WARNING_LABELS = {
  unknown_tag: "未知文本标记。标记名读到第一个非字母数字字符为止，`#Gfoo#!` 会被引擎当作名字为 Gfoo 的标记",
  unclosed_tag: "未闭合的文本标记",
  unmatched_close: "多余的 `#!` 收尾标记",
  unclosed_variable: "未闭合的 `$` 变量",
  unclosed_function: "未闭合的 `[` 函数",
};

/** Strip the characters the contract forbids in a value (a real CR/LF or NUL). */
export function sanitizeValue(value) {
  return String(value ?? "").replace(/[\r\n\x00]/g, "");
}

/**
 * Index `draft.roots` into bilingual groups.
 *
 * A group is one logical file: mod root + directory + stem, with one physical file per language. The
 * stem drops the `_l_<language>.yml` suffix, so all languages of the pair share a group.
 *
 * @param {{roots: Array<{root: string, files: Array<object>}>}} draft the contract's `draft`
 * @returns {Array<object>} groups with `values` maps, ordered `order`, `editable` and read-only hints
 */
export function groupLocalizationFiles(draft) {
  const groups = new Map();
  for (const { root, files } of draft?.roots || []) {
    for (const file of files) {
      const parts = file.path.split("/");
      const languageIndex = parts.indexOf("localization") + 1;
      const language = languageIndex > 0 ? parts[languageIndex] : "";
      const suffix = `_l_${language}.yml`;
      const basename = parts.at(-1);
      const name = basename.endsWith(suffix) ? basename.slice(0, -suffix.length) : basename;
      const directory = parts.slice(0, languageIndex > 0 ? languageIndex : parts.length - 1).join("/");
      const key = `${root}|${directory}|${name}`;
      let group = groups.get(key);
      if (!group) {
        group = { key, root, directory, name, files: {}, readOnly: false, reason: "", sourceData: [] };
        groups.set(key, group);
      }
      group.files[language] = file;
      // Either file of the pair being generated makes the whole pair read-only, so the guard cannot be
      // bypassed by editing the other language path (contract 6.2).
      group.readOnly ||= file.read_only === true;
      if (file.read_only && !group.reason) group.reason = file.read_only_reason || "";
      for (const path of file.source_data || []) if (!group.sourceData.includes(path)) group.sourceData.push(path);
    }
  }

  const result = [...groups.values()];
  // Ordered by root, directory and name rather than by the joined identity key: a `|` separator sorts
  // after `_`, which would otherwise put `src_engineering_department` ahead of `src`.
  result.sort((left, right) => left.root.localeCompare(right.root)
    || left.directory.localeCompare(right.directory)
    || left.name.localeCompare(right.name));
  for (const group of result) {
    // Every file of a group carries the same pair arrays, so one source is authoritative.
    const source = group.files.english || group.files.simp_chinese || Object.values(group.files)[0];
    const rows = (language) => source?.languages?.[language] || [];
    group.values = {
      english: new Map(rows("english").map((row) => [row.key, row.value])),
      simp_chinese: new Map(rows("simp_chinese").map((row) => [row.key, row.value])),
    };
    const order = [...group.values.english.keys()];
    const seen = new Set(order);
    for (const key of group.values.simp_chinese.keys()) if (!seen.has(key)) order.push(key);
    group.order = order;
    group.paths = { english: group.files.english?.path, simp_chinese: group.files.simp_chinese?.path };
    group.editable = Boolean(group.paths.english && group.paths.simp_chinese) && !group.readOnly;
    group.sourceData.sort();
  }
  return result;
}

function presenceFor(group, key, edits) {
  const edit = edits?.[group.key]?.[key];
  return {
    english: group.values.english.has(key) || typeof edit?.english === "string",
    simp_chinese: group.values.simp_chinese.has(key) || typeof edit?.simp_chinese === "string",
  };
}

/**
 * One table row's effective state: the value shown for each language (draft edit over loaded value),
 * whether each language currently has the key at all, and which side is missing a translation.
 *
 * @param {object} group a group from `groupLocalizationFiles`
 * @param {string} key localization key
 * @param {object} edits draft edits, `{groupKey: {key: {english?, simp_chinese?}}}`
 * @returns {{key: string, english: string, simp_chinese: string, present: object, missing: boolean,
 *   missingLanguages: string[], edited: boolean}}
 */
export function entryFor(group, key, edits) {
  const edit = edits?.[group.key]?.[key];
  const present = presenceFor(group, key, edits);
  const value = (language) => typeof edit?.[language] === "string"
    ? edit[language]
    : group.values[language].get(key) ?? "";
  const missingLanguages = [];
  if (present.english && !present.simp_chinese) missingLanguages.push("simp_chinese");
  if (!present.english && present.simp_chinese) missingLanguages.push("english");
  return {
    key,
    english: value("english"),
    simp_chinese: value("simp_chinese"),
    present,
    missing: missingLanguages.length > 0,
    missingLanguages,
    edited: edit !== undefined,
  };
}

/** Every entry of a group, in file order with keys that exist only in one language appended. */
export function entriesFor(group, edits) {
  const keys = Object.keys(edits?.[group.key] || {});
  const appended = keys.filter((key) => !group.values.english.has(key) && !group.values.simp_chinese.has(key));
  return [...group.order, ...appended].map((key) => entryFor(group, key, edits));
}

/**
 * Keys that are missing a translation in one of the two languages, mirroring the server's
 * bidirectional presence difference (the value is irrelevant; only presence counts).
 *
 * @returns {{english: string[], simp_chinese: string[]}} keys missing in that language's file
 */
export function missingKeysFor(group, edits) {
  const result = { english: [], simp_chinese: [] };
  for (const key of group.order) {
    const present = presenceFor(group, key, edits);
    if (present.english && !present.simp_chinese) result.simp_chinese.push(key);
    else if (!present.english && present.simp_chinese) result.english.push(key);
  }
  return result;
}

/** Resource-wide counts for the sidebar: editable groups/keys and missing translations across them. */
export function localizationSummary(groups, edits) {
  let editable = 0, keys = 0, missing = 0, generated = 0;
  for (const group of groups) {
    if (group.readOnly && group.sourceData.length) generated += 1;
    if (!group.editable) continue;
    editable += 1;
    keys += group.order.length;
    const absent = missingKeysFor(group, edits);
    missing += absent.english.length + absent.simp_chinese.length;
  }
  return { groups: groups.length, editable, keys, missing, generated };
}

/**
 * Edits that cannot be committed, checked before preview so the server's 400 is not the first report.
 * A new key (absent from both loaded languages) must carry both languages, exactly as contract 6.2
 * requires; a malformed key is rejected by the same pattern the server uses.
 *
 * @returns {string[]} one message per invalid key, empty when the draft is committable
 */
export function draftErrors(groups, edits) {
  const errors = [];
  for (const group of groups) {
    if (!group.editable) continue;
    for (const [key, edit] of Object.entries(edits?.[group.key] || {})) {
      if (!edit) continue;
      if (KEY_PATTERN.test(key) === false) {
        errors.push(`非法 key ${key}：只能使用字母、数字、下划线、点和短横线`);
        continue;
      }
      const known = group.values.english.has(key) || group.values.simp_chinese.has(key);
      if (known) continue;
      if (EDITABLE_LANGUAGES.some((language) => typeof edit[language] !== "string")) {
        errors.push(`新增键 ${key} 必须同时提供 English 与简体中文值`);
      }
    }
  }
  return errors;
}

/** Number of edited keys across all groups. */
export function editCount(edits) {
  return Object.values(edits || {}).reduce((total, changes) => total + Object.keys(changes).length, 0);
}

/**
 * Record one language's value for one key, keeping the draft equal to "what actually differs".
 * Writing a value back to the loaded one deletes the edit, so reverting clears the dirty flag; an
 * empty edit object removes its key, and an empty changes object removes its group.
 *
 * @returns {object} new edits object (the caller's is not mutated)
 */
export function writeEdit(edits, group, key, language, value) {
  const changes = { ...(edits?.[group.key] || {}) };
  const edit = { ...(changes[key] || {}) };
  if (value === group.values[language].get(key)) delete edit[language];
  else edit[language] = value;
  if (Object.keys(edit).length) changes[key] = edit;
  else delete changes[key];
  const next = { ...(edits || {}) };
  if (Object.keys(changes).length) next[group.key] = changes;
  else delete next[group.key];
  return next;
}

/**
 * Materialize the contract request body: `{edits: {path: {key: {language: value}}}, base}`.
 *
 * Every entry goes through the group's english path — the pair's two paths are equally valid entries,
 * and using one of them can never name the same key/language twice. Languages whose value equals the
 * loaded one are omitted, so the request carries only real changes.
 *
 * @returns {{edits: object, base: object}} request body for preview/commit
 */
export function buildEdits(groups, edits, base) {
  const result = {};
  for (const group of groups) {
    const changes = edits?.[group.key];
    if (!changes) continue;
    const path = group.paths.english || group.paths.simp_chinese;
    const fields = {};
    for (const [key, edit] of Object.entries(changes)) {
      if (!edit) continue;
      const values = {};
      for (const language of EDITABLE_LANGUAGES) {
        const value = edit[language];
        if (typeof value !== "string") continue;
        if (group.values[language].get(key) === value) continue;
        values[language] = value;
      }
      if (Object.keys(values).length) fields[key] = values;
    }
    if (Object.keys(fields).length) result[path] = fields;
  }
  return { edits: result, base };
}

function entryMatchesFilter(entry, filter) {
  if (filter === "missing") return entry.missing;
  if (filter === "edited") return entry.edited;
  return true;
}

function entryMatchesQuery(entry, query) {
  if (!query) return true;
  const needle = query.toLowerCase();
  return entry.key.toLowerCase().includes(needle)
    || entry.english.toLowerCase().includes(needle)
    || entry.simp_chinese.toLowerCase().includes(needle);
}

/** Apply the toolbar's filter and search to a group's entries. */
export function filterEntries(entries, filter, query) {
  const needle = String(query || "").trim();
  return entries.filter((entry) => entryMatchesFilter(entry, filter) && entryMatchesQuery(entry, needle));
}

export function createLocalizationPanel(root, { pageSize = PAGE_SIZE } = {}) {
  root.dataset.busy = "false";
  root.innerHTML = `<div class="localization-layout">
    <aside class="localization-sidebar">
      <div>
        <p class="eyebrow">Localization</p>
        <strong>文件分组</strong>
      </div>
      <label class="localization-search">
        <span>搜索</span>
        <input type="search" data-search placeholder="key / English / 中文">
      </label>
      <div class="localization-filters" data-filters></div>
      <div class="localization-groups" data-groups></div>
      <p class="localization-counts" data-counts role="status"></p>
    </aside>
    <main class="localization-main">
      <h2 data-title>未选择分组</h2>
      <p class="localization-current" data-meta></p>
      <p class="localization-note" data-note hidden></p>
      <div class="localization-toolbar">
        <button type="button" data-add-toggle>新增条目</button>
        <span class="localization-dirty hidden" data-dirty></span>
        <span class="localization-counts" data-table-count></span>
      </div>
      <div class="localization-new-row" data-new-row hidden>
        <input type="text" data-new-key placeholder="新 key（字母、数字、下划线、点、短横线）">
        <input type="text" data-new-english placeholder="English（必填）">
        <input type="text" data-new-chinese placeholder="简体中文（必填）">
        <button type="button" data-new-add>添加条目</button>
      </div>
      <div class="localization-scroll" data-table></div>
      <button type="button" data-more hidden>显示更多</button>
      <div class="localization-preview" data-preview hidden></div>
      <div class="localization-actions">
        <button type="button" id="loc-save-btn" class="primary-button">保存</button>
        <button type="button" id="loc-reload-btn">重新加载</button>
      </div>
      <p id="loc-status" class="job-status" role="status">就绪</p>
      <pre id="loc-log"></pre>
    </main>
  </div>`;

  const nodes = {
    search: root.querySelector("[data-search]"),
    filters: root.querySelector("[data-filters]"),
    groups: root.querySelector("[data-groups]"),
    counts: root.querySelector("[data-counts]"),
    title: root.querySelector("[data-title]"),
    meta: root.querySelector("[data-meta]"),
    note: root.querySelector("[data-note]"),
    addToggle: root.querySelector("[data-add-toggle]"),
    dirty: root.querySelector("[data-dirty]"),
    tableCount: root.querySelector("[data-table-count]"),
    newRow: root.querySelector("[data-new-row]"),
    newKey: root.querySelector("[data-new-key]"),
    newEnglish: root.querySelector("[data-new-english]"),
    newChinese: root.querySelector("[data-new-chinese]"),
    newAdd: root.querySelector("[data-new-add]"),
    table: root.querySelector("[data-table]"),
    more: root.querySelector("[data-more]"),
    preview: root.querySelector("[data-preview]"),
    save: root.querySelector("#loc-save-btn"),
    reload: root.querySelector("#loc-reload-btn"),
  };

  const state = {
    groups: [],
    activeKey: null,
    filter: "all",
    query: "",
    limit: pageSize,
    selectedKey: null,
    loaded: false,
    rowNodes: new Map(),
    resource: new ResourceState({
      saved: { edits: {} },
      draft: { edits: {} },
      isDirty: (_saved, draft) => editCount(draft.edits) > 0,
      onChange: () => syncControls(),
      onDirtyChange: (dirty) => setToolDirty("localization", dirty),
    }),
  };
  // Entries are derived from the loaded values plus the draft, so a table of tens of thousands of rows
  // is rebuilt only when the values behind it change; every edit invalidates this cache once.
  const entryCache = new Map();

  const edits = () => state.resource.draft.edits;
  const activeGroup = () => state.groups.find((group) => group.key === state.activeKey) || null;

  function entriesOf(group) {
    if (!entryCache.has(group.key)) entryCache.set(group.key, entriesFor(group, edits()));
    return entryCache.get(group.key);
  }

  function setStatus(text, kind = "default") {
    editor.status.set(text, kind);
  }

  function applyPayload(payload) {
    state.groups = groupLocalizationFiles(payload.draft);
    entryCache.clear();
    // Prefer an editable group: the generated ones are read-only showcases.
    const first = state.groups.find((group) => group.editable) || state.groups[0] || null;
    if (!state.groups.some((group) => group.key === state.activeKey)) state.activeKey = first?.key ?? null;
    state.limit = pageSize;
    state.selectedKey = null;
    state.loaded = true;
    // The payload itself is not retained: the heavy arrays are already indexed into the group maps.
    state.resource.replace({ base: resourceBase(payload), saved: { edits: {} }, draft: { edits: {} } });
  }

  function updateEdit(group, key, language, value) {
    if (state.resource.busy) return false;
    const applied = state.resource.mutate((draft) => {
      draft.edits = writeEdit(draft.edits, group, key, language, value);
    });
    if (!applied) return false;
    entryCache.clear();
    state.selectedKey = key;
    updateRow(group, key);
    renderCounts();
    renderPreview();
    return true;
  }

  function syncControls() {
    const busy = state.resource.busy;
    root.dataset.busy = String(busy);
    const controls = [...root.querySelectorAll("button, input")].filter((node) => node !== nodes.save);
    setControlsBusy(controls, busy);
    const changes = editCount(edits());
    // Disabled while there is nothing to send: preview/commit of an empty edit set writes nothing.
    nodes.save.disabled = busy || changes === 0;
    nodes.dirty.textContent = `未保存的更改（${changes} 个键）`;
    nodes.dirty.classList.toggle("hidden", changes === 0);
    nodes.addToggle.disabled = busy || !activeGroup()?.editable;
  }

  function renderFilters() {
    nodes.filters.innerHTML = "";
    for (const [id, label] of Object.entries(LOCALIZATION_FILTERS)) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.filter = id;
      button.textContent = label;
      button.classList.toggle("active", state.filter === id);
      button.addEventListener("click", () => {
        if (state.filter === id) return;
        state.filter = id;
        state.limit = pageSize;
        renderFilters();
        renderTable();
      });
      nodes.filters.appendChild(button);
    }
  }

  function renderGroups() {
    nodes.groups.innerHTML = "";
    for (const group of state.groups) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "localization-group";
      button.dataset.group = group.key;
      button.classList.toggle("active", group.key === state.activeKey);
      const name = document.createElement("span");
      name.className = "localization-group-name";
      name.textContent = group.name;
      const meta = document.createElement("span");
      meta.className = "localization-group-meta";
      const languages = Object.keys(group.files).map((language) => LANGUAGE_LABELS[language] || language).join("/");
      meta.textContent = `${group.root} · ${languages} · ${group.order.length} 键${group.editable ? "" : " · 只读"}`;
      button.appendChild(name);
      button.appendChild(meta);
      button.addEventListener("click", () => {
        if (state.resource.busy || group.key === state.activeKey) return;
        state.activeKey = group.key;
        state.limit = pageSize;
        state.selectedKey = null;
        renderGroups();
        renderTitle();
        renderTable();
        renderPreview();
        syncControls();
      });
      nodes.groups.appendChild(button);
    }
  }

  function renderTitle() {
    const group = activeGroup();
    nodes.title.textContent = group ? group.name : "未选择分组";
    nodes.meta.textContent = group
      ? `${group.root} · ${group.directory} · ${group.order.length} 个键${group.editable ? "" : "（只读）"}`
      : "";
    const generated = group && group.readOnly && group.sourceData.length;
    nodes.note.hidden = !group || !group.readOnly;
    nodes.note.textContent = !group || !group.readOnly ? "" : generated
      ? `该分组是生成物（只读）。应改其 data 源：${group.sourceData.join("、")}`
      : `该分组只读：${group.reason || "只有 english 与 simp_chinese 可编辑"}`;
  }

  function updateRow(group, key) {
    const node = state.rowNodes.get(key);
    if (!node) return;
    const entry = entryFor(group, key, edits());
    node.row.dataset.missing = String(entry.missing);
    node.row.dataset.edited = String(entry.edited);
    for (const language of EDITABLE_LANGUAGES) {
      node.inputs[language].dataset.missing = String(entry.missingLanguages.includes(language));
      node.cells[language].dataset.missing = String(entry.missingLanguages.includes(language));
    }
  }

  function valueInput(group, entry, language) {
    const input = document.createElement("input");
    input.type = "text";
    input.dataset.key = entry.key;
    input.dataset.language = language;
    input.value = entry[language];
    input.disabled = !group.editable;
    input.dataset.missing = String(entry.missingLanguages.includes(language));
    input.addEventListener("input", () => {
      updateEdit(group, entry.key, language, sanitizeValue(input.value));
    });
    input.addEventListener("focus", () => {
      state.selectedKey = entry.key;
      renderPreview();
    });
    return input;
  }

  function renderRow(group, entry) {
    const row = document.createElement("tr");
    row.className = "localization-row";
    row.dataset.key = entry.key;
    row.dataset.missing = String(entry.missing);
    row.dataset.edited = String(entry.edited);
    const keyCell = document.createElement("td");
    keyCell.className = "localization-key";
    keyCell.textContent = entry.key;
    row.appendChild(keyCell);
    const inputs = {}, cells = {};
    for (const language of EDITABLE_LANGUAGES) {
      const cell = document.createElement("td");
      cell.dataset.language = language;
      cell.dataset.missing = String(entry.missingLanguages.includes(language));
      if (group.editable) {
        const input = valueInput(group, entry, language);
        cell.appendChild(input);
        inputs[language] = input;
      } else {
        // Read-only groups still show the value; the note above names the data source to edit instead.
        cell.textContent = entry[language];
      }
      row.appendChild(cell);
      cells[language] = cell;
    }
    state.rowNodes.set(entry.key, { row, inputs, cells });
    return row;
  }

  function renderTable() {
    nodes.table.innerHTML = "";
    state.rowNodes.clear();
    nodes.more.hidden = true;
    const group = activeGroup();
    if (!group) {
      const empty = document.createElement("p");
      empty.className = "localization-empty";
      empty.textContent = "没有可显示的文件分组。";
      nodes.table.appendChild(empty);
      nodes.tableCount.textContent = "";
      return;
    }
    const entries = filterEntries(entriesOf(group), state.filter, state.query);
    const visible = entries.slice(0, state.limit);
    nodes.tableCount.textContent = `显示 ${visible.length} / ${entries.length} 条（分组共 ${group.order.length} 键）`;
    const table = document.createElement("table");
    table.className = "localization-table";
    table.innerHTML = `<colgroup><col class="key"><col class="en"><col class="zh"></colgroup>
      <thead><tr><th>Key</th><th>English</th><th>简体中文</th></tr></thead><tbody></tbody>`;
    const body = table.querySelector("tbody");
    for (const entry of visible) body.appendChild(renderRow(group, entry));
    nodes.table.appendChild(table);
    nodes.more.hidden = entries.length <= state.limit;
    nodes.more.textContent = `显示更多（还有 ${Math.max(0, entries.length - state.limit)} 条）`;
  }

  function renderCounts() {
    const summary = localizationSummary(state.groups, edits());
    nodes.counts.textContent = state.groups.length
      ? `已加载 ${summary.groups} 个分组（可编辑 ${summary.editable} 个，生成物 ${summary.generated} 个）；可编辑键 ${summary.keys}；缺译 ${summary.missing} 处`
      : "尚未加载。";
  }

  function renderPreview() {
    const group = activeGroup();
    const entry = group && state.selectedKey !== null
      ? entryFor(group, state.selectedKey, edits())
      : null;
    nodes.preview.hidden = !entry;
    if (!entry) {
      nodes.preview.innerHTML = "";
      return;
    }
    nodes.preview.innerHTML = "";
    const heading = document.createElement("h3");
    heading.textContent = `游戏内近似预览 · ${entry.key}`;
    nodes.preview.appendChild(heading);
    for (const language of EDITABLE_LANGUAGES) {
      const row = document.createElement("div");
      row.className = "localization-preview-row";
      const label = document.createElement("span");
      label.className = "localization-preview-label";
      label.textContent = LANGUAGE_LABELS[language];
      const text = document.createElement("div");
      text.className = "localization-preview-text";
      text.dataset.language = language;
      // Renders the supported tags/variables/functions; unsupported markup stays visible as a
      // placeholder (see static/localization_text.js for the supported/unsupported scope).
      text.innerHTML = renderLocalizationText(entry[language]);
      row.appendChild(label);
      row.appendChild(text);
      nodes.preview.appendChild(row);
      const warnings = [];
      for (const warning of localizationTextWarnings(entry[language])) {
        warnings.push(`${WARNING_LABELS[warning.type] || warning.type}（第 ${warning.index + 1} 个字符）`);
      }
      if (warnings.length) {
        const list = document.createElement("ul");
        list.className = "localization-preview-warnings";
        for (const warning of warnings) {
          const item = document.createElement("li");
          item.textContent = warning;
          list.appendChild(item);
        }
        nodes.preview.appendChild(list);
      }
    }
    const note = document.createElement("p");
    note.className = "localization-note";
    note.textContent = "预览为近似效果：不渲染 @icon! 贴图，不展开变量与本地化函数，也不还原字体与排版。";
    nodes.preview.appendChild(note);
  }

  function render() {
    renderFilters();
    renderGroups();
    renderTitle();
    renderTable();
    renderCounts();
    renderPreview();
    syncControls();
  }

  function addKey() {
    const group = activeGroup();
    if (!group || !group.editable) {
      setStatus("只读分组不能新增条目", "error");
      return;
    }
    const key = nodes.newKey.value.trim();
    const english = sanitizeValue(nodes.newEnglish.value);
    const chinese = sanitizeValue(nodes.newChinese.value);
    if (!KEY_PATTERN.test(key)) {
      setStatus("key 只能使用字母、数字、下划线、点和短横线", "error");
      return;
    }
    if (group.values.english.has(key) || group.values.simp_chinese.has(key) || Object.hasOwn(edits()[group.key] || {}, key)) {
      setStatus(`key 已存在：${key}`, "error");
      return;
    }
    // A new key is required to carry both languages (contract 6.2), so the form asks for both.
    if (!english || !chinese) {
      setStatus(`新增键 ${key} 必须同时提供 English 与简体中文值`, "error");
      return;
    }
    state.resource.mutate((draft) => {
      let next = writeEdit(draft.edits, group, key, "english", english);
      next = writeEdit(next, group, key, "simp_chinese", chinese);
      draft.edits = next;
    });
    entryCache.clear();
    nodes.newKey.value = "";
    nodes.newEnglish.value = "";
    nodes.newChinese.value = "";
    state.selectedKey = key;
    setStatus(`已加入 ${key}（尚未保存）`);
    renderTable();
    renderCounts();
    renderPreview();
  }

  nodes.search.addEventListener("input", () => {
    state.query = nodes.search.value;
    state.limit = pageSize;
    renderTable();
  });
  nodes.addToggle.addEventListener("click", () => {
    nodes.newRow.hidden = !nodes.newRow.hidden;
    if (!nodes.newRow.hidden) nodes.newKey.focus();
  });
  nodes.newAdd.addEventListener("click", () => addKey());
  nodes.more.addEventListener("click", () => {
    state.limit += pageSize;
    renderTable();
  });

  const editor = createEditorPanel({
    prefix: "loc",
    resourceId: "editor.localization",
    resource: state.resource,
    request: () => buildEdits(state.groups, edits(), state.resource.base),
    apply: applyPayload,
    buttons: { save: nodes.save, reload: nodes.reload },
    beforeSave: () => {
      const errors = draftErrors(state.groups, edits());
      if (errors.length) {
        setStatus(errors[0], "error");
        return false;
      }
      return true;
    },
    // Saving writes localization files only and runs no generator, so the shared "保存并重新生成"
    // wording is wrong here; this panel passes its own copy (see editor_panel.js defaultEditorCopy).
    copy: {
      saving: "正在保存本地化文件",
      previewChanges: (count) => `${count} 个本地化条目变更；确认后写入文件（不触发生成）。`,
      previewNoChanges: "没有内容差异；确认后仍会写入本地化文件（不触发生成）。",
    },
    onSaved: (payload) => {
      editor.log.report(payload);
      editor.log.append("\n[ok] 本地化文件已保存（不触发生成）。\n");
      editor.status.set("本地化文件已保存");
    },
    onLoaded: (payload) => {
      const missing = (payload.draft.missing_translations || [])
        .reduce((total, entry) => total + entry.keys.length, 0);
      editor.status.set(missing
        ? `已加载；服务端报告缺译 ${missing} 处，提交会被拒绝`
        : "已加载");
    },
    afterLoad: async () => { render(); },
    afterSave: async () => { render(); },
  });

  window.addEventListener("keydown", (event) => {
    if (document.body?.dataset?.activeTool !== "localization") return;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
      event.preventDefault();
      void editor.save();
    }
  });

  render();

  return {
    state,
    render,
    addKey,
    entriesOf,
    load: () => editor.load({ context: { initial: true } }),
    save: () => editor.save(),
  };
}

// Page entry: the resource is a large GET, so the tab loads it on first activation instead of at page
// load. shared.js dispatches `tool-activated` when a tab becomes visible.
const root = document.getElementById("localization-root");
const page = root ? createLocalizationPanel(root) : null;
document.addEventListener("tool-activated", (event) => {
  if (event.detail?.tool !== "localization" || !page || page.state.loaded) return;
  void page.load();
});
