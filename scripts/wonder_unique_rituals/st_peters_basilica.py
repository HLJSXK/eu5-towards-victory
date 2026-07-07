T = "\t"
ST_PETERS_BASILICA_WONDER_ID = 112
ST_PETERS_BASILICA_CARD_WIDTH = 462
ST_PETERS_BASILICA_ROW_WIDTH = ST_PETERS_BASILICA_CARD_WIDTH - 16
ST_PETERS_BASILICA_ROW_HEIGHT = 28
ST_PETERS_BASILICA_CHIP_WIDTH = 116
ST_PETERS_BASILICA_LABEL_WIDTH = ST_PETERS_BASILICA_ROW_WIDTH - ST_PETERS_BASILICA_CHIP_WIDTH - 8
ST_PETERS_BASILICA_CARD_HEIGHT = 176
ST_PETERS_BASILICA_ROW_PREFIX = "tv_wonder_unique_st_peters_basilica_ritual"
ST_PETERS_BASILICA_OFFICIAL_ROW = "sacred_official_candidates"
ST_PETERS_BASILICA_DUTIES_ROW = "apostolic_service_duties"


def st_peters_basilica_locked_expr() -> str:
    return (
        f"And({player_var('tv_wonder_locked')}.IsSet, "
        f"{eq('tv_wonder_locked', ST_PETERS_BASILICA_WONDER_ID)})"
    )


def st_peters_basilica_visible() -> str:
    return fold_bool("And", [active_ritual_visible(), st_peters_basilica_locked_expr()])


def st_peters_basilica_row_var(row_key: str, suffix: str) -> str:
    return f"{ST_PETERS_BASILICA_ROW_PREFIX}_{row_key}_{suffix}"


def value_visible(var_name: str, value: int) -> str:
    return f"And({var_is_set(var_name)}, {eq(var_name, value)})"


def row_started_visible(row_key: str) -> str:
    return value_visible(st_peters_basilica_row_var(row_key, "started"), 1)


def row_completed_visible(row_key: str) -> str:
    return value_visible(st_peters_basilica_row_var(row_key, "completed"), 1)


def row_failed_visible(row_key: str) -> str:
    return value_visible(st_peters_basilica_row_var(row_key, "failed"), 1)


def row_branch_visible(row_key: str) -> str:
    return value_visible(st_peters_basilica_row_var(row_key, "branch"), 1)


def row_waiting_visible(row_key: str) -> str:
    return fold_bool(
        "And",
        [
            f"Not({row_started_visible(row_key)})",
            f"Not({row_completed_visible(row_key)})",
            f"Not({row_failed_visible(row_key)})",
        ],
    )


def row_active_visible(row_key: str) -> str:
    return fold_bool(
        "And",
        [
            row_started_visible(row_key),
            f"Not({row_completed_visible(row_key)})",
            f"Not({row_failed_visible(row_key)})",
            f"Not({row_branch_visible(row_key)})",
        ],
    )


def row_branch_recorded_visible(row_key: str) -> str:
    return fold_bool(
        "And",
        [
            row_branch_visible(row_key),
            f"Not({row_completed_visible(row_key)})",
            f"Not({row_failed_visible(row_key)})",
        ],
    )


def any_row_failed_visible() -> str:
    return f"Or({row_failed_visible(ST_PETERS_BASILICA_OFFICIAL_ROW)}, {row_failed_visible(ST_PETERS_BASILICA_DUTIES_ROW)})"


def reward_ready_visible() -> str:
    return f"And({row_completed_visible(ST_PETERS_BASILICA_OFFICIAL_ROW)}, {row_completed_visible(ST_PETERS_BASILICA_DUTIES_ROW)})"


def duties_stage_visible() -> str:
    return fold_bool(
        "And",
        [
            row_completed_visible(ST_PETERS_BASILICA_OFFICIAL_ROW),
            f"Not({row_completed_visible(ST_PETERS_BASILICA_DUTIES_ROW)})",
            f"Not({any_row_failed_visible()})",
        ],
    )


def official_stage_visible() -> str:
    return fold_bool(
        "And",
        [
            f"Not({reward_ready_visible()})",
            f"Not({duties_stage_visible()})",
            f"Not({any_row_failed_visible()})",
        ],
    )


def reward_branch_pending_visible() -> str:
    return fold_bool(
        "And",
        [
            f"Not({reward_ready_visible()})",
            f"Not({row_branch_visible(ST_PETERS_BASILICA_OFFICIAL_ROW)})",
            f"Not({row_branch_visible(ST_PETERS_BASILICA_DUTIES_ROW)})",
            f"Not({any_row_failed_visible()})",
        ],
    )


