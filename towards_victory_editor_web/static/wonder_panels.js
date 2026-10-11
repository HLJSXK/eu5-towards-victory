import { escapeHtml } from "./display.js";

export function wonderSearchHaystack(wonder) {
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

export function wondersForMode(wonders, mode) {
    const isUnique = mode === "unique";
    return wonders.filter((wonder) => Boolean(wonder.is_unique) === isUnique);
}

export function findWonderByKey(wonders, key, isUnique = null) {
    return wonders.find((wonder) => {
        if (wonder.key !== key) {
            return false;
        }
        if (isUnique === null) {
            return true;
        }
        return Boolean(wonder.is_unique) === Boolean(isUnique);
    });
}

export function wonderImageAlt(wonder) {
    const summary = wonder?.summary || wonder || {};
    const name = summary.name_zh || summary.name_en || summary.key || "wonder";
    return `${name} image`;
}

export function uniqueInitialLevelStartStateLabel(stateValue) {
    if (!stateValue.valid) {
        return stateValue.value ? `Invalid level: ${stateValue.value}` : "Invalid level";
    }
    return stateValue.level > 0 ? `Level ${stateValue.level}` : "Not present";
}

export function createWonderPanels({
    elements,
    getWonders,
    getCurrentWonder,
    getListMode,
    setListMode,
    getInitialLevelState,
    isBusy,
    onSelect,
}) {
    function renderKindTabs() {
        const modes = [
            { id: "generic", label: "通用奇观" },
            { id: "unique", label: "独特奇观" },
        ];
        elements.wonderKindTabs.innerHTML = "";
        for (const mode of modes) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "kind-switch-button";
            if (getListMode() === mode.id) {
                button.classList.add("active");
            }
            button.textContent = `${mode.label} (${wondersForMode(getWonders(), mode.id).length})`;
            button.addEventListener("click", () => {
                if (isBusy()) return;
                setListMode(mode.id);
                renderKindTabs();
                renderList();
            });
            elements.wonderKindTabs.append(button);
        }
    }

    function renderList() {
        const currentWonder = getCurrentWonder();
        const query = elements.searchInput.value.trim().toLowerCase();
        const pool = wondersForMode(getWonders(), getListMode());
        const wonders = pool.filter((wonder) => wonderSearchHaystack(wonder).includes(query));
        const label = getListMode() === "unique" ? "独特奇观" : "通用奇观";

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
            if (currentWonder && currentWonder.summary.id === wonder.id) {
                button.classList.add("active");
            }
            const image = wonder.image || null;
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
                void onSelect(wonder.id);
            });
            elements.wonderList.append(button);
        }
    }

    function renderMeta() {
        const currentWonder = getCurrentWonder();
        elements.wonderMeta.innerHTML = "";
        if (!currentWonder) {
            return;
        }

        const { meta, summary } = currentWonder;
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
            entries.push(["Start state", uniqueInitialLevelStartStateLabel(getInitialLevelState())]);
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

    function renderImage() {
        const frame = elements.wonderImageFrame;
        if (!frame) {
            return;
        }
        frame.innerHTML = "";
        frame.classList.remove("has-image", "is-missing");

        const currentWonder = getCurrentWonder();
        if (!currentWonder) {
            frame.classList.add("is-missing");
            return;
        }

        const image = currentWonder.summary?.image || currentWonder.meta?.image || null;
        if (image?.url) {
            const img = document.createElement("img");
            img.src = image.url;
            img.alt = wonderImageAlt(currentWonder);
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

    return { renderKindTabs, renderList, renderMeta, renderImage };
}
