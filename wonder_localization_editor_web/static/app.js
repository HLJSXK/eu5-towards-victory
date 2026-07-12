const state = {
    title: "Towards Victory 奇观编辑器",
    wonders: [],
    currentWonder: null,
    activeEditorTab: "english",
    listMode: "generic",
    status: "就绪",
    statusKind: "default",
    logText: "",
    busy: false,
    rendering: false,
    pageDrafts: {},
    ritualDesigns: null,
    ritualPromptDrafts: {},
};

const elements = {
    appTitle: document.getElementById("app-title"),
    wonderKindTabs: document.getElementById("wonder-kind-tabs"),
    wonderCount: document.getElementById("wonder-count"),
    wonderList: document.getElementById("wonder-list"),
    wonderMeta: document.getElementById("wonder-meta"),
    wonderImageFrame: document.getElementById("wonder-image-frame"),
    wonderNameEditors: document.getElementById("wonder-name-editors"),
    searchInput: document.getElementById("search-input"),
    languageTabs: document.getElementById("language-tabs"),
    languagePanels: document.getElementById("language-panels"),
    saveButton: document.getElementById("save-button"),
    reloadButton: document.getElementById("reload-button"),
    copyLogButton: document.getElementById("copy-log-button"),
    statusBadge: document.getElementById("status-badge"),
    dirtyBadge: document.getElementById("dirty-badge"),
    logOutput: document.getElementById("log-output"),
    toast: document.getElementById("toast"),
};

function normalizeLocalizationText(value) {
    return value.replace(/\r\n/g, "\n").replace(/\r/g, "\n").replace(/\n/g, " ").trim();
}

function normalizeMultilineText(value) {
    return value.replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();
}

function wonderSearchHaystack(wonder) {
    return [
        wonder.id,
        wonder.key,
        wonder.concept,
        wonder.name_zh,
        wonder.name_en,
        wonder.display_name,
        wonder.kind_label,
        wonder.size,
        wonder.size_label,
    ]
        .join(" ")
        .toLowerCase();
}

function showToast(message, kind = "info") {
    const toast = elements.toast;
    toast.textContent = message;
    toast.className = `toast ${kind}`;
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => {
        toast.className = "toast hidden";
    }, 2600);
}

function updateStatus(text, kind = "default") {
    state.status = text;
    state.statusKind = kind;
    elements.statusBadge.textContent = text;
    elements.statusBadge.dataset.kind = kind;
}

function setBusy(isBusy) {
    state.busy = isBusy;
    elements.saveButton.disabled = isBusy;
    elements.reloadButton.disabled = isBusy;
    elements.copyLogButton.disabled = isBusy && !state.logText;
    for (const control of document.querySelectorAll("[data-ritual-prompt-control='true']")) {
        control.disabled = isBusy;
    }
    document.body.dataset.busy = String(isBusy);
}

function getEditorFields() {
    return document.querySelectorAll(
        "#wonder-name-editors [data-editor-field='true'], #language-panels [data-editor-field='true']",
    );
}

function emptyDraft() {
    return {
        values: {
            english: {},
            simp_chinese: {},
        },
        mechanics: {},
    };
}

function draftHasChanges(draft) {
    return Boolean(
        draft &&
            (Object.values(draft.values || {}).some((values) => Object.keys(values || {}).length > 0) ||
                Object.keys(draft.mechanics || {}).length > 0),
    );
}

function dirtyPageCount() {
    return Object.values(state.pageDrafts).filter(draftHasChanges).length;
}

function currentWonderId() {
    return state.currentWonder?.summary?.id ?? null;
}

function uniqueInitialLevelFieldKey(wonderPayload = state.currentWonder) {
    const key = wonderPayload?.summary?.key || wonderPayload?.meta?.key || "";
    return key ? `mechanics.unique_initial_level.${key}` : "";
}

function parseUniqueInitialLevelValue(rawValue) {
    const value = String(rawValue ?? "").trim();
    if (!/^[0-6]$/.test(value)) {
        return { valid: false, value };
    }
    return { valid: true, level: Number.parseInt(value, 10), value };
}

function draftValueForField(draft, field, scope) {
    if (!draft) {
        return undefined;
    }
    if (scope === "localization") {
        return draft.values?.[field.language]?.[field.key];
    }
    return draft.mechanics?.[field.key];
}

function setDraftValueForField(draft, field, value) {
    const scope = field.dataset.fieldScope;
    if (scope === "localization") {
        const language = field.dataset.language;
        draft.values[language] ||= {};
        draft.values[language][field.dataset.key] = value;
    } else {
        draft.mechanics[field.dataset.key] = value;
    }
}

function collectCurrentDraft() {
    const draft = emptyDraft();
    for (const field of getEditorFields()) {
        if (normalizeFieldValue(field) === field.dataset.originalValue) {
            continue;
        }
        setDraftValueForField(draft, field, field.value);
    }
    return draft;
}

function cacheCurrentWonderDraft() {
    const wonderId = currentWonderId();
    if (wonderId === null || state.rendering) {
        return;
    }
    const draft = collectCurrentDraft();
    if (draftHasChanges(draft)) {
        state.pageDrafts[String(wonderId)] = draft;
    } else {
        delete state.pageDrafts[String(wonderId)];
    }
}

function cacheCurrentRitualPromptDraft() {
    const wonderId = currentWonderId();
    if (wonderId === null || state.rendering) {
        return;
    }
    const input = document.querySelector("[data-ritual-prompt-input='true']");
    if (!input) {
        return;
    }
    const originalPrompt = String(input.dataset.originalPrompt || "");
    const value = normalizeMultilineText(String(input.value || ""));
    if (value === originalPrompt) {
        delete state.ritualPromptDrafts[String(wonderId)];
    } else {
        state.ritualPromptDrafts[String(wonderId)] = value;
    }
}

function applyDraftToField(field, scope, draft) {
    const cachedValue = draftValueForField(draft, field, scope);
    if (cachedValue === undefined) {
        return;
    }
    field.value = cachedValue;
    if (isStructuredFieldType(field.field_type || "text")) {
        try {
            field.structured_value = JSON.parse(cachedValue);
        } catch {
            field.structured_value = field.structured_value ?? {};
        }
    }
}

function applyDraftNamePreview(wonderPayload, draft) {
    const nameKey = wonderNameKeyForKey(wonderPayload?.summary?.key || "");
    if (!nameKey) {
        return;
    }
    const englishName = draft.values?.english?.[nameKey];
    const chineseName = draft.values?.simp_chinese?.[nameKey];
    if (englishName !== undefined) {
        const normalized = normalizeLocalizationText(String(englishName));
        wonderPayload.summary.name_en = normalized;
        wonderPayload.meta.name_en = normalized;
    }
    if (chineseName !== undefined) {
        const normalized = normalizeLocalizationText(String(chineseName));
        wonderPayload.summary.name_zh = normalized;
        wonderPayload.meta.name_zh = normalized;
    }
    wonderPayload.summary.display_name = `${wonderPayload.summary.name_zh} / ${wonderPayload.summary.name_en}`;
}

function applyDraftInitialLevelPreview(wonderPayload, draft) {
    if (!wonderPayload?.summary?.is_unique) {
        return;
    }
    const fieldKey = uniqueInitialLevelFieldKey(wonderPayload);
    const draftValue = fieldKey ? draft.mechanics?.[fieldKey] : undefined;
    if (draftValue === undefined) {
        return;
    }
    const parsed = parseUniqueInitialLevelValue(draftValue);
    if (!parsed.valid) {
        return;
    }
    wonderPayload.summary.initial_level = parsed.level;
    wonderPayload.meta.initial_level = parsed.level;
    const summary = state.wonders.find((wonder) => Number(wonder.id) === Number(wonderPayload.summary.id));
    if (summary) {
        summary.initial_level = parsed.level;
    }
}

function applyDraftToWonderPayload(wonderPayload) {
    if (!wonderPayload?.summary?.id) {
        return wonderPayload;
    }
    const draft = state.pageDrafts[String(wonderPayload.summary.id)];
    if (!draftHasChanges(draft)) {
        return wonderPayload;
    }
    for (const payload of Object.values(wonderPayload.languages || {})) {
        for (const section of payload.sections || []) {
            for (const field of section.fields || []) {
                applyDraftToField(field, "localization", draft);
            }
        }
    }
    for (const section of wonderPayload.mechanics?.sections || []) {
        for (const field of section.fields || []) {
            applyDraftToField(field, "mechanics", draft);
        }
    }
    applyDraftNamePreview(wonderPayload, draft);
    applyDraftInitialLevelPreview(wonderPayload, draft);
    return wonderPayload;
}

function setCurrentWonderPayload(wonderPayload) {
    state.currentWonder = applyDraftToWonderPayload(wonderPayload);
}

function normalizeFieldValue(element) {
    const scope = element.dataset.fieldScope;
    const fieldType = element.dataset.fieldType || "text";
    if (fieldType === "boolean" && element.type === "checkbox") {
        return element.checked ? "yes" : "no";
    }
    const value = String(element.value ?? "");
    if (scope === "localization") {
        return normalizeLocalizationText(value);
    }
    if (fieldType === "yaml" || fieldType === "script") {
        return normalizeMultilineText(value);
    }
    return value.trim();
}

function hasUnsavedChanges() {
    cacheCurrentWonderDraft();
    return dirtyPageCount() > 0;
}

function refreshDirtyState() {
    const hasChanges = hasUnsavedChanges();
    const pageCount = dirtyPageCount();
    elements.dirtyBadge.textContent = pageCount > 1 ? `Unsaved changes (${pageCount} pages)` : "未保存更改";
    elements.dirtyBadge.classList.toggle("hidden", !hasChanges);
}

function wonderNameKeyForKey(wonderKey) {
    return `tv_wonder_${wonderKey}`;
}

function currentWonderNameKey() {
    if (!state.currentWonder?.summary?.key) {
        return "";
    }
    return wonderNameKeyForKey(state.currentWonder.summary.key);
}

function isCurrentWonderNameField(field) {
    const wonderNameKey = currentWonderNameKey();
    return Boolean(wonderNameKey) && field.key === wonderNameKey && field.label === "Wonder name";
}

function currentWonderNameFields() {
    if (!state.currentWonder) {
        return [];
    }
    const nameFields = [];
    for (const [language, payload] of Object.entries(state.currentWonder.languages || {})) {
        for (const section of payload.sections || []) {
            for (const field of section.fields || []) {
                if (field.key === currentWonderNameKey() && field.label === "Wonder name") {
                    nameFields.push({
                        language,
                        languageLabel: payload.label || language,
                        field,
                    });
                }
            }
        }
    }
    return nameFields;
}

function updateWonderNamePreview(language, value) {
    if (!state.currentWonder) {
        return;
    }
    const normalizedValue = normalizeLocalizationText(String(value ?? ""));
    if (language === "english") {
        state.currentWonder.summary.name_en = normalizedValue;
        state.currentWonder.meta.name_en = normalizedValue;
    } else if (language === "simp_chinese") {
        state.currentWonder.summary.name_zh = normalizedValue;
        state.currentWonder.meta.name_zh = normalizedValue;
    }
    state.currentWonder.summary.display_name = `${state.currentWonder.summary.name_zh} / ${state.currentWonder.summary.name_en}`;

    const summary = state.wonders.find((wonder) => wonder.id === state.currentWonder.summary.id);
    if (summary) {
        summary.name_en = state.currentWonder.summary.name_en;
        summary.name_zh = state.currentWonder.summary.name_zh;
        summary.display_name = state.currentWonder.summary.display_name;
    }

    renderWonderList();
    renderMeta();
}

