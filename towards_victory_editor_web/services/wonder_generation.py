"""Wonder editor generation catalog; domain rules stay in the generators."""

from pathlib import Path

from .generation import GeneratorSpec, GenerationPlan, build_generation_plan


LOCALIZATION_SCRIPTS = {
    "english": "scripts_engineering_department/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
    "simp_chinese": "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py",
}

WONDER_GENERATORS = (
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/building_types/gen_tv_wonder_module_buildings.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/building_types/gen_tv_engineering_department_wonder_mechanics_buildings.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/generic_actions/gen_tv_engineering_department_wonder_mechanics_actions.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_module_effects.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py",
    ),
    GeneratorSpec(
        LOCALIZATION_SCRIPTS["english"],
    ),
    GeneratorSpec(
        LOCALIZATION_SCRIPTS["simp_chinese"],
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
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
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_country_modifiers.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_local_modifiers.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ceremony_effects.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/events/gen_tv_wonder_ceremony_events.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/english/gen_tv_wonder_ceremony_l_english.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ceremony_l_simp_chinese.py",
    ),
    GeneratorSpec(
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py",
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
        ),
    ),
)


def wonder_generation_plan(
    changed: dict[str, bool], *, repo_root: Path, regenerate: bool = True,
) -> GenerationPlan:
    roots = ()
    if regenerate:
        if any(changed.get(key) for key in ("wonders", "mechanics", "unique")):
            roots = tuple(spec.script for spec in WONDER_GENERATORS)
        elif changed.get("localization"):
            roots = tuple(LOCALIZATION_SCRIPTS.values())
    return build_generation_plan(WONDER_GENERATORS, roots, repo_root=repo_root)
