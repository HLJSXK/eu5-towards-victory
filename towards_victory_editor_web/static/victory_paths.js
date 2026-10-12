import { fetchJson } from "./api.js";
import { createDiffView } from "./editor_panel.js";
import { createLogView, createStatusView } from "./display.js";
import { ResourceState, setControlsBusy, setToolDirty } from "./resource_state.js";

const RESOURCE_ID = "editor.victory_paths";
const URL = `api/resources/${RESOURCE_ID}`;
const COPY = {
  saving: "正在保存胜利路径并生成登记产物",
  previewChanges: (count) => `${count} 个字段变更；确认后由后端保存源数据并生成登记产物。`,
  previewNoChanges: "没有字段差异；是否保存以服务端生成计划为准。",
};

function indexOf(container, part) {
  return typeof part === "object"
    ? container.findIndex((item) => Object.entries(part).every(([key, value]) => item[key] === value))
    : part;
}

export function fieldValue(document, address) {
  let value = document;
  for (const part of address) {
    if (value === undefined || value === null) return undefined;
    value = value[indexOf(value, part)];
  }
  return value;
}

export function fieldName(address) {
  return address.map((part, index) => typeof part === "object"
    ? `[${Object.values(part).join(":")}]`
    : typeof part === "number" ? `[${part}]` : `${index ? "." : ""}${part}`).join("");
}

function assignField(document, address, value) {
  const parent = fieldValue(document, address.slice(0, -1));
  parent[indexOf(parent, address.at(-1))] = structuredClone(value);
}

function sameValue(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function fieldsOf(value, address, readOnly = false) {
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    return Object.entries(value).flatMap(([key, child]) => fieldsOf(child, [...address, key], readOnly));
  }
  return [{ address, name: fieldName(address), value, readOnly,
    kind: value === null || Array.isArray(value) ? "json" : typeof value }];
}

export function victoryFieldGroups(document, pathId) {
  const groups = [{ key: "shared", title: "共享字段", fields: fieldsOf(document.shared, ["shared"]) }];
  const path = document.paths.find((item) => item.id === pathId);
  if (path) {
    const address = ["paths", { id: pathId }];
    groups.push({ key: "path", title: `路径基础 · ${pathId}`, open: true,
      fields: Object.entries(path).filter(([key]) => !["gui", "loc", "milestones", "tasks"].includes(key))
        .flatMap(([key, value]) => fieldsOf(value, [...address, key], key === "id")) });
    groups.push({ key: "gui", title: "路径 GUI", fields: fieldsOf(path.gui, [...address, "gui"]) });
    groups.push({ key: "loc", title: "路径本地化", fields: fieldsOf(path.loc, [...address, "loc"]) });
    for (const milestone of path.milestones) {
      const milestoneAddress = [...address, "milestones", { n: milestone.n }];
      groups.push({ key: `milestone-${milestone.n}`, title: `里程碑 ${milestone.n}`, open: milestone.n === 1,
        fields: Object.entries(milestone).flatMap(([key, value]) => key === "reward_options"
          ? [{ address: [...milestoneAddress, key], name: fieldName([...milestoneAddress, key]), value,
            readOnly: true, kind: "json" }]
          : fieldsOf(value, [...milestoneAddress, key], key === "n")) });
    }
    groups.push({ key: "task-settings", title: "三槽任务 · 目录设置", slots: true,
      fields: [...fieldsOf(path.tasks.label, [...address, "tasks", "label"]),
        ...fieldsOf(path.tasks.color, [...address, "tasks", "color"])] });
    for (const task of path.tasks.items) {
      const taskAddress = [...address, "tasks", "items", { task_id: task.task_id }];
      groups.push({ key: `task-${task.task_id}`, title: `任务 ${task.task_id} · ${task.fields.key} (${task.fields.type})`,
        fields: [...fieldsOf(task.task_id, [...taskAddress, "task_id"], true),
          ...fieldsOf(task.source, [...taskAddress, "source"], true),
          ...fieldsOf(task.fields, [...taskAddress, "fields"])] });
    }
  }
  groups.push({ key: "on-actions", title: "共享 on_actions（JSON）", fields: fieldsOf(document.on_actions, ["on_actions"]) });
  groups.push({ key: "national-special", title: "国家特殊任务（独立目录）", fields: [] });
  for (const task of document.national_special.tasks) {
    const address = ["national_special", "tasks", { task_id: task.task_id }];
    groups.push({ key: `national-${task.task_id}`, title: `国家特殊任务 ${task.task_id} · ${task.fields.key}`,
      fields: [...fieldsOf(task.task_id, [...address, "task_id"], true),
        ...fieldsOf(task.source, [...address, "source"], true), ...fieldsOf(task.fields, [...address, "fields"])] });
  }
  return groups;
}