function updateUniqueInitialLevelPreview(value) {
    if (!state.currentWonder?.summary?.is_unique) {
        return;
    }
    const parsed = parseUniqueInitialLevelValue(value);
    if (parsed.valid) {
        state.currentWonder.summary.initial_level = parsed.level;
        state.currentWonder.meta.initial_level = parsed.level;
        const summary = state.wonders.find((wonder) => Number(wonder.id) === Number(state.currentWonder.summary.id));
        if (summary) {
            summary.initial_level = parsed.level;
        }
    }
    renderMeta();
}

function currentWonderKind() {
    return state.currentWonder?.summary?.is_unique ? "unique" : "generic";
}

function wonderImageForSummary(wonder) {
    return wonder?.image || null;
}

function currentWonderImage() {
    return state.currentWonder?.summary?.image || state.currentWonder?.meta?.image || null;
}

function wonderImageAlt(wonder) {
    const summary = wonder?.summary || wonder || {};
    const name = summary.name_zh || summary.name_en || summary.key || "wonder";
    return `${name} image`;
}

function renderWonderImage() {
    const frame = elements.wonderImageFrame;
    if (!frame) {
        return;
    }
    frame.innerHTML = "";
    frame.classList.remove("has-image", "is-missing");

    if (!state.currentWonder) {
        frame.classList.add("is-missing");
        return;
    }

    const image = currentWonderImage();
    if (image?.url) {
        const img = document.createElement("img");
        img.src = image.url;
        img.alt = wonderImageAlt(state.currentWonder);
        img.loading = "eager";
        frame.append(img);
        frame.classList.add("has-image");
    } else {
        const placeholder = document.createElement("div");
        placeholder.className = "wonder-image-placeholder";
        placeholder.textContent = "No generated image";
        frame.append(placeholder);
        frame.classList.add("is-missing");
    }

    if (image?.filename) {
        const caption = document.createElement("figcaption");
        caption.textContent = image.path || image.filename;
        frame.append(caption);
    }
}

function currentUniqueInitialLevelState() {
    if (!state.currentWonder?.summary?.is_unique) {
        return { valid: true, level: 0, value: "0" };
    }
    const draft = state.pageDrafts[String(state.currentWonder.summary.id)];
    const fieldKey = uniqueInitialLevelFieldKey(state.currentWonder);
    const draftValue = fieldKey ? draft?.mechanics?.[fieldKey] : undefined;
    const rawValue =
        draftValue === undefined
            ? (state.currentWonder.meta?.initial_level ?? state.currentWonder.summary?.initial_level ?? 0)
            : draftValue;
    return parseUniqueInitialLevelValue(rawValue);
}

function uniqueInitialLevelStartStateLabel() {
    const stateValue = currentUniqueInitialLevelState();
    if (!stateValue.valid) {
        return stateValue.value ? `Invalid level: ${stateValue.value}` : "Invalid level";
    }
    return stateValue.level > 0 ? `Level ${stateValue.level}` : "Not present";
}

function findWonderByKey(key, isUnique = null) {
    return state.wonders.find((wonder) => {
        if (wonder.key !== key) {
            return false;
        }
        if (isUnique === null) {
            return true;
        }
        return Boolean(wonder.is_unique) === Boolean(isUnique);
    });
}

function wondersForMode(mode) {
    const isUnique = mode === "unique";
    return state.wonders.filter((wonder) => Boolean(wonder.is_unique) === isUnique);
}

function renderWonderKindTabs() {
    const modes = [
        { id: "generic", label: "通用奇观" },
        { id: "unique", label: "独特奇观" },
    ];
    elements.wonderKindTabs.innerHTML = "";
    for (const mode of modes) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "kind-switch-button";
        if (state.listMode === mode.id) {
            button.classList.add("active");
        }
        button.textContent = `${mode.label} (${wondersForMode(mode.id).length})`;
        button.addEventListener("click", () => {
            state.listMode = mode.id;
            renderWonderKindTabs();
            renderWonderList();
        });
        elements.wonderKindTabs.append(button);
    }
}

function renderWonderList() {
    const query = elements.searchInput.value.trim().toLowerCase();
    const pool = wondersForMode(state.listMode);
    const wonders = pool.filter((wonder) => wonderSearchHaystack(wonder).includes(query));
    const label = state.listMode === "unique" ? "独特奇观" : "通用奇观";

    elements.wonderCount.textContent = `显示 ${wonders.length} / ${pool.length} 个${label}`;
    elements.wonderList.innerHTML = "";

    if (!wonders.length) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = "没有匹配的奇观。";
        elements.wonderList.append(empty);
        return;
    }

    for (const wonder of wonders) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "wonder-item";
        if (state.currentWonder && state.currentWonder.summary.id === wonder.id) {
            button.classList.add("active");
        }
        const image = wonderImageForSummary(wonder);
        const thumbnailHtml = image?.url
            ? `<img class="wonder-thumb" src="${escapeHtml(image.url)}" alt="${escapeHtml(wonderImageAlt(wonder))}" loading="lazy">`
            : `<span class="wonder-thumb wonder-thumb-missing" aria-hidden="true"></span>`;
        button.innerHTML = `
            ${thumbnailHtml}
            <span class="wonder-list-copy">
                <span class="wonder-row">
                    <span class="wonder-id">#${wonder.id}</span>
                    <span class="wonder-badges">
                        <span class="wonder-kind">${escapeHtml(wonder.kind_label)}</span>
                        <span class="wonder-size">${escapeHtml(wonder.size_label || wonder.size || "-")}</span>
                    </span>
                </span>
                <strong>${escapeHtml(wonder.name_zh || wonder.key)}</strong>
                <span class="wonder-subtitle">${escapeHtml(wonder.name_en || wonder.concept)}</span>
                <code>${escapeHtml(wonder.key)}</code>
            </span>
        `;
        button.addEventListener("click", () => {
            void selectWonder(wonder.id);
        });
        elements.wonderList.append(button);
    }
}

function renderMeta() {
    elements.wonderMeta.innerHTML = "";
    if (!state.currentWonder) {
        return;
    }

    const { meta, summary } = state.currentWonder;
    const entries = [
        ["ID", String(meta.id)],
        ["Key", meta.key],
        ["Concept key", meta.concept],
        ["Size", meta.size_label || summary.size_label || meta.size || "-"],
        ["类型", summary.kind_label],
        ["中文名", meta.name_zh || "-"],
        ["英文名", meta.name_en || "-"],
    ];
    if (meta.base_key) {
        entries.push(["原型", meta.base_key]);
    }
    if (meta.base_effect_multiplier && Number(meta.base_effect_multiplier) !== 1) {
        entries.push(["Base effect x", `x${meta.base_effect_multiplier}`]);
    }
    if (meta.location) {
        entries.push(["固定地点", meta.location]);
    }

    if (summary.is_unique) {
        entries.push(["Start state", uniqueInitialLevelStartStateLabel()]);
    }

    if (meta.image?.filename) {
        entries.push(["Image", meta.image.exists ? meta.image.filename : `${meta.image.filename} (missing)`]);
    }

    for (const [label, value] of entries) {
        const card = document.createElement("div");
        card.className = "meta-card";
        card.innerHTML = `<span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>`;
        elements.wonderMeta.append(card);
    }
}

function createSingleLineEditorBinding(field, scope, onInput = null) {
    const input = document.createElement("input");
    const fieldType = field.field_type || "text";
    input.type = fieldType === "number" ? "number" : "text";
    input.value = field.value;
    input.dataset.editorField = "true";
    input.dataset.fieldScope = scope;
    input.dataset.fieldType = fieldType;
    input.dataset.key = field.key;
    input.dataset.originalValue = field.original_value;
    if (fieldType === "number") {
        input.step = "1";
    }
    if (field.target_kind === "unique_initial_level") {
        input.min = "0";
        input.max = "6";
        input.step = "1";
    }
    if (scope === "localization") {
        input.dataset.language = field.language;
    }
    input.addEventListener("input", () => {
        refreshDirtyState();
        onInput?.(input.value);
    });
    input.addEventListener("change", () => {
        refreshDirtyState();
        onInput?.(input.value);
    });
    return input;
}

function renderWonderNameEditors() {
    elements.wonderNameEditors.innerHTML = "";
    if (!state.currentWonder) {
        elements.wonderNameEditors.classList.add("hidden");
        return;
    }

    const fields = currentWonderNameFields();
    if (!fields.length) {
        elements.wonderNameEditors.classList.add("hidden");
        return;
    }

    for (const { language, languageLabel, field } of fields) {
        const card = document.createElement("article");
        card.className = "name-editor-card";
        card.innerHTML = `
            <div class="name-editor-head">
                <span class="eyebrow">${escapeHtml(languageLabel)}</span>
                <strong>${escapeHtml(field.label)}</strong>
                <code class="name-editor-key">${escapeHtml(field.key)}</code>
            </div>
        `;
        const input = createSingleLineEditorBinding(field, "localization", (value) => {
            updateWonderNamePreview(language, value);
        });
        input.classList.add("name-editor-input");
        card.append(input);
        elements.wonderNameEditors.append(card);
    }

    elements.wonderNameEditors.classList.remove("hidden");
}

function editorTabsForCurrentWonder() {
    if (!state.currentWonder) {
        return [];
    }
    const tabs = Object.entries(state.currentWonder.languages).map(([id, payload]) => ({
        id,
        label: payload.label,
        kind: "localization",
    }));
    if (state.currentWonder.mechanics) {
        tabs.push({
            id: "mechanics",
            label: state.currentWonder.mechanics.label || "机制",
            kind: "mechanics",
        });
    }
    if (state.currentWonder.summary?.is_unique && state.ritualDesigns) {
        tabs.push({
            id: "ritual-design",
            label: "仪式设计",
            kind: "ritual-design",
        });
    }
    return tabs;
}

function renderEditorTabs() {
    elements.languageTabs.innerHTML = "";
    if (!state.currentWonder) {
        return;
    }

    const tabs = editorTabsForCurrentWonder();
    if (!tabs.some((tab) => tab.id === state.activeEditorTab)) {
        state.activeEditorTab = tabs[0]?.id || "english";
    }

    for (const tab of tabs) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "tab-button";
        if (tab.id === state.activeEditorTab) {
            button.classList.add("active");
        }
        button.textContent = tab.label;
        button.addEventListener("click", () => {
            state.activeEditorTab = tab.id;
            renderEditorTabs();
            syncActiveEditorPanel();
        });
        elements.languageTabs.append(button);
    }
}

const STRUCTURED_FIELD_TYPES = new Set([
    "modifier_table",
    "reward_editor",
    "unique_ritual_editor",
    "unique_ceremony_editor",
    "site_trigger_template",
    "site_preference_template",
]);

function isStructuredFieldType(fieldType) {
    return STRUCTURED_FIELD_TYPES.has(fieldType);
}

function stableStringify(value) {
    if (value === null) {
        return "null";
    }
    if (Array.isArray(value)) {
        return `[${value.map((entry) => stableStringify(entry)).join(",")}]`;
    }
    if (typeof value === "object") {
        const keys = Object.keys(value).sort();
        return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
    }
    return JSON.stringify(value);
}

