import { fetchJson } from "./api.js";
import { escapeHtml } from "./display.js";
import { normalizeMultilineText } from "./wonder_values.js";

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

export function ritualDesignEntriesForDisplay(design) {
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

function ritualDesignValueToPromptLines(key, value, labelForKey, depth = 0) {
    if (value === null || value === undefined || value === "") {
        return [];
    }
    const indent = "  ".repeat(depth);
    const label = labelForKey(key);
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
            lines.push(...ritualDesignValueToPromptLines(nestedKey, value[nestedKey], labelForKey, depth + 1));
        }
        return lines;
    }
    return [`${indent}${label}: ${String(value)}`];
}

export function buildRitualImplementationPrompt(design) {
    const ritualDesign = ritualDesignForDisplay(design);
    const labelForKey = (key) => design?.field_labels?.[key] || key.replaceAll("_", " ");
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
        lines.push(...ritualDesignValueToPromptLines(key, ritualDesign[key], labelForKey));
    }
    if (ritualDesignHasTranslation(design)) {
        const original = ritualDesignOriginal(design);
        lines.push("", "英文原文标题：", String(original.title || ""));
    }
    return lines.join("\n").trim();
}

export function createWonderRituals({
    getCurrentWonder,
    getPromptDraft,
    setPromptDraft,
    isBusy,
    onDirty,
    onToast,
    request = fetchJson,
}) {
    let catalog = null;
    let catalogError = "";
    let catalogRequest = null;
    let generation = 0;
    let currentPanel = null;
    const details = {};
    const detailRequests = new Map();

    function currentWonder() {
        return getCurrentWonder() || null;
    }

    function currentRitualDesign() {
        const wonder = currentWonder();
        return wonder?.summary?.is_unique ? wonder.ritual_design || null : null;
    }

    function currentRitualPromptOriginal() {
        return String(currentWonder()?.ritual_prompt?.prompt || "");
    }

    function currentRitualPromptValue() {
        const wonderId = currentWonder()?.summary?.id;
        const draftValue = wonderId === undefined ? undefined : getPromptDraft(wonderId);
        return draftValue === undefined ? currentRitualPromptOriginal() : draftValue;
    }

    function ritualDesignLabel(key) {
        return currentWonder()?.ritual_design?.field_labels?.[key]
            || catalog?.field_labels?.[key]
            || key.replaceAll("_", " ");
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
        const detailsNode = document.createElement("details");
        detailsNode.className = "ritual-design-original";
        const summary = document.createElement("summary");
        summary.textContent = "英文原文";
        detailsNode.append(summary, renderRitualDesignBody(design, ritualDesignOriginal(design)));
        container.append(detailsNode);
    }

    function renderRitualPromptCard(panel) {
        const wonder = currentWonder();
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
                <span class="origin-pill">${escapeHtml(wonder.ritual_prompt?.source_path || "")}</span>
            </div>
        `;

        const textarea = document.createElement("textarea");
        textarea.className = "ritual-prompt-input";
        textarea.rows = 10;
        textarea.placeholder = "在这里输入用于后续指示 AI 实现该独特奇观仪式的 prompt。";
        textarea.value = value;
        textarea.dataset.ritualPromptInput = "true";
        textarea.dataset.originalPrompt = originalPrompt;

        const actions = document.createElement("div");
        actions.className = "ritual-prompt-actions";
        const draftButton = document.createElement("button");
        draftButton.type = "button";
        draftButton.className = "secondary-button";
        draftButton.textContent = "用当前设计生成 Prompt 草稿";
        const status = document.createElement("span");
        status.className = "ritual-prompt-status";

        const refreshPromptState = () => {
            onDirty();
            const changed = normalizeMultilineText(textarea.value) !== textarea.dataset.originalPrompt;
            status.textContent = changed ? "Prompt 尚未保存，使用页面顶部的统一保存" : "Prompt 已同步";
        };
        textarea.addEventListener("input", () => {
            const normalized = normalizeMultilineText(textarea.value);
            setPromptDraft(wonder.summary.id, normalized === originalPrompt ? undefined : normalized);
            refreshPromptState();
        });
        draftButton.addEventListener("click", () => {
            if (isBusy()) return;
            const design = currentRitualDesign();
            if (!design) {
                return;
            }
            textarea.value = buildRitualImplementationPrompt(design);
            textarea.dispatchEvent(new Event("input", { bubbles: true }));
            textarea.focus();
        });
        actions.append(draftButton, status);
        section.append(textarea, actions);
        panel.append(section);
        refreshPromptState();
    }

    function renderRitualDesignPanel(panel) {
        const wonder = currentWonder();
        if (!wonder?.summary?.is_unique) {
            panel.innerHTML = '<div class="empty-state wide">请选择一个独特奇观以查看仪式设计。</div>';
            return;
        }
        const currentDesign = currentRitualDesign();
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

        const catalogContainer = document.createElement("div");
        catalogContainer.className = "ritual-design-catalog-content";
        panel.append(catalogContainer);
        renderRitualDesignCatalog(catalogContainer);
    }

    function renderRitualDesignCatalog(container) {
        if (!container) return;
        container.innerHTML = "";
        if (!catalog) {
            const status = document.createElement("div");
            status.className = "empty-state wide";
            status.textContent = catalogError || "正在加载仪式设计目录...";
            if (catalogError) {
                const retry = document.createElement("button");
                retry.type = "button";
                retry.className = "secondary-button";
                retry.textContent = "重试";
                retry.addEventListener("click", () => { void loadCatalog(); });
                status.append(document.createElement("br"), retry);
            }
            container.append(status);
            return;
        }

        const wonder = currentWonder();
        const allSection = document.createElement("section");
        allSection.className = "ritual-design-all";
        allSection.innerHTML = `
            <div class="section-header">
                <h3>全部独特奇观仪式原始设计</h3>
            </div>
            <p class="ritual-design-count">
                来源：${escapeHtml(catalog.source_path || "")} · 共 ${escapeHtml(catalog.count || 0)} 条。
            </p>
        `;
        const list = document.createElement("div");
        list.className = "ritual-design-listing";
        for (const design of catalog.wonders || []) {
            const isCurrent = Number(design.id) === Number(wonder?.summary?.id);
            const item = document.createElement("details");
            item.className = "ritual-design-card";
            item.open = isCurrent;
            const fullDesign = isCurrent ? wonder?.ritual_design : details[String(design.id)];
            item.append(renderRitualDesignSummary(design, isCurrent));
            if (fullDesign) {
                item.append(renderRitualDesignBody(fullDesign));
                appendOriginalRitualDesign(item, fullDesign, { showFallbackNote: false });
            }
            item.addEventListener("toggle", () => {
                if (item.open && !fullDesign && !item.dataset.loaded) {
                    void loadDetailItem(design.id, item);
                }
            });
            list.append(item);
        }
        allSection.append(list);
        container.append(allSection);
    }

    async function loadCatalog() {
        if (catalog || catalogRequest) {
            return;
        }
        const requestGeneration = generation;
        catalogError = "";
        renderRitualDesignCatalog(currentPanel?.querySelector(".ritual-design-catalog-content"));
        const pending = request("api/wonder-localization/ritual-designs");
        catalogRequest = pending;
        try {
            const result = await pending;
            if (requestGeneration === generation) {
                catalog = result;
                catalogError = "";
            }
        } catch (error) {
            if (requestGeneration === generation) {
                catalogError = `仪式设计加载失败: ${error.message}`;
                onToast(catalogError, "error");
            }
        } finally {
            if (requestGeneration === generation && catalogRequest === pending) {
                catalogRequest = null;
                renderRitualDesignCatalog(currentPanel?.querySelector(".ritual-design-catalog-content"));
            }
        }
    }

    async function loadDetailItem(wonderId, item) {
        const requestGeneration = generation;
        const key = String(wonderId);
        item.dataset.loaded = "true";
        item.querySelector(".ritual-design-load-state")?.remove();
        const status = document.createElement("p");
        status.className = "ritual-design-load-state";
        status.textContent = "正在加载仪式设计...";
        item.append(status);
        try {
            if (!detailRequests.has(key)) {
                detailRequests.set(key, request(`api/wonder-localization/ritual-designs/${wonderId}`));
            }
            const design = await detailRequests.get(key);
            if (requestGeneration !== generation) {
                return;
            }
            details[key] = design;
            status.remove();
            if (item.isConnected) {
                item.append(renderRitualDesignBody(design));
                appendOriginalRitualDesign(item, design, { showFallbackNote: false });
            }
        } catch (error) {
            if (requestGeneration === generation) {
                delete item.dataset.loaded;
                status.textContent = `仪式设计加载失败: ${error.message}`;
                onToast(status.textContent, "error");
            }
        } finally {
            if (requestGeneration === generation) {
                detailRequests.delete(key);
            }
        }
    }

    function invalidate() {
        generation += 1;
        catalogRequest = null;
        detailRequests.clear();
        catalog = null;
        catalogError = "";
        for (const key of Object.keys(details)) {
            delete details[key];
        }
    }

    return {
        render(panel) {
            currentPanel = panel;
            renderRitualDesignPanel(panel);
        },
        loadCatalog,
        invalidate,
    };
}
