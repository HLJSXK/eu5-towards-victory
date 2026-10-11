"""Parse and render site trigger and preference editor state."""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from .site_templates import (
    PREFERENCE_BRANCH_OPTIONS,
    PREFERENCE_CONDITION_BY_ID,
    PREFERENCE_CONDITION_OPTIONS,
    PREFERENCE_CONDITION_SCRIPT_TO_ID,
    PREFERENCE_PRESET_SIGNATURE_TO_ID,
    PREFERENCE_SCALE_SOURCE_BY_ID,
    PREFERENCE_SCALE_SOURCE_OPTIONS,
    PREFERENCE_SCALE_SOURCE_PATH_TO_ID,
    PREFERENCE_TEMPLATE_PRESETS,
    TRIGGER_CONDITION_BY_ID,
    TRIGGER_CONDITION_OPTIONS,
    TRIGGER_CONDITION_SCRIPT_TO_ID,
    TRIGGER_PRESET_SIGNATURE_TO_ID,
    TRIGGER_TEMPLATE_PRESETS,
    _bonus_rule,
    _preference_signature,
    _scaled_rule,
    _site_value_row,
    _trigger_signature,
    normalize_inline_script,
)
from .values import (
    list_from_string_rows,
    normalize_multiline_editor_text,
    parse_structured_editor_value,
)


TRIGGER_SET_RE = re.compile(
    r"^set_variable = \{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site\.([A-Za-z0-9_:]+) \}$"
)
TRIGGER_CLAMP_RE = re.compile(
    r"^clamp_variable = \{ name = tv_wonder_site_preference_bonus min = ([^ ]+) max = ([^ ]+) \}$"
)
TRIGGER_MULTIPLY_RE = re.compile(
    r"^change_variable = \{ name = tv_wonder_site_preference_bonus multiply = ([^ ]+) \}$"
)
PREFERENCE_RULE_RE = re.compile(
    r"^(if|else_if) = \{ limit = \{ var:tv_wonder_survey_site \?= \{ (.+?) \} \} tv_wonder_change_all_survey_competence_target_effect = \{ value = (.+?) \} \}$"
)