function deepClone(value) {
    return value == null ? value : JSON.parse(JSON.stringify(value));
}

function parseNumberMaybe(value) {
    const text = String(value ?? "").trim();
    if (!text) {
        return "";
    }
    if (/^-?\d+$/.test(text)) {
        return Number.parseInt(text, 10);
    }
    if (/^-?(?:\d+|\d*\.\d+)(?:[eE][+-]?\d+)?$/.test(text)) {
        return Number.parseFloat(text);
    }
    return text;
}

function rowsToModifierMapping(rows, keyField = "modifier") {
    const mapping = {};
    for (const row of rows || []) {
        const key = String(row?.[keyField] ?? "").trim();
        const value = String(row?.value ?? "").trim();
        if (!key || !value) {
            continue;
        }
        mapping[key] = parseNumberMaybe(value);
    }
    return mapping;
}

function rowsToStringList(rows) {
    const values = [];
    for (const row of rows || []) {
        const value = String(row?.value ?? "").trim();
        if (!value) {
            continue;
        }
        values.push(value);
    }
    return values;
}

function rowsToRewardList(rows) {
    const reward = [];
    for (const row of rows || []) {
        const type = String(row?.type ?? "").trim();
        const value = String(row?.value ?? "").trim();
        if (!type || !value) {
            continue;
        }
        reward.push({
            type,
            value: parseNumberMaybe(value),
        });
    }
    return reward;
}

function asOptionalText(value) {
    const text = normalizeMultilineText(String(value ?? ""));
    return text || null;
}

function uniqueRitualPayloadFromState(stateValue) {
    const timedYears = Number.parseInt(String(stateValue.timed?.years ?? "1").trim() || "1", 10);
    const maxLevels = Number.parseInt(
        String(stateValue.auxiliary_building?.max_levels ?? "1").trim() || "1",
        10,
    );

    return {
        key: String(stateValue.key ?? "").trim() || "ritual",
        mode: String(stateValue.mode ?? "").trim() || "immediate",
        cost_type: String(stateValue.cost_type ?? "").trim() || null,
        listeners: rowsToStringList(stateValue.listeners?.rows),
        runtime_variables: rowsToStringList(stateValue.runtime_variables?.rows),
        country_modifier: rowsToModifierMapping(stateValue.country_modifier?.rows),
        reward: rowsToRewardList(stateValue.reward?.rows),
        confirmation_trigger_script: normalizeMultilineText(String(stateValue.confirmation_trigger_script ?? "")),
        start_effect_script: normalizeMultilineText(String(stateValue.start_effect_script ?? "")),
        snapshot_effect_script: normalizeMultilineText(String(stateValue.snapshot_effect_script ?? "")),
        progress_effect_script: normalizeMultilineText(String(stateValue.progress_effect_script ?? "")),
        completion_trigger_script: normalizeMultilineText(String(stateValue.completion_trigger_script ?? "")),
        completion_effect_script: normalizeMultilineText(String(stateValue.completion_effect_script ?? "")),
        timed: {
            years: Number.isFinite(timedYears) && timedYears > 0 ? timedYears : 1,
            burden_modifier: rowsToModifierMapping(stateValue.timed?.burden_modifier?.rows),
            blessing_modifier: rowsToModifierMapping(stateValue.timed?.blessing_modifier?.rows),
        },
        auxiliary_building: {
            local_modifier: rowsToModifierMapping(stateValue.auxiliary_building?.local_modifier?.rows),
            maintenance: asOptionalText(stateValue.auxiliary_building?.maintenance),
            build_time: asOptionalText(stateValue.auxiliary_building?.build_time),
            construction_demand: asOptionalText(stateValue.auxiliary_building?.construction_demand),
            price: asOptionalText(stateValue.auxiliary_building?.price),
            attributes: rowsToModifierMapping(stateValue.auxiliary_building?.attributes?.rows),
            max_levels: Number.isFinite(maxLevels) && maxLevels > 0 ? maxLevels : 1,
        },
    };
}

function uniqueCeremonyPayloadFromState(stateValue) {
    return {
        stages: (stateValue.stages || []).map((stage) => ({
            title_en: normalizeMultilineText(String(stage.title_en ?? "")),
            title_zh: normalizeMultilineText(String(stage.title_zh ?? "")),
            desc_en: normalizeMultilineText(String(stage.desc_en ?? "")),
            desc_zh: normalizeMultilineText(String(stage.desc_zh ?? "")),
            icon: String(stage.icon ?? "").trim(),
            icon_rationale: normalizeMultilineText(String(stage.icon_rationale ?? "")),
            cost: rowsToRewardList(stage.cost?.rows),
        })),
    };
}

function optionByValue(options) {
    const mapping = new Map();
    for (const option of options || []) {
        mapping.set(option.value, option);
    }
    return mapping;
}

function renderSiteTriggerScript(stateValue) {
    if (stateValue.template_id === "custom_script") {
        return normalizeMultilineText(String(stateValue.raw_script ?? ""));
    }
    const conditionMap = optionByValue(stateValue.condition_options);
    const anyRows = rowsToStringList(stateValue.any_of?.rows);
    const allRows = rowsToStringList(stateValue.all_of?.rows);
    const lines = [];

    if (anyRows.length === 1) {
        lines.push(conditionMap.get(anyRows[0])?.script || anyRows[0]);
    } else if (anyRows.length > 1) {
        lines.push("OR = {");
        for (const value of anyRows) {
            lines.push(`\t${conditionMap.get(value)?.script || value}`);
        }
        lines.push("}");
    }

    for (const value of allRows) {
        lines.push(conditionMap.get(value)?.script || value);
    }

    if (!lines.length) {
        return "always = yes";
    }
    return lines.join("\n");
}

function renderSitePreferenceScript(stateValue) {
    if (stateValue.template_id === "custom_script") {
        return normalizeMultilineText(String(stateValue.raw_script ?? ""));
    }
    const conditionMap = optionByValue(stateValue.condition_options);
    const sourceMap = optionByValue(stateValue.scale_source_options);
    const lines = [];

    for (const row of stateValue.bonus_rules?.rows || []) {
        const branch = String(row.branch ?? "if").trim() || "if";
        const condition = String(row.condition ?? "").trim();
        const value = String(row.value ?? "").trim();
        if (!condition || !value) {
            continue;
        }
        const script = conditionMap.get(condition)?.script || condition;
        lines.push(`${branch} = {`);
        lines.push(`\tlimit = { var:tv_wonder_survey_site ?= { ${script} } }`);
        lines.push(`\ttv_wonder_change_all_survey_competence_target_effect = { value = ${value} }`);
        lines.push("}");
    }

    let renderedScaled = false;
    for (const row of stateValue.scaled_rules?.rows || []) {
        const source = String(row.source ?? "").trim();
        const min = String(row.min ?? "").trim();
        const max = String(row.max ?? "").trim();
        const multiplier = String(row.multiplier ?? "").trim();
        if (!source || !min || !max || !multiplier) {
            continue;
        }
        const sourcePath = sourceMap.get(source)?.path || source;
        lines.push(`set_variable = { name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.${sourcePath} }`);
        lines.push(`clamp_variable = { name = tv_wonder_site_preference_bonus min = ${min} max = ${max} }`);
        lines.push(`change_variable = { name = tv_wonder_site_preference_bonus multiply = ${multiplier} }`);
        lines.push("tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }");
        renderedScaled = true;
    }

    if (renderedScaled) {
        lines.push("remove_variable = tv_wonder_site_preference_bonus");
    }

    return lines.join("\n");
}

function previewPayloadForField(field, stateValue) {
    if (field.field_type === "modifier_table") {
        if (field.target_kind === "generic_ritual") {
            if (field.target_parent_key === "style_1") {
                return { country_modifier: rowsToModifierMapping(stateValue.rows) };
            }
            return { local_modifier: rowsToModifierMapping(stateValue.rows) };
        }
        return rowsToModifierMapping(stateValue.rows);
    }
    if (field.field_type === "reward_editor") {
        return {
            cost_type: String(stateValue.cost_type ?? "").trim() || null,
            reward: rowsToRewardList(stateValue.rows),
        };
    }
    if (field.field_type === "unique_ritual_editor") {
        return uniqueRitualPayloadFromState(stateValue);
    }
    if (field.field_type === "unique_ceremony_editor") {
        return uniqueCeremonyPayloadFromState(stateValue);
    }
    return stateValue;
}

