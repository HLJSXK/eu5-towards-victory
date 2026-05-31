import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_modifier_for_style,
    ceremony_styles,
    final_building_for_style,
    level_static_modifier_loc,
    load_all_wonder_mechanics_data,
    loc_line,
    mechanic_key,
    render_header,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
    unique_ritual,
)
from wonder_localization_lib import apply_localization_values, load_localization_map, load_wonder_localization_data

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_engineering_department_wonder_mechanics_l_english.yml"
SCRIPT_REL = "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py"
DATA_REL = "data/wonders.yaml + data/wonder_mechanics.yaml + data/unique_wonders.yaml + data/wonder_localization.yaml"
MANUAL_CONCEPT_LOC_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_game_concepts_l_english.yml"
SIZE_CONCEPT = {
    "small": "tv_wonder_small",
    "medium": "tv_wonder_medium",
    "large": "tv_wonder_large",
}


def display_key(key: str) -> str:
    return key.upper()


def branch_effect_text(branch: dict) -> str:
    return branch.get("effect", "").rstrip(".\u3002")


def unique_effect_text(wonder: dict, language: str) -> str:
    return unique_ritual(wonder).get("effect", {}).get(language, "")


def unique_active_ritual_text(wonder: dict, language: str) -> str:
    ritual = unique_ritual(wonder)
    custom = ritual.get("active_text", {}).get(language, "")
    if custom:
        return custom
    branch_name = ritual["loc"][language]
    effect = unique_effect_text(wonder, language)
    name = wonder["loc"][language]
    return f"Confirm the {branch_name} ceremony for the {name}. {effect}.".rstrip()


