import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_expansion_lib import final_building_for_style, load_wonder_data, loc_line, render_header

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_engineering_department_wonder_expansion_l_english.yml"
SCRIPT_REL = "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_expansion_l_english.py"
SIZE_CONCEPT = {
    "small": "tv_wonder_small",
    "medium": "tv_wonder_medium",
    "large": "tv_wonder_large",
}


def display_key(key: str) -> str:
    return key.upper()


def branch_effect_text(branch: dict) -> str:
    return branch.get("effect", "").rstrip("。.")


def generate() -> str:
    wonders, expansion = load_wonder_data()
    lines = ["l_english:"]
    for line in render_header(SCRIPT_REL):
        lines.append(f" {line}")

    lines.append(loc_line("tv_wonder_confirm_new_ceremony", "Confirm Ceremony"))
    lines.append(loc_line("tv_wonder_confirm_new_ceremony_desc", "Confirm the selected ceremony branch and inaugurate the completed wonder."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_new_ceremony_ACTION_SETUP", "When we confirm a newly designed wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_new_ceremony_ACTION_LOG", "We confirmed the wonder ceremony."))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_new_ceremony_ACTION_MAP", ""))

    for wonder in wonders:
        key = wonder["key"]
        design = expansion["designs"][key]
        name = wonder["loc"]["en"]
        concept = wonder["concept"]
        size_concept = SIZE_CONCEPT[wonder["size"]]
        branch_list = [design["branches"][style] for style in range(1, 4)]
        branch_names = ", ".join(branch["en"] for branch in branch_list)
        code = display_key(key)

        lines.append(loc_line(f"game_concept_{concept}", name))
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
        lines.append(loc_line(f"tv_wonder_{key}_desc", f"An unconsecrated {name} preserved as completed construction."))

        for style, branch in ((style, design["branches"][style]) for style in range(1, 4)):
            building = final_building_for_style(wonder, style)
            branch_name = branch["en"]
            effect = branch_effect_text(branch)
            ceremony_key = building.removeprefix("tv_wonder_").upper()
            lines.append(loc_line(building, branch_name))
            lines.append(loc_line(f"{building}_desc", f"The {branch_name} branch of the {name}."))
            lines.append(loc_line(f"STATIC_MODIFIER_NAME_{building}_modifier", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_CEREMONY_{ceremony_key}_BUTTON", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_ACTIVE_RITUAL_{code}_{style}", f"Confirm the {branch_name} ceremony for the {name}. {effect}."))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