export function stageVictoryEdit(document, edits, field, raw) {
  if (field.readOnly) return false;
  const key = JSON.stringify(field.address);
  let value = raw, error = "";
  try {
    if (field.kind === "number") {
      value = Number(raw);
      if (!String(raw).trim() || !Number.isFinite(value)) throw new Error("请输入有限数字");
    } else if (field.kind === "json") {
      value = JSON.parse(raw);
    }
  } catch (problem) { error = problem.message; }
  if (!error && sameValue(fieldValue(document, field.address), value)) delete edits[key];
  else edits[key] = { address: field.address, raw, kind: field.kind, value, error };
  return true;
}

export function rebaseVictoryEdits(before, after, edits) {
  const kept = {}, warnings = [];
  for (const [key, edit] of Object.entries(edits)) {
    const latest = fieldValue(after, edit.address);
    const name = fieldName(edit.address);
    if (latest === undefined) {
      kept[key] = { ...edit, orphan: true };
      warnings.push(`${name} 已移除；草稿仍保留，恢复条目或移除该草稿后才可提交。`);
      continue;
    }
    if (!sameValue(fieldValue(before, edit.address), latest)) warnings.push(`${name} 原值已变化；保留用户草稿。`);
    if (edit.error || !sameValue(latest, edit.value)) kept[key] = { ...edit, orphan: false };
  }
  return { edits: kept, warnings };
}

export function buildVictoryRequest(document, resource, message = "") {
  const candidate = structuredClone(document);
  for (const edit of Object.values(resource.draft.edits)) {
    if (edit.error || edit.orphan) throw new Error(`草稿字段不可提交：${fieldName(edit.address)}`);
    assignField(candidate, edit.address, edit.value);
  }
  return { document: candidate, base: { sources: Object.entries(resource.base).map(([path, sha256]) => ({ path, sha256 })) }, message };
}

export function missingRewardReferences(references) {
  return (references?.rewards || []).filter((item) => !item.resolved);
}

export function victoryPreview(preview) {
  return { diff: preview.diff.fields,
    file_diff: preview.diff.sources.filter((item) => item.changed).map((item) => ({ path: item.path,
      field: "源文件摘要", before: item.before_sha256, after: item.after_sha256 })),
    generation_plan: preview.generation };
}

export function generationPlanText(plan, artifacts = []) {
  if (!plan) return "尚未加载生成计划。";
  const lines = [`生成计划：${plan.required ? "源字段已变化，提交后执行" : "当前未要求执行"}；${plan.generators.length} 个生成器；${plan.outputs.length} 个只读产物。`,
    `注册表：${plan.registry_complete ? "完整" : "不完整，禁止提交"}`,
    ...plan.steps.map((step, index) => `${index + 1}. ${step.script}\n${step.outputs.map((path) => `   ${path}`).join("\n")}`),
    "只读产物（去重）：", ...plan.outputs,
    ...(plan.errors || []).map((item) => `${item.path}: ${item.message}`)];
  if (artifacts.length) lines.push("最近提交的产物报告：", ...artifacts.map((item) => `${item.path}: ${item.changed ? "已变化" : "未变化"}`));
  return lines.join("\n");
}