function isPlainObject(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function yamlScalar(value) {
    if (value === null) {
        return "null";
    }
    if (typeof value === "number") {
        return String(value);
    }
    if (typeof value === "boolean") {
        return value ? "true" : "false";
    }
    const text = String(value ?? "");
    if (!text) {
        return '""';
    }
    if (/^[A-Za-z0-9_:.+\-/]+$/.test(text)) {
        return text;
    }
    return JSON.stringify(text);
}

function inlineYamlValue(value) {
    if (Array.isArray(value) && !value.length) {
        return "[]";
    }
    if (isPlainObject(value) && !Object.keys(value).length) {
        return "{}";
    }
    return yamlScalar(value);
}

function renderYamlLines(value, indent = 0) {
    const prefix = "  ".repeat(indent);
    if (Array.isArray(value)) {
        if (!value.length) {
            return [`${prefix}[]`];
        }
        const lines = [];
        for (const entry of value) {
            if (Array.isArray(entry) || (isPlainObject(entry) && Object.keys(entry).length)) {
                lines.push(`${prefix}-`);
                lines.push(...renderYamlLines(entry, indent + 1));
            } else {
                lines.push(`${prefix}- ${inlineYamlValue(entry)}`);
            }
        }
        return lines;
    }
    if (isPlainObject(value)) {
        const entries = Object.entries(value);
        if (!entries.length) {
            return [`${prefix}{}`];
        }
        const lines = [];
        for (const [key, entry] of entries) {
            if (Array.isArray(entry) || (isPlainObject(entry) && Object.keys(entry).length)) {
                lines.push(`${prefix}${key}:`);
                lines.push(...renderYamlLines(entry, indent + 1));
            } else {
                lines.push(`${prefix}${key}: ${inlineYamlValue(entry)}`);
            }
        }
        return lines;
    }
    return [`${prefix}${inlineYamlValue(value)}`];
}

function previewTextForField(field, stateValue) {
    if (field.field_type === "site_trigger_template" || field.field_type === "site_preference_template") {
        const script =
            field.field_type === "site_trigger_template"
                ? renderSiteTriggerScript(stateValue)
                : renderSitePreferenceScript(stateValue);
        const lines = [field.target_path || field.key];
        for (const line of String(script || "").split("\n")) {
            lines.push(`  ${line}`);
        }
        return lines.join("\n");
    }
    const payload = previewPayloadForField(field, stateValue);
    const lines = [];
    if (field.target_path) {
        lines.push(`${field.target_path}:`);
        lines.push(...renderYamlLines(payload, 1));
    } else {
        lines.push(...renderYamlLines(payload, 0));
    }
    return lines.join("\n");
}

function normalizeOption(option) {
    if (typeof option === "string") {
        return {
            value: option,
            label: option,
            key_label: option,
            localized_label: option,
            search_text: option.toLowerCase(),
        };
    }
    const value = String(option?.value ?? "");
    const label = String(option?.label ?? value);
    const keyLabel = String(option?.key_label ?? value);
    const localizedLabel = String(option?.localized_label ?? label);
    const searchText = String(
        option?.search_text ||
            [
                value,
                label,
                keyLabel,
                localizedLabel,
                option?.label_en,
                option?.label_zh,
                option?.description_en,
                option?.description_zh,
                option?.source,
            ]
                .filter(Boolean)
                .join(" "),
    ).toLowerCase();
    return {
        ...option,
        value,
        label,
        key_label: keyLabel,
        localized_label: localizedLabel,
        search_text: searchText,
    };
}

function normalizeOptionList(options) {
    return (options || []).map(normalizeOption);
}

function optionsWithBlank(options, blankLabel) {
    const normalized = normalizeOptionList(options);
    if (normalized.some((option) => option.value === "")) {
        return normalized;
    }
    return [
        normalizeOption({
            value: "",
            label: blankLabel,
            key_label: "",
            localized_label: blankLabel,
        }),
        ...normalized,
    ];
}

function optionPrimaryText(option, displayMode) {
    if (!option) {
        return "";
    }
    return displayMode === "key" ? option.key_label || option.value : option.localized_label || option.label || option.value;
}

function optionSecondaryText(option, displayMode) {
    if (!option) {
        return "";
    }
    return displayMode === "key" ? option.localized_label || option.label || "" : option.key_label || option.value || "";
}

function createSearchableSelect(options, value, config = {}) {
    const normalizedOptions = normalizeOptionList(options);
    const wrapper = document.createElement("div");
    wrapper.className = "option-combobox";
    wrapper.dataset.displayMode = "localized";

    const input = document.createElement("input");
    input.type = "text";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.placeholder = config.placeholder || "Search...";

    const modeButton = document.createElement("button");
    modeButton.type = "button";
    modeButton.className = "option-mode-button";
    modeButton.textContent = "Text";

    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.className = "option-open-button";
    openButton.textContent = "v";
    openButton.setAttribute("aria-label", "Open options");

    const menu = document.createElement("div");
    menu.className = "option-menu";
    menu.hidden = true;

    let currentValue = String(value ?? "");
    let query = "";
    let displayMode = "localized";

    const selectedOption = () => normalizedOptions.find((option) => option.value === currentValue) || null;

    const displayForValue = () => {
        const option = selectedOption();
        if (option) {
            return optionPrimaryText(option, displayMode);
        }
        return currentValue;
    };

    const filteredOptions = () => {
        const normalizedQuery = query.trim().toLowerCase();
        if (!normalizedQuery) {
            return normalizedOptions;
        }
        return normalizedOptions.filter((option) => option.search_text.includes(normalizedQuery));
    };

    const setOpen = (isOpen) => {
        menu.hidden = !isOpen;
        wrapper.classList.toggle("open", isOpen);
        if (isOpen) {
            renderMenu();
        }
    };

    const renderInput = () => {
        input.value = displayForValue();
        const option = selectedOption();
        input.title = option
            ? `${option.key_label || option.value}\n${option.localized_label || option.label || ""}`
            : currentValue;
        modeButton.textContent = displayMode === "key" ? "Key" : "Text";
        wrapper.dataset.displayMode = displayMode;
    };

    const commitValue = (nextValue) => {
        currentValue = String(nextValue ?? "");
        query = "";
        renderInput();
        setOpen(false);
        wrapper.dispatchEvent(new Event("input", { bubbles: true }));
        wrapper.dispatchEvent(new Event("change", { bubbles: true }));
    };

    const renderMenu = () => {
        menu.innerHTML = "";
        const matches = filteredOptions();
        if (!matches.length) {
            const empty = document.createElement("div");
            empty.className = "option-empty";
            empty.textContent = "No matching entries";
            menu.append(empty);
            return;
        }
        for (const option of matches) {
            const item = document.createElement("button");
            item.type = "button";
            item.className = "option-item";
            if (option.value === currentValue) {
                item.classList.add("selected");
            }
            const primary = optionPrimaryText(option, displayMode);
            const secondary = optionSecondaryText(option, displayMode);
            const description = displayMode === "key" ? option.description_zh || option.description_en : "";
            item.innerHTML = `
                <span class="option-item-main">${escapeHtml(primary || option.value || "(empty)")}</span>
                <span class="option-item-sub">${escapeHtml(secondary || option.source || "")}</span>
                ${description ? `<span class="option-item-desc">${escapeHtml(description)}</span>` : ""}
            `;
            item.addEventListener("mousedown", (event) => {
                event.preventDefault();
                commitValue(option.value);
            });
            menu.append(item);
        }
    };

    Object.defineProperty(wrapper, "value", {
        get() {
            return currentValue;
        },
        set(nextValue) {
            currentValue = String(nextValue ?? "");
            query = "";
            renderInput();
            renderMenu();
        },
    });
    Object.defineProperty(wrapper, "disabled", {
        get() {
            return input.disabled;
        },
        set(isDisabled) {
            input.disabled = Boolean(isDisabled);
            modeButton.disabled = Boolean(isDisabled);
            openButton.disabled = Boolean(isDisabled);
            wrapper.classList.toggle("disabled", Boolean(isDisabled));
            if (isDisabled) {
                setOpen(false);
            }
        },
    });

    input.addEventListener("focus", () => {
        query = "";
        input.select();
        setOpen(true);
    });
    input.addEventListener("input", () => {
        query = input.value;
        setOpen(true);
    });
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            const first = filteredOptions()[0];
            if (first) {
                event.preventDefault();
                commitValue(first.value);
            }
        } else if (event.key === "Escape") {
            query = "";
            renderInput();
            setOpen(false);
        }
    });
    modeButton.addEventListener("click", () => {
        displayMode = displayMode === "key" ? "localized" : "key";
        renderInput();
        renderMenu();
    });
    openButton.addEventListener("click", () => {
        const shouldOpen = menu.hidden;
        query = "";
        renderInput();
        setOpen(shouldOpen);
        if (shouldOpen) {
            input.focus();
        }
    });
    wrapper.addEventListener("focusout", () => {
        window.setTimeout(() => {
            if (wrapper.contains(document.activeElement)) {
                return;
            }
            query = "";
            renderInput();
            setOpen(false);
        }, 0);
    });

    wrapper.append(input, modeButton, openButton, menu);
    renderInput();
    return wrapper;
}

function createEditorBinding(field, scope) {
    const fieldType = field.field_type || "text";
    const input = document.createElement("input");
    if (isStructuredFieldType(fieldType)) {
        input.type = "hidden";
        input.value = field.original_value;
    } else if (fieldType === "boolean") {
        input.type = "checkbox";
        input.checked = ["yes", "true", "1"].includes(String(field.value || "").trim().toLowerCase());
        input.value = input.checked ? "yes" : "no";
        input.addEventListener("change", () => {
            input.value = input.checked ? "yes" : "no";
            refreshDirtyState();
        });
    } else if (fieldType === "select") {
        input.remove();
        const select = createSearchableSelect(field.options || [], field.value, {
            placeholder: `Search ${field.label || "entries"}`,
        });
        select.value = field.value;
        select.dataset.editorField = "true";
        select.dataset.fieldScope = scope;
        select.dataset.fieldType = fieldType;
        select.dataset.key = field.key;
        select.dataset.originalValue = field.original_value;
        if (scope === "localization") {
            select.dataset.language = field.language;
        }
        select.addEventListener("input", refreshDirtyState);
        select.addEventListener("change", refreshDirtyState);
        return select;
    } else if (scope === "localization" || fieldType === "yaml" || fieldType === "script") {
        input.remove();
        const textarea = document.createElement("textarea");
        textarea.rows = Math.max(field.height || 4, 3);
        textarea.value = field.value;
        textarea.dataset.editorField = "true";
        textarea.dataset.fieldScope = scope;
        textarea.dataset.fieldType = fieldType;
        textarea.dataset.key = field.key;
        textarea.dataset.originalValue = field.original_value;
        if (scope === "localization") {
            textarea.dataset.language = field.language;
        }
        textarea.addEventListener("input", refreshDirtyState);
        textarea.addEventListener("change", refreshDirtyState);
        return textarea;
    } else {
        input.type = "text";
        input.value = field.value;
    }

    input.dataset.editorField = "true";
    input.dataset.fieldScope = scope;
    input.dataset.fieldType = fieldType;
    input.dataset.key = field.key;
    input.dataset.originalValue = field.original_value;
    if (scope === "localization") {
        input.dataset.language = field.language;
    }
    if (!isStructuredFieldType(fieldType) && fieldType !== "boolean") {
        input.addEventListener("input", refreshDirtyState);
        input.addEventListener("change", refreshDirtyState);
    }
    return input;
}

function createStructuredShell(field, scope) {
    const stateValue = deepClone(field.structured_value ?? {});
    const binding = createEditorBinding(field, scope);
    const shell = document.createElement("div");
    shell.className = "structured-field";

    const layout = document.createElement("div");
    layout.className = "structured-layout";

    const editor = document.createElement("div");
    editor.className = "structured-editor";

    const preview = document.createElement("aside");
    preview.className = "code-state-pane";
    preview.innerHTML = `
        <div class="code-state-head">
            <strong>Code State</strong>
            <span>${escapeHtml(field.source_path || "")}</span>
        </div>
    `;
    const previewMeta = document.createElement("p");
    previewMeta.className = "code-state-meta";
    previewMeta.textContent = field.target_path || field.key;
    preview.append(previewMeta);
    const previewOutput = document.createElement("pre");
    previewOutput.className = "code-state-output";
    preview.append(previewOutput);

    const commit = () => {
        binding.value = stableStringify(stateValue);
        previewOutput.textContent = previewTextForField(field, stateValue);
        refreshDirtyState();
    };

    shell.append(binding, layout);
    layout.append(editor, preview);
    commit();
    return { shell, editor, stateValue, commit };
}

function buildReadonlyStructuredNote(field) {
    const note = document.createElement("div");
    note.className = "readonly-note";

    const message = document.createElement("div");
    message.innerHTML = `
        <strong>Inherited from prototype</strong>
        <p>Effects are listed below in read-only form. Edit the prototype wonder to change them.</p>
    `;
    note.append(message);

    if (field.prototype_key) {
        const actions = document.createElement("div");
        actions.className = "readonly-actions";
        const button = document.createElement("button");
        button.type = "button";
        button.className = "mini-button";
        button.textContent = "Open prototype";
        button.addEventListener("click", () => {
            const target = findWonderByKey(field.prototype_key, false);
            if (target) {
                void selectWonder(target.id);
            }
        });
        actions.append(button);
        note.append(actions);
    }

    return note;
}

