"""Build Wonder field specifications from explicit source data and catalogs."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts_engineering_department.wonder_mechanics.modifiers import authored_final_building_local_modifiers
from scripts_engineering_department.wonder_mechanics.naming import (
    final_building_for_style,
    mechanic_key,
    wonder_static_display_modifier_name,
    wonder_static_local_display_modifier_name,
)
from scripts_engineering_department.wonder_mechanics.rituals import (
    SUPPORTED_RITUAL_COST_TYPES,
    ceremony_styles,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
)
from scripts_engineering_department.wonder_mechanics.schema import (
    site_preference_script_for_key,
    site_trigger_script_for_key,
)

from . import sources
from .field_types import FieldSpec, MechanicsFieldSpec
from .localization import (
    LANGUAGES,
    ROMAN_NUMERALS,
    active_ritual_key,
    branch_button_key,
    ceremony_modifier_for_style,
    concept_key_for_wonder,
    event_desc_key,
    localization_value,
    wonder_name_key,
)
from .site_rules import parse_preference_builder_state, parse_trigger_builder_state
from .sources import get_unique_wonder_source
from .values import (
    GENERIC_STYLE_2_DERIVED_HELP_TEXT,
    GENERIC_STYLE_2_DERIVED_TITLE,
    WONDER_SIZE_OPTIONS,
    build_modifier_editor_state,
    build_reward_editor_state,
    build_unique_ceremony_editor_state,
    build_unique_ritual_editor_state,
    generic_style_2_derived_modifier_mapping,
    parse_unique_initial_level,
    reward_rows_from_list,
    scale_numeric_mapping,
    serialize_structured_editor_value,
    stringify_editor_scalar,
)


def build_mechanics_specs_for_wonder(
    wonder: dict[str, Any],
    *,
    mechanics: dict[str, Any],
    mechanics_data: dict[str, Any],
    unique_wonders_data: dict[str, Any],
    generic_options: list[dict[str, str]],
    option_catalogs: dict[str, list[dict[str, Any]]],
) -> list[MechanicsFieldSpec]:
    specs: list[MechanicsFieldSpec] = []
    prototype_key = mechanic_key(wonder)
    shared_source_kind = "shared"
    inherits_from_prototype = bool(wonder.get("is_unique"))
    base_effect_multiplier = wonder.get("base_effect_multiplier", 1)
    site_help_text = (
        "Inherited from the prototype. Use the prototype selector to change this rule set; edit the prototype wonder to modify the script."
        if inherits_from_prototype
        else "Choose a site-condition template, then adjust the allowed condition atoms instead of editing the raw trigger script directly."
    )
    preference_help_text = (
        "Inherited from the prototype. Use the prototype selector to change this rule set; edit the prototype wonder to modify the script."
        if inherits_from_prototype
        else "Choose a preference template, then edit condition bonus rows and scaled bonus rows; player-visible suitability rows are derived from these rules."
    )
    base_modifier_help_text = (
        (
            f"Inherited from the prototype. Displayed values already apply this unique wonder's x{base_effect_multiplier} "
            "base-effect multiplier; edit the prototype wonder to modify the underlying modifier list."
        )
        if inherits_from_prototype
        else "Structured editor for data/wonder_base_modifiers.yaml base_modifiers entries."
    )
    base_modifier_mapping = mechanics_data.get("base_modifiers", {}).get(prototype_key, {})
    displayed_base_modifier_mapping = (
        scale_numeric_mapping(base_modifier_mapping, base_effect_multiplier)
        if inherits_from_prototype
        else base_modifier_mapping
    )
    building_design = mechanics_data.get("buildings", {}).get(prototype_key, {})
    final_local_mapping = building_design.get("final_local", {})
    displayed_final_building_local_mapping = (
        authored_final_building_local_modifiers(wonder, mechanics)
        if inherits_from_prototype
        else {}
    )

    if not inherits_from_prototype:
        _add_mechanics_spec(
            specs,
            group="Core Data",
            label="Wonder size",
            key=f"mechanics.generic_size.{wonder['key']}",
            source_kind="generic",
            file_path=sources.WONDERS_FILE,
            original_value=str(wonder["size"]),
            field_type="select",
            target_kind="generic_size",
            target_key=wonder["key"],
            height=1,
            options=WONDER_SIZE_OPTIONS,
            help_text="Small, medium, or large. Unique wonders inherit this value from their prototype wonder.",
            target_path=f"wonders[{wonder['key']}].size",
        )

    _add_mechanics_spec(
        specs,
        group="Site Rules",
        label="Build condition template",
        key=f"mechanics.site_trigger.{wonder['key']}",
        source_kind=shared_source_kind,
        file_path=sources.WONDER_SITE_RULES_FILE,
        original_value=serialize_structured_editor_value(
            parse_trigger_builder_state(site_trigger_script_for_key(mechanics_data, prototype_key))
        ),
        field_type="site_trigger_template",
        target_kind="site_rule",
        target_key=prototype_key,
        target_parent_key="trigger_script",
        height=10,
        help_text=site_help_text,
        target_path=f"site_rules.{prototype_key}.trigger_script",
        structured_value=parse_trigger_builder_state(site_trigger_script_for_key(mechanics_data, prototype_key)),
        editable=not inherits_from_prototype,
        prototype_key=prototype_key if inherits_from_prototype else "",
    )
    _add_mechanics_spec(
        specs,
        group="Site Rules",
        label="Survey preference template",
        key=f"mechanics.site_preference.{wonder['key']}",
        source_kind=shared_source_kind,
        file_path=sources.WONDER_SITE_RULES_FILE,
        original_value=serialize_structured_editor_value(
            parse_preference_builder_state(site_preference_script_for_key(mechanics_data, prototype_key))
        ),
        field_type="site_preference_template",
        target_kind="site_rule",
        target_key=prototype_key,
        target_parent_key="preference_script",
        height=14,
        help_text=preference_help_text,
        target_path=f"site_rules.{prototype_key}.preference_script",
        structured_value=parse_preference_builder_state(site_preference_script_for_key(mechanics_data, prototype_key)),
        editable=not inherits_from_prototype,
        prototype_key=prototype_key if inherits_from_prototype else "",
    )
    if inherits_from_prototype:
        inherited_local_state = build_modifier_editor_state(
            displayed_final_building_local_mapping,
            modifier_scope="local",
            options=option_catalogs["local_modifier"],
        )
        _add_mechanics_spec(
            specs,
            group="Final Building Local Effects",
            label="Inherited doubled local effects",
            key=f"mechanics.building_local.inherited.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=sources.WONDER_FINAL_BUILDINGS_FILE,
            original_value=serialize_structured_editor_value(inherited_local_state),
            field_type="modifier_table",
            target_kind="building_local",
            target_key=prototype_key,
            target_parent_key="final_local",
            height=10,
            help_text=(
                f"Inherited from prototype. Displayed values already apply this unique wonder's x{base_effect_multiplier} "
                "multiplier to the prototype's authored final_local package; edit the prototype wonder to modify the source."
            ),
            target_path=f"buildings.{prototype_key}.final_local",
            structured_value=inherited_local_state,
            editable=False,
            prototype_key=prototype_key,
        )
    else:
        final_local_state = build_modifier_editor_state(
            final_local_mapping,
            modifier_scope="local",
            options=option_catalogs["local_modifier"],
        )
        _add_mechanics_spec(
            specs,
            group="Final Building Local Effects",
            label="Shared final local effects",
            key=f"mechanics.building_local.{wonder['key']}.final_local",
            source_kind=shared_source_kind,
            file_path=sources.WONDER_FINAL_BUILDINGS_FILE,
            original_value=serialize_structured_editor_value(final_local_state),
            field_type="modifier_table",
            target_kind="building_local",
            target_key=prototype_key,
            target_parent_key="final_local",
            height=10,
            help_text="Shared local effects applied identically to all three final-building branches.",
            target_path=f"buildings.{prototype_key}.final_local",
            structured_value=final_local_state,
        )
    _add_mechanics_spec(
        specs,
        group="Base Modifiers",
        label="Per-level base modifiers",
        key=f"mechanics.base_modifiers.{wonder['key']}",
        source_kind=shared_source_kind,
        file_path=sources.WONDER_BASE_MODIFIERS_FILE,
        original_value=serialize_structured_editor_value(
            build_modifier_editor_state(
                displayed_base_modifier_mapping,
                modifier_scope="country",
                options=option_catalogs["country_modifier"],
            )
        ),
        field_type="modifier_table",
        target_kind="base_modifiers",
        target_key=prototype_key,
        height=10,
        help_text=base_modifier_help_text,
        target_path=f"base_modifiers.{prototype_key}",
        structured_value=build_modifier_editor_state(
            displayed_base_modifier_mapping,
            modifier_scope="country",
            options=option_catalogs["country_modifier"],
        ),
        editable=not inherits_from_prototype,
        prototype_key=prototype_key if inherits_from_prototype else "",
    )

    if wonder.get("is_unique"):
        unique_key = wonder["key"]
        unique_entry = get_unique_wonder_source(unique_wonders_data, unique_key)
        _add_mechanics_spec(
            specs,
            group="Unique Wonder",
            label="Prototype wonder",
            key=f"mechanics.unique_prototype.{unique_key}",
            source_kind="unique",
            file_path=sources.UNIQUE_WONDERS_FILE,
            original_value=str(unique_entry["base_key"]),
            field_type="select",
            target_kind="unique_prototype",
            target_key=unique_key,
            height=1,
            options=generic_options,
            help_text="Choose which generic wonder this unique wonder inherits its site rules and base modifiers from.",
            target_path=f"unique_wonders[{unique_key}].base_key",
        )
        _add_mechanics_spec(
            specs,
            group="Unique Wonder",
            label="Fixed location",
            key=f"mechanics.unique_location.{unique_key}",
            source_kind="unique",
            file_path=sources.UNIQUE_WONDERS_FILE,
            original_value=str(unique_entry["location"]),
            field_type="text",
            target_kind="unique_location",
            target_key=unique_key,
            height=2,
            help_text="Edits data/unique_wonders.yaml location.",
            target_path=f"unique_wonders[{unique_key}].location",
        )
        _add_mechanics_spec(
            specs,
            group="Unique Wonder",
            label="Initial level",
            key=f"mechanics.unique_initial_level.{unique_key}",
            source_kind="unique",
            file_path=sources.UNIQUE_WONDERS_FILE,
            original_value=stringify_editor_scalar(
                parse_unique_initial_level(
                    unique_entry.get("initial_level"),
                    context=f"unique_wonders[{unique_key}].initial_level",
                )
            ),
            field_type="number",
            target_kind="unique_initial_level",
            target_key=unique_key,
            height=1,
            help_text="Sets the fixed-site unique wonder level at game-start initialization. Use 0 when absent at start.",
            target_path=f"unique_wonders[{unique_key}].initial_level",
        )
        _add_mechanics_spec(
            specs,
            group="Unique Wonder",
            label="Ritual plan",
            key=f"mechanics.unique_ritual.{unique_key}",
            source_kind="unique",
            file_path=sources.UNIQUE_WONDERS_FILE,
            original_value=serialize_structured_editor_value(
                build_unique_ritual_editor_state(
                    unique_entry["ritual"],
                    country_modifier_options=option_catalogs["country_modifier"],
                    local_modifier_options=option_catalogs["local_modifier"],
                    reward_type_options=option_catalogs["reward_type"],
                )
            ),
            field_type="unique_ritual_editor",
            target_kind="unique_ritual",
            target_key=unique_key,
            height=18,
            help_text="Structured editor for data/unique_wonders.yaml ritual. Advanced script hooks stay visible but no longer require editing a whole YAML block.",
            target_path=f"unique_wonders[{unique_key}].ritual",
            structured_value=build_unique_ritual_editor_state(
                unique_entry["ritual"],
                country_modifier_options=option_catalogs["country_modifier"],
                local_modifier_options=option_catalogs["local_modifier"],
                reward_type_options=option_catalogs["reward_type"],
            ),
        )
        ceremony = unique_entry.get("ceremony")
        if ceremony is not None:
            ceremony_editor_state = build_unique_ceremony_editor_state(
                ceremony,
                cost_type_options=option_catalogs["ceremony_cost_type"],
            )
            _add_mechanics_spec(
                specs,
                group="Unique Wonder",
                label="Eight-stage ceremony",
                key=f"mechanics.unique_ceremony.{unique_key}",
                source_kind="unique",
                file_path=sources.UNIQUE_WONDERS_FILE,
                original_value=serialize_structured_editor_value(ceremony_editor_state),
                field_type="unique_ceremony_editor",
                target_kind="unique_ceremony",
                target_key=unique_key,
                height=32,
                help_text=(
                    "Structured editor for the automatic eight-stage ceremony. "
                    "Stage 2 uses the prototype style 3 reward, stage 4 builds its style 2 annex, "
                    "and stage 8 applies its style 1 modifier through finalization."
                ),
                target_path=f"unique_wonders[{unique_key}].ceremony",
                structured_value=ceremony_editor_state,
            )
        return specs

    generic_ritual = mechanics_data.get("generic_rituals", {}).get(wonder["key"], {})
    style_1 = generic_ritual.get("style_1", {})
    style_2 = generic_ritual.get("style_2", {})
    style_3 = generic_ritual.get("style_3", {})

    _add_mechanics_spec(
        specs,
        group="Generic Ritual",
        label="Style 1 country modifiers",
        key=f"mechanics.generic_ritual.{wonder['key']}.style_1",
        source_kind="shared",
        file_path=sources.WONDER_GENERIC_RITUALS_FILE,
        original_value=serialize_structured_editor_value(
            build_modifier_editor_state(
                style_1.get("country_modifier", {}),
                modifier_scope="country",
                options=option_catalogs["country_modifier"],
            )
        ),
        field_type="modifier_table",
        target_kind="generic_ritual",
        target_key=wonder["key"],
        target_parent_key="style_1",
        height=10,
        help_text="Structured editor for generic ritual style 1 country modifiers.",
        target_path=f"generic_rituals.{wonder['key']}.style_1.country_modifier",
        structured_value=build_modifier_editor_state(
            style_1.get("country_modifier", {}),
            modifier_scope="country",
            options=option_catalogs["country_modifier"],
        ),
    )
    style_2_editor_state = build_modifier_editor_state(
        style_2.get("local_modifier", {}),
        modifier_scope="local",
        options=option_catalogs["local_modifier"],
        derived_mapping=generic_style_2_derived_modifier_mapping(wonder),
        derived_title=GENERIC_STYLE_2_DERIVED_TITLE,
        derived_help_text=GENERIC_STYLE_2_DERIVED_HELP_TEXT,
    )
    _add_mechanics_spec(
        specs,
        group="Generic Ritual",
        label="Style 2 local modifiers",
        key=f"mechanics.generic_ritual.{wonder['key']}.style_2",
        source_kind="shared",
        file_path=sources.WONDER_GENERIC_RITUALS_FILE,
        original_value=serialize_structured_editor_value(style_2_editor_state),
        field_type="modifier_table",
        target_kind="generic_ritual",
        target_key=wonder["key"],
        target_parent_key="style_2",
        height=10,
        help_text="Structured editor for generic ritual style 2 local modifiers. The read-only section below shows the estate power that the building generator adds automatically.",
        target_path=f"generic_rituals.{wonder['key']}.style_2.local_modifier",
        structured_value=style_2_editor_state,
    )
    _add_mechanics_spec(
        specs,
        group="Generic Ritual",
        label="Style 3 reward package",
        key=f"mechanics.generic_ritual.{wonder['key']}.style_3",
        source_kind="shared",
        file_path=sources.WONDER_GENERIC_RITUALS_FILE,
        original_value=serialize_structured_editor_value(
            build_reward_editor_state(
                rows=reward_rows_from_list(style_3.get("reward", [])),
                options=option_catalogs["reward_type"],
                cost_type=style_3.get("cost_type"),
                cost_options=[
                    {"value": "", "label": "None"},
                    *[
                        {"value": cost_type, "label": cost_type}
                        for cost_type in sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None)
                    ],
                ],
            )
        ),
        field_type="reward_editor",
        target_kind="generic_ritual",
        target_key=wonder["key"],
        target_parent_key="style_3",
        height=10,
        help_text="Structured editor for style 3 cost type and one-time rewards.",
        target_path=f"generic_rituals.{wonder['key']}.style_3",
        structured_value=build_reward_editor_state(
            rows=reward_rows_from_list(style_3.get("reward", [])),
            options=option_catalogs["reward_type"],
            cost_type=style_3.get("cost_type"),
            cost_options=[
                {"value": "", "label": "None"},
                *[
                    {"value": cost_type, "label": cost_type}
                    for cost_type in sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None)
                ],
            ],
        ),
    )
    return specs


def _add_mechanics_spec(
    specs: list[MechanicsFieldSpec],
    *,
    group: str,
    label: str,
    key: str,
    source_kind: str,
    file_path: Path,
    original_value: str,
    field_type: str,
    target_kind: str,
    target_key: str,
    target_parent_key: str = "",
    height: int = 3,
    options: list[dict[str, Any]] | None = None,
    help_text: str = "",
    target_path: str = "",
    structured_value: Any | None = None,
    editable: bool = True,
    prototype_key: str = "",
) -> None:
    specs.append(
        MechanicsFieldSpec(
            key=key,
            label=label,
            group=group,
            source_kind=source_kind,
            file_path=file_path,
            original_value=original_value,
            field_type=field_type,
            target_kind=target_kind,
            target_key=target_key,
            target_parent_key=target_parent_key,
            height=height,
            options=list(options or []),
            help_text=help_text,
            source_path=str(file_path.relative_to(sources.REPO_ROOT)),
            target_path=target_path,
            structured_value=structured_value,
            editable=editable,
            prototype_key=prototype_key,
        )
    )


def build_specs_for_wonder(
    wonder: dict[str, Any],
    *,
    mechanics: dict[str, Any],
    event_suffixes: dict[int, str],
    localization_data: dict[str, dict[str, str]],
) -> dict[str, list[FieldSpec]]:
    specs = {language: [] for language in LANGUAGES}
    code = wonder["key"].upper()

    for language in LANGUAGES:
        _add_localization_field(localization_data, specs, language, "Concept", "Concept description", f"{concept_key_for_wonder(wonder)}_desc", height=5)

        _add_localization_field(localization_data, specs, language, "Proposal", "Proposal brief", f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", height=3)
        _add_localization_field(localization_data, specs, language, "Proposal", "Resume proposal", f"TV_ENGINEERING_PROPOSAL_RESUME_{code}_TEXT", height=3)
        _add_localization_field(localization_data, specs, language, "Proposal", "Expand proposal", f"TV_ENGINEERING_PROPOSAL_EXPAND_{code}_TEXT", height=3)
        _add_localization_field(localization_data, specs, language, "Proposal", "Locked text", f"TV_ENGINEERING_LOCKED_{code}_TEXT", height=2)
        _add_localization_field(localization_data, specs, language, "Proposal", "Proposal button", f"TV_ENGINEERING_PROPOSAL_BUTTON_{code}", height=2)
        _add_localization_field(localization_data, specs, language, "Proposal", "Lock tooltip", f"TV_WONDER_LOCK_{code}_TT", height=2)

        _add_localization_field(localization_data, specs, language, "Wonder", "Wonder name", wonder_name_key(wonder), height=2)
        _add_localization_field(localization_data, specs, language, "Wonder", "Wonder description", f"{wonder_name_key(wonder)}_desc", height=3)
        for part, label in (
            ("foundation", "Foundation module"),
            ("body", "Main structure module"),
            ("function", "Functional module"),
            ("decoration", "Crowning module"),
        ):
            _add_localization_field(localization_data, specs, language, "Wonder", f"{label} name", f"{wonder_name_key(wonder)}_{part}", height=2)
            _add_localization_field(localization_data, specs, language, "Wonder", f"{label} description", f"{wonder_name_key(wonder)}_{part}_desc", height=3)

        if not wonder.get("is_unique"):
            _add_localization_field(localization_data, specs, language, "Wonder", "Ritual annex name", f"{wonder_name_key(wonder)}_ritual_annex", height=2)
            _add_localization_field(localization_data, specs, language, "Wonder", "Ritual annex description", f"{wonder_name_key(wonder)}_ritual_annex_desc", height=3)

        for level in range(1, 7):
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Modifiers",
                f"Level {ROMAN_NUMERALS[level]} national display modifier",
                f"STATIC_MODIFIER_NAME_{wonder_static_display_modifier_name(wonder, level)}",
                height=2,
            )
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Modifiers",
                f"Level {ROMAN_NUMERALS[level]} local display modifier",
                f"STATIC_MODIFIER_NAME_{wonder_static_local_display_modifier_name(wonder, level)}",
                height=2,
            )

        if not wonder.get("is_unique"):
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Modifiers",
                "Ritual burden modifier",
                f"STATIC_MODIFIER_NAME_{ritual_burden_modifier_name(wonder)}",
                height=2,
            )
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Modifiers",
                "Ritual blessing modifier",
                f"STATIC_MODIFIER_NAME_{ritual_blessing_modifier_name(wonder)}",
                height=2,
            )

        for style in ceremony_styles(wonder):
            branch_name = _branch_name(localization_data, wonder, style, language)
            building = final_building_for_style(wonder, style)
            label_prefix = f"Style {style}: {branch_name}"
            _add_localization_field(localization_data, specs, language, "Branches", f"{label_prefix} final building name", building, height=2)
            _add_localization_field(localization_data, specs, language, "Branches", f"{label_prefix} final building description", f"{building}_desc", height=3)
            ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
            if ceremony_modifier is not None:
                _add_localization_field(
                    localization_data,
                    specs,
                    language,
                    "Branches",
                    f"{label_prefix} modifier name",
                    f"STATIC_MODIFIER_NAME_{ceremony_modifier[0]}",
                    height=2,
                )
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Branches",
                f"{label_prefix} button",
                branch_button_key(building),
                height=2,
            )
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Branches",
                f"{label_prefix} active ritual text",
                active_ritual_key(wonder, style),
                height=3,
            )

        if wonder.get("is_unique"):
            _add_localization_field(
                localization_data,
                specs,
                language,
                "Events",
                "Wonder completion event",
                event_desc_key(wonder, event_suffixes),
                height=6,
            )
        else:
            suffix = event_suffixes.get(int(wonder["id"]))
            if suffix is not None:
                for style in ceremony_styles(wonder):
                    branch_name = _branch_name(localization_data, wonder, style, language)
                    _add_localization_field(
                        localization_data,
                        specs,
                        language,
                        "Events",
                        f"Completion event style {style}: {branch_name}",
                        event_desc_key(wonder, event_suffixes, style),
                        height=6,
                    )
                _add_localization_field(
                    localization_data,
                    specs,
                    language,
                    "Events",
                    "World news event",
                    event_desc_key(wonder, event_suffixes, None),
                    height=6,
                )

    return specs


def _branch_name(localization_data: dict[str, dict[str, str]], wonder: dict[str, Any], style: int, language: str) -> str:
    building = final_building_for_style(wonder, style)
    return localization_value(localization_data, language, branch_button_key(building))


def _add_localization_field(
    localization_data: dict[str, dict[str, str]],
    specs: dict[str, list[FieldSpec]],
    language: str,
    group: str,
    label: str,
    key: str | None,
    *,
    height: int = 3,
) -> None:
    if key is None:
        raise KeyError(f"Missing generated localization key for {label}")
    specs[language].append(
        FieldSpec(
            key=key,
            label=label,
            group=group,
            language=language,
            file_path=sources.WONDER_LOCALIZATION_FILE,
            original_value=localization_value(localization_data, language, key),
            height=height,
        )
    )