export function createVictoryPathsController({ api = fetchJson, confirmPreview = async () => false,
  onChange = () => {}, onDocument = () => {}, status = () => {}, diagnostic = () => {}, report = () => {},
  onCommitted = () => {} } = {}) {
  const state = { document: null, references: { rewards: [], tasks: [] }, plan: null, artifacts: [],
    validation: { errors: [], warnings: [] }, loaded: false, refreshPending: false,
    resource: new ResourceState({ saved: { edits: {} }, isDirty: (_saved, draft) => Object.keys(draft.edits).length > 0,
      onChange, onDirtyChange: (dirty) => setToolDirty("victory-paths", dirty) }) };
  const resource = state.resource;
  const localErrors = () => Object.values(resource.draft.edits).filter((edit) => edit.error || edit.orphan);
  const blocked = () => !state.loaded || localErrors().length > 0 || missingRewardReferences(state.references).length > 0
    || !state.plan?.registry_complete;

  function install(payload, keepDrafts = false, committed = false) {
    const rebased = keepDrafts ? rebaseVictoryEdits(state.document, payload.document, resource.draft.edits) : { edits: {}, warnings: [] };
    state.document = structuredClone(payload.document);
    state.references = payload.references;
    state.plan = committed ? { ...state.plan, required: false } : payload.generation;
    state.artifacts = committed ? payload.generation.artifacts : [];
    state.validation = { errors: [], warnings: rebased.warnings.map((message) => ({ path: "同步", message })) };
    state.loaded = true;
    resource.replace({ base: Object.fromEntries(payload.sources.map(({ path, sha256 }) => [path, sha256])),
      saved: { edits: {} }, draft: { edits: rebased.edits } });
    for (const warning of rebased.warnings) diagnostic(`[warning] ${warning}`);
    onDocument();
  }

  function acceptReport(payload, validation) {
    state.references = payload.references;
    state.plan = payload.generation;
    state.validation = validation;
    onChange();
  }

  function error(problem, label) {
    diagnostic(`${label}: ${problem.message}`);
    report(problem);
    status(`${label}: ${problem.message}`, "error");
    if (problem.status === 409 && problem.code !== "resource_busy") state.refreshPending = true;
  }

  async function refreshKeepingDrafts() {
    state.refreshPending = true;
    while (state.refreshPending && !resource.busy) {
      state.refreshPending = false;
      status("正在刷新源数据与奖励引用，保留草稿", "working");
      try {
        await resource.run("loading", () => api(URL), { apply: (payload) => install(payload, true) });
        status("已刷新；草稿已保留，原值冲突见日志");
      } catch (problem) { error(problem, "刷新失败，旧 base 与草稿已保留"); state.refreshPending = false; }
    }
  }

  async function drainRefresh() {
    if (state.refreshPending) await refreshKeepingDrafts();
  }

  async function load() {
    if (resource.busy) return;
    status("正在加载胜利路径", "working");
    try {
      await resource.run("loading", () => api(URL), { apply: (payload) => install(payload) });
      status("已加载胜利路径；产物与奖励引用只读");
    } catch (problem) { error(problem, "加载失败，草稿已保留"); }
    await drainRefresh();
  }

  function edit(field, raw) {
    if (resource.busy || field.readOnly) return false;
    state.validation = { errors: [], warnings: [] };
    return resource.mutate((draft) => stageVictoryEdit(state.document, draft.edits, field, raw));
  }

  async function validate() {
    if (resource.busy || !state.loaded || localErrors().length) return;
    status("正在校验草稿与奖励引用", "working");
    try {
      const payload = await resource.run("validating", () => api(`${URL}/validate`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(buildVictoryRequest(state.document, resource)),
      }), { apply: (payload) => acceptReport(payload, { errors: payload.errors, warnings: payload.warnings }) });
      status(payload.valid ? "校验通过；未写入文件、未执行生成器" : "校验失败，禁止提交", payload.valid ? "default" : "error");
    } catch (problem) { error(problem, "校验失败，草稿已保留"); }
    await drainRefresh();
  }

  async function save(message = "") {
    if (resource.busy || blocked()) return;
    let committed;
    try {
      await resource.run("saving", async () => {
        const options = { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(buildVictoryRequest(state.document, resource, message)) };
        status("正在校验草稿", "working");
        const validation = await api(`${URL}/validate`, options);
        acceptReport(validation, { errors: validation.errors, warnings: validation.warnings });
        if (!validation.valid || missingRewardReferences(validation.references).length || !validation.generation.registry_complete) {
          status("校验失败或奖励引用失效，禁止提交", "error");
          return null;
        }
        status("正在获取只读预览", "working");
        const preview = await api(`${URL}/preview`, options);
        acceptReport(preview, preview.validation);
        if (!preview.ready || missingRewardReferences(preview.references).length || !preview.generation.registry_complete) {
          status("预览未就绪或奖励引用失效，禁止提交", "error");
          return null;
        }
        status("请确认字段变更与生成计划", "working");
        if (!await confirmPreview(victoryPreview(preview))) {
          status("已返回编辑，草稿与 base 已保留");
          return null;
        }
        status(COPY.saving, "working");
        return api(`${URL}/commit`, options);
      }, { apply: (payload) => {
        if (!payload) return;
        committed = payload;
        install(payload, false, true);
        report(payload);
        status("已保存；生成与恢复结果见报告");
      } });
    } catch (problem) { error(problem, committed ? "已保存，但页面更新失败" : "保存失败，草稿已保留"); }
    if (committed) onCommitted(committed);
    await drainRefresh();
  }

  function handleCommitted(detail) {
    if (!state.loaded || detail.resourceId === RESOURCE_ID) return;
    if (detail.resourceId === "editor.cost_reward" || detail.writtenPaths.some((path) => Object.hasOwn(resource.base, path))) {
      void refreshKeepingDrafts();
    }
  }

  return { state, blocked, localErrors, edit, load, validate, save, refreshKeepingDrafts, handleCommitted };
}