function buildRowListEditor(config) {
    const section = document.createElement("section");
    section.className = "structured-group";
    const readonly = config.readonly === true;

    const header = document.createElement("div");
    header.className = "structured-group-head";
    header.innerHTML = `<h4>${escapeHtml(config.title)}</h4>`;
    let addButton = null;
    if (!readonly) {
        addButton = document.createElement("button");
        addButton.type = "button";
        addButton.className = "mini-button";
        addButton.textContent = config.addLabel || "Add row";
        addButton.addEventListener("click", () => {
            if (Number.isInteger(config.maxRows) && config.rows.length >= config.maxRows) {
                return;
            }
            config.rows.push(config.createRow());
            renderRows();
            config.onChange();
        });
        header.append(addButton);
    }
    section.append(header);

    if (config.note) {
        const note = document.createElement("p");
        note.className = "structured-group-note";
        note.textContent = config.note;
        section.append(note);
    }

    const rowsNode = document.createElement("div");
    rowsNode.className = "structured-rows";
    section.append(rowsNode);

    const renderRows = () => {
        if (addButton) {
            addButton.disabled = Number.isInteger(config.maxRows) && config.rows.length >= config.maxRows;
        }
        rowsNode.innerHTML = "";
        if (!config.rows.length) {
            const empty = document.createElement("div");
            empty.className = "structured-empty";
            empty.textContent = config.emptyText || "No rows yet.";
            rowsNode.append(empty);
        }
        config.rows.forEach((row, index) => {
            const rowNode = document.createElement("div");
            rowNode.className = "structured-row";
            if (!config.secondaryKey) {
                rowNode.classList.add("single-value");
            }

            const primaryOptions = config.primaryOptions || [];
            const primaryControl = config.primaryControl || "text";
            let primary;
            if (primaryControl === "select" || primaryOptions.length) {
                primary = createSearchableSelect(
                    optionsWithBlank(
                        primaryOptions,
                        config.primaryPlaceholder || `Choose ${config.primaryLabel || "value"}`,
                    ),
                    row[config.primaryKey] || "",
                    {
                        placeholder: config.primaryPlaceholder || `Search ${config.primaryLabel || "value"}`,
                    },
                );
            } else {
                primary = document.createElement("input");
                primary.type = "text";
                primary.placeholder = config.primaryPlaceholder || config.primaryLabel;
                primary.value = row[config.primaryKey] || "";
            }
            if (readonly) {
                primary.disabled = true;
            } else {
                primary.addEventListener("input", () => {
                    row[config.primaryKey] = primary.value;
                    config.onChange();
                });
                primary.addEventListener("change", () => {
                    row[config.primaryKey] = primary.value;
                    config.onChange();
                });
            }
            rowNode.append(primary);

            if (config.secondaryKey) {
                const secondaryOptions = config.secondaryOptions || [];
                const secondaryControl = config.secondaryControl || "text";
                let secondary;
                if (secondaryControl === "select" || secondaryOptions.length) {
                    secondary = createSearchableSelect(
                        optionsWithBlank(
                            secondaryOptions,
                            config.secondaryPlaceholder || `Choose ${config.secondaryLabel || "value"}`,
                        ),
                        row[config.secondaryKey] || "",
                        {
                            placeholder: config.secondaryPlaceholder || `Search ${config.secondaryLabel || "value"}`,
                        },
                    );
                } else {
                    secondary = document.createElement("input");
                    secondary.type = "text";
                    secondary.placeholder = config.secondaryPlaceholder || config.secondaryLabel;
                    secondary.value = row[config.secondaryKey] || "";
                }
                if (readonly) {
                    secondary.disabled = true;
                } else {
                    secondary.addEventListener("input", () => {
                        row[config.secondaryKey] = secondary.value;
                        config.onChange();
                    });
                    secondary.addEventListener("change", () => {
                        row[config.secondaryKey] = secondary.value;
                        config.onChange();
                    });
                }
                rowNode.append(secondary);
            }

            if (!readonly) {
                const removeButton = document.createElement("button");
                removeButton.type = "button";
                removeButton.className = "mini-button danger";
                removeButton.textContent = "Remove";
                removeButton.disabled = Number.isInteger(config.minRows) && config.rows.length <= config.minRows;
                removeButton.addEventListener("click", () => {
                    config.rows.splice(index, 1);
                    renderRows();
                    config.onChange();
                });
                rowNode.append(removeButton);
            }
            rowsNode.append(rowNode);
        });
    };

    renderRows();
    return section;
}

function buildTableListEditor(config) {
    const section = document.createElement("section");
    section.className = "structured-group";

    const header = document.createElement("div");
    header.className = "structured-group-head";
    header.innerHTML = `<h4>${escapeHtml(config.title)}</h4>`;
    const addButton = document.createElement("button");
    addButton.type = "button";
    addButton.className = "mini-button";
    addButton.textContent = config.addLabel || "Add row";
    header.append(addButton);
    section.append(header);

    const rowsNode = document.createElement("div");
    rowsNode.className = "structured-rows";
    section.append(rowsNode);

    const renderRows = () => {
        rowsNode.innerHTML = "";
        if (!config.rows.length) {
            const empty = document.createElement("div");
            empty.className = "structured-empty";
            empty.textContent = "No rows yet.";
            rowsNode.append(empty);
        }
        config.rows.forEach((row, index) => {
            const rowNode = document.createElement("div");
            rowNode.className = "structured-row dynamic";
            rowNode.style.gridTemplateColumns = `${config.columns.map((column) => column.width || "minmax(0, 1fr)").join(" ")} auto`;

            for (const column of config.columns) {
                const options =
                    typeof column.options === "function" ? column.options(row) : column.options || [];
                let input;
                if (column.control === "select" || options.length) {
                    input = createSearchableSelect(options, row[column.key] || "", {
                        placeholder: `Search ${column.label || "value"}`,
                    });
                } else {
                    input = document.createElement("input");
                    input.type = "text";
                    input.value = row[column.key] || "";
                    input.placeholder = column.label;
                }
                input.addEventListener("input", () => {
                    row[column.key] = input.value;
                    config.onChange();
                });
                input.addEventListener("change", () => {
                    row[column.key] = input.value;
                    if (column.rerenderOnChange) {
                        renderRows();
                    }
                    config.onChange();
                });
                rowNode.append(input);
            }

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className = "mini-button danger";
            removeButton.textContent = "Remove";
            removeButton.addEventListener("click", () => {
                config.rows.splice(index, 1);
                renderRows();
                config.onChange();
            });
            rowNode.append(removeButton);
            rowsNode.append(rowNode);
        });
    };

    addButton.addEventListener("click", () => {
        config.rows.push(config.createRow());
        renderRows();
        config.onChange();
    });

    renderRows();
    return section;
}

function buildScalarEditor(label, value, onChange, options = null) {
    const node = document.createElement("label");
    node.className = "scalar-field";
    const title = document.createElement("span");
    title.textContent = label;
    node.append(title);

    let input;
    if (options && options.length) {
        input = createSearchableSelect(options, value ?? "", {
            placeholder: `Search ${label || "value"}`,
        });
    } else {
        input = document.createElement("input");
        input.type = "text";
        input.value = value ?? "";
    }
    input.addEventListener("input", () => onChange(input.value));
    input.addEventListener("change", () => onChange(input.value));
    node.append(input);
    return node;
}

function buildTextareaEditor(label, value, rows, onChange) {
    const node = document.createElement("label");
    node.className = "scalar-field wide";
    const title = document.createElement("span");
    title.textContent = label;
    node.append(title);
    const input = document.createElement("textarea");
    input.rows = rows;
    input.value = value ?? "";
    input.addEventListener("input", () => onChange(input.value));
    node.append(input);
    return node;
}

function applyPresetRows(targetRows, sourceRows) {
    targetRows.splice(0, targetRows.length, ...deepClone(sourceRows || []));
}

function buildPresetEditor(stateValue, label, onApply) {
    return buildScalarEditor(label, stateValue.template_id, (value) => {
        const previousValue = stateValue.template_id;
        stateValue.template_id = value;
        onApply(value, previousValue);
    }, stateValue.template_options || []);
}

function renderSiteTriggerField(field, scope) {
    const shell = createStructuredShell(field, scope);
    const { editor, stateValue, commit } = shell;
    const body = document.createElement("div");
    body.className = "structured-editor-body";
    editor.append(body);

    const renderBody = () => {
        body.innerHTML = "";
        body.append(
            buildPresetEditor(stateValue, "Condition template", (value, previousValue) => {
                if (value === "custom_script" && previousValue !== "custom_script") {
                    const previewState = deepClone(stateValue);
                    previewState.template_id = previousValue;
                    stateValue.raw_script = renderSiteTriggerScript(previewState);
                }
                if (value !== "custom_script" && value !== "current_variant") {
                    const preset = (stateValue.presets || []).find((item) => item.id === value);
                    if (preset) {
                        applyPresetRows(stateValue.any_of.rows, preset.any_of.map((entry) => ({ value: entry })));
                        applyPresetRows(stateValue.all_of.rows, preset.all_of.map((entry) => ({ value: entry })));
                    }
                }
                commit();
                renderBody();
            }),
        );

        if (stateValue.template_id === "custom_script") {
            body.append(
                buildTextareaEditor("Custom trigger script", stateValue.raw_script, 10, (value) => {
                    stateValue.raw_script = value;
                    commit();
                }),
            );
            return;
        }

        body.append(
            buildRowListEditor({
                title: "Any-of conditions",
                rows: stateValue.any_of.rows,
                primaryKey: "value",
                primaryLabel: "Condition",
                primaryOptions: stateValue.any_of.options || stateValue.condition_options || [],
                addLabel: "Add any-of",
                createRow: () => ({ value: "" }),
                onChange: commit,
            }),
            buildRowListEditor({
                title: "All-of conditions",
                rows: stateValue.all_of.rows,
                primaryKey: "value",
                primaryLabel: "Condition",
                primaryOptions: stateValue.all_of.options || stateValue.condition_options || [],
                addLabel: "Add all-of",
                createRow: () => ({ value: "" }),
                onChange: commit,
            }),
        );
    };

    renderBody();
    commit();
    return shell.shell;
}

function renderSitePreferenceField(field, scope) {
    const shell = createStructuredShell(field, scope);
    const { editor, stateValue, commit } = shell;
    const body = document.createElement("div");
    body.className = "structured-editor-body";
    editor.append(body);

    const renderBody = () => {
        body.innerHTML = "";
        body.append(
            buildPresetEditor(stateValue, "Preference template", (value, previousValue) => {
                if (value === "custom_script" && previousValue !== "custom_script") {
                    const previewState = deepClone(stateValue);
                    previewState.template_id = previousValue;
                    stateValue.raw_script = renderSitePreferenceScript(previewState);
                }
                if (value !== "custom_script" && value !== "current_variant") {
                    const preset = (stateValue.presets || []).find((item) => item.id === value);
                    if (preset) {
                        applyPresetRows(stateValue.bonus_rules.rows, preset.bonus_rules);
                        applyPresetRows(stateValue.scaled_rules.rows, preset.scaled_rules);
                    }
                }
                commit();
                renderBody();
            }),
        );

        if (stateValue.template_id === "custom_script") {
            body.append(
                buildTextareaEditor("Custom preference script", stateValue.raw_script, 14, (value) => {
                    stateValue.raw_script = value;
                    commit();
                }),
            );
            return;
        }

        body.append(
            buildTableListEditor({
                title: "Conditional bonus rows",
                rows: stateValue.bonus_rules.rows,
                columns: [
                    { key: "branch", label: "Branch", control: "select", options: stateValue.branch_options || [], width: "120px" },
                    { key: "condition", label: "Condition", control: "select", options: stateValue.condition_options || [], width: "minmax(0, 1.8fr)" },
                    { key: "value", label: "Value", width: "140px" },
                ],
                addLabel: "Add bonus rule",
                createRow: () => ({ branch: "if", condition: "", value: "" }),
                onChange: commit,
            }),
            buildTableListEditor({
                title: "Scaled bonus rows",
                rows: stateValue.scaled_rules.rows,
                columns: [
                    { key: "source", label: "Source", control: "select", options: stateValue.scale_source_options || [], width: "minmax(0, 1.4fr)" },
                    { key: "min", label: "Min", width: "110px" },
                    { key: "max", label: "Max", width: "110px" },
                    { key: "multiplier", label: "Multiplier", width: "140px" },
                ],
                addLabel: "Add scale rule",
                createRow: () => {
                    const defaults = stateValue.scale_source_options?.[0] || {};
                    return {
                        source: defaults.value || "",
                        min: defaults.default_min || "",
                        max: defaults.default_max || "",
                        multiplier: defaults.default_multiplier || "",
                    };
                },
                onChange: commit,
            }),
        );
    };

    renderBody();
    commit();
    return shell.shell;
}

