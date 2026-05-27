import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_expansion_lib import final_building_for_style, load_wonder_data, loc_line, render_header

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_wonder_expansion_l_simp_chinese.yml"
SCRIPT_REL = "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_expansion_l_simp_chinese.py"
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
    lines = ["l_simp_chinese:"]
    for line in render_header(SCRIPT_REL):
        lines.append(f" {line}")

    lines.append(loc_line("tv_wonder_confirm_new_ceremony", "确认仪式"))
    lines.append(loc_line("tv_wonder_confirm_new_ceremony_desc", "确认已选择的仪式分支，并让完工的奇观正式落成。"))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_new_ceremony_ACTION_SETUP", "当我们确认一种新设计奇观的落成仪式时。"))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_new_ceremony_ACTION_LOG", "我们确认了奇观落成仪式。"))
    lines.append(loc_line("PERFORM_tv_wonder_confirm_new_ceremony_ACTION_MAP", ""))

    for wonder in wonders:
        key = wonder["key"]
        design = expansion["designs"][key]
        name = wonder["loc"]["zh"]
        concept = wonder["concept"]
        size_concept = SIZE_CONCEPT[wonder["size"]]
        branch_list = [design["branches"][style] for style in range(1, 4)]
        branch_names = "、".join(branch["zh"] for branch in branch_list)
        code = display_key(key)

        lines.append(loc_line(f"game_concept_{concept}", name))
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

        for style, branch in ((style, design["branches"][style]) for style in range(1, 4)):
            building = final_building_for_style(wonder, style)
            branch_name = branch["zh"]
            effect = branch_effect_text(branch)
            ceremony_key = building.removeprefix("tv_wonder_").upper()
            lines.append(loc_line(building, branch_name))
            lines.append(loc_line(f"{building}_desc", f"{name}的{branch_name}仪式分支。"))
            lines.append(loc_line(f"STATIC_MODIFIER_NAME_{building}_modifier", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_CEREMONY_{ceremony_key}_BUTTON", branch_name))
            lines.append(loc_line(f"TV_ENGINEERING_ACTIVE_RITUAL_{code}_{style}", f"确认{name}的{branch_name}仪式。{effect}。"))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