def unique_completion_text(wonder: dict, language: str) -> str:
    ritual = unique_ritual(wonder)
    custom = ritual.get("completion_text", {}).get(language, "")
    if custom:
        return custom
    ceremony_name = ritual["loc"][language]
    flavor = wonder["flavor"][language]
    history_intro = wonder["history_intro"][language]
    effect = unique_effect_text(wonder, language)
    return f"{flavor} {history_intro} The {ceremony_name} now completes the wonder at its fixed historical site. {effect}"


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics_data()
    manual_concepts = load_localization_map(MANUAL_CONCEPT_LOC_FILE)
    localization = load_wonder_localization_data()["english"]
    lines = ["l_english:"]
    for line in render_header(SCRIPT_REL, DATA_REL):
        lines.append(f" {line}")

    lines.append(loc_line("tv_wonder_confirm_ceremony", "Confirm Ceremony"))
    lines.append(loc_line("tv_wonder_confirm_ceremony_desc", "Confirm the selected ceremony branch and inaugurate the completed wonder."))
    lines.append(loc_line("tv_wonder_confirm_ceremony_scaled_gold", "Confirm Scaled-Gold Ceremony"))
    lines.append(loc_line("tv_wonder_confirm_ceremony_scaled_gold_desc", "Pay the scaled-gold ceremony cost and inaugurate the completed wonder."))
    lines.append(loc_line("tv_wonder_confirm_ceremony_prestige", "Confirm Prestige Ceremony"))
    lines.append(loc_line("tv_wonder_confirm_ceremony_prestige_desc", "Pay the Prestige ceremony cost and inaugurate the completed wonder."))
    lines.append(loc_line("tv_wonder_ritual_style_3_scaled_gold_price", "Scaled-Gold Ceremony"))
    lines.append(loc_line("tv_wonder_ritual_style_3_prestige_price", "Prestige Ceremony"))
    lines.append(loc_line("tv_wonder_ritual_annex_small_price", "Small Ritual Annex"))
    lines.append(loc_line("tv_wonder_ritual_annex_medium_price", "Medium Ritual Annex"))
    lines.append(loc_line("tv_wonder_ritual_annex_large_price", "Large Ritual Annex"))
    lines.append(loc_line("MODIFIER_TYPE_NAME_tv_wonder_ritual_style_3_scaled_gold_price_cost_modifier", "Scaled-Gold Ceremony Cost"))
    lines.append(loc_line("MODIFIER_TYPE_DESC_tv_wonder_ritual_style_3_scaled_gold_price_cost_modifier", "Modifies the scaled gold cost of third-style wonder ceremonies."))
    lines.append(loc_line("MODIFIER_TYPE_NAME_tv_wonder_ritual_style_3_prestige_price_cost_modifier", "Prestige Ceremony Cost"))
    lines.append(loc_line("MODIFIER_TYPE_DESC_tv_wonder_ritual_style_3_prestige_price_cost_modifier", "Modifies the Prestige cost of third-style wonder ceremonies."))
    lines.append(loc_line("MODIFIER_TYPE_NAME_tv_wonder_ritual_annex_small_price_cost_modifier", "Small Ritual Annex Cost"))
    lines.append(loc_line("MODIFIER_TYPE_DESC_tv_wonder_ritual_annex_small_price_cost_modifier", "Modifies the gold construction cost of small wonder ritual annexes."))
    lines.append(loc_line("MODIFIER_TYPE_NAME_tv_wonder_ritual_annex_medium_price_cost_modifier", "Medium Ritual Annex Cost"))
    lines.append(loc_line("MODIFIER_TYPE_DESC_tv_wonder_ritual_annex_medium_price_cost_modifier", "Modifies the gold construction cost of medium wonder ritual annexes."))
    lines.append(loc_line("MODIFIER_TYPE_NAME_tv_wonder_ritual_annex_large_price_cost_modifier", "Large Ritual Annex Cost"))
    lines.append(loc_line("MODIFIER_TYPE_DESC_tv_wonder_ritual_annex_large_price_cost_modifier", "Modifies the gold construction cost of large wonder ritual annexes."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_ACTION_SETUP", "When we confirm a wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_ACTION_LOG", "We confirmed the wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_ACTION_MAP", ""))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION_SETUP", "When we confirm a scaled-gold wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION_LOG", "We confirmed the scaled-gold wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION_MAP", ""))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION_SETUP", "When we confirm a Prestige wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION_LOG", "We confirmed the Prestige wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION_MAP", ""))
    for wonder in wonders:
        key = wonder["key"]
        design = mechanics["designs"].get(mechanic_key(wonder))
        name = wonder["loc"]["en"]
        concept = wonder["concept"]
        size_concept = SIZE_CONCEPT[wonder["size"]]
        code = display_key(key)

        concept_name_key = f"game_concept_{concept}"
        concept_desc_key = f"{concept_name_key}_desc"
        include_concept_name = concept_name_key not in manual_concepts
        include_concept_desc = concept_desc_key not in manual_concepts
        if include_concept_name:
            lines.append(loc_line(f"game_concept_{concept}", name))
        if wonder.get("is_unique"):
            ritual = unique_ritual(wonder)
            ceremony_name = ritual["loc"]["en"]
            flavor = wonder["flavor"]["en"]
            history_intro = wonder["history_intro"]["en"]
            if include_concept_desc:
                lines.append(loc_line(f"game_concept_{concept}_desc", f"{flavor} This unique [tv_wonder_construction|e] project must be raised at its fixed historical site, follows the same site rules as its generic archetype, and culminates in the {ceremony_name} ritual sequence."))
            lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", f"{history_intro} Brief: [{concept}|E], a unique [{size_concept}|E] historical wonder at its fixed historical site."))
        else:
            if design is None:
                raise ValueError(f"Missing design data for {key}")
            branch_list = [design["branches"][style] for style in range(1, 4)]
            branch_names = ", ".join(branch["en"] for branch in branch_list)
            if include_concept_desc:
                lines.append(loc_line(f"game_concept_{concept}_desc", f"A {name} is a [tv_wonder_construction|e] project focused on {design['positioning']}. It prefers {design['site']} Its ceremonies can emphasize {branch_names}."))
            lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", f"Brief: [{concept}|E], a [{size_concept}|E] project for {design['positioning']}."))
        lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_RESUME_{code}_TEXT", f"The [tv_great_engineer|E] wants to complete the existing [{concept}|E] and reuse the preserved construction at the site."))
        lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_EXPAND_{code}_TEXT", f"The [tv_great_engineer|E] wants to expand the existing [{concept}|E] toward the site's preserved maximum level."))
        lines.append(loc_line(f"TV_ENGINEERING_LOCKED_{code}_TEXT", f"@lock! Locked Wonder: [{concept}|E]."))
        lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_BUTTON_{code}", f"@city! {name}"))
        lines.append(loc_line(f"TV_WONDER_LOCK_{code}_TT", f"Locks [{concept}|E] as the Engineering Department's active wonder."))

        for part in ["foundation", "body", "function", "decoration"]:
            building_key = f"tv_wonder_{key}_{part}"
            part_name = {
                "foundation": "Foundation",
                "body": "Main Structure",
                "function": "Functional Works",
                "decoration": "Crowning Works",
            }[part]
            lines.append(loc_line(building_key, f"{name} {part_name}"))
            lines.append(loc_line(f"{building_key}_desc", f"A preserved {part_name.lower()} module for the {name}."))
        lines.append(loc_line(f"tv_wonder_{key}", name))
        if not wonder.get("is_unique"):
            annex_key = f"tv_wonder_{key}_ritual_annex"
            lines.append(loc_line(annex_key, f"{name} Ritual Annex"))
            lines.append(loc_line(f"{annex_key}_desc", f"An auxiliary ritual annex used to complete the second ceremony branch of the {name}."))
        lines.append(loc_line(f"tv_wonder_{key}_desc", f"An unconsecrated {name} preserved as completed construction."))
        for level in range(1, 7):
            lines.append(
                loc_line(
                    f"STATIC_MODIFIER_NAME_tv_wonder_{key}_level_{level}",
                    level_static_modifier_loc(concept, level),
                )
            )
        if not wonder.get("is_unique"):
            style_one_name = design["branches"][1]["en"]
            lines.append(
                loc_line(
                    f"STATIC_MODIFIER_NAME_{ritual_burden_modifier_name(wonder)}",
                    f"{style_one_name} Ritual Burden",
                )
            )
            lines.append(
                loc_line(
                    f"STATIC_MODIFIER_NAME_{ritual_blessing_modifier_name(wonder)}",
                    f"{style_one_name} Blessing",
                )
            )

        for style in ceremony_styles(wonder):
            building = final_building_for_style(wonder, style)
            if wonder.get("is_unique"):
                ritual = unique_ritual(wonder)
                branch_name = ritual["loc"]["en"]
                building_name = name
                building_desc = wonder["flavor"]["en"]
                effect = unique_effect_text(wonder, "en")
            else:
                branch = design["branches"][style]
                branch_name = branch["en"]
                building_name = branch_name
                building_desc = f"The {branch_name} branch of the {name}."
                effect = branch_effect_text(branch)
            ceremony_key = building.removeprefix("tv_wonder_").upper()
            ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
            lines.append(loc_line(building, building_name))
            lines.append(loc_line(f"{building}_desc", building_desc))
            if ceremony_modifier is not None:
                lines.append(loc_line(f"STATIC_MODIFIER_NAME_{ceremony_modifier[0]}", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_CEREMONY_{ceremony_key}_BUTTON", branch_name))
            if wonder.get("is_unique"):
                lines.append(loc_line(f"TV_ENGINEERING_ACTIVE_RITUAL_{code}_{style}", unique_active_ritual_text(wonder, "en")))
            else:
                lines.append(loc_line(f"TV_ENGINEERING_ACTIVE_RITUAL_{code}_{style}", f"Confirm the {branch_name} ceremony for the {name}. {effect}."))
        if wonder.get("is_unique"):
            lines.append(loc_line(f"tv_engineering_department.500.d_{key}", unique_completion_text(wonder, "en")))

    return apply_localization_values("\n".join(lines).rstrip() + "\n", localization)


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
