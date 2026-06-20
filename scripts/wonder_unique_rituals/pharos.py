T = "\t"
PHAROS_WONDER_ID = 101
PHAROS_ROUTE_KEYS = [
    "constantinople",
    "venice",
    "genoa",
    "malta",
    "tunis",
    "palermo",
    "candia",
    "gibraltar",
]
PHAROS_ROUTE_IDS = {route_key: index for index, route_key in enumerate(PHAROS_ROUTE_KEYS, start=1)}
PHAROS_ROUTE_COUNT = len(PHAROS_ROUTE_KEYS)
PHAROS_CARD_WIDTH = 462
PHAROS_ROW_HEIGHT = 28
PHAROS_ROUTE_CARD_HEIGHT = 386
PHAROS_PHASE_CARD_HEIGHT = 126


def append_pharos_set_route_projection_lines(lines: list[str], route_key: str, indent: int) -> None:
    prefix = T * indent
    route_id = PHAROS_ROUTE_IDS[route_key]
    location_var = f"tv_wonder_pharos_route_{route_key}_location"
    status_var = f"tv_wonder_pharos_route_{route_key}_status"
    owner_var = f"tv_wonder_pharos_route_{route_key}_owner"
    lines.append(f"{prefix}remove_variable = {location_var}")
    lines.append(f"{prefix}remove_variable = {owner_var}")
    lines.append(f"{prefix}location:{route_key} = {{")
    lines.append(f"{prefix}{T}save_scope_as = tv_wonder_pharos_projection_location")
    lines.append(
        f"{prefix}{T}root = {{ set_variable = {{ name = {location_var} value = scope:tv_wonder_pharos_projection_location }} }}"
    )
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ has_owner = yes }}")
    lines.append(f"{prefix}{T}{T}owner = {{")
    lines.append(f"{prefix}{T}{T}{T}save_scope_as = tv_wonder_pharos_projection_owner")
    lines.append(
        f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = {owner_var} value = scope:tv_wonder_pharos_projection_owner }} }}"
    )
    lines.append(f"{prefix}{T}{T}}}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{ tv_wonder_pharos_route_{route_key}_controlled_trigger = yes }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = {status_var} value = 1 }}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}else_if = {{")
    lines.append(f"{prefix}{T}limit = {{ tv_wonder_pharos_route_{route_key}_basing_trigger = yes }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = {status_var} value = 2 }}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}else = {{")
    lines.append(f"{prefix}{T}set_variable = {{ name = {status_var} value = 0 }}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{")
    lines.append(f"{prefix}{T}{T}has_variable = tv_wonder_pharos_active_route")
    lines.append(f"{prefix}{T}{T}var:tv_wonder_pharos_active_route ?= {route_id}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route_id value = {route_id} }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route_status value = var:{status_var} }}")
    lines.append(f"{prefix}{T}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ has_variable = {owner_var} }}")
    lines.append(f"{prefix}{T}{T}set_variable = {{ name = tv_wonder_pharos_active_route_owner value = var:{owner_var} }}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def append_pharos_select_route_lines(lines: list[str], route_key: str, indent: int) -> None:
    prefix = T * indent
    route_id = PHAROS_ROUTE_IDS[route_key]
    lines.append(f"{prefix}set_variable = {{ name = tv_wonder_pharos_active_route value = {route_id} }}")
    lines.append(f"{prefix}set_variable = {{ name = tv_wonder_pharos_active_route_id value = {route_id} }}")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_event_route_location")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_event_route_owner")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_event_route_has_owner")
    lines.append(f"{prefix}location:{route_key} = {{")
    lines.append(f"{prefix}{T}save_scope_as = tv_wonder_pharos_selected_route_location")
    lines.append(
        f"{prefix}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_event_route_location value = scope:tv_wonder_pharos_selected_route_location }} }}"
    )
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ has_owner = yes }}")
    lines.append(f"{prefix}{T}{T}owner = {{")
    lines.append(f"{prefix}{T}{T}{T}save_scope_as = tv_wonder_pharos_selected_route_owner")
    lines.append(
        f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_event_route_owner value = scope:tv_wonder_pharos_selected_route_owner }} }}"
    )
    lines.append(f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_event_route_has_owner value = 1 }} }}")
    lines.append(
        f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_active_route_owner value = scope:tv_wonder_pharos_selected_route_owner }} }}"
    )
    lines.append(f"{prefix}{T}{T}}}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def append_pharos_selected_route_completion_lines(lines: list[str], route_key: str, indent: int) -> None:
    prefix = T * indent
    route_id = PHAROS_ROUTE_IDS[route_key]
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{")
    lines.append(f"{prefix}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
    lines.append(f"{prefix}{T}{T}tv_wonder_pharos_route_{route_key}_pending_trigger = yes")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_route_{route_key}_passed value = 1 }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route value = {route_id} }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route_id value = {route_id} }}")
    lines.append(f"{prefix}{T}change_variable = {{ name = tv_wonder_pharos_route_progress add = 1 }}")
    lines.append(f"{prefix}}}")