def split_top_level_statements(script: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    balance = 0
    for raw_line in normalize_multiline_editor_text(script).splitlines():
        stripped = raw_line.rstrip()
        if not stripped and not current:
            continue
        current.append(stripped)
        balance += stripped.count("{") - stripped.count("}")
        if balance == 0 and current:
            statements.append("\n".join(current).strip())
            current = []
    if current:
        raise ValueError(f"Unbalanced script block: {script}")
    return statements


def parse_trigger_builder_state(script: str) -> dict[str, Any]:
    normalized = normalize_multiline_editor_text(script)
    try:
        any_of: list[str] = []
        all_of: list[str] = []
        for statement in split_top_level_statements(normalized):
            statement_lines = statement.splitlines()
            if normalize_inline_script(statement) == "always = yes":
                continue
            if statement.startswith("OR = {"):
                if len(statement_lines) < 3:
                    raise ValueError(f"Malformed OR statement: {statement}")
                for line in statement_lines[1:-1]:
                    condition_id = TRIGGER_CONDITION_SCRIPT_TO_ID.get(normalize_inline_script(line))
                    if condition_id is None:
                        raise ValueError(f"Unknown trigger condition: {line}")
                    any_of.append(condition_id)
            else:
                condition_id = TRIGGER_CONDITION_SCRIPT_TO_ID.get(normalize_inline_script(statement))
                if condition_id is None:
                    raise ValueError(f"Unknown trigger condition: {statement}")
                if condition_id.startswith("not_"):
                    all_of.append(condition_id)
                else:
                    any_of.append(condition_id)
        signature = _trigger_signature(any_of, all_of)
        template_id = TRIGGER_PRESET_SIGNATURE_TO_ID.get(signature, "current_variant")
        return {
            "template_id": template_id,
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in TRIGGER_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(TRIGGER_TEMPLATE_PRESETS),
            "condition_options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            "any_of": {
                "rows": [_site_value_row(value) for value in any_of],
                "options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            },
            "all_of": {
                "rows": [_site_value_row(value) for value in all_of],
                "options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            },
            "raw_script": normalized,
        }
    except Exception:
        return {
            "template_id": "custom_script",
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in TRIGGER_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(TRIGGER_TEMPLATE_PRESETS),
            "condition_options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            "any_of": {"rows": [], "options": deepcopy(TRIGGER_CONDITION_OPTIONS)},
            "all_of": {"rows": [], "options": deepcopy(TRIGGER_CONDITION_OPTIONS)},
            "raw_script": normalized,
        }


def render_trigger_script_from_state(raw_value: object, *, context: str) -> str:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    if payload.get("template_id") == "custom_script":
        script = normalize_multiline_editor_text(str(payload.get("raw_script", "")))
        if not script:
            raise ValueError(f"{context}.raw_script cannot be empty")
        return script
    any_of = list_from_string_rows(payload.get("any_of", {}), context=f"{context}.any_of")
    all_of = list_from_string_rows(payload.get("all_of", {}), context=f"{context}.all_of")
    lines: list[str] = []
    for item in any_of + all_of:
        if item not in TRIGGER_CONDITION_BY_ID:
            raise ValueError(f"Unknown trigger condition {item!r} in {context}")
    if any_of:
        if len(any_of) == 1:
            lines.append(TRIGGER_CONDITION_BY_ID[any_of[0]]["script"])
        else:
            lines.append("OR = {")
            lines.extend(f"\t{TRIGGER_CONDITION_BY_ID[item]['script']}" for item in any_of)
            lines.append("}")
    lines.extend(TRIGGER_CONDITION_BY_ID[item]["script"] for item in all_of)
    if not lines:
        return "always = yes"
    return "\n".join(lines)


def parse_preference_builder_state(script: str) -> dict[str, Any]:
    normalized = normalize_multiline_editor_text(script)
    try:
        bonus_rules: list[dict[str, str]] = []
        scaled_rules: list[dict[str, str]] = []
        statements = [normalize_inline_script(statement) for statement in split_top_level_statements(normalized)]
        index = 0
        while index < len(statements):
            statement = statements[index]
            match = PREFERENCE_RULE_RE.match(statement)
            if match:
                branch, condition_script, value = match.groups()
                condition_id = PREFERENCE_CONDITION_SCRIPT_TO_ID.get(normalize_inline_script(condition_script))
                if condition_id is None:
                    raise ValueError(f"Unknown preference condition: {condition_script}")
                bonus_rules.append(_bonus_rule(branch, condition_id, value))
                index += 1
                continue

            if index + 4 < len(statements):
                set_match = TRIGGER_SET_RE.match(statement)
                clamp_match = TRIGGER_CLAMP_RE.match(statements[index + 1])
                multiply_match = TRIGGER_MULTIPLY_RE.match(statements[index + 2])
                if (
                    set_match
                    and clamp_match
                    and multiply_match
                    and statements[index + 3]
                    == "tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }"
                    and statements[index + 4] == "remove_variable = tv_wonder_site_preference_bonus"
                ):
                    source_id = PREFERENCE_SCALE_SOURCE_PATH_TO_ID.get(set_match.group(1))
                    if source_id is None:
                        raise ValueError(f"Unknown scale source: {set_match.group(1)}")
                    scaled_rules.append(
                        _scaled_rule(source_id, clamp_match.group(1), clamp_match.group(2), multiply_match.group(1))
                    )
                    index += 5
                    continue

            if statement == "remove_variable = tv_wonder_site_preference_bonus":
                index += 1
                continue

            if index + 3 < len(statements):
                set_match = TRIGGER_SET_RE.match(statement)
                clamp_match = TRIGGER_CLAMP_RE.match(statements[index + 1])
                multiply_match = TRIGGER_MULTIPLY_RE.match(statements[index + 2])
                if (
                    set_match
                    and clamp_match
                    and multiply_match
                    and statements[index + 3]
                    == "tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }"
                ):
                    source_id = PREFERENCE_SCALE_SOURCE_PATH_TO_ID.get(set_match.group(1))
                    if source_id is None:
                        raise ValueError(f"Unknown scale source: {set_match.group(1)}")
                    scaled_rules.append(
                        _scaled_rule(source_id, clamp_match.group(1), clamp_match.group(2), multiply_match.group(1))
                    )
                    index += 4
                    continue

            raise ValueError(f"Unknown preference statement: {statement}")

        signature = _preference_signature(bonus_rules, scaled_rules)
        template_id = PREFERENCE_PRESET_SIGNATURE_TO_ID.get(signature, "current_variant")
        return {
            "template_id": template_id,
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in PREFERENCE_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(PREFERENCE_TEMPLATE_PRESETS),
            "condition_options": deepcopy(PREFERENCE_CONDITION_OPTIONS),
            "branch_options": deepcopy(PREFERENCE_BRANCH_OPTIONS),
            "scale_source_options": deepcopy(PREFERENCE_SCALE_SOURCE_OPTIONS),
            "bonus_rules": {"rows": deepcopy(bonus_rules)},
            "scaled_rules": {"rows": deepcopy(scaled_rules)},
            "raw_script": normalized,
        }
    except Exception:
        return {
            "template_id": "custom_script",
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in PREFERENCE_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(PREFERENCE_TEMPLATE_PRESETS),
            "condition_options": deepcopy(PREFERENCE_CONDITION_OPTIONS),
            "branch_options": deepcopy(PREFERENCE_BRANCH_OPTIONS),
            "scale_source_options": deepcopy(PREFERENCE_SCALE_SOURCE_OPTIONS),
            "bonus_rules": {"rows": []},
            "scaled_rules": {"rows": []},
            "raw_script": normalized,
        }


def render_preference_script_from_state(raw_value: object, *, context: str) -> str:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    if payload.get("template_id") == "custom_script":
        script = normalize_multiline_editor_text(str(payload.get("raw_script", "")))
        if not script:
            raise ValueError(f"{context}.raw_script cannot be empty")
        return script

    bonus_rows = payload.get("bonus_rules", {}).get("rows", [])
    scaled_rows = payload.get("scaled_rules", {}).get("rows", [])
    if not isinstance(bonus_rows, list) or not isinstance(scaled_rows, list):
        raise ValueError(f"{context} rows must be lists")

    lines: list[str] = []
    for index, row in enumerate(bonus_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.bonus_rules.rows[{index}] must be an object")
        branch = str(row.get("branch", "if")).strip() or "if"
        condition = str(row.get("condition", "")).strip()
        value = str(row.get("value", "")).strip()
        if not condition and not value:
            continue
        if branch not in {"if", "else_if"}:
            raise ValueError(f"{context}.bonus_rules.rows[{index}] has invalid branch {branch!r}")
        if condition not in PREFERENCE_CONDITION_BY_ID:
            raise ValueError(f"{context}.bonus_rules.rows[{index}] has unknown condition {condition!r}")
        if not value:
            raise ValueError(f"{context}.bonus_rules.rows[{index}] is missing value")
        condition_script = PREFERENCE_CONDITION_BY_ID[condition]["script"]
        lines.extend(
            [
                f"{branch} = {{",
                f"\tlimit = {{ var:tv_wonder_survey_site ?= {{ {condition_script} }} }}",
                f"\ttv_wonder_change_all_survey_competence_target_effect = {{ value = {value} }}",
                "}",
            ]
        )

    rendered_scaled = False
    for index, row in enumerate(scaled_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.scaled_rules.rows[{index}] must be an object")
        source = str(row.get("source", "")).strip()
        minimum = str(row.get("min", "")).strip()
        maximum = str(row.get("max", "")).strip()
        multiplier = str(row.get("multiplier", "")).strip()
        if not source and not minimum and not maximum and not multiplier:
            continue
        if source not in PREFERENCE_SCALE_SOURCE_BY_ID:
            raise ValueError(f"{context}.scaled_rules.rows[{index}] has unknown source {source!r}")
        if not minimum or not maximum or not multiplier:
            raise ValueError(f"{context}.scaled_rules.rows[{index}] must define min, max, and multiplier")
        source_path = PREFERENCE_SCALE_SOURCE_BY_ID[source]["path"]
        lines.extend(
            [
                f"set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.{source_path} }}",
                f"clamp_variable = {{ name = tv_wonder_site_preference_bonus min = {minimum} max = {maximum} }}",
                f"change_variable = {{ name = tv_wonder_site_preference_bonus multiply = {multiplier} }}",
                "tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }",
            ]
        )
        rendered_scaled = True

    if rendered_scaled:
        lines.append("remove_variable = tv_wonder_site_preference_bonus")

    if not lines:
        raise ValueError(f"{context} must define at least one rule")
    return "\n".join(lines)
