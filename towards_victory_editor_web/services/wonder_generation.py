"""Wonder editor generation catalog; domain rules stay in the generators."""

from collections.abc import Iterable
from pathlib import Path

from .generation import GeneratorSpec, GenerationPlan, build_generation_plan


LOCALIZATION_SCRIPTS = {
    "english": "scripts_engineering_department/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
    "simp_chinese": "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py",
}

# These are the data files read by the Wonder generators.  Keeping the paths on
# each spec makes the generation plan useful as an input dependency report and
# lets the runner reject a plan before any source file is written.
WONDERS_INPUT = ("data/wonders.yaml",)
DESIGN_NOTES_INPUT = ("data/wonder_design_notes.yaml",)
MECHANICS_INPUTS = (
    "data/wonder_final_buildings.yaml",
    "data/wonder_generic_rituals.yaml",
    "data/wonder_base_modifiers.yaml",
    "data/wonder_site_rules.yaml",
)
UNIQUE_INPUT = ("data/unique_wonders.yaml",)
COST_REWARD_INPUT = ("data/cost_reward_units.yaml",)
ALL_WONDER_INPUTS = WONDERS_INPUT + DESIGN_NOTES_INPUT + MECHANICS_INPUTS + UNIQUE_INPUT
WONDER_LOADER_INPUTS = ALL_WONDER_INPUTS + COST_REWARD_INPUT
LOCALIZATION_INPUTS = WONDER_LOADER_INPUTS + ("data/wonder_localization.yaml",)
MECHANICS_EFFECTS_INPUTS = WONDER_LOADER_INPUTS + ("data/pulse_registry.yaml",)

MECHANICS_GROUPS = (
    "mechanics.buildings",
    "mechanics.rituals",
    "mechanics.base_modifiers",
    "mechanics.site_rules",
)
ALL_SOURCE_GROUPS = ("wonders", *MECHANICS_GROUPS, "unique")

# The editor writes these seven source documents.  Keep this mapping beside the
# generation catalog so source-to-plan routing and generator declarations share
# one vocabulary.
WONDER_SOURCE_GROUPS = {
    "data/wonder_localization.yaml": "localization",
    "data/wonder_final_buildings.yaml": "mechanics.buildings",
    "data/wonder_generic_rituals.yaml": "mechanics.rituals",
    "data/wonder_base_modifiers.yaml": "mechanics.base_modifiers",
    "data/wonder_site_rules.yaml": "mechanics.site_rules",
    "data/wonders.yaml": "wonders",
    "data/unique_wonders.yaml": "unique",
}

