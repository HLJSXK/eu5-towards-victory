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
};

const elements = {
    appTitle: document.getElementById("app-title"),
    wonderKindTabs: document.getElementById("wonder-kind-tabs"),
    wonderCount: document.getElementById("wonder-count"),
    wonderList: document.getElementById("wonder-list"),
    wonderMeta: document.getElementById("wonder-meta"),
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
    document.body.dataset.busy = String(isBusy);
}

function getEditorFields() {
    return elements.languagePanels.querySelectorAll("[data-editor-field='true']");
}

function normalizeFieldValue(element) {
    const scope = element.dataset.fieldScope;
    const fieldType = element.dataset.fieldType || "text";
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
    for (const field of getEditorFields()) {
        if (normalizeFieldValue(field) !== field.dataset.originalValue) {
            return true;
        }
    }
    return false;
}

function refreshDirtyState() {
    elements.dirtyBadge.classList.toggle("hidden", !hasUnsavedChanges());
}

function currentWonderKind() {
    return state.currentWonder?.summary?.is_unique ? "unique" : "generic";
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
        button.innerHTML = `
            <span class="wonder-row">
                <span class="wonder-id">#${wonder.id}</span>
                <span class="wonder-kind">${escapeHtml(wonder.kind_label)}</span>
            </span>
            <strong>${escapeHtml(wonder.name_zh || wonder.key)}</strong>
            <span class="wonder-subtitle">${escapeHtml(wonder.name_en || wonder.concept)}</span>
            <code>${escapeHtml(wonder.key)}</code>
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
        ["Concept", meta.concept],
        ["类型", summary.kind_label],
        ["中文名", meta.name_zh || "-"],
        ["英文名", meta.name_en || "-"],
    ];
    if (meta.base_key) {
        entries.push(["原型", meta.base_key]);
    }
    if (meta.location) {
        entries.push(["固定地点", meta.location]);
    }

    for (const [label, value] of entries) {
        const card = document.createElement("div");
        card.className = "meta-card";
        card.innerHTML = `<span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>`;
        elements.wonderMeta.append(card);
    }
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

function buildEditorInput(field, scope) {
    const fieldType = field.field_type || "text";
    const isMultiLine = scope === "localization" || fieldType === "yaml" || fieldType === "script";
    let input;

    if (fieldType === "select") {
        input = document.createElement("select");
        for (const option of field.options || []) {
            const optionNode = document.createElement("option");
            optionNode.value = option.value;
            optionNode.textContent = option.label;
            input.append(optionNode);
        }
        input.value = field.value;
    } else if (isMultiLine) {
        input = document.createElement("textarea");
        input.rows = Math.max(field.height || 4, 3);
        input.value = field.value;
    } else {
        input = document.createElement("input");
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
    input.addEventListener("input", refreshDirtyState);
    input.addEventListener("change", refreshDirtyState);
    return input;
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
            const fieldNode = document.createElement("label");
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
            if (field.help_text) {
                const help = document.createElement("p");
                help.className = "field-help";
                help.textContent = field.help_text;
                fieldNode.append(help);
            }
            fieldNode.append(buildEditorInput(field, scope));
            fields.append(fieldNode);
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
    elements.appTitle.textContent = state.title;
    renderWonderKindTabs();
    renderWonderList();
    renderMeta();
    renderEditorTabs();
    renderEditorPanels();
    renderLog();
    updateStatus(state.status, state.statusKind);
}

function collectPayload() {
    const payload = {
        values: {
            english: {},
            simp_chinese: {},
        },
        mechanics: {},
    };

    for (const field of getEditorFields()) {
        const key = field.dataset.key;
        if (field.dataset.fieldScope === "localization") {
            payload.values[field.dataset.language][key] = field.value;
        } else {
            payload.mechanics[key] = field.value;
        }
    }
    return payload;
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
        state.currentWonder = payload.current_wonder;
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
    if (hasUnsavedChanges()) {
        const shouldDiscard = window.confirm("当前奇观有未保存修改。切换会丢失这些修改，是否继续？");
        if (!shouldDiscard) {
            renderWonderList();
            return;
        }
    }

    setBusy(true);
    updateStatus("正在切换奇观", "working");
    try {
        const payload = await fetchJson(`/api/wonders/${wonderId}`);
        state.currentWonder = payload;
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
    setBusy(true);
    updateStatus("正在保存并重新生成", "working");
    try {
        const payload = await fetchJson(`/api/wonders/${state.currentWonder.summary.id}/save`, {
            method: "POST",
            body: JSON.stringify({
                regenerate: true,
                ...collectPayload(),
            }),
        });
        state.wonders = payload.wonders;
        state.currentWonder = payload.wonder;
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

async function reloadCurrentWonder() {
    if (!state.currentWonder || state.busy) {
        return;
    }
    if (hasUnsavedChanges()) {
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
        state.wonders = payload.wonders;
        state.currentWonder = payload.wonder;
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
