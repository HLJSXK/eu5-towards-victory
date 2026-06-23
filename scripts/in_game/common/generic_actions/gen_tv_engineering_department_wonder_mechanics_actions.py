import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.io import load_all_wonder_mechanics_data
from wonder_mechanics.render import render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "generic_actions" / "tv_engineering_department_wonder_mechanics_actions.txt"
SCRIPT_REL = "scripts/in_game/common/generic_actions/gen_tv_engineering_department_wonder_mechanics_actions.py"
T = "\t"
HAGIA_WONDER_ID = 102
HAGIA_ACTIONS = [
    (1, "tv_wonder_hagia_assign_step_1", "tv_wonder_hagia_select_character", "tv_wonder_hagia_no_character_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_1", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_1_DESC"),
    (2, "tv_wonder_hagia_assign_step_2", "tv_wonder_hagia_select_character", "tv_wonder_hagia_no_character_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_2", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_2_DESC"),
    (3, "tv_wonder_hagia_assign_step_3", "tv_wonder_hagia_select_character", "tv_wonder_hagia_no_character_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_3", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_3_DESC"),
    (4, "tv_wonder_hagia_assign_step_4", None, None, None, "TV_ENGINEERING_HAGIA_ASSIGN_STEP_4", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_4_DESC"),
    (5, "tv_wonder_hagia_assign_step_5", "tv_wonder_hagia_select_character", "tv_wonder_hagia_no_character_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_5", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_5_DESC"),
    (6, "tv_wonder_hagia_assign_step_6", "tv_wonder_hagia_select_character", "tv_wonder_hagia_no_character_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_6", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_6_DESC"),
    (7, "tv_wonder_hagia_assign_step_7", "tv_wonder_hagia_select_noble", "tv_wonder_hagia_no_noble_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_7", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_7_DESC"),
    (8, "tv_wonder_hagia_assign_step_8", "tv_wonder_hagia_select_character", "tv_wonder_hagia_no_character_available", "character_info", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_8", "TV_ENGINEERING_HAGIA_ASSIGN_STEP_8_DESC"),
]


def confirm_action_block(action_name: str, trigger_name: str, effect_name: str, price: str | None = None) -> list[str]:
    lines = [
        f"{action_name} = {{",
        f"{T}type = owncountry",
        f"{T}sound = UI_action_religion_generic",
        f"{T}ai_tick = monthly",
        f"{T}ai_tick_frequency = 99999",
        f"{T}potential = {{ scope:actor = {{ has_variable = tv_engineering_department_member }} }}",
        f"{T}allow = {{ scope:actor = {{ {trigger_name} = yes }} }}",
    ]
    if price is not None:
        lines.append(f"{T}price = price:{price}")
    lines.extend(
        [
            f"{T}effect = {{ scope:actor = {{ {effect_name} = yes }} }}",
            f"{T}ai_will_do = {{ add = -100 }}",
            "}",
            "",
        ]
    )
    return lines


def hagia_action_block(step: int, action_name: str, trigger_name: str | None, none_available_key: str | None, column_data: str | None, title_key: str, desc_key: str) -> list[str]:
    del title_key, desc_key
    lines = [
        f"{action_name} = {{",
        f"{T}type = owncountry",
        f"{T}sound = UI_action_religion_generic",
        f"{T}ai_tick = monthly",
        f"{T}ai_tick_frequency = 99999",
        f"{T}potential = {{ scope:actor = {{ has_variable = tv_engineering_department_member }} }}",
        f"{T}allow = {{ scope:actor = {{ has_variable = tv_wonder_locked var:tv_wonder_locked ?= {HAGIA_WONDER_ID} tv_wonder_hagia_step_{step}_available_trigger = yes }} }}",
    ]
    if trigger_name is not None:
        lines.append(
            f"{T}select_trigger = {{"
        )
        lines.append(f"{T}{T}looking_for_a = character")
        lines.append(f"{T}{T}source = actor")
        lines.append(f"{T}{T}target_flag = target")
        lines.append(f"{T}{T}name = \"{trigger_name}\"")
        if none_available_key is not None:
            lines.append(f"{T}{T}none_available_msg_key = \"{none_available_key}\"")
        if column_data is not None:
            lines.append(f"{T}{T}column = {{ data = {column_data} }}")
        lines.append(f"{T}{T}visible = {{")
        lines.append(f"{T}{T}{T}is_alive = yes")
        lines.append(f"{T}{T}{T}is_adult = yes")
        lines.append(f"{T}{T}{T}is_ruler = no")
        if step == 7:
            lines.append(f"{T}{T}{T}has_estate = estate_type:nobles_estate")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
    if trigger_name is None:
        lines.append(f"{T}effect = {{ scope:actor = {{ tv_wonder_hagia_assign_step_{step}_effect = yes }} }}")
    else:
        lines.extend(
            [
                f"{T}effect = {{",
                f"{T}{T}if = {{",
                f"{T}{T}{T}limit = {{ exists = scope:target }}",
                f"{T}{T}{T}scope:actor = {{ tv_wonder_hagia_assign_step_{step}_effect = yes }}",
                f"{T}{T}}}",
                f"{T}}}",
            ]
        )
    lines.extend(
        [
            f"{T}ai_will_do = {{ add = -100 }}",
            "}",
            "",
        ]
    )
    return lines


def generate() -> str:
    load_all_wonder_mechanics_data()
    lines = render_header(SCRIPT_REL)
    lines.extend(confirm_action_block("tv_wonder_confirm_ceremony", "tv_wonder_ceremony_ready_for_free_confirmation_trigger", "tv_wonder_confirm_ceremony_effect"))
    lines.extend(
        confirm_action_block(
            "tv_wonder_confirm_ceremony_scaled_gold",
            "tv_wonder_ceremony_ready_for_scaled_gold_confirmation_trigger",
            "tv_wonder_confirm_ceremony_effect",
            "tv_wonder_ritual_style_3_scaled_gold_price",
        )
    )
    lines.extend(
        confirm_action_block(
            "tv_wonder_confirm_ceremony_prestige",
            "tv_wonder_ceremony_ready_for_prestige_confirmation_trigger",
            "tv_wonder_confirm_ceremony_effect",
            "tv_wonder_ritual_style_3_prestige_price",
        )
    )
    for step, action_name, trigger_name, none_available_key, column_data, title_key, desc_key in HAGIA_ACTIONS:
        lines.extend(hagia_action_block(step, action_name, trigger_name, none_available_key, column_data, title_key, desc_key))
    return "\n".join(lines)


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