def reward_branch_recorded_visible() -> str:
    return fold_bool(
        "And",
        [
            f"Not({reward_ready_visible()})",
            f"Not({any_row_failed_visible()})",
            f"Or({row_branch_visible(ST_PETERS_BASILICA_OFFICIAL_ROW)}, {row_branch_visible(ST_PETERS_BASILICA_DUTIES_ROW)})",
        ],
    )


def st_peters_basilica_chip(indent: int, *, visible: str, text_key: str, texture: str, alpha: str) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{visible}]"',
        f"{prefix}{T}layoutpolicy_horizontal = fixed",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {ST_PETERS_BASILICA_CHIP_WIDTH} 22 }}",
        f"{prefix}{T}alwaystransparent = yes",
        f"{prefix}{T}background = {{",
        f"{prefix}{T}{T}using = {texture}",
        f"{prefix}{T}{T}alpha = {alpha}",
        f"{prefix}{T}}}",
        f"{prefix}{T}text_single = {{",
        f'{prefix}{T}{T}text = "{text_key}"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}max_width = {ST_PETERS_BASILICA_CHIP_WIDTH - 10}",
        f"{prefix}{T}{T}fontsize = 12",
        f"{prefix}{T}{T}align = center|nobaseline",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def st_peters_basilica_status_row(
    indent: int,
    *,
    label_key: str,
    waiting_visible: str,
    active_visible: str,
    branch_visible: str | None = None,
    complete_visible: str,
    failed_visible: str,
) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}hbox = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {ST_PETERS_BASILICA_ROW_WIDTH} {ST_PETERS_BASILICA_ROW_HEIGHT} }}",
        f"{prefix}{T}spacing = 8",
        f"{prefix}{T}ignoreinvisible = yes",
        f"{prefix}{T}text_single = {{",
        f'{prefix}{T}{T}text = "{label_key}"',
        f"{prefix}{T}{T}size = {{ {ST_PETERS_BASILICA_LABEL_WIDTH} 24 }}",
        f"{prefix}{T}{T}max_width = {ST_PETERS_BASILICA_LABEL_WIDTH}",
        f"{prefix}{T}{T}fontsize = 13",
        f"{prefix}{T}{T}align = nobaseline|left",
        f"{prefix}{T}}}",
    ]
    lines.extend(
        st_peters_basilica_chip(
            indent + 1,
            visible=failed_visible,
            text_key="TV_ENGINEERING_ST_PETERS_BASILICA_STATUS_FAILED",
            texture="color_mid_red_texture",
            alpha="0.34",
        )
    )
    lines.extend(
        st_peters_basilica_chip(
            indent + 1,
            visible=complete_visible,
            text_key="TV_ENGINEERING_ST_PETERS_BASILICA_STATUS_COMPLETE",
            texture="color_market_green_texture",
            alpha="0.34",
        )
    )
    if branch_visible is not None:
        lines.extend(
            st_peters_basilica_chip(
                indent + 1,
                visible=branch_visible,
                text_key="TV_ENGINEERING_ST_PETERS_BASILICA_STATUS_BRANCH_RECORDED",
                texture="color_yellow_texture",
                alpha="0.30",
            )
        )
    lines.extend(
        st_peters_basilica_chip(
            indent + 1,
            visible=active_visible,
            text_key="TV_ENGINEERING_ST_PETERS_BASILICA_STATUS_ACTIVE",
            texture="color_yellow_texture",
            alpha="0.28",
        )
    )
    lines.extend(
        st_peters_basilica_chip(
            indent + 1,
            visible=waiting_visible,
            text_key="TV_ENGINEERING_ST_PETERS_BASILICA_STATUS_WAITING",
            texture="color_yellow_texture",
            alpha="0.16",
        )
    )
    lines.append(f"{prefix}}}")
    return lines


