import {
    normalizeLocalizationText,
    normalizeMultilineText,
    isStructuredFieldType,
    restoreEditorOptions,
} from "./wonder_values.js";

export function wonderNameKeyForKey(wonderKey) {
    return `tv_wonder_${wonderKey}`;
}

export function uniqueInitialLevelFieldKey(wonderPayload) {
    const key = wonderPayload?.summary?.key || wonderPayload?.meta?.key || "";
    return key ? `mechanics.unique_initial_level.${key}` : "";
}

export function parseUniqueInitialLevelValue(rawValue) {
    const value = String(rawValue ?? "").trim();
    if (!/^[0-6]$/.test(value)) {
        return { valid: false, value };
    }
    return { valid: true, level: Number.parseInt(value, 10), value };
}

export function emptyDraft() {
    return {
        values: {
            english: {},
            simp_chinese: {},
        },
        mechanics: {},
    };
}

export function draftHasChanges(draft) {
    return Boolean(
        draft &&
            (Object.values(draft.values || {}).some((values) => Object.keys(values || {}).length > 0) ||
                Object.keys(draft.mechanics || {}).length > 0 || draft.ritual_prompt !== undefined),
    );
}

export function dirtyPageCount(drafts) {
    return Object.values(drafts || {}).filter(draftHasChanges).length;
}

export function draftValueForField(draft, ref) {
    if (!draft || !ref) {
        return undefined;
    }
    if (ref.scope === "localization") {
        return draft.values?.[ref.language]?.[ref.key];
    }
    return draft.mechanics?.[ref.key];
}

function comparableFieldValue(value, ref) {
    const text = String(value ?? "");
    if (ref.scope === "localization") {
        return normalizeLocalizationText(text);
    }
    if (ref.fieldType === "yaml" || ref.fieldType === "script") {
        return normalizeMultilineText(text);
    }
    return text.trim();
}

export function setFieldDraft(drafts, wonderId, ref, value, original) {
    const pageKey = String(wonderId);
    const draft = drafts[pageKey] || emptyDraft();
    const section = ref.scope === "localization" ? (draft.values[ref.language] ||= {}) : draft.mechanics;

    if (comparableFieldValue(value, ref) === comparableFieldValue(original, ref)) {
        delete section[ref.key];
    } else {
        section[ref.key] = value;
    }

    if (draftHasChanges(draft)) {
        drafts[pageKey] = draft;
    } else {
        delete drafts[pageKey];
    }
}

export function setPromptDraft(drafts, wonderId, value) {
    const pageKey = String(wonderId);
    const current = drafts[pageKey];
    if (value === undefined) {
        if (!current) {
            return;
        }
        delete current.ritual_prompt;
        if (!draftHasChanges(current)) {
            delete drafts[pageKey];
        }
        return;
    }

    const draft = current || emptyDraft();
    draft.ritual_prompt = value;
    drafts[pageKey] = draft;
}

function applyDraftNamePreview(payload, draft) {
    const wonderKey = payload.summary?.key || "";
    if (!wonderKey) {
        return;
    }
    const nameKey = wonderNameKeyForKey(wonderKey);
    const englishName = draft.values?.english?.[nameKey];
    const chineseName = draft.values?.simp_chinese?.[nameKey];
    if (englishName !== undefined) {
        const normalized = normalizeLocalizationText(String(englishName));
        payload.summary.name_en = normalized;
        payload.meta.name_en = normalized;
    }
    if (chineseName !== undefined) {
        const normalized = normalizeLocalizationText(String(chineseName));
        payload.summary.name_zh = normalized;
        payload.meta.name_zh = normalized;
    }
    payload.summary.display_name = `${payload.summary.name_zh} / ${payload.summary.name_en}`;
}

function applyDraftInitialLevelPreview(payload, draft) {
    if (!payload.summary?.is_unique) {
        return;
    }
    const fieldKey = uniqueInitialLevelFieldKey(payload);
    const value = fieldKey ? draft.mechanics?.[fieldKey] : undefined;
    if (value === undefined) {
        return;
    }
    const parsed = parseUniqueInitialLevelValue(value);
    if (!parsed.valid) {
        return;
    }
    payload.summary.initial_level = parsed.level;
    payload.meta.initial_level = parsed.level;
}

export function applyDraftToWonderPayload(payload, draft) {
    if (!payload?.summary?.id || !draftHasChanges(draft)) {
        return { name_en: payload?.summary?.name_en, name_zh: payload?.summary?.name_zh,
            display_name: payload?.summary?.display_name, initial_level: payload?.summary?.initial_level };
    }

    for (const [language, languagePayload] of Object.entries(payload.languages || {})) {
        for (const section of languagePayload.sections || []) {
            for (const field of section.fields || []) {
                const value = draftValueForField(draft, { scope: "localization", language, key: field.key });
                if (value !== undefined) {
                    field.value = value;
                }
            }
        }
    }
    for (const section of payload.mechanics?.sections || []) {
        for (const field of section.fields || []) {
            const value = draftValueForField(draft, { scope: "mechanics", key: field.key });
            if (value === undefined) {
                continue;
            }
            field.value = value;
            if (isStructuredFieldType(field.field_type || "text")) {
                try {
                    field.structured_value = restoreEditorOptions(JSON.parse(value), field.structured_value);
                } catch {
                    field.structured_value = field.structured_value ?? {};
                }
            }
        }
    }

    applyDraftNamePreview(payload, draft);
    applyDraftInitialLevelPreview(payload, draft);
    return { name_en: payload.summary.name_en, name_zh: payload.summary.name_zh,
        display_name: payload.summary.display_name, initial_level: payload.summary.initial_level };
}
