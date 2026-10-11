import { createWonderFields } from "./wonder_fields.js";
import { createWonderEditor } from "./wonder_editor.js";
import { createWonderRituals } from "./wonder_rituals.js";
import { fetchJson } from "./api.js";
import { createStatusView, escapeHtml } from "./display.js";
import { ResourceState, setControlsBusy } from "./resource_state.js";

import {
    normalizeLocalizationText,
    normalizeMultilineText,
    isStructuredFieldType,
    restoreEditorOptions,
} from "./wonder_values.js";

const state = {
    title: "Towards Victory 奇观编辑器",
    resource: new ResourceState({
        saved: { wonders: [], pageDrafts: {} },
        isDirty: (_saved, draft) => Object.values(draft.pageDrafts).some(draftHasChanges),
        onChange: () => syncBusyControls(),
    }),
    get wonders() { return this.resource.draft.wonders; },
    get pageDrafts() { return this.resource.draft.pageDrafts; },
    get busy() { return this.resource.busy; },
    currentWonder: null,
    activeEditorTab: "english",
    listMode: "generic",
    status: "就绪",
    statusKind: "default",
    rendering: false,
};
let optionCatalog = null;
let optionCatalogRequest = null;

const toolSection = document.querySelector('.tool-panel[data-tool="wonder-localization"]');

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
    retryDetailButton: document.getElementById("retry-detail-button"),
    copyLogButton: document.getElementById("copy-log-button"),
    statusBadge: document.getElementById("status-badge"),
    dirtyBadge: document.getElementById("dirty-badge"),
    logOutput: document.getElementById("log-output"),
    toast: document.getElementById("toast"),
};
const wonderStatus = createStatusView(elements.statusBadge);
const { buildEditorInput, createSingleLineEditorBinding } = createWonderFields({
    onChange: refreshDirtyState,
    onOpenPrototype: (key) => {
        const target = findWonderByKey(key, false);
        if (target) {
            void wonderEditor.select(target.id);
        }
    },
    onInitialLevelChange: updateUniqueInitialLevelPreview,
});

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
    wonderStatus.set(text, kind);
}

function syncBusyControls() {
    setControlsBusy(document.querySelectorAll("#wonder-kind-tabs button, #wonder-list button, #language-tabs button, #search-input, #wonder-name-editors input, #wonder-name-editors textarea, #language-panels input, #language-panels textarea, #language-panels select, #language-panels button, #save-button, #reload-button, #retry-detail-button"), state.busy);
    toolSection.dataset.busy = String(state.busy);
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
                Object.keys(draft.mechanics || {}).length > 0 || draft.ritual_prompt !== undefined),
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
    const prompt = state.pageDrafts[String(currentWonderId())]?.ritual_prompt;
    if (prompt !== undefined) draft.ritual_prompt = prompt;
    return draft;
}

function cacheCurrentWonderDraft() {
    const wonderId = currentWonderId();
    if (wonderId === null || state.rendering || state.busy) {
        return;
    }
    const draft = collectCurrentDraft();
    state.resource.mutate((resourceDraft) => {
        if (draftHasChanges(draft)) resourceDraft.pageDrafts[String(wonderId)] = draft;
        else delete resourceDraft.pageDrafts[String(wonderId)];
    });
}

function applyDraftToField(field, scope, draft) {
    const cachedValue = draftValueForField(draft, field, scope);
    if (cachedValue === undefined) {
        return;
    }
    field.value = cachedValue;
    if (isStructuredFieldType(field.field_type || "text")) {
        try {
            field.structured_value = restoreEditorOptions(JSON.parse(cachedValue), field.structured_value);
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

function setPromptDraft(wonderId, value) {
    const key = String(wonderId);
    state.resource.mutate((resourceDraft) => {
        const current = resourceDraft.pageDrafts[key];
        if (value === undefined) {
            if (!current) return;
            delete current.ritual_prompt;
            if (!draftHasChanges(current)) delete resourceDraft.pageDrafts[key];
            return;
        }
        const draft = current || emptyDraft();
        draft.ritual_prompt = value;
        resourceDraft.pageDrafts[key] = draft;
    });
}

const wonderRituals = createWonderRituals({
    getCurrentWonder: () => state.currentWonder,
    getPromptDraft: (wonderId) => state.pageDrafts[String(wonderId)]?.ritual_prompt,
    setPromptDraft,
    isBusy: () => state.busy,
    onDirty: refreshDirtyState,
    onToast: showToast,
});

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
            if (state.busy) return;
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
        button.dataset.wonderKey = wonder.key;
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
            void wonderEditor.select(wonder.id);
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
    if (state.currentWonder.summary?.is_unique) {
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
            if (state.busy) return;
            state.activeEditorTab = tab.id;
            renderEditorTabs();
            syncActiveEditorPanel();
            if (tab.id === "ritual-design") {
                void wonderRituals.loadCatalog();
            }
        });
        elements.languageTabs.append(button);
    }
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

    if (state.currentWonder.summary?.is_unique) {
        const panel = document.createElement("div");
        panel.className = "language-panel";
        panel.dataset.editorTab = "ritual-design";
        wonderRituals.render(panel);
        elements.languagePanels.append(panel);
    }

    syncActiveEditorPanel();
    refreshDirtyState();
    if (state.activeEditorTab === "ritual-design") {
        void wonderRituals.loadCatalog();
    }
}