def current_stage_row(indent: int) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}hbox = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {ST_PETERS_BASILICA_ROW_WIDTH} {ST_PETERS_BASILICA_ROW_HEIGHT} }}",
        f"{prefix}{T}spacing = 8",
        f"{prefix}{T}ignoreinvisible = yes",
        f"{prefix}{T}text_single = {{ text = \"TV_ENGINEERING_ST_PETERS_BASILICA_CURRENT_STAGE\" size = {{ {ST_PETERS_BASILICA_LABEL_WIDTH} 24 }} max_width = {ST_PETERS_BASILICA_LABEL_WIDTH} fontsize = 13 align = nobaseline|left }}",
    ]
    for visible, text_key, texture, alpha in (
        (any_row_failed_visible(), "TV_ENGINEERING_ST_PETERS_BASILICA_STATUS_FAILED", "color_mid_red_texture", "0.34"),
        (reward_ready_visible(), "TV_ENGINEERING_ST_PETERS_BASILICA_STAGE_REWARD", "color_market_green_texture", "0.34"),
        (duties_stage_visible(), "TV_ENGINEERING_ST_PETERS_BASILICA_STAGE_APOSTOLIC_SERVICE_DUTIES", "color_yellow_texture", "0.28"),
        (official_stage_visible(), "TV_ENGINEERING_ST_PETERS_BASILICA_STAGE_SACRED_OFFICIAL_CANDIDATES", "color_yellow_texture", "0.20"),
    ):
        lines.extend(
            st_peters_basilica_chip(
                indent + 1,
                visible=visible,
                text_key=text_key,
                texture=texture,
                alpha=alpha,
            )
        )
    lines.append(f"{prefix}}}")
    return lines


def reward_branch_row(indent: int) -> list[str]:
    return st_peters_basilica_status_row(
        indent,
        label_key="TV_ENGINEERING_ST_PETERS_BASILICA_REWARD_BRANCH_STATUS",
        waiting_visible=reward_branch_pending_visible(),
        active_visible="False",
        branch_visible=reward_branch_recorded_visible(),
        complete_visible=reward_ready_visible(),
        failed_visible=any_row_failed_visible(),
    )


def st_peters_basilica_ritual_card(indent: int) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{st_peters_basilica_visible()}]"',
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {ST_PETERS_BASILICA_CARD_WIDTH} {ST_PETERS_BASILICA_CARD_HEIGHT} }}",
        f"{prefix}{T}using = bg_text_mask_container_dark_blue",
        f"{prefix}{T}vbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}margin = {{ 8 8 }}",
        f"{prefix}{T}{T}spacing = 6",
        f"{prefix}{T}{T}ignoreinvisible = yes",
        f'{prefix}{T}{T}text_single = {{ text = "TV_ENGINEERING_ST_PETERS_BASILICA_OPENING_TITLE" size = {{ {ST_PETERS_BASILICA_ROW_WIDTH} 24 }} max_width = {ST_PETERS_BASILICA_ROW_WIDTH} fontsize = 14 align = nobaseline|left }}',
    ]
    lines.extend(current_stage_row(indent + 2))
    lines.extend(
        st_peters_basilica_status_row(
            indent + 2,
            label_key="TV_ENGINEERING_ST_PETERS_BASILICA_SACRED_OFFICIAL_CANDIDATES_STATUS",
            waiting_visible=row_waiting_visible(ST_PETERS_BASILICA_OFFICIAL_ROW),
            active_visible=row_active_visible(ST_PETERS_BASILICA_OFFICIAL_ROW),
            branch_visible=row_branch_recorded_visible(ST_PETERS_BASILICA_OFFICIAL_ROW),
            complete_visible=row_completed_visible(ST_PETERS_BASILICA_OFFICIAL_ROW),
            failed_visible=row_failed_visible(ST_PETERS_BASILICA_OFFICIAL_ROW),
        )
    )
    lines.extend(
        st_peters_basilica_status_row(
            indent + 2,
            label_key="TV_ENGINEERING_ST_PETERS_BASILICA_APOSTOLIC_SERVICE_DUTIES_STATUS",
            waiting_visible=row_waiting_visible(ST_PETERS_BASILICA_DUTIES_ROW),
            active_visible=row_active_visible(ST_PETERS_BASILICA_DUTIES_ROW),
            branch_visible=row_branch_recorded_visible(ST_PETERS_BASILICA_DUTIES_ROW),
            complete_visible=row_completed_visible(ST_PETERS_BASILICA_DUTIES_ROW),
            failed_visible=row_failed_visible(ST_PETERS_BASILICA_DUTIES_ROW),
        )
    )
    lines.extend(reward_branch_row(indent + 2))
    lines.extend(
        [
            f"{prefix}{T}}}",
            f"{prefix}}}",
        ]
    )
    return lines


def append_effects(lines: list[str]) -> None:
    return None


def append_triggers(lines: list[str]) -> None:
    return None


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    globals().update(helpers)
    lines.extend(st_peters_basilica_ritual_card(indent))
