import { escapeHtml } from "./display.js";
import {
    isStructuredFieldType,
    stableStringify,
    withoutEditorOptions,
    deepClone,
    renderSiteTriggerScript,
    renderSitePreferenceScript,
    previewTextForField,
    normalizeOptionList,
    optionsWithBlank,
    optionPrimaryText,
    optionSecondaryText,
} from "./wonder_values.js";

export function createWonderFields({ onChange, onOpenPrototype, onInitialLevelChange }) {
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
            onChange();
            onInput?.(input.value);
        });
        input.addEventListener("change", () => {
            onChange();
            onInput?.(input.value);
        });
        return input;
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
                onChange();
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
            select.addEventListener("input", onChange);
            select.addEventListener("change", onChange);
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
            textarea.addEventListener("input", onChange);
            textarea.addEventListener("change", onChange);
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
            input.addEventListener("input", onChange);
            input.addEventListener("change", onChange);
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
            binding.value = stableStringify(withoutEditorOptions(stateValue));
            previewOutput.textContent = previewTextForField(field, stateValue);
            onChange();
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
                onOpenPrototype(field.prototype_key);
            });
            actions.append(button);
            note.append(actions);
        }

        return note;
    }

    function buildRowListEditor(config) {
        const section = document.createElement("section");
        section.className = "structured-group";
        if (config.listId) {
            section.dataset.rowList = config.listId;
        }
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
                    listId: "stage-cost",
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

            const optionFields = document.createElement("div");
            optionFields.className = "scalar-grid";
            optionFields.append(
                buildTextareaEditor("Pay option text (English)", stage.option_pay_en, 2, (value) => {
                    stage.option_pay_en = value;
                    commit();
                }),
                buildTextareaEditor("Pay option text (Simplified Chinese)", stage.option_pay_zh, 2, (value) => {
                    stage.option_pay_zh = value;
                    commit();
                }),
                buildTextareaEditor("Decline option text (English)", stage.option_decline_en, 2, (value) => {
                    stage.option_decline_en = value;
                    commit();
                }),
                buildTextareaEditor("Decline option text (Simplified Chinese)", stage.option_decline_zh, 2, (value) => {
                    stage.option_decline_zh = value;
                    commit();
                }),
            );
            group.append(optionFields);
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
            return createSingleLineEditorBinding(field, scope, onInitialLevelChange);
        }
        return createEditorBinding(field, scope);
    }

    return { buildEditorInput, createSingleLineEditorBinding };
}