function syncActiveEditorPanel() {
    const panels = elements.languagePanels.querySelectorAll(".language-panel");
    for (const panel of panels) {
        panel.classList.toggle("hidden", panel.dataset.editorTab !== state.activeEditorTab);
    }
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
        wonderEditor.renderLog();
        updateStatus(state.status, state.statusKind);
    } finally {
        state.rendering = false;
    }
    refreshDirtyState();
    syncBusyControls();
}

function resolveOptionReferences(value, catalogs) {
    if (Array.isArray(value)) {
        value.forEach((item) => resolveOptionReferences(item, catalogs));
    } else if (value !== null && typeof value === "object") {
        for (const [key, item] of Object.entries(value)) {
            if (item !== null && typeof item === "object" && !Array.isArray(item) &&
                Object.hasOwn(item, "catalog_ref")) {
                const options = catalogs[item.catalog_ref];
                if (!Array.isArray(options)) {
                    throw new Error(`Unknown option catalog: ${item.catalog_ref}`);
                }
                value[key] = options;
            } else {
                resolveOptionReferences(item, catalogs);
            }
        }
    }
}

async function hydrateWonderPayload(payload) {
    if (!payload) {
        return payload;
    }
    if (optionCatalog?.version !== payload.catalog_version) {
        optionCatalogRequest ||= fetchJson("api/wonder-localization/catalog")
            .finally(() => { optionCatalogRequest = null; });
        let catalog = await optionCatalogRequest;
        if (catalog.version !== payload.catalog_version) {
            catalog = await fetchJson("api/wonder-localization/catalog");
        }
        if (catalog.version !== payload.catalog_version) {
            throw new Error("Option catalog changed while loading the wonder");
        }
        optionCatalog = catalog;
    }
    resolveOptionReferences(payload.mechanics, optionCatalog.catalogs);
    return payload;
}

function syncWonderModeWithSelection() {
    if (!state.currentWonder) {
        return;
    }
    state.listMode = currentWonderKind();
}

const wonderEditor = createWonderEditor({
    state, elements,
    cacheDraft: () => cacheCurrentWonderDraft(), dirtyCount: dirtyPageCount, draftHasChanges,
    currentId: currentWonderId, setCurrent: setCurrentWonderPayload,
    hydrate: (payload) => hydrateWonderPayload(payload), invalidateDesigns: wonderRituals.invalidate,
    syncSelection: syncWonderModeWithSelection, render: () => render(), updateStatus,
    showToast: (message, kind) => showToast(message, kind),
});

async function copyLog() {
    const text = wonderEditor.log.text;
    if (!text) {
        return;
    }
    try {
        await navigator.clipboard.writeText(text);
        showToast("日志已复制", "success");
    } catch (error) {
        console.error(error);
        showToast(`复制失败: ${error.message}`, "error");
    }
}

elements.searchInput.addEventListener("input", renderWonderList);
elements.copyLogButton.addEventListener("click", () => {
    void copyLog();
});

window.addEventListener("keydown", (event) => {
    if (document.body.dataset.activeTool !== "wonder-localization") {
        return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        void wonderEditor.save();
    }
});

window.addEventListener("beforeunload", (event) => {
    if (!hasUnsavedChanges()) return;
    event.preventDefault();
    event.returnValue = "";
});

void wonderEditor.load({ context: { initial: true } });