export function createVictoryPathsPanel(root, { api = fetchJson, confirmPreview } = {}) {
  root.innerHTML = `<div class="victory-paths-layout">
    <aside class="victory-paths-sidebar"><h2>路径列表</h2><nav data-paths aria-label="胜利路径列表"></nav>
      <p data-dirty role="status"></p><div data-drafts></div></aside>
    <div class="victory-paths-main">
      <div class="actions"><button id="vp-validate-btn" type="button">校验草稿</button>
        <button id="vp-save-btn" type="button" class="primary-button">预览并保存</button>
        <button id="vp-refresh-btn" type="button">刷新并保留草稿</button>
        <button id="vp-reload-btn" type="button">重新加载</button></div>
      <p id="vp-status" class="job-status" role="status">打开标签页后加载</p>
      <div data-validation role="status"></div><div data-fields></div>
      <section class="victory-paths-references"><h2>奖励引用（只读）</h2>
        <p>引用状态由后端解析；失效时禁止提交。奖励目录值请到花费/奖励编辑器修改，再刷新本页。</p>
        <div data-references></div></section>
      <details class="victory-paths-plan" open><summary>生成计划与只读产物</summary>
        <p>计划来自最近一次加载、校验或预览；草稿修改后需重新校验，实际执行由提交决定。</p><pre data-plan></pre></details>
      <details><summary>源文件 base 与写入边界</summary><pre data-sources></pre>
        <p>只写两个源文件；保留 BOM、文件头注释及换行风格，不保留正文注释，未改键的顺序不保证。</p></details>
      <pre id="vp-log"></pre>
    </div></div>`;
  const nodes = Object.fromEntries(["paths", "dirty", "drafts", "validation", "fields", "references", "plan", "sources"]
    .map((name) => [name, root.querySelector(`[data-${name}]`)]));
  const buttons = Object.fromEntries(["validate", "save", "refresh", "reload"]
    .map((name) => [name, root.querySelector(`#vp-${name}-btn`)]));
  const status = createStatusView(root.querySelector("#vp-status"));
  const log = createLogView(root.querySelector("#vp-log"));
  const diff = createDiffView(document.getElementById("vp-preview"), COPY);
  let activePath = null;
  const controller = createVictoryPathsController({ api, confirmPreview: confirmPreview || diff.confirm,
    onChange: sync, onDocument: render, status: (text, kind) => status.set(text, kind),
    diagnostic: (text) => log.append(`\n${text}\n`), report: (payload) => {
      log.report(payload);
      const rollback = payload.rollback || payload.operation?.details?.rollback;
      if (rollback) log.append(`\n恢复结果: ${JSON.stringify(rollback)}\n`);
    }, onCommitted: (payload) => {
      if (payload.written_paths.length) window.dispatchEvent(new CustomEvent("resource-committed", {
        detail: { resourceId: RESOURCE_ID, writtenPaths: payload.written_paths },
      }));
      window.dispatchEvent(new CustomEvent("resource-saved", { detail: { resourceId: RESOURCE_ID } }));
    } });
  const { state } = controller;

  function sync() {
    const { resource } = state;
    root.dataset.busy = String(resource.busy);
    setControlsBusy(root.querySelectorAll("button, input, textarea, select"), resource.busy);
    buttons.save.disabled = resource.busy || controller.blocked();
    buttons.validate.disabled = resource.busy || !state.loaded || controller.localErrors().length > 0;
    nodes.dirty.textContent = resource.dirty ? `未保存草稿：${Object.keys(resource.draft.edits).length} 个字段` : "无未保存草稿";
    nodes.drafts.replaceChildren();
    for (const [key, edit] of Object.entries(resource.draft.edits)) {
      if (!edit.orphan) continue;
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `移除失去目标的草稿：${fieldName(edit.address)}`;
      button.disabled = resource.busy;
      button.addEventListener("click", () => resource.mutate((draft) => { delete draft.edits[key]; }));
      nodes.drafts.appendChild(button);
    }
    nodes.validation.textContent = [...controller.localErrors().map((edit) => `${fieldName(edit.address)}: ${edit.orphan ? "目标已移除，草稿保留" : edit.error}`),
      ...state.validation.errors.map((item) => `错误 · ${item.path}: ${item.message}`),
      ...state.validation.warnings.map((item) => `提示 · ${item.path}: ${item.message}`)].join("\n");
    nodes.references.replaceChildren();
    for (const reference of state.references.rewards) {
      const row = document.createElement("p");
      row.dataset.resolved = String(reference.resolved);
      row.textContent = `${reference.key} · ${reference.resolved ? "已解析" : "引用失效，禁止提交"} · ${reference.source_resource} · 只读`;
      nodes.references.appendChild(row);
    }
    nodes.plan.textContent = generationPlanText(state.plan, state.artifacts);
    nodes.sources.textContent = JSON.stringify(state.resource.base, null, 2);
  }

  function renderField(field) {
    const label = document.createElement("label");
    label.className = "victory-paths-field";
    const title = document.createElement("span");
    title.textContent = field.name;
    label.appendChild(title);
    if (field.readOnly) {
      const value = document.createElement("pre");
      value.textContent = typeof field.value === "object" ? JSON.stringify(field.value, null, 2) : String(field.value);
      value.dataset.readOnly = "true";
      label.appendChild(value);
      return label;
    }
    const edit = state.resource.draft.edits[JSON.stringify(field.address)];
    const raw = edit ? edit.raw : field.kind === "json" ? JSON.stringify(field.value, null, 2) : field.value;
    const multiline = field.kind === "json" || (typeof raw === "string" && (raw.includes("\n") || raw.length > 100));
    const control = document.createElement(multiline ? "textarea" : "input");
    control.dataset.field = field.name;
    control.dataset.kind = field.kind;
    if (field.kind === "boolean") { control.type = "checkbox"; control.checked = raw; }
    else {
      control.value = raw;
      if (!multiline) control.type = "text";
      if (field.kind === "number") control.inputMode = "decimal";
      if (field.kind === "json") control.setAttribute("aria-description", "JSON 结构，允许 null；输入错误会保留草稿并禁止提交");
    }
    control.setAttribute("aria-invalid", String(!!edit?.error));
    control.addEventListener(field.kind === "boolean" ? "change" : "input", () => {
      controller.edit(field, field.kind === "boolean" ? control.checked : control.value);
      control.setAttribute("aria-invalid", String(!!state.resource.draft.edits[JSON.stringify(field.address)]?.error));
    });
    label.appendChild(control);
    return label;
  }

  function render() {
    if (!state.document.paths.some((path) => path.id === activePath)) activePath = state.document.paths[0]?.id;
    nodes.paths.replaceChildren();
    for (const path of state.document.paths) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.path = path.id;
      button.className = path.id === activePath ? "active" : "";
      button.textContent = `${path.tasks.label.zh} · ${path.id}`;
      button.setAttribute("aria-pressed", String(path.id === activePath));
      button.addEventListener("click", () => { if (!state.resource.busy) { activePath = path.id; render(); } });
      nodes.paths.appendChild(button);
    }
    nodes.fields.replaceChildren();
    for (const group of victoryFieldGroups(state.document, activePath)) {
      const section = document.createElement("details");
      section.className = "victory-paths-group";
      section.dataset.group = group.key;
      section.open = !!group.open;
      const summary = document.createElement("summary");
      summary.textContent = group.title;
      section.appendChild(summary);
      if (group.slots) {
        const note = document.createElement("p");
        note.className = "victory-paths-slot-note";
        note.textContent = "源任务是目录，运行时分配到三槽；不写入 slot 字段，也不把目录条目固定分槽。";
        section.appendChild(note);
        const slots = document.createElement("div");
        slots.className = "victory-paths-slots";
        for (const slot of [1, 2, 3]) {
          const item = document.createElement("span");
          item.textContent = `槽 ${slot} · 运行时选择（只读）`;
          slots.appendChild(item);
        }
        section.appendChild(slots);
      }
      for (const field of group.fields) section.appendChild(renderField(field));
      if (!group.fields.length) {
        const empty = document.createElement("p");
        empty.textContent = "当前目录无任务。";
        section.appendChild(empty);
      }
      nodes.fields.appendChild(section);
    }
    sync();
  }

  buttons.save.addEventListener("click", () => void controller.save());
  buttons.validate.addEventListener("click", () => void controller.validate());
  buttons.refresh.addEventListener("click", () => void controller.refreshKeepingDrafts());
  buttons.reload.addEventListener("click", () => {
    if (!state.resource.dirty || window.confirm("重新加载会丢弃未保存的修改，继续吗？")) void controller.load();
  });
  window.addEventListener("resource-committed", ({ detail }) => controller.handleCommitted(detail));
  window.addEventListener("beforeunload", (event) => {
    if (!state.resource.dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });
  sync();
  return controller;
}

if (typeof document !== "undefined") {
  const root = document.getElementById("victory-paths-root");
  if (root) {
    const page = createVictoryPathsPanel(root);
    document.addEventListener("tool-activated", (event) => {
      if (event.detail?.tool === "victory-paths" && !page.state.loaded) void page.load();
    });
  }
}
