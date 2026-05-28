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
    load_all_wonder_mechanics_data,
    load_manual_game_concept_ids,
    loc_line,
    mechanic_key,
    render_header,
)

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_wonder_mechanics_l_simp_chinese.yml"
SCRIPT_REL = "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py"
SIZE_CONCEPT = {
    "small": "tv_wonder_small",
    "medium": "tv_wonder_medium",
    "large": "tv_wonder_large",
}


def display_key(key: str) -> str:
    return key.upper()


def branch_effect_text(branch: dict) -> str:
    return branch.get("effect", "").rstrip(".。")


def unique_effect_text(wonder: dict, language: str) -> str:
    return wonder.get("ceremony", {}).get("effect", {}).get(language, "")


def unique_completion_text(wonder: dict, language: str) -> str:
    ceremony_name = wonder["ceremony"]["loc"][language]
    flavor = wonder["flavor"][language]
    history_intro = wonder["history_intro"][language]
    effect = unique_effect_text(wonder, language)
    return f"{flavor} {history_intro} 如今，{ceremony_name}为这座奇观完成了固定历史地点上的落成。{effect}"


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics_data()
    manual_concepts = load_manual_game_concept_ids()
    lines = ["l_simp_chinese:"]
    for line in render_header(SCRIPT_REL):
        lines.append(f" {line}")

    lines.append(loc_line("tv_wonder_confirm_ceremony", "确认仪式"))
    lines.append(loc_line("tv_wonder_confirm_ceremony_desc", "确认已选择的仪式分支，并让完工的奇观正式落成。"))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_ACTION_SETUP", "当我们确认奇观的落成仪式时。"))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_ACTION_LOG", "我们确认了奇观落成仪式。"))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_ceremony_ACTION_MAP", ""))

    for wonder in wonders:
        key = wonder["key"]
        design = mechanics["designs"].get(mechanic_key(wonder))
        name = wonder["loc"]["zh"]
        concept = wonder["concept"]
        size_concept = SIZE_CONCEPT[wonder["size"]]
        code = display_key(key)
        include_concept_loc = concept not in manual_concepts

        if include_concept_loc:
            lines.append(loc_line(f"game_concept_{concept}", name))
        if wonder.get("is_unique"):
            ceremony_name = wonder["ceremony"]["loc"]["zh"]
            flavor = wonder["flavor"]["zh"]
            history_intro = wonder["history_intro"]["zh"]
            lines.append(loc_line(f"game_concept_{concept}_desc", f"{flavor} 这是一项必须在固定历史地点建造的独特[tv_wonder_construction|e]工程，沿用其通用原型的地点规则，并以{ceremony_name}作为唯一落成仪式。"))
            lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", f"{history_intro} 简报：[{concept}|E]是一项固定于其历史地点的独特历史[{size_concept}|E]工程。"))
        else:
            if design is None:
                raise ValueError(f"Missing design data for {key}")
            branch_list = [design["branches"][style] for style in range(1, 4)]
            branch_names = "、".join(branch["zh"] for branch in branch_list)
            lines.append(loc_line(f"game_concept_{concept}_desc", f"{name}是一项侧重{design['positioning']}的[tv_wonder_construction|e]项目。它偏好{design['site']}仪式可转向{branch_names}。"))
            lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", f"简报：[{concept}|E]，定位于{design['positioning']}的[{size_concept}|E]工程。"))
        lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_RESUME_{code}_TEXT", f"[tv_great_engineer|E]建议完成造了一半的[{concept}|E]，并利用当地已经保留下来的工程部分。"))
        lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_EXPAND_{code}_TEXT", f"[tv_great_engineer|E]建议扩建[{concept}|E]，继续利用该地点已经保存的最大等级适性。"))
        lines.append(loc_line(f"TV_ENGINEERING_LOCKED_{code}_TEXT", f"@lock! 已锁定奇观：[{concept}|E]。"))
        lines.append(loc_line(f"TV_ENGINEERING_PROPOSAL_BUTTON_{code}", f"@city! {name}"))
        lines.append(loc_line(f"TV_WONDER_LOCK_{code}_TT", f"将[{concept}|E]锁定为工程部当前奇观。"))

        for part in ["foundation", "body", "function", "decoration"]:
            building_key = f"tv_wonder_{key}_{part}"
            part_name = {
                "foundation": "基础",
                "body": "主体",
                "function": "功能",
                "decoration": "封顶装饰",
            }[part]
            lines.append(loc_line(building_key, f"{name}{part_name}"))
            lines.append(loc_line(f"{building_key}_desc", f"{name}已经保留下来的{part_name}模块。"))
        lines.append(loc_line(f"tv_wonder_{key}", name))
        lines.append(loc_line(f"tv_wonder_{key}_desc", f"尚未落成、但已作为完整工程保存下来的{name}。"))

        for style in ceremony_styles(wonder):
            building = final_building_for_style(wonder, style)
            if wonder.get("is_unique"):
                branch_name = wonder["ceremony"]["loc"]["zh"]
                building_name = name
                building_desc = wonder["flavor"]["zh"]
                effect = unique_effect_text(wonder, "zh")
            else:
                branch = design["branches"][style]
                branch_name = branch["zh"]
                building_name = branch_name
                building_desc = f"{name}的{branch_name}仪式分支。"
                effect = branch_effect_text(branch)
            ceremony_key = building.removeprefix("tv_wonder_").upper()
            ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
            lines.append(loc_line(building, building_name))
            lines.append(loc_line(f"{building}_desc", building_desc))
            if ceremony_modifier is not None:
                lines.append(loc_line(f"STATIC_MODIFIER_NAME_{ceremony_modifier[0]}", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_CEREMONY_{ceremony_key}_BUTTON", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_ACTIVE_RITUAL_{code}_{style}", f"确认{name}的{branch_name}仪式。{effect}。"))
        if wonder.get("is_unique"):
            lines.append(loc_line(f"tv_engineering_department.500.d_{key}", unique_completion_text(wonder, "zh")))

    filtered_lines: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("game_concept_"):
            key = stripped.split(":", 1)[0]
            concept_key = key.removeprefix("game_concept_")
            if concept_key.endswith("_desc"):
                concept_key = concept_key[: -len("_desc")]
            if concept_key in manual_concepts:
                continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