function renderModifierTableField(field, scope) {
    const shell = createStructuredShell(field, scope);
    const { editor, stateValue, commit } = shell;
    editor.append(
        buildRowListEditor({
            title: stateValue.modifier_scope === "local" ? "Local modifier list" : "Country modifier list",
            rows: stateValue.rows,
            primaryKey: "modifier",
            secondaryKey: "value",
            primaryLabel: "Modifier",
            secondaryLabel: "Value",
            primaryOptions: stateValue.options || [],
            primaryControl: "select",
            addLabel: "Add modifier",
            createRow: () => ({ modifier: "", value: "" }),
            onChange: commit,
        }),
    );
    if (Array.isArray(stateValue.derived_rows) && stateValue.derived_rows.length) {
        editor.append(
            buildRowListEditor({
                title: stateValue.derived_title || "Auto-applied modifiers",
                note: stateValue.derived_help_text || "",
                rows: stateValue.derived_rows,
                primaryKey: "modifier",
                secondaryKey: "value",
                primaryLabel: "Modifier",
                secondaryLabel: "Value",
                primaryControl: "text",
                secondaryControl: "text",
                readonly: true,
                emptyText: "No auto-applied modifiers.",
            }),
        );
    }
    commit();
    return shell.shell;
}

function renderRewardEditorField(field, scope) {
    const shell = createStructuredShell(field, scope);
    const { editor, stateValue, commit } = shell;

    if (stateValue.cost_options) {
        editor.append(
            buildScalarEditor("Cost type", stateValue.cost_type ?? "", (value) => {
                stateValue.cost_type = value || null;
                commit();
            }, stateValue.cost_options),
        );
    }

    editor.append(
        buildRowListEditor({
            title: "Reward rows",
            rows: stateValue.rows,
            primaryKey: "type",
            secondaryKey: "value",
            primaryLabel: "Reward type",
            secondaryLabel: "Value",
            primaryOptions: stateValue.options || [],
            primaryControl: "select",
            addLabel: "Add reward",
            createRow: () => ({ type: "", value: "" }),
            onChange: commit,
        }),
    );
    commit();
    return shell.shell;
}

