"""Hagia Sophia (unique_hagia_sophia) ritual content.

Ported unchanged from the retired scripts/wonder_unique_rituals/hagia.py and
scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py: the
8-step Justinianic Synaxis actor-assignment chain already matches its
data/unique_wonder_ritual_specs.yaml node_graph with full per-step fidelity, so
this pass only relocates it onto the single scripts/gen_unique_wonder_rituals.py
pipeline instead of rewriting the mechanic.
"""
from wonder_mechanics.render import monthly_country_pulse_event

T = "\t"
WONDER_ID = 102
WONDER_KEY = "unique_hagia_sophia"
NAME_SLUG = "hagia_sophia"
RUNTIME_PREFIX = "tv_wonder_hagia"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_hagia_sophia_cropped.dds"

HAGIA_STEPS = range(1, 9)
HAGIA_STEP_ATTRIBUTE = {
    1: "add_adm",
    2: "add_adm",
    3: "add_dip",
    4: None,
    5: "add_dip",
    6: "add_adm",
    7: "add_mil",
    8: "add_mil",
}
HAGIA_CARD_WIDTH = 462
HAGIA_CARD_HEIGHT = 92

EVENTS = [
    {"id": 6301, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_1_effect = yes", "retry": True},
    {"id": 6302, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_2_effect = yes", "retry": True},
    {"id": 6303, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_3_effect = yes", "retry": True},
    {"id": 6304, "outcome": "positive", "effect": "tv_wonder_hagia_complete_step_4_effect = yes", "retry": False},
    {"id": 6305, "outcome": "positive", "effect": "tv_wonder_hagia_complete_step_5_effect = yes", "retry": False},
    {"id": 6306, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_6_effect = yes", "retry": True},
    {"id": 6307, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_7_effect = yes", "retry": True},
    {"id": 6308, "outcome": "positive", "effect": "tv_wonder_hagia_complete_step_8_effect = yes", "retry": False},
]


def _indent_lines(text: str, level: int) -> list[str]:
    prefix = T * level
    return [f"{prefix}{line}" if line else line for line in text.splitlines()]


def _render_option(event: dict) -> list[str]:
    event_id = event["id"]
    lines = [
        f"{T}option = {{",
        f"{T}{T}name = tv_engineering_department.{event_id}.a",
    ]
    lines.extend(_indent_lines(event["effect"], 2))
    lines.append(f"{T}}}")
    if event.get("retry"):
        lines.extend(
            [
                "",
                f"{T}option = {{",
                f"{T}{T}name = tv_engineering_department.{event_id}.b",
                f"{T}{T}tv_wonder_hagia_retry_step_effect = yes",
                f"{T}}}",
            ]
        )
    return lines


def _render_event(event: dict) -> list[str]:
    event_id = event["id"]
    lines = [
        f"# -- tv_engineering_department.{event_id} ----------------------------------------------",
        f"tv_engineering_department.{event_id} = {{",
        f"{T}type = country_event",
        f"{T}title = tv_engineering_department.{event_id}.t",
        f"{T}desc = tv_engineering_department.{event_id}.d",
        f'{T}image = "{IMAGE}"',
        f"{T}outcome = {event['outcome']}",
        "",
    ]
    lines.extend(_render_option(event))
    lines.append("}")
    return lines


def build_events_body() -> list[str]:
    lines: list[str] = []
    for event in EVENTS:
        lines.extend(_render_event(event))
        lines.append("")
    return lines


def append_hagia_assign_burden_lines(lines: list[str], step: int, indent: int) -> None:
    prefix = T * indent
    attr = HAGIA_STEP_ATTRIBUTE[step]
    if attr is not None:
        lines.append(f"{prefix}{attr} = 10")
    lines.append(f"{prefix}add_character_modifier = {{ modifier = banned_from_cabinet years = -1 mode = add_and_extend }}")
    lines.append(f"{prefix}add_character_modifier = {{ modifier = block_leading_armies_or_navies years = -1 mode = add_and_extend }}")


def append_hagia_assignment_effect(lines: list[str], step: int) -> None:
    lines.append(f"tv_wonder_hagia_assign_step_{step}_effect = {{")
    lines.append(f"{T}if = {{")
    if step == 4:
        lines.append(f"{T}{T}limit = {{ tv_wonder_hagia_step_4_available_trigger = yes has_ruler = yes }}")
        lines.append(f"{T}{T}ruler ?= {{")
        lines.append(f"{T}{T}{T}save_scope_as = tv_wonder_hagia_selected_ruler")
        append_hagia_assign_burden_lines(lines, step, 3)
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_assignee_4 value = scope:tv_wonder_hagia_selected_ruler }}")
        lines.append(f"{T}{T}add_country_modifier = {{ modifier = tv_wonder_hagia_ruler_procession_modifier years = -1 mode = add_and_extend }}")
    else:
        lines.append(f"{T}{T}limit = {{ tv_wonder_hagia_step_{step}_available_trigger = yes exists = scope:target }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_assignee_{step} value = scope:target }}")
        lines.append(f"{T}{T}scope:target = {{")
        append_hagia_assign_burden_lines(lines, step, 3)
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_months value = 0 }}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_hagia_pending_event")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_hagia_effects(lines: list[str]) -> None:
    for step in HAGIA_STEPS:
        append_hagia_assignment_effect(lines, step)

    lines.append("tv_wonder_hagia_retry_step_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_hagia_months value = 0 }}")
    lines.append(f"{T}remove_variable = tv_wonder_hagia_pending_event")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_advance_step_effect = {")
    for step in HAGIA_STEPS:
        head = "if" if step == 1 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_hagia_step ?= {step} }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_step_{step}_done value = 1 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_months value = 0 }}")
        lines.append(f"{T}{T}remove_variable = tv_wonder_hagia_pending_event")
        if step < 8:
            lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_step value = {step + 1} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_1_effect = {")
    lines.append(f"{T}change_gold_effect = {{ scale = -1 }}")
    lines.append(f"{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_2_effect = {")
    lines.append(f"{T}add_prestige = -10")
    lines.append(f"{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_3_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ country_has_estate = estate_type:clergy_estate }}")
    lines.append(f"{T}{T}save_scope_as = tv_wonder_hagia_privilege_country")
    lines.append(f'{T}{T}"estate(estate_type:clergy_estate)" = {{')
    lines.append(f"{T}{T}{T}estate_privilege:tv_hagia_great_church_endowment_privilege = {{")
    lines.append(f"{T}{T}{T}{T}scope:tv_wonder_hagia_privilege_country = {{")
    lines.append(f"{T}{T}{T}{T}{T}grant_estate_privilege = prev")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_hagia_retry_step_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_4_effect = {")
    lines.append(f"{T}remove_country_modifier = tv_wonder_hagia_ruler_procession_modifier")
    lines.append(f"{T}add_country_modifier = {{ modifier = tv_wonder_hagia_imperial_procession_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_5_effect = {")
    lines.append(f"{T}location:constantinople = {{")
    lines.append(f"{T}{T}add_location_modifier = {{ modifier = tv_wonder_hagia_sanctuary_order_location_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_roll_step_6_cost_effect = {")
    lines.append(f"{T}random_list = {{")
    lines.append(f"{T}{T}33 = {{ set_variable = {{ name = tv_wonder_hagia_step_6_cost value = 1 }} }}")
    lines.append(f"{T}{T}33 = {{ set_variable = {{ name = tv_wonder_hagia_step_6_cost value = 2 }} }}")
    lines.append(f"{T}{T}34 = {{ set_variable = {{ name = tv_wonder_hagia_step_6_cost value = 3 }} }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_6_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_hagia_step_6_cost var:tv_wonder_hagia_step_6_cost ?= 1 }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = -1 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_hagia_step_6_cost var:tv_wonder_hagia_step_6_cost ?= 2 }}")
    lines.append(f"{T}{T}add_prestige = -5")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ country_has_estate = estate_type:clergy_estate }}")
    lines.append(f"{T}{T}{T}add_estate_satisfaction = {{ type = estate_type:clergy_estate value = -0.025 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ country_has_estate = estate_type:nobles_estate }}")
    lines.append(f"{T}{T}{T}add_estate_satisfaction = {{ type = estate_type:nobles_estate value = -0.025 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = tv_wonder_hagia_step_6_cost")
    lines.append(f"{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_7_effect = {")
    lines.append(f"{T}change_gold_effect = {{ scale = -1 }}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_hagia_assignee_7 }}")
    lines.append(f"{T}{T}var:tv_wonder_hagia_assignee_7 ?= {{ save_scope_as = tv_wonder_hagia_icon_painter }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}location:constantinople = {{")
    lines.append(f"{T}{T}create_art = {{")
    lines.append(f"{T}{T}{T}quality = {{ 70 100 }}")
    lines.append(f"{T}{T}{T}type = work_of_art_type:icon")
    lines.append(f"{T}{T}{T}key = tv_hagia_sophia_synaxis_icon")
    lines.append(f"{T}{T}{T}target = scope:tv_wonder_hagia_icon_painter")
    lines.append(f"{T}{T}{T}artist = scope:tv_wonder_hagia_icon_painter")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_hagia_advance_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_begin_step_8_procession_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_hagia_prosperity_active value = 1 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_hagia_months value = 0 }}")
    lines.append(f"{T}remove_variable = tv_wonder_hagia_pending_event")
    lines.append(f"{T}location:constantinople = {{")
    lines.append(f"{T}{T}add_location_modifier = {{ modifier = tv_wonder_hagia_public_procession_location_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_complete_step_8_effect = {")
    lines.append(f"{T}location:constantinople = {{")
    lines.append(f"{T}{T}remove_location_modifier = tv_wonder_hagia_public_procession_location_modifier")
    lines.append(f"{T}{T}change_prosperity = 0.1")
    lines.append(f"{T}}}")
    lines.append(f"{T}add_prestige = 10")
    lines.append(f"{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}remove_variable = tv_wonder_hagia_pending_event")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_hagia_step_8_done value = 1 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_hagia_completed value = 1 }}")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_fire_step_event_effect = {")
    for step in HAGIA_STEPS:
        head = "if" if step == 1 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_hagia_step ?= {step} }}")
        if step == 6:
            lines.append(f"{T}{T}tv_wonder_hagia_roll_step_6_cost_effect = yes")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_hagia_pending_event value = {step} }}")
        lines.append(f"{T}{T}{monthly_country_pulse_event(f'tv_engineering_department.{6300 + step}')}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_hagia_monthly_progress_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_hagia_active_trigger = yes }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}has_variable = tv_wonder_hagia_prosperity_active")
    lines.append(f"{T}{T}{T}{T}tv_wonder_hagia_constantinople_prosperous_trigger = yes")
    lines.append(f"{T}{T}{T}{T}NOT = {{ has_variable = tv_wonder_hagia_pending_event }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_hagia_pending_event value = 8 }}")
    lines.append(f"{T}{T}{T}{monthly_country_pulse_event('tv_engineering_department.6308')}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}NOT = {{ has_variable = tv_wonder_hagia_prosperity_active }}")
    lines.append(f"{T}{T}{T}{T}NOT = {{ has_variable = tv_wonder_hagia_pending_event }}")
    lines.append(f"{T}{T}{T}{T}OR = {{")
    for step in HAGIA_STEPS:
        lines.append(f"{T}{T}{T}{T}{T}AND = {{ var:tv_wonder_hagia_step ?= {step} has_variable = tv_wonder_hagia_assignee_{step} }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_hagia_months }} }}")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = tv_wonder_hagia_months value = 0 }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = tv_wonder_hagia_months add = 1 }}")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ var:tv_wonder_hagia_months >= 3 }}")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = tv_wonder_hagia_months value = 0 }}")
    lines.append(f"{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ var:tv_wonder_hagia_step ?= 8 }}")
    lines.append(f"{T}{T}{T}{T}{T}tv_wonder_hagia_begin_step_8_procession_effect = yes")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}else = {{")
    lines.append(f"{T}{T}{T}{T}{T}tv_wonder_hagia_fire_step_event_effect = yes")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_hagia_triggers(lines: list[str]) -> None:
    lines.append("tv_wonder_hagia_active_trigger = {")
    lines.append(f"{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}var:tv_wonder_locked ?= {WONDER_ID}")
    lines.append(f"{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append(f"{T}has_variable = tv_wonder_hagia_step")
    lines.append(f"{T}NOT = {{ has_variable = tv_wonder_hagia_completed }}")
    lines.append("}")
    lines.append("")

    for step in HAGIA_STEPS:
        lines.append(f"tv_wonder_hagia_step_{step}_current_trigger = {{")
        lines.append(f"{T}tv_wonder_hagia_active_trigger = yes")
        lines.append(f"{T}var:tv_wonder_hagia_step ?= {step}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_hagia_step_{step}_done_trigger = {{")
        lines.append(f"{T}has_variable = tv_wonder_hagia_step_{step}_done")
        lines.append(f"{T}var:tv_wonder_hagia_step_{step}_done ?= 1")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_hagia_step_{step}_visible_trigger = {{")
        lines.append(f"{T}OR = {{")
        lines.append(f"{T}{T}tv_wonder_hagia_step_{step}_current_trigger = yes")
        lines.append(f"{T}{T}tv_wonder_hagia_step_{step}_done_trigger = yes")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_hagia_step_{step}_assigned_trigger = {{")
        lines.append(f"{T}has_variable = tv_wonder_hagia_assignee_{step}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_hagia_step_{step}_available_trigger = {{")
        lines.append(f"{T}tv_wonder_hagia_step_{step}_current_trigger = yes")
        lines.append(f"{T}NOT = {{ has_variable = tv_wonder_hagia_assignee_{step} }}")
        lines.append(f"{T}NOT = {{ has_variable = tv_wonder_hagia_pending_event }}")
        if step == 4:
            lines.append(f"{T}has_ruler = yes")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_hagia_constantinople_prosperous_trigger = {")
    lines.append(f"{T}location:constantinople = {{ prosperity >= 1 }}")
    lines.append("}")
    lines.append("")


def append_effects(lines: list[str]) -> None:
    append_hagia_effects(lines)


def append_triggers(lines: list[str]) -> None:
    append_hagia_triggers(lines)


def hagia_locked_expr() -> str:
    return (
        f"And({player_var('tv_wonder_locked')}.IsSet, "
        f"{eq('tv_wonder_locked', WONDER_ID)})"
    )


def hagia_step_visible(step: int) -> str:
    return fold_bool(
        "And",
        [
            active_ritual_visible(),
            hagia_locked_expr(),
            f"Or3({var_is_set(f'tv_wonder_hagia_assignee_{step}')}, {var_is_set(f'tv_wonder_hagia_step_{step}_done')}, {hagia_step_current_visible(step)})",
        ],
    )


def hagia_step_done_visible(step: int) -> str:
    return var_is_set(f"tv_wonder_hagia_step_{step}_done")


def hagia_step_current_visible(step: int) -> str:
    return f"And({var_is_set('tv_wonder_hagia_step')}, {eq('tv_wonder_hagia_step', step)})"


def hagia_step_assigned_visible(step: int) -> str:
    return var_is_set(f"tv_wonder_hagia_assignee_{step}")


def hagia_step_waiting_visible(step: int) -> str:
    return fold_bool(
        "And",
        [
            hagia_step_current_visible(step),
            f"Not({hagia_step_assigned_visible(step)})",
            f"Not({hagia_step_done_visible(step)})",
        ],
    )


def hagia_step_active_visible(step: int) -> str:
    return fold_bool(
        "And",
        [
            hagia_step_current_visible(step),
            hagia_step_assigned_visible(step),
            f"Not({hagia_step_done_visible(step)})",
        ],
    )


def hagia_step_portrait(step: int, indent: int) -> list[str]:
    prefix = T * indent
    assignee_var = f"tv_wonder_hagia_assignee_{step}"
    return [
        f"{prefix}widget = {{",
        f"{prefix}{T}size = {{ 64 64 }}",
        f"{prefix}{T}portrait_standard_head_button = {{",
        f'{prefix}{T}{T}visible = "[{var_is_set(assignee_var)}]"',
        f"{prefix}{T}{T}size = {{ 64 64 }}",
        f'{prefix}{T}{T}datacontext = "[{PLAYER}.GetVariable(\'{assignee_var}\').GetCharacter]"',
        f"{prefix}{T}}}",
        f"{prefix}{T}action_button_diamond = {{",
        f'{prefix}{T}{T}visible = "[{hagia_step_waiting_visible(step)}]"',
        f"{prefix}{T}{T}size = {{ 64 64 }}",
        f'{prefix}{T}{T}raw_text = "@characters!"',
        f'{prefix}{T}{T}title = "TV_ENGINEERING_HAGIA_ASSIGN_STEP_{step}"',
        f'{prefix}{T}{T}description = "TV_ENGINEERING_HAGIA_ASSIGN_STEP_{step}_DESC"',
        f'{prefix}{T}{T}actor = "[InternationalOrganizationsView.GetPlayer]"',
        f'{prefix}{T}{T}left_action = {{ action_name = "tv_wonder_hagia_assign_step_{step}" }}',
        f"{prefix}{T}}}",
        f"{prefix}{T}widget = {{",
        f'{prefix}{T}{T}visible = "[Not(Or({var_is_set(assignee_var)}, {hagia_step_waiting_visible(step)}))]"',
        f"{prefix}{T}{T}size = {{ 64 64 }}",
        f"{prefix}{T}{T}alwaystransparent = yes",
        f"{prefix}{T}{T}background = {{",
        f"{prefix}{T}{T}{T}using = color_yellow_texture",
        f"{prefix}{T}{T}{T}alpha = 0.14",
        f"{prefix}{T}{T}}}",
        f'{prefix}{T}{T}text_single = {{ raw_text = "@time!" size = {{ 64 64 }} fontsize = 24 align = center|nobaseline }}',
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def hagia_step_card(step: int, indent: int) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{hagia_step_visible(step)}]"',
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {HAGIA_CARD_WIDTH} {HAGIA_CARD_HEIGHT} }}",
        f"{prefix}{T}using = bg_text_mask_container_dark_blue",
        f"{prefix}{T}widget = {{",
        f'{prefix}{T}{T}visible = "[{hagia_step_done_visible(step)}]"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}alwaystransparent = yes",
        f"{prefix}{T}{T}background = {{",
        f"{prefix}{T}{T}{T}using = color_market_green_texture",
        f"{prefix}{T}{T}{T}alpha = 0.22",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}}}",
        f"{prefix}{T}hbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}margin = {{ 8 8 }}",
        f"{prefix}{T}{T}spacing = 12",
    ]
    lines.extend(hagia_step_portrait(step, indent + 2))
    lines.extend(
        [
            f"{prefix}{T}{T}widget = {{",
            f"{prefix}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{prefix}{T}{T}{T}layoutpolicy_vertical = shrinking",
            f"{prefix}{T}{T}{T}vbox = {{",
            f"{prefix}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{prefix}{T}{T}{T}{T}spacing = 2",
            f"{prefix}{T}{T}{T}{T}ignoreinvisible = yes",
            f'{prefix}{T}{T}{T}{T}text_multi = {{ visible = "[{hagia_step_waiting_visible(step)}]" max_width = 370 autoresize = yes text = "TV_ENGINEERING_HAGIA_STEP_{step}_WAITING" align = nobaseline|left }}',
            f'{prefix}{T}{T}{T}{T}text_multi = {{ visible = "[{hagia_step_active_visible(step)}]" max_width = 370 autoresize = yes text = "TV_ENGINEERING_HAGIA_STEP_{step}_ACTIVE" align = nobaseline|left }}',
            f'{prefix}{T}{T}{T}{T}text_multi = {{ visible = "[{hagia_step_done_visible(step)}]" max_width = 370 autoresize = yes text = "TV_ENGINEERING_HAGIA_STEP_{step}_DONE" align = nobaseline|left }}',
            f"{prefix}{T}{T}{T}}}",
            f"{prefix}{T}{T}}}",
            f"{prefix}{T}}}",
            f"{prefix}}}",
        ]
    )
    return lines


def hagia_ritual_cards(indent: int) -> list[str]:
    lines: list[str] = []
    for step in range(1, 9):
        lines.extend(hagia_step_card(step, indent))
    return lines


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    globals().update(helpers)
    lines.extend(hagia_ritual_cards(indent))
