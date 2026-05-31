const state = {
    title: "Towards Victory 奇观本地化编辑器",
    wonders: [],
    currentWonder: null,
    activeLanguage: "english",
    status: "就绪",
    statusKind: "default",
    logText: "",
    busy: false,
};

const elements = {
    appTitle: document.getElementById("app-title"),
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

function normalizeEditorText(value) {
    return value.replace(/\r\n/g, "\n").replace(/\r/g, "\n").replace(/\n/g, " ").trim();
}

function wonderSearchHaystack(wonder) {
    return [
        wonder.id,
        wonder.key,
        wonder.concept,
        wonder.name_zh,
        wonder.name_en,
        wonder.display_name,
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

function hasUnsavedChanges() {
    const textareas = elements.languagePanels.querySelectorAll("textarea[data-original-value]");
    for (const textarea of textareas) {
        if (normalizeEditorText(textarea.value) !== textarea.dataset.originalValue) {
            return true;
        }
    }
    return false;
}

function refreshDirtyState() {
    elements.dirtyBadge.classList.toggle("hidden", !hasUnsavedChanges());
}

function renderWonderList() {
    const query = elements.searchInput.value.trim().toLowerCase();
    const wonders = state.wonders.filter((wonder) => wonderSearchHaystack(wonder).includes(query));
    elements.wonderCount.textContent = `显示 ${wonders.length} / ${state.wonders.length} 个奇观`;
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
                <span class="wonder-kind">${wonder.kind_label}</span>
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
        entries.push(["地点", meta.location]);
    }
    for (const [label, value] of entries) {
        const card = document.createElement("div");
        card.className = "meta-card";
        card.innerHTML = `<span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>`;
        elements.wonderMeta.append(card);
    }
}

function renderLanguageTabs() {
    elements.languageTabs.innerHTML = "";
    if (!state.currentWonder) {
        return;
    }
    const languages = state.currentWonder.languages;
    if (!languages[state.activeLanguage]) {
        state.activeLanguage = Object.keys(languages)[0];
    }
    for (const [language, payload] of Object.entries(languages)) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "tab-button";
        if (language === state.activeLanguage) {
            button.classList.add("active");
        }
        button.textContent = payload.label;
        button.addEventListener("click", () => {
            state.activeLanguage = language;
            renderLanguageTabs();
            syncActiveLanguagePanel();
        });
        elements.languageTabs.append(button);
    }
}

function renderLanguagePanels() {
    elements.languagePanels.innerHTML = "";
    if (!state.currentWonder) {
        elements.languagePanels.innerHTML = '<div class="empty-state wide">没有可编辑的奇观数据。</div>';
        return;
    }

    for (const [language, languagePayload] of Object.entries(state.currentWonder.languages)) {
        const panel = document.createElement("div");
        panel.className = "language-panel";
        panel.dataset.language = language;

        for (const section of languagePayload.sections) {
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
                        <span class="origin-pill">${escapeHtml(field.origin_label)}</span>
                    </div>
                `;
                const textarea = document.createElement("textarea");
                textarea.rows = Math.max(field.height * 2, 3);
                textarea.value = field.value;
                textarea.dataset.language = field.language;
                textarea.dataset.key = field.key;
                textarea.dataset.originalValue = field.original_value;
                textarea.addEventListener("input", refreshDirtyState);
                fieldNode.append(textarea);
                fields.append(fieldNode);
            }
            sectionNode.append(fields);
            panel.append(sectionNode);
        }
        elements.languagePanels.append(panel);
    }
    syncActiveLanguagePanel();
    refreshDirtyState();
}

function syncActiveLanguagePanel() {
    const panels = elements.languagePanels.querySelectorAll(".language-panel");
    for (const panel of panels) {
        panel.classList.toggle("hidden", panel.dataset.language !== state.activeLanguage);
    }
}

function renderLog() {
    elements.logOutput.textContent = state.logText || "[server] 暂无新日志";
    elements.copyLogButton.disabled = !state.logText;
}

function render() {
    elements.appTitle.textContent = state.title;
    renderWonderList();
    renderMeta();
    renderLanguageTabs();
    renderLanguagePanels();
    renderLog();
    updateStatus(state.status, state.statusKind);
}

function collectValues() {
    const values = {
        english: {},
        simp_chinese: {},
    };
    const textareas = elements.languagePanels.querySelectorAll("textarea[data-key]");
    for (const textarea of textareas) {
        values[textarea.dataset.language][textarea.dataset.key] = textarea.value;
    }
    return values;
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
        render();
    } catch (error) {
        console.error(error);
        updateStatus("加载失败", "error");
        showToast(`加载失败：${error.message}`, "error");
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
        const shouldDiscard = window.confirm("当前奇观有未保存修改。切换会丢弃这些修改，是否继续？");
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
        render();
    } catch (error) {
        console.error(error);
        updateStatus("切换失败", "error");
        showToast(`切换失败：${error.message}`, "error");
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
                values: collectValues(),
            }),
        });
        state.wonders = payload.wonders;
        state.currentWonder = payload.wonder;
        state.logText = payload.log_text || state.logText;
        state.status = payload.status;
        state.statusKind = "default";
        render();
        showToast(payload.status, "success");
    } catch (error) {
        console.error(error);
        updateStatus("保存失败", "error");
        showToast(`保存失败：${error.message}`, "error");
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
        render();
        showToast(payload.status, "success");
    } catch (error) {
        console.error(error);
        updateStatus("重新加载失败", "error");
        showToast(`重新加载失败：${error.message}`, "error");
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
        showToast(`复制失败：${error.message}`, "error");
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
window.addEventListener("beforeunload", (event) => {
    if (!hasUnsavedChanges()) {
        return;
    }
    event.preventDefault();
    event.returnValue = "";
});

void loadBootstrap();