function renderUniqueRitualEditorField(field, scope) {
    const shell = createStructuredShell(field, scope);
    const { editor, stateValue, commit } = shell;

    const overview = document.createElement("div");
    overview.className = "scalar-grid";
    overview.append(
        buildScalarEditor("Ritual key", stateValue.key, (value) => {
            stateValue.key = value;
            commit();
        }),
        buildScalarEditor("Mode", stateValue.mode, (value) => {
            stateValue.mode = value;
            commit();
        }, stateValue.mode_options || []),
        buildScalarEditor("Cost type", stateValue.cost_type ?? "", (value) => {
            stateValue.cost_type = value || null;
            commit();
        }, stateValue.cost_options || []),
        buildScalarEditor("Timed years", stateValue.timed?.years ?? 1, (value) => {
            stateValue.timed.years = value;
            commit();
        }),
        buildScalarEditor("Auxiliary max levels", stateValue.auxiliary_building?.max_levels ?? 1, (value) => {
            stateValue.auxiliary_building.max_levels = value;
            commit();
        }),
    );
    editor.append(overview);

    editor.append(
        buildRowListEditor({
            title: "Listeners",
            rows: stateValue.listeners.rows,
            primaryKey: "value",
            primaryLabel: "Listener",
            primaryOptions: stateValue.listeners.options || [],
            addLabel: "Add listener",
            createRow: () => ({ value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Runtime variables",
            rows: stateValue.runtime_variables.rows,
            primaryKey: "value",
            primaryLabel: "Variable",
            addLabel: "Add variable",
            createRow: () => ({ value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Country modifiers",
            rows: stateValue.country_modifier.rows,
            primaryKey: "modifier",
            secondaryKey: "value",
            primaryLabel: "Modifier",
            secondaryLabel: "Value",
            primaryOptions: stateValue.country_modifier.options || [],
            primaryControl: "select",
            addLabel: "Add modifier",
            createRow: () => ({ modifier: "", value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Reward rows",
            rows: stateValue.reward.rows,
            primaryKey: "type",
            secondaryKey: "value",
            primaryLabel: "Reward type",
            secondaryLabel: "Value",
            primaryOptions: stateValue.reward.options || [],
            addLabel: "Add reward",
            createRow: () => ({ type: "", value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Timed burden modifiers",
            rows: stateValue.timed.burden_modifier.rows,
            primaryKey: "modifier",
            secondaryKey: "value",
            primaryLabel: "Modifier",
            secondaryLabel: "Value",
            primaryOptions: stateValue.timed.burden_modifier.options || [],
            primaryControl: "select",
            addLabel: "Add modifier",
            createRow: () => ({ modifier: "", value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Timed blessing modifiers",
            rows: stateValue.timed.blessing_modifier.rows,
            primaryKey: "modifier",
            secondaryKey: "value",
            primaryLabel: "Modifier",
            secondaryLabel: "Value",
            primaryOptions: stateValue.timed.blessing_modifier.options || [],
            primaryControl: "select",
            addLabel: "Add modifier",
            createRow: () => ({ modifier: "", value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Auxiliary local modifiers",
            rows: stateValue.auxiliary_building.local_modifier.rows,
            primaryKey: "modifier",
            secondaryKey: "value",
            primaryLabel: "Modifier",
            secondaryLabel: "Value",
            primaryOptions: stateValue.auxiliary_building.local_modifier.options || [],
            primaryControl: "select",
            addLabel: "Add modifier",
            createRow: () => ({ modifier: "", value: "" }),
            onChange: commit,
        }),
        buildRowListEditor({
            title: "Auxiliary attributes",
            rows: stateValue.auxiliary_building.attributes.rows,
            primaryKey: "modifier",
            secondaryKey: "value",
            primaryLabel: "Attribute",
            secondaryLabel: "Value",
            addLabel: "Add attribute",
            createRow: () => ({ modifier: "", value: "" }),
            onChange: commit,
        }),
    );

    const auxiliary = document.createElement("div");
    auxiliary.className = "scalar-grid";
    auxiliary.append(
        buildScalarEditor("Maintenance", stateValue.auxiliary_building.maintenance, (value) => {
            stateValue.auxiliary_building.maintenance = value;
            commit();
        }),
        buildScalarEditor("Build time", stateValue.auxiliary_building.build_time, (value) => {
            stateValue.auxiliary_building.build_time = value;
            commit();
        }),
        buildScalarEditor("Construction demand", stateValue.auxiliary_building.construction_demand, (value) => {
            stateValue.auxiliary_building.construction_demand = value;
            commit();
        }),
        buildScalarEditor("Price", stateValue.auxiliary_building.price, (value) => {
            stateValue.auxiliary_building.price = value;
            commit();
        }),
    );
    editor.append(auxiliary);

    const scripts = document.createElement("div");
    scripts.className = "scalar-grid";
    scripts.append(
        buildTextareaEditor("Confirmation trigger script", stateValue.confirmation_trigger_script, 5, (value) => {
            stateValue.confirmation_trigger_script = value;
            commit();
        }),
        buildTextareaEditor("Start effect script", stateValue.start_effect_script, 5, (value) => {
            stateValue.start_effect_script = value;
            commit();
        }),
        buildTextareaEditor("Snapshot effect script", stateValue.snapshot_effect_script, 5, (value) => {
            stateValue.snapshot_effect_script = value;
            commit();
        }),
        buildTextareaEditor("Progress effect script", stateValue.progress_effect_script, 5, (value) => {
            stateValue.progress_effect_script = value;
            commit();
        }),
        buildTextareaEditor("Completion trigger script", stateValue.completion_trigger_script, 5, (value) => {
            stateValue.completion_trigger_script = value;
            commit();
        }),
        buildTextareaEditor("Completion effect script", stateValue.completion_effect_script, 5, (value) => {
            stateValue.completion_effect_script = value;
            commit();
        }),
    );
    editor.append(scripts);

    commit();
    return shell.shell;
}

function renderUniqueCeremonyEditorField(field, scope) {
    const shell = createStructuredShell(field, scope);
    const { editor, stateValue, commit } = shell;
    const stageCount = Number.parseInt(
        String(stateValue.stage_count ?? stateValue.stages?.length ?? ""),
        10,
    );

    for (const [index, stage] of (stateValue.stages || []).entries()) {
        const group = document.createElement("section");
        group.className = "structured-group";

        const header = document.createElement("div");
        header.className = "structured-group-head";
        const title = document.createElement("h4");
        title.textContent = `Stage ${index + 1} of ${
            Number.isFinite(stageCount) ? stageCount : stateValue.stages.length
        }`;
        header.append(title);

        const textFields = document.createElement("div");
        textFields.className = "scalar-grid";
        textFields.append(
            buildScalarEditor("Title (English)", stage.title_en, (value) => {
                stage.title_en = value;
                commit();
            }),
            buildScalarEditor("Title (Simplified Chinese)", stage.title_zh, (value) => {
                stage.title_zh = value;
                commit();
            }),
            buildTextareaEditor("Description (English)", stage.desc_en, 4, (value) => {
                stage.desc_en = value;
                commit();
            }),
            buildTextareaEditor("Description (Simplified Chinese)", stage.desc_zh, 4, (value) => {
                stage.desc_zh = value;
                commit();
            }),
            buildScalarEditor("Card icon (vanilla font icon key)", stage.icon, (value) => {
                stage.icon = value;
                commit();
            }),
            buildTextareaEditor("Icon rationale", stage.icon_rationale, 2, (value) => {
                stage.icon_rationale = value;
                commit();
            }),
        );

        group.append(
            header,
            textFields,
            buildRowListEditor({
                title: "Stage costs (one or two required)",
                rows: stage.cost.rows,
                primaryKey: "type",
                secondaryKey: "value",
                primaryLabel: "Cost type",
                secondaryLabel: "Value",
                primaryOptions: stage.cost.options || [],
                primaryControl: "select",
                addLabel: "Add cost",
                minRows: 1,
                maxRows: 2,
                createRow: () => ({ type: "", value: "" }),
                onChange: commit,
            }),
        );
        editor.append(group);
    }

    commit();
    return shell.shell;
}

function renderStructuredFieldByType(field, scope) {
    if (field.field_type === "modifier_table") {
        return renderModifierTableField(field, scope);
    }
    if (field.field_type === "reward_editor") {
        return renderRewardEditorField(field, scope);
    }
    if (field.field_type === "unique_ritual_editor") {
        return renderUniqueRitualEditorField(field, scope);
    }
    if (field.field_type === "unique_ceremony_editor") {
        return renderUniqueCeremonyEditorField(field, scope);
    }
    if (field.field_type === "site_trigger_template") {
        return renderSiteTriggerField(field, scope);
    }
    if (field.field_type === "site_preference_template") {
        return renderSitePreferenceField(field, scope);
    }
    return createEditorBinding(field, scope);
}

function renderReadonlyStructuredField(field, scope) {
    const shell = renderStructuredFieldByType(field, scope);
    const editor = shell.querySelector(".structured-editor");
    if (editor) {
        editor.prepend(buildReadonlyStructuredNote(field));
        for (const control of editor.querySelectorAll("input, select, textarea, button")) {
            if (control.closest(".readonly-actions")) {
                continue;
            }
            control.disabled = true;
        }
    }
    return shell;
}

function buildEditorInput(field, scope) {
    if (field.editable === false && isStructuredFieldType(field.field_type || "text")) {
        return renderReadonlyStructuredField(field, scope);
    }
    if (isStructuredFieldType(field.field_type || "text")) {
        return renderStructuredFieldByType(field, scope);
    }
    if (scope === "mechanics" && field.target_kind === "unique_initial_level") {
        return createSingleLineEditorBinding(field, scope, updateUniqueInitialLevelPreview);
    }
    return createEditorBinding(field, scope);
}

function renderSections(panel, sections, scope) {
    for (const section of sections) {
        const sectionNode = document.createElement("section");
        sectionNode.className = "field-section";

        const header = document.createElement("div");
        header.className = "section-header";
        header.innerHTML = `<h3>${escapeHtml(section.group)}</h3>`;
        sectionNode.append(header);

        const fields = document.createElement("div");
        fields.className = "field-list";

        for (const field of section.fields) {
            if (scope === "localization" && isCurrentWonderNameField(field)) {
                continue;
            }
            const fieldNode = document.createElement("article");
            fieldNode.className = "field-card";
            fieldNode.innerHTML = `
                <div class="field-head">
                    <div>
                        <span class="field-label">${escapeHtml(field.label)}</span>
                        <code>${escapeHtml(field.key)}</code>
                    </div>
                    <span class="origin-pill">${escapeHtml(field.origin_label || "")}</span>
                </div>
            `;
            if (scope === "mechanics" && field.source_path) {
                const sourceMap = document.createElement("p");
                sourceMap.className = "field-source-map";
                sourceMap.textContent = `${field.source_path} -> ${field.target_path || field.key}`;
                fieldNode.append(sourceMap);
            }
            if (field.help_text) {
                const help = document.createElement("p");
                help.className = "field-help";
                help.textContent = field.help_text;
                fieldNode.append(help);
            }
            fieldNode.append(buildEditorInput(field, scope));
            fields.append(fieldNode);
        }

        if (!fields.childElementCount) {
            continue;
        }
        sectionNode.append(fields);
        panel.append(sectionNode);
    }
}

const RITUAL_DESIGN_FIELD_ORDER = [
    "title",
    "historical_flavor",
    "mode",
    "duration",
    "listeners",
    "confirmation_logic",
    "start_logic",
    "progress_logic",
    "completion_logic",
    "failure_or_timeout_logic",
    "implementation_mapping",
    "intended_rewards",
    "notes",
];

function ritualDesignForDisplay(design) {
    const translated = design?.ritual_design_zh;
    if (translated && typeof translated === "object" && Object.keys(translated).length > 0) {
        return translated;
    }
    return design?.ritual_design || {};
}

function ritualDesignOriginal(design) {
    return design?.ritual_design || {};
}

function ritualDesignHasTranslation(design) {
    const translated = design?.ritual_design_zh;
    return Boolean(translated && typeof translated === "object" && Object.keys(translated).length > 0);
}

function currentRitualDesignEntry() {
    if (!state.currentWonder?.summary?.is_unique) {
        return null;
    }
    if (state.currentWonder.ritual_design) {
        return state.currentWonder.ritual_design;
    }
    const wonderId = state.currentWonder.summary.id;
    return (state.ritualDesigns?.wonders || []).find((entry) => Number(entry.id) === Number(wonderId)) || null;
}

function currentRitualPromptOriginal() {
    const wonderId = currentWonderId();
    const currentPrompt = state.currentWonder?.ritual_prompt?.prompt;
    if (currentPrompt !== undefined) {
        return String(currentPrompt || "");
    }
    const entry = (state.ritualDesigns?.wonders || []).find((item) => Number(item.id) === Number(wonderId));
    return String(entry?.prompt || "");
}

function currentRitualPromptValue() {
    const wonderId = currentWonderId();
    const draftValue = state.ritualPromptDrafts[String(wonderId)];
    return draftValue === undefined ? currentRitualPromptOriginal() : draftValue;
}

function ritualDesignLabel(key) {
    return state.ritualDesigns?.field_labels?.[key] || key.replaceAll("_", " ");
}

function ritualDesignEntriesForDisplay(design) {
    const keys = Object.keys(design || {}).filter(
        (key) =>
            ![
                "id",
                "key",
                "base_key",
                "location",
                "source_ritual_key",
                "status",
                "name_en",
                "name_zh",
                "display_name",
                "source_path",
                "prompt",
            ].includes(key),
    );
    const ordered = RITUAL_DESIGN_FIELD_ORDER.filter((key) => keys.includes(key));
    return [...ordered, ...keys.filter((key) => !ordered.includes(key))];
}

function ritualDesignValueToPromptLines(key, value, depth = 0) {
    if (value === null || value === undefined || value === "") {
        return [];
    }
    const indent = "  ".repeat(depth);
    const label = ritualDesignLabel(key);
    if (Array.isArray(value)) {
        const lines = [`${indent}${label}:`];
        for (const item of value) {
            lines.push(`${indent}- ${String(item)}`);
        }
        return lines;
    }
    if (typeof value === "object") {
        const lines = [`${indent}${label}:`];
        for (const nestedKey of ritualDesignEntriesForDisplay(value)) {
            lines.push(...ritualDesignValueToPromptLines(nestedKey, value[nestedKey], depth + 1));
        }
        return lines;
    }
    return [`${indent}${label}: ${String(value)}`];
}

function buildRitualImplementationPrompt(design) {
    const ritualDesign = ritualDesignForDisplay(design);
    const lines = [
        `请实现独特奇观仪式：${design?.display_name || design?.key || ""}`,
        `奇观 key: ${design?.key || ""}`,
        `base_key: ${design?.base_key || ""}`,
        `location: ${design?.location || ""}`,
        `source_ritual_key: ${design?.source_ritual_key || ""}`,
        "",
        "实现要求：",
        "- 遵守 data/unique_wonder_ritual_designs.yaml 的三阶段事件链与奖励契约。",
        "- 不要把自然语言设计稿直接接入生成器；先落成明确 schema 和 EU5 脚本。",
        "- 保留永久国家修正、本地奖励建筑、一次性奖励三种奖励渠道各一次。",
        "- 修改前按 CLAUDE.md 读取风险上下文，修改后运行 validate.py --changed --fix --ai-report。",
        "",
        "仪式设计稿：",
    ];
    for (const key of ritualDesignEntriesForDisplay(ritualDesign)) {
        lines.push(...ritualDesignValueToPromptLines(key, ritualDesign[key]));
    }
    if (ritualDesignHasTranslation(design)) {
        const original = ritualDesignOriginal(design);
        lines.push("", "英文原文标题：", String(original.title || ""));
    }
    return lines.join("\n").trim();
}

function appendRitualDesignValue(container, key, value) {
    if (value === null || value === undefined || value === "") {
        return;
    }
    const field = document.createElement("div");
    field.className = "ritual-design-field";
    const title = document.createElement("h4");
    title.textContent = ritualDesignLabel(key);
    field.append(title);

    if (Array.isArray(value)) {
        const list = document.createElement("ul");
        list.className = "ritual-design-list";
        for (const item of value) {
            const row = document.createElement("li");
            row.textContent = String(item);
            list.append(row);
        }
        field.append(list);
    } else if (typeof value === "object") {
        const nested = document.createElement("div");
        nested.className = "ritual-design-nested";
        for (const nestedKey of ritualDesignEntriesForDisplay(value)) {
            appendRitualDesignValue(nested, nestedKey, value[nestedKey]);
        }
        field.append(nested);
    } else {
        const text = document.createElement("p");
        text.className = "ritual-design-text";
        text.textContent = String(value);
        field.append(text);
    }
    container.append(field);
}

function renderRitualDesignBody(design, ritualDesign = ritualDesignForDisplay(design)) {
    const body = document.createElement("div");
    body.className = "ritual-design-body";
    for (const key of ritualDesignEntriesForDisplay(ritualDesign)) {
        appendRitualDesignValue(body, key, ritualDesign[key]);
    }
    return body;
}

function renderRitualDesignSummary(design, isCurrent) {
    const summary = document.createElement("summary");
    summary.className = "ritual-design-summary";
    const ritualDesign = ritualDesignForDisplay(design);
    const listeners = (ritualDesign.listeners || []).join(", ") || "none";
    const translationState = ritualDesignHasTranslation(design) ? "中文" : "英文原文";
    summary.innerHTML = `
        <span class="ritual-design-title">${escapeHtml(design.display_name || design.key || "")}</span>
        <span class="ritual-design-subtitle">${escapeHtml(ritualDesign.title || "")}</span>
        <span class="ritual-design-meta">
            ID ${escapeHtml(design.id || "")} · ${escapeHtml(design.key || "")} · ${escapeHtml(ritualDesign.mode || "")} · ${escapeHtml(listeners)}
            ${isCurrent ? " · 当前奇观" : ""}
        </span>
    `;
    const badge = document.createElement("span");
    badge.className = "ritual-design-translation-state";
    badge.textContent = translationState;
    summary.append(badge);
    return summary;
}

function appendOriginalRitualDesign(container, design, { showFallbackNote = true } = {}) {
    if (!ritualDesignHasTranslation(design)) {
        if (!showFallbackNote) {
            return;
        }
        const note = document.createElement("p");
        note.className = "ritual-design-translation-note";
        note.textContent = "尚未提供中文 ritual_design_zh，当前显示英文原文。";
        container.append(note);
        return;
    }
    const details = document.createElement("details");
    details.className = "ritual-design-original";
    const summary = document.createElement("summary");
    summary.textContent = "英文原文";
    details.append(summary, renderRitualDesignBody(design, ritualDesignOriginal(design)));
    container.append(details);
}

function renderRitualPromptCard(panel) {
    const section = document.createElement("section");
    section.className = "ritual-prompt-card";
    const originalPrompt = currentRitualPromptOriginal();
    const value = currentRitualPromptValue();
    section.innerHTML = `
        <div class="panel-header compact">
            <div>
                <p class="eyebrow">AI Prompt</p>
                <h3>实现指令 Prompt</h3>
            </div>
            <span class="origin-pill">${escapeHtml(state.ritualDesigns?.prompt_source_path || "")}</span>
        </div>
    `;

    const textarea = document.createElement("textarea");
    textarea.className = "ritual-prompt-input";
    textarea.rows = 10;
    textarea.placeholder = "在这里输入用于后续指示 AI 实现该独特奇观仪式的 prompt。";
    textarea.value = value;
    textarea.dataset.ritualPromptInput = "true";
    textarea.dataset.originalPrompt = originalPrompt;
    textarea.dataset.ritualPromptControl = "true";

    const actions = document.createElement("div");
    actions.className = "ritual-prompt-actions";
    const draftButton = document.createElement("button");
    draftButton.type = "button";
    draftButton.className = "secondary-button";
    draftButton.textContent = "用当前设计生成 Prompt 草稿";
    draftButton.dataset.ritualPromptControl = "true";
    const saveButton = document.createElement("button");
    saveButton.type = "button";
    saveButton.className = "primary-button";
    saveButton.textContent = "保存 Prompt 到 YAML";
    saveButton.dataset.ritualPromptControl = "true";
    const status = document.createElement("span");
    status.className = "ritual-prompt-status";

    const refreshPromptState = () => {
        cacheCurrentRitualPromptDraft();
        const changed = normalizeMultilineText(textarea.value) !== textarea.dataset.originalPrompt;
        saveButton.disabled = state.busy || !changed;
        status.textContent = changed ? "Prompt 尚未保存" : "Prompt 已同步";
    };
    textarea.addEventListener("input", refreshPromptState);
    draftButton.addEventListener("click", () => {
        const currentDesign = currentRitualDesignEntry();
        if (!currentDesign) {
            return;
        }
        textarea.value = buildRitualImplementationPrompt(currentDesign);
        refreshPromptState();
        textarea.focus();
    });
    saveButton.addEventListener("click", () => {
        void saveCurrentRitualPrompt(textarea.value);
    });
    actions.append(draftButton, saveButton, status);
    section.append(textarea, actions);
    panel.append(section);
    refreshPromptState();
}

function renderRitualDesignPanel(panel) {
    if (!state.currentWonder?.summary?.is_unique) {
        panel.innerHTML = '<div class="empty-state wide">请选择一个独特奇观以查看仪式设计。</div>';
        return;
    }
    const currentDesign = currentRitualDesignEntry();
    renderRitualPromptCard(panel);

    if (currentDesign) {
        const currentSection = document.createElement("section");
        currentSection.className = "ritual-design-current";
        currentSection.innerHTML = `
            <div class="section-header">
                <h3>当前独特奇观原始设计</h3>
            </div>
        `;
        const card = document.createElement("article");
        card.className = "ritual-design-card current";
        card.append(renderRitualDesignSummary(currentDesign, true), renderRitualDesignBody(currentDesign));
        appendOriginalRitualDesign(card, currentDesign);
        currentSection.append(card);
        panel.append(currentSection);
    }

    const allSection = document.createElement("section");
    allSection.className = "ritual-design-all";
    allSection.innerHTML = `
        <div class="section-header">
            <h3>全部独特奇观仪式原始设计</h3>
        </div>
        <p class="ritual-design-count">
            来源：${escapeHtml(state.ritualDesigns?.source_path || "")} · 共 ${escapeHtml(state.ritualDesigns?.count || 0)} 条。
        </p>
    `;
    const list = document.createElement("div");
    list.className = "ritual-design-listing";
    for (const design of state.ritualDesigns?.wonders || []) {
        const isCurrent = Number(design.id) === Number(state.currentWonder.summary.id);
        const item = document.createElement("details");
        item.className = "ritual-design-card";
        item.open = isCurrent;
        item.append(renderRitualDesignSummary(design, isCurrent), renderRitualDesignBody(design));
        appendOriginalRitualDesign(item, design, { showFallbackNote: false });
        list.append(item);
    }
    allSection.append(list);
    panel.append(allSection);
}

function renderEditorPanels() {
    elements.languagePanels.innerHTML = "";
    if (!state.currentWonder) {
        elements.languagePanels.innerHTML = '<div class="empty-state wide">没有可编辑的奇观数据。</div>';
        return;
    }

    for (const [language, payload] of Object.entries(state.currentWonder.languages)) {
        const panel = document.createElement("div");
        panel.className = "language-panel";
        panel.dataset.editorTab = language;
        renderSections(panel, payload.sections, "localization");
        elements.languagePanels.append(panel);
    }

    if (state.currentWonder.mechanics) {
        const panel = document.createElement("div");
        panel.className = "language-panel";
        panel.dataset.editorTab = "mechanics";
        renderSections(panel, state.currentWonder.mechanics.sections, "mechanics");
        elements.languagePanels.append(panel);
    }

    if (state.currentWonder.summary?.is_unique && state.ritualDesigns) {
        const panel = document.createElement("div");
        panel.className = "language-panel";
        panel.dataset.editorTab = "ritual-design";
        renderRitualDesignPanel(panel);
        elements.languagePanels.append(panel);
    }

    syncActiveEditorPanel();
    refreshDirtyState();
}

function syncActiveEditorPanel() {
    const panels = elements.languagePanels.querySelectorAll(".language-panel");
    for (const panel of panels) {
        panel.classList.toggle("hidden", panel.dataset.editorTab !== state.activeEditorTab);
    }
}

function renderLog() {
    elements.logOutput.textContent = state.logText || "[server] 暂无新日志";
    elements.copyLogButton.disabled = !state.logText;
}

function render() {
    state.rendering = true;
    try {
        elements.appTitle.textContent = state.title;
        renderWonderKindTabs();
        renderWonderList();
        renderMeta();
        renderWonderImage();
        renderWonderNameEditors();
        renderEditorTabs();
        renderEditorPanels();
        renderLog();
        updateStatus(state.status, state.statusKind);
    } finally {
        state.rendering = false;
    }
    refreshDirtyState();
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });
    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`;
        try {
            const payload = await response.json();
            detail = payload.detail || detail;
        } catch {
            detail = await response.text();
        }
        throw new Error(detail);
    }
    return response.json();
}

function syncWonderModeWithSelection() {
    if (!state.currentWonder) {
        return;
    }
    state.listMode = currentWonderKind();
}

async function loadBootstrap() {
    setBusy(true);
    updateStatus("正在加载", "working");
    try {
        const payload = await fetchJson("/api/bootstrap");
        state.title = payload.title;
        state.wonders = payload.wonders;
        state.ritualDesigns = payload.ritual_designs || null;
        setCurrentWonderPayload(payload.current_wonder);
        state.logText = payload.log_text || "";
        state.status = payload.status || (state.currentWonder ? state.currentWonder.status : "就绪");
        state.statusKind = "default";
        syncWonderModeWithSelection();
        render();
    } catch (error) {
        console.error(error);
        updateStatus("加载失败", "error");
        showToast(`加载失败: ${error.message}`, "error");
    } finally {
        setBusy(false);
    }
}

async function selectWonder(wonderId) {
    if (state.busy) {
        return;
    }
    if (state.currentWonder && state.currentWonder.summary.id === wonderId) {
        return;
    }
    cacheCurrentWonderDraft();
    cacheCurrentRitualPromptDraft();

    setBusy(true);
    updateStatus("正在切换奇观", "working");
    try {
        const payload = await fetchJson(`/api/wonders/${wonderId}`);
        setCurrentWonderPayload(payload);
        state.status = payload.status;
        state.statusKind = "default";
        syncWonderModeWithSelection();
        render();
    } catch (error) {
        console.error(error);
        updateStatus("切换失败", "error");
        showToast(`切换失败: ${error.message}`, "error");
    } finally {
        setBusy(false);
    }
}

async function saveCurrentWonder() {
    if (!state.currentWonder || state.busy) {
        return;
    }
    cacheCurrentWonderDraft();
    cacheCurrentRitualPromptDraft();
    const currentId = currentWonderId();
    const drafts = Object.entries(state.pageDrafts)
        .filter(([, draft]) => draftHasChanges(draft))
        .map(([wonderId, draft]) => ({
            wonder_id: Number.parseInt(wonderId, 10),
            ...draft,
        }));
    setBusy(true);
    updateStatus("正在保存并重新生成", "working");
    try {
        const payload = await fetchJson("/api/wonders/save", {
            method: "POST",
            body: JSON.stringify({
                regenerate: true,
                current_wonder_id: currentId,
                wonders: drafts,
            }),
        });
        state.pageDrafts = {};
        state.wonders = payload.wonders;
        setCurrentWonderPayload(payload.wonder);
        state.logText = payload.log_text || state.logText;
        state.status = payload.status;
        state.statusKind = "default";
        syncWonderModeWithSelection();
        render();
        showToast(payload.status, "success");
    } catch (error) {
        console.error(error);
        updateStatus("保存失败", "error");
        showToast(`保存失败: ${error.message}`, "error");
    } finally {
        setBusy(false);
    }
}

async function saveCurrentRitualPrompt(prompt) {
    if (!state.currentWonder?.summary?.is_unique || state.busy) {
        return;
    }
    const wonderId = currentWonderId();
    setBusy(true);
    updateStatus("正在保存 Prompt", "working");
    try {
        const normalizedPrompt = normalizeMultilineText(String(prompt || ""));
        const payload = await fetchJson(`/api/ritual-prompts/${wonderId}`, {
            method: "POST",
            body: JSON.stringify({
                prompt: normalizedPrompt,
            }),
        });
        state.ritualDesigns = payload.ritual_designs || state.ritualDesigns;
        state.currentWonder.ritual_prompt = payload.prompt || state.currentWonder.ritual_prompt;
        delete state.ritualPromptDrafts[String(wonderId)];
        state.logText = payload.log_text || state.logText;
        state.status = payload.status;
        state.statusKind = "default";
        render();
        showToast(payload.status, "success");
    } catch (error) {
        console.error(error);
        updateStatus("Prompt 保存失败", "error");
        showToast(`Prompt 保存失败: ${error.message}`, "error");
    } finally {
        setBusy(false);
    }
}

async function reloadCurrentWonder() {
    if (!state.currentWonder || state.busy) {
        return;
    }
    cacheCurrentWonderDraft();
    const currentId = currentWonderId();
    if (draftHasChanges(state.pageDrafts[String(currentId)])) {
        const shouldDiscard = window.confirm("放弃当前未保存编辑并重新读取文件吗？");
        if (!shouldDiscard) {
            return;
        }
    }

    setBusy(true);
    updateStatus("正在重新加载", "working");
    try {
        const payload = await fetchJson(`/api/wonders/${state.currentWonder.summary.id}/reload`, {
            method: "POST",
        });
        delete state.pageDrafts[String(currentId)];
        state.wonders = payload.wonders;
        setCurrentWonderPayload(payload.wonder);
        state.logText = payload.log_text || state.logText;
        state.status = payload.status;
        state.statusKind = "default";
        syncWonderModeWithSelection();
        render();
        showToast(payload.status, "success");
    } catch (error) {
        console.error(error);
        updateStatus("重新加载失败", "error");
        showToast(`重新加载失败: ${error.message}`, "error");
    } finally {
        setBusy(false);
    }
}

async function copyLog() {
    if (!state.logText) {
        return;
    }
    try {
        await navigator.clipboard.writeText(state.logText);
        showToast("日志已复制", "success");
    } catch (error) {
        console.error(error);
        showToast(`复制失败: ${error.message}`, "error");
    }
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

elements.searchInput.addEventListener("input", renderWonderList);
elements.saveButton.addEventListener("click", () => {
    void saveCurrentWonder();
});
elements.reloadButton.addEventListener("click", () => {
    void reloadCurrentWonder();
});
elements.copyLogButton.addEventListener("click", () => {
    void copyLog();
});

window.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        void saveCurrentWonder();
    }
});

void loadBootstrap();
