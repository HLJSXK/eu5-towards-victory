import { createWonderPanels, findWonderByKey } from "./wonder_panels.js";
import { createWonderFields } from "./wonder_fields.js";
import { createWonderEditor } from "./wonder_editor.js";
import { createWonderRituals } from "./wonder_rituals.js";
import {
    applyDraftToWonderPayload,
    dirtyPageCount as countDirtyPages,
    draftHasChanges,
    parseUniqueInitialLevelValue,
    setFieldDraft,
    setPromptDraft as updatePromptDraft,
    uniqueInitialLevelFieldKey,
    wonderNameKeyForKey,
} from "./wonder_drafts.js";
import { fetchJson } from "./api.js";
import { createStatusView, escapeHtml } from "./display.js";
import { ResourceState, setControlsBusy } from "./resource_state.js";

import { normalizeLocalizationText } from "./wonder_values.js";

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
    onChange: handleFieldChange,
    onOpenPrototype: (key) => {
        const target = findWonderByKey(state.wonders, key, false);
        if (target) {
            void wonderEditor.select(target.id);
        }
    },
    onInitialLevelChange: updateUniqueInitialLevelPreview,
});

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

function dirtyPageCount() {
    return countDirtyPages(state.pageDrafts);
}

function currentWonderId() {
    return state.currentWonder?.summary?.id ?? null;
}

function handleFieldChange(field) {
    const wonderId = currentWonderId();
    if (wonderId === null || state.rendering || state.busy || !field?.dataset?.key) {
        return;
    }
    state.resource.mutate((resourceDraft) => {
        setFieldDraft(resourceDraft.pageDrafts, wonderId, {
            scope: field.dataset.fieldScope,
            language: field.dataset.language,
            key: field.dataset.key,
            fieldType: field.dataset.fieldType || "text",
        }, field.value, field.dataset.originalValue);
    });
    refreshDirtyState();
}

function setCurrentWonderPayload(wonderPayload) {
    if (!wonderPayload) {
        state.currentWonder = null;
        return;
    }
    const preview = applyDraftToWonderPayload(wonderPayload, state.pageDrafts[String(wonderPayload.summary?.id)]);
    state.currentWonder = wonderPayload;
    const summary = state.wonders.find((wonder) => Number(wonder.id) === Number(wonderPayload.summary?.id));
    if (summary) {
        Object.assign(summary, preview);
    }
}

function hasUnsavedChanges() {
    return dirtyPageCount() > 0;
}

function refreshDirtyState() {
    const hasChanges = hasUnsavedChanges();
    const pageCount = dirtyPageCount();
    elements.dirtyBadge.textContent = pageCount > 1 ? `Unsaved changes (${pageCount} pages)` : "未保存更改";
    elements.dirtyBadge.classList.toggle("hidden", !hasChanges);
}

function setPromptDraft(wonderId, value) {
    state.resource.mutate((resourceDraft) => {
        updatePromptDraft(resourceDraft.pageDrafts, wonderId, value);
    });
    refreshDirtyState();
}

const wonderRituals = createWonderRituals({
    getCurrentWonder: () => state.currentWonder,
    getPromptDraft: (wonderId) => state.pageDrafts[String(wonderId)]?.ritual_prompt,
    setPromptDraft,
    isBusy: () => state.busy,
    onDirty: refreshDirtyState,
    onToast: showToast,
});

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

    wonderPanels.renderList();
    wonderPanels.renderMeta();
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
    wonderPanels.renderMeta();
}

function currentWonderKind() {
    return state.currentWonder?.summary?.is_unique ? "unique" : "generic";
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

const wonderPanels = createWonderPanels({
    elements,
    getWonders: () => state.wonders,
    getCurrentWonder: () => state.currentWonder,
    getListMode: () => state.listMode,
    setListMode: (mode) => { state.listMode = mode; },
    getInitialLevelState: currentUniqueInitialLevelState,
    isBusy: () => state.busy,
    onSelect: (id) => wonderEditor.select(id),
});

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
        wonderPanels.renderKindTabs();
        wonderPanels.renderList();
        wonderPanels.renderMeta();
        wonderPanels.renderImage();
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
    dirtyCount: dirtyPageCount, draftHasChanges,
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

elements.searchInput.addEventListener("input", wonderPanels.renderList);
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
