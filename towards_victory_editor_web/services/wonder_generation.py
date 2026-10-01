"""Wonder editor generation catalog; domain rules stay in the generators."""

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

WONDER_GENERATORS = (
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/building_types/gen_tv_wonder_module_buildings.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/building_types/gen_tv_engineering_department_wonder_mechanics_buildings.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/generic_actions/gen_tv_engineering_department_wonder_mechanics_actions.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_module_effects.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py",
        inputs=MECHANICS_EFFECTS_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        LOCALIZATION_SCRIPTS["english"],
        inputs=LOCALIZATION_INPUTS,
    ),
    GeneratorSpec(
        LOCALIZATION_SCRIPTS["simp_chinese"],
        inputs=LOCALIZATION_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
        inputs=WONDER_LOADER_INPUTS,
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
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_country_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_local_modifiers.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ceremony_effects.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/events/gen_tv_wonder_ceremony_events.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/english/gen_tv_wonder_ceremony_l_english.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ceremony_l_simp_chinese.py",
        inputs=WONDER_LOADER_INPUTS,
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py",
        inputs=UNIQUE_INPUT,
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
) -> GenerationPlan:
    roots: list[str] = []
    if regenerate:
        # Generic/mechanics and unique data are shared by the complete Wonder
        # output surface.  Keep that full closure until each generator has a
        # narrower semantic dependency than the common loader provides.
        if any(changed.get(key) for key in ("wonders", "mechanics", "unique")):
            roots.extend(spec.script for spec in WONDER_GENERATORS)
        if changed.get("localization"):
            roots.extend(LOCALIZATION_SCRIPTS.values())
        if changed.get("cost_reward"):
            roots.extend(
                spec.script
                for spec in WONDER_GENERATORS
                if COST_REWARD_INPUT[0] in spec.inputs
            )
    return build_generation_plan(WONDER_GENERATORS, tuple(dict.fromkeys(roots)), repo_root=repo_root)