def append_pharos_effects(lines: list[str]) -> None:
    lines.append("tv_wonder_pharos_refresh_threat_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_privateer_threat_pct value = 0 }}")
    for count, pct in ((4, 100), (3, 75), (2, 50), (1, 25)):
        head = "if" if count == 4 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ tv_wonder_pharos_alexandria_hostile_privateers_at_least_{count}_trigger = yes }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_pharos_privateer_threat_pct value = {pct} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_refresh_route_progress_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_route_progress value = 0 }}")
    for route_key in PHAROS_ROUTE_KEYS:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_pharos_route_{route_key}_passed }}")
        lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_pharos_route_progress add = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}clamp_variable = {{ name = tv_wonder_pharos_route_progress min = 0 max = {len(PHAROS_ROUTE_KEYS)} }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_refresh_display_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= 101")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_pharos_refresh_threat_effect = yes")
    lines.append(f"{T}{T}tv_wonder_pharos_refresh_route_progress_effect = yes")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_id")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_owner")
    for route_key in PHAROS_ROUTE_KEYS:
        append_pharos_set_route_projection_lines(lines, route_key, 2)
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_clear_privateers_effect = {")
    lines.append(f"{T}location:alexandria = {{")
    lines.append(f"{T}{T}sea_zone = {{")
    lines.append(f"{T}{T}{T}area = {{")
    lines.append(f"{T}{T}{T}{T}every_privateer_in_area = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ NOT = {{ owner = root }} }}")
    lines.append(f"{T}{T}{T}{T}{T}change_privateer_power = -0.4")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_enter_stage_2_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_stage value = 2 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_quarter_month value = 0 }}")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route_id")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_event_route_location")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_event_route_owner")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_event_route_has_owner")
    lines.append(f"{T}add_prestige = 5")
    lines.append(f"{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_complete_selected_controlled_route_effect = {")
    for route_key in PHAROS_ROUTE_KEYS:
        append_pharos_selected_route_completion_lines(lines, route_key, 1)
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_active_route_status value = 1 }}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append(f"{T}tv_wonder_pharos_maybe_finish_routes_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_complete_selected_basing_route_effect = {")
    for route_key in PHAROS_ROUTE_KEYS:
        append_pharos_selected_route_completion_lines(lines, route_key, 1)
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_active_route_status value = 2 }}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append(f"{T}tv_wonder_pharos_maybe_finish_routes_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_create_selected_route_basing_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ exists = scope:tv_wonder_pharos_event_route_owner }}")
    lines.append(f"{T}{T}create_relation = {{")
    lines.append(f"{T}{T}{T}first = root")
    lines.append(f"{T}{T}{T}second = scope:tv_wonder_pharos_event_route_owner")
    lines.append(f"{T}{T}{T}type = relation_type:fleet_basing_rights")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}create_relation = {{")
    lines.append(f"{T}{T}{T}first = scope:tv_wonder_pharos_event_route_owner")
    lines.append(f"{T}{T}{T}second = root")
    lines.append(f"{T}{T}{T}type = relation_type:fleet_basing_rights")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_pharos_active_route_owner value = scope:tv_wonder_pharos_event_route_owner }}")
    lines.append(f"{T}{T}tv_wonder_pharos_complete_selected_basing_route_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_evaluate_selected_route_effect = {")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    first = True
    for route_key in PHAROS_ROUTE_KEYS:
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_{route_key}_controlled_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7305 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_{route_key}_basing_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7306 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_{route_key}_has_owner_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7307 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_roll_route_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_pharos_has_pending_route_trigger = yes }}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_id")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{T}{T}random_list = {{")
    for route_key in PHAROS_ROUTE_KEYS:
        lines.append(f"{T}{T}{T}10 = {{")
        lines.append(f"{T}{T}{T}{T}trigger = {{ tv_wonder_pharos_route_{route_key}_pending_trigger = yes }}")
        append_pharos_select_route_lines(lines, route_key, 4)
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_pharos_evaluate_selected_route_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_pharos_maybe_finish_routes_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_maybe_finish_routes_effect = {")
    lines.append(f"{T}tv_wonder_pharos_refresh_route_progress_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_pharos_route_progress")
    lines.append(f"{T}{T}{T}var:tv_wonder_pharos_route_progress >= {len(PHAROS_ROUTE_KEYS)}")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = tv_wonder_pharos_routes_complete_pending_event }}")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = tv_wonder_pharos_routes_complete }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_pharos_routes_complete_pending_event value = 1 }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7308 }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_finish_ritual_effect = {")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_routes_complete_pending_event")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_routes_complete value = 1 }}")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")
    lines.append("")