WONDER_GENERATORS = (
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/building_types/gen_tv_wonder_module_buildings.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("wonders", "unique", "mechanics.buildings", "mechanics.base_modifiers", "mechanics.rituals"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/building_types/gen_tv_engineering_department_wonder_mechanics_buildings.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("wonders", "unique", "mechanics.buildings", "mechanics.base_modifiers", "mechanics.rituals", "mechanics.site_rules"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("wonders", "unique", "mechanics.base_modifiers", "mechanics.rituals"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/generic_actions/gen_tv_engineering_department_wonder_mechanics_actions.py",
        inputs=WONDER_LOADER_INPUTS,
        # Fixed output; the loader call only validates data.  Full plans only.
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_module_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py",
        inputs=MECHANICS_EFFECTS_INPUTS,
        input_groups=(*ALL_SOURCE_GROUPS, "pulse_registry"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("wonders", "unique", *MECHANICS_GROUPS),
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("wonders", "unique"),
    ),
    GeneratorSpec(
        LOCALIZATION_SCRIPTS["english"],
        inputs=LOCALIZATION_INPUTS,
        input_groups=(*ALL_SOURCE_GROUPS, "localization"),
    ),
    GeneratorSpec(
        LOCALIZATION_SCRIPTS["simp_chinese"],
        inputs=LOCALIZATION_INPUTS,
        input_groups=(*ALL_SOURCE_GROUPS, "localization"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/merge_tv_engineering_department_wonder_mechanics_gui.py",
        depends_on=(
            "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
        ),
        inputs=(
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui",
            "src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui",
        ),
        extra_outputs=(
            "src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui",
        ),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/customizable_localization/gen_tv_wonder_ceremony_options.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_country_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique", "cost_reward"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_local_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique", "cost_reward"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ceremony_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique", "mechanics.rituals", "cost_reward"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/events/gen_tv_wonder_ceremony_events.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/english/gen_tv_wonder_ceremony_l_english.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique", "cost_reward"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ceremony_l_simp_chinese.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=("unique", "cost_reward"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py",
        inputs=UNIQUE_INPUT,
        input_groups=("unique",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/merge_tv_wonder_ceremony_cards_gui.py",
        depends_on=(
            "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py",
            "scripts_engineering_department/in_game/gui/panels/organization/merge_tv_engineering_department_wonder_mechanics_gui.py",
        ),
        inputs=(
            "data/generated_fragments/tv_wonder_ceremony_cards.gui",
            "src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui",
        ),
        extra_outputs=(
            "src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui",
        ),
    ),
    # Wonder generators registered in data/generated_files.yaml that are also
    # affected by editor controlled Wonder sources.
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_index_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_survey_effects.py",
        inputs=MECHANICS_EFFECTS_INPUTS,
        input_groups=(*ALL_SOURCE_GROUPS, "pulse_registry"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_finalization_effects.py",
        inputs=MECHANICS_EFFECTS_INPUTS,
        input_groups=(*ALL_SOURCE_GROUPS, "pulse_registry"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/events/gen_tv_wonder_finalization_events.py",
        # Falls back to shared desc keys based on which localization keys exist.
        inputs=LOCALIZATION_INPUTS,
        input_groups=(*ALL_SOURCE_GROUPS, "localization"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/events/gen_tv_wonder_ownership_events.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_proposal_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ownership_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/english/gen_tv_wonder_ownership_l_english.py",
        inputs=("data/wonder_localization.yaml",),
        input_groups=("localization",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ownership_l_simp_chinese.py",
        inputs=("data/wonder_localization.yaml",),
        input_groups=("localization",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_location_display_effects.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/auto_modifiers/gen_tv_engineering_department_wonder_mechanics_auto_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/gui/shared/gen_tv_ceremony_font_icons_gui.py",
        inputs=(
            "data/unique_wonders.yaml",
            "reference_game_files/game/main_menu/gui/shared/font_icons.gui",
        ),
        input_groups=("unique",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/gen_tv_encyclopedia_wonders_cards_gui.py",
        inputs=WONDER_LOADER_INPUTS,
        input_groups=ALL_SOURCE_GROUPS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/merge_tv_encyclopedia_wonders_cards_gui.py",
        depends_on=(
            "scripts_engineering_department/in_game/gui/gen_tv_encyclopedia_wonders_cards_gui.py",
        ),
        inputs=(
            "data/generated_fragments/tv_encyclopedia_wonders_cards.gui",
            "src_engineering_department/in_game/gui/encyclopedia_lateralview.gui",
        ),
        extra_outputs=(
            "src_engineering_department/in_game/gui/encyclopedia_lateralview.gui",
        ),
    ),
    GeneratorSpec(
        "scripts/compat/gen_tv_prosper_or_perish_encyclopedia_lateralview.py",
        depends_on=(
            "scripts_engineering_department/in_game/gui/merge_tv_encyclopedia_wonders_cards_gui.py",
        ),
        inputs=(
            "src_engineering_department/in_game/gui/encyclopedia_lateralview.gui",
            "reference_mods/3613232232/in_game/gui/encyclopedia_lateralview.gui",
        ),
    ),
    GeneratorSpec(
        "scripts_engineering_department/gen_unique_wonder_ritual_specs.py",
        inputs=(
            "data/unique_wonders.yaml",
            "data/wonder_localization.yaml",
            "data/unique_wonder_ritual_designs.yaml",
            "data/unique_wonder_ritual_prompts.yaml",
            "data/unique_wonder_ritual_codegen_templates.yaml",
            "data/unique_wonder_ritual_capabilities.yaml",
        ),
        input_groups=("unique", "localization"),
    ),
    GeneratorSpec(
        "scripts_engineering_department/gen_wonder_editor_catalog.py",
        inputs=(
            "data/cost_reward_units.yaml",
            "reference_game_files/game/in_game/events",
            "reference_game_files/game/main_menu/common/static_modifiers",
            "reference_game_files/game/main_menu/common/modifier_type_definitions",
        ),
        input_groups=("cost_reward",),
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/gen_location_window.py",
        inputs=(
            "reference_mods/3601047146/in_game/gui/location_window.gui",
            "reference_mods/3601047146/in_game/gui/glorpUI_shared_types.gui",
            "reference_mods/3601047146/in_game/gui/vanilla/cmfg_location_window_vanilla_types.gui",
            # This generator only reads the three reference GUI sources.
        ),
    ),
)


def wonder_generation_plan(
    changed: dict[str, bool], *, repo_root: Path, regenerate: bool = True,
    input_groups: Iterable[str] | None = None,
) -> GenerationPlan:
    if not regenerate:
        return build_generation_plan(WONDER_GENERATORS, (), repo_root=repo_root)

    # An explicit source delta takes precedence over the coarse flags used to
    # decide which YAML documents to serialize.
    if input_groups is None and changed.get("mechanics"):
        # The public full-mechanics operation covers the complete Wonder output
        # surface, including generators no editor source group selects.
        roots = tuple(spec.script for spec in WONDER_GENERATORS)
        return build_generation_plan(WONDER_GENERATORS, roots, repo_root=repo_root)

    groups = set(input_groups) if input_groups is not None else {key for key, value in changed.items() if value}
    roots = (
        spec.script for spec in WONDER_GENERATORS
        if any(group in groups for group in spec.input_groups)
    )
    return build_generation_plan(WONDER_GENERATORS, roots, repo_root=repo_root)