def append_pharos_triggers(lines: list[str]) -> None:
    lines.append("tv_wonder_pharos_alexandria_hostile_privateers_trigger = {")
    lines.append(f"{T}location:alexandria = {{")
    lines.append(f"{T}{T}sea_zone = {{")
    lines.append(f"{T}{T}{T}area = {{")
    lines.append(f"{T}{T}{T}{T}any_privateer_in_area = {{")
    lines.append(f"{T}{T}{T}{T}{T}NOT = {{ owner = root }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    for count in range(1, 5):
        lines.append(f"tv_wonder_pharos_alexandria_hostile_privateers_at_least_{count}_trigger = {{")
        lines.append(f"{T}location:alexandria = {{")
        lines.append(f"{T}{T}sea_zone = {{")
        lines.append(f"{T}{T}{T}area = {{")
        lines.append(f"{T}{T}{T}{T}any_privateer_in_area = {{")
        lines.append(f"{T}{T}{T}{T}{T}count >= {count}")
        lines.append(f"{T}{T}{T}{T}{T}NOT = {{ owner = root }}")
        lines.append(f"{T}{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

    for route_key in PHAROS_ROUTE_KEYS:
        route_id = PHAROS_ROUTE_KEYS.index(route_key) + 1
        lines.append(f"tv_wonder_pharos_route_{route_key}_controlled_trigger = {{")
        lines.append(f"{T}owns = location:{route_key}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_pharos_route_{route_key}_has_owner_trigger = {{")
        lines.append(f"{T}location:{route_key} = {{ has_owner = yes }}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_pharos_route_{route_key}_basing_trigger = {{")
        lines.append(f"{T}location:{route_key} = {{")
        lines.append(f"{T}{T}has_owner = yes")
        lines.append(f"{T}{T}owner = {{")
        lines.append(f"{T}{T}{T}gives_fleet_basing_rights_to = root")
        lines.append(f"{T}{T}{T}receives_fleet_basing_rights_from = root")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_pharos_route_{route_key}_pending_trigger = {{")
        lines.append(f"{T}NOT = {{ has_variable = tv_wonder_pharos_route_{route_key}_passed }}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_wonder_pharos_route_selected_{route_key}_trigger = {{")
        lines.append(f"{T}has_variable = tv_wonder_pharos_active_route")
        lines.append(f"{T}var:tv_wonder_pharos_active_route ?= {route_id}")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_pharos_has_pending_route_trigger = {")
    lines.append(f"{T}OR = {{")
    for route_key in PHAROS_ROUTE_KEYS:
        lines.append(f"{T}{T}tv_wonder_pharos_route_{route_key}_pending_trigger = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_effects(lines: list[str]) -> None:
    append_pharos_effects(lines)


def append_triggers(lines: list[str]) -> None:
    append_pharos_triggers(lines)


def pharos_locked_expr() -> str:
    return (
        f"And({player_var('tv_wonder_locked')}.IsSet, "
        f"{eq('tv_wonder_locked', PHAROS_WONDER_ID)})"
    )


def pharos_stage_visible(stage: int) -> str:
    return fold_bool(
        "And",
        [
            active_ritual_visible(),
            pharos_locked_expr(),
            var_is_set("tv_wonder_pharos_stage"),
            eq("tv_wonder_pharos_stage", stage),
        ],
    )


def pharos_status_visible(route_key: str, status: int) -> str:
    status_var = f"tv_wonder_pharos_route_{route_key}_status"
    return f"And({var_is_set(status_var)}, {eq(status_var, status)})"


def pharos_route_success_visible(route_key: str) -> str:
    return f"Or({pharos_status_visible(route_key, 1)}, {pharos_status_visible(route_key, 2)})"


def pharos_route_uncontrolled_visible(route_key: str) -> str:
    status_var = f"tv_wonder_pharos_route_{route_key}_status"
    return f"Or(Not({var_is_set(status_var)}), {eq(status_var, 0)})"


def pharos_piechart(
    indent: int,
    *,
    value_var: str,
    max_value: int,
    icon_text: str,
    fill_color: str,
) -> list[str]:
    prefix = T * indent
    value_expr = player_var(value_var)
    return [
        f"{prefix}widget = {{",
        f"{prefix}{T}size = {{ 98 98 }}",
        f"{prefix}{T}piechart = {{",
        f"{prefix}{T}{T}size = {{ 88 88 }}",
        f"{prefix}{T}{T}parentanchor = center",
        f"{prefix}{T}{T}widgetanchor = center",
        f"{prefix}{T}{T}using = piechart_angles",
        f"{prefix}{T}{T}pieslice = {{ texture = \"gfx/interface/pie_charts/pie_chart_alpha_80.dds\" value = \"[{value_expr}.GetValue]\" color = {{ {fill_color} }} alpha = 0.82 }}",
        f"{prefix}{T}{T}pieslice = {{ texture = \"gfx/interface/pie_charts/pie_chart_alpha_80.dds\" value = \"[Subtract_CFixedPoint('(CFixedPoint){max_value}.0', {value_expr}.GetValue)]\" color = {{ 0.06 0.08 0.10 0.78 }} }}",
        f"{prefix}{T}{T}using = bg_circle_piechart_big",
        f"{prefix}{T}}}",
        f"{prefix}{T}text_single = {{",
        f"{prefix}{T}{T}size = {{ 88 88 }}",
        f"{prefix}{T}{T}parentanchor = center",
        f"{prefix}{T}{T}widgetanchor = center",
        f'{prefix}{T}{T}raw_text = "{icon_text}"',
        f"{prefix}{T}{T}fontsize = 32",
        f"{prefix}{T}{T}align = center|nobaseline",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def pharos_stage_1_card(indent: int) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{pharos_stage_visible(1)}]"',
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}size = {{ {PHAROS_CARD_WIDTH} {PHAROS_PHASE_CARD_HEIGHT} }}",
        f"{prefix}{T}using = bg_text_mask_container_dark_blue",
        "",
        f"{prefix}{T}hbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}margin = {{ 8 8 }}",
        f"{prefix}{T}{T}spacing = 12",
    ]
    lines.extend(
        pharos_piechart(
            indent + 2,
            value_var="tv_wonder_pharos_privateer_threat_pct",
            max_value=100,
            icon_text="@ship!",
            fill_color="0.78 0.18 0.12 1",
        )
    )
    lines.extend(
        [
            f"{prefix}{T}{T}text_multi = {{",
            f"{prefix}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{prefix}{T}{T}{T}max_width = 328",
            f"{prefix}{T}{T}{T}autoresize = yes",
            f'{prefix}{T}{T}{T}text = "TV_ENGINEERING_PHAROS_STAGE_1_TEXT"',
            f"{prefix}{T}{T}{T}align = nobaseline|left",
            f"{prefix}{T}{T}}}",
            f"{prefix}{T}}}",
            f"{prefix}}}",
        ]
    )
    return lines


def pharos_route_row(route_key: str, indent: int) -> list[str]:
    prefix = T * indent
    location_var = player_var(f"tv_wonder_pharos_route_{route_key}_location")
    owner_var = player_var(f"tv_wonder_pharos_route_{route_key}_owner")
    success_visible = pharos_route_success_visible(route_key)
    uncontrolled_visible = pharos_route_uncontrolled_visible(route_key)
    return [
        f"{prefix}widget = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {PHAROS_CARD_WIDTH - 16} {PHAROS_ROW_HEIGHT} }}",
        f"{prefix}{T}alwaystransparent = yes",
        f"{prefix}{T}background = {{",
        f"{prefix}{T}{T}using = color_mid_red_texture",
        f"{prefix}{T}{T}alpha = 0.22",
        f"{prefix}{T}}}",
        f"{prefix}{T}widget = {{",
        f'{prefix}{T}{T}visible = "[{success_visible}]"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}alwaystransparent = yes",
        f"{prefix}{T}{T}background = {{",
        f"{prefix}{T}{T}{T}using = color_market_green_texture",
        f"{prefix}{T}{T}{T}alpha = 0.24",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}}}",
        f"{prefix}{T}hbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}margin = {{ 6 3 }}",
        f"{prefix}{T}{T}spacing = 4",
        f'{prefix}{T}{T}text_single = {{ size = {{ 18 22 }} raw_text = "@location!" fontsize = 14 align = nobaseline|left }}',
        f"{prefix}{T}{T}text_single = {{",
        f'{prefix}{T}{T}{T}visible = "[{location_var}.IsSet]"',
        f"{prefix}{T}{T}{T}size = {{ 126 22 }}",
        f'{prefix}{T}{T}{T}text = "[{location_var}.GetLocation.GetName]"',
        f"{prefix}{T}{T}{T}max_width = 126",
        f"{prefix}{T}{T}{T}fontsize = 13",
        f"{prefix}{T}{T}{T}align = nobaseline|left",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}{T}expand = {{}}",
        f"{prefix}{T}{T}text_single = {{",
        f'{prefix}{T}{T}{T}visible = "[{owner_var}.IsSet]"',
        f"{prefix}{T}{T}{T}size = {{ 162 22 }}",
        f'{prefix}{T}{T}{T}raw_text = "[{owner_var}.GetCountry.GetNameWithFlag]"',
        f"{prefix}{T}{T}{T}max_width = 162",
        f"{prefix}{T}{T}{T}fontsize = 13",
        f"{prefix}{T}{T}{T}align = nobaseline|right",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}{T}text_single = {{",
        f'{prefix}{T}{T}{T}visible = "[Not({owner_var}.IsSet)]"',
        f"{prefix}{T}{T}{T}size = {{ 162 22 }}",
        f'{prefix}{T}{T}{T}text = "TV_ENGINEERING_PHAROS_NO_OWNER"',
        f"{prefix}{T}{T}{T}max_width = 162",
        f"{prefix}{T}{T}{T}fontsize = 13",
        f"{prefix}{T}{T}{T}align = nobaseline|right",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}{T}text_single = {{ visible = \"[{pharos_status_visible(route_key, 1)}]\" size = {{ 58 22 }} text = \"TV_ENGINEERING_PHAROS_STATUS_CONTROLLED\" fontsize = 13 align = nobaseline|right }}",
        f"{prefix}{T}{T}text_single = {{ visible = \"[{pharos_status_visible(route_key, 2)}]\" size = {{ 58 22 }} text = \"TV_ENGINEERING_PHAROS_STATUS_BASING\" fontsize = 13 align = nobaseline|right }}",
        f"{prefix}{T}{T}text_single = {{ visible = \"[{uncontrolled_visible}]\" size = {{ 58 22 }} text = \"TV_ENGINEERING_PHAROS_STATUS_UNCONTROLLED\" fontsize = 13 align = nobaseline|right }}",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def pharos_stage_2_card(indent: int) -> list[str]:
    prefix = T * indent
    progress_var = player_var("tv_wonder_pharos_route_progress")
    lines = [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{pharos_stage_visible(2)}]"',
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}size = {{ {PHAROS_CARD_WIDTH} {PHAROS_ROUTE_CARD_HEIGHT} }}",
        f"{prefix}{T}using = bg_text_mask_container_dark_blue",
        "",
        f"{prefix}{T}vbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}margin = {{ 8 8 }}",
        f"{prefix}{T}{T}spacing = 7",
        f"{prefix}{T}{T}ignoreinvisible = yes",
        f"{prefix}{T}{T}hbox = {{",
        f"{prefix}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}{T}size = {{ {PHAROS_CARD_WIDTH - 16} 92 }}",
        f"{prefix}{T}{T}{T}spacing = 12",
    ]
    lines.extend(
        pharos_piechart(
            indent + 3,
            value_var="tv_wonder_pharos_route_progress",
            max_value=PHAROS_ROUTE_COUNT,
            icon_text="@port!",
            fill_color="0.18 0.58 0.42 1",
        )
    )
    lines.extend(
        [
            f"{prefix}{T}{T}{T}vbox = {{",
            f"{prefix}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{prefix}{T}{T}{T}{T}spacing = 4",
            f"{prefix}{T}{T}{T}{T}text_multi = {{ max_width = 328 autoresize = yes text = \"TV_ENGINEERING_PHAROS_STAGE_2_TEXT\" align = nobaseline|left }}",
            f"{prefix}{T}{T}{T}{T}text_single = {{",
            f"{prefix}{T}{T}{T}{T}{T}size = {{ 328 22 }}",
            f'{prefix}{T}{T}{T}{T}{T}raw_text = "[{progress_var}.GetValue|0]/{PHAROS_ROUTE_COUNT}"',
            f"{prefix}{T}{T}{T}{T}{T}fontsize = 14",
            f"{prefix}{T}{T}{T}{T}{T}align = nobaseline|right",
            f"{prefix}{T}{T}{T}{T}}}",
            f"{prefix}{T}{T}{T}}}",
            f"{prefix}{T}{T}}}",
        ]
    )
    for route_key in PHAROS_ROUTE_KEYS:
        lines.extend(pharos_route_row(route_key, indent + 2))
    lines.extend(
        [
            f"{prefix}{T}}}",
            f"{prefix}}}",
        ]
    )
    return lines


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    globals().update(helpers)
    lines.extend(pharos_stage_1_card(indent))
    lines.extend(pharos_stage_2_card(indent))
