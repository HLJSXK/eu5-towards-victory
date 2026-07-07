T = "\t"
DOME_OF_THE_ROCK_WONDER_ID = 103
DOME_OF_THE_ROCK_CARD_WIDTH = 462
DOME_OF_THE_ROCK_ROW_WIDTH = DOME_OF_THE_ROCK_CARD_WIDTH - 16
DOME_OF_THE_ROCK_ROW_HEIGHT = 28
DOME_OF_THE_ROCK_CHIP_WIDTH = 116
DOME_OF_THE_ROCK_LABEL_WIDTH = DOME_OF_THE_ROCK_ROW_WIDTH - DOME_OF_THE_ROCK_CHIP_WIDTH - 8
DOME_OF_THE_ROCK_CARD_HEIGHT = 176
DOME_OF_THE_ROCK_ROW_PREFIX = "tv_wonder_unique_dome_of_the_rock_ritual"
DOME_OF_THE_ROCK_SANCTUARY_ROW = "sanctuary_access_groups"
DOME_OF_THE_ROCK_CUSTODY_ROW = "custody_duties"


def dome_of_the_rock_locked_expr() -> str:
    return (
        f"And({player_var('tv_wonder_locked')}.IsSet, "
        f"{eq('tv_wonder_locked', DOME_OF_THE_ROCK_WONDER_ID)})"
    )


def dome_of_the_rock_visible() -> str:
    return fold_bool("And", [active_ritual_visible(), dome_of_the_rock_locked_expr()])


def dome_of_the_rock_row_var(row_key: str, suffix: str) -> str:
    return f"{DOME_OF_THE_ROCK_ROW_PREFIX}_{row_key}_{suffix}"


def value_visible(var_name: str, value: int) -> str:
    return f"And({var_is_set(var_name)}, {eq(var_name, value)})"


def row_started_visible(row_key: str) -> str:
    return value_visible(dome_of_the_rock_row_var(row_key, "started"), 1)


def row_completed_visible(row_key: str) -> str:
    return value_visible(dome_of_the_rock_row_var(row_key, "completed"), 1)


def row_failed_visible(row_key: str) -> str:
    return value_visible(dome_of_the_rock_row_var(row_key, "failed"), 1)


def row_branch_visible(row_key: str) -> str:
    return value_visible(dome_of_the_rock_row_var(row_key, "branch"), 1)


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
    return f"Or({row_failed_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW)}, {row_failed_visible(DOME_OF_THE_ROCK_CUSTODY_ROW)})"


def reward_ready_visible() -> str:
    return f"And({row_completed_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW)}, {row_completed_visible(DOME_OF_THE_ROCK_CUSTODY_ROW)})"


def custody_stage_visible() -> str:
    return fold_bool(
        "And",
        [
            row_completed_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW),
            f"Not({row_completed_visible(DOME_OF_THE_ROCK_CUSTODY_ROW)})",
            f"Not({any_row_failed_visible()})",
        ],
    )


def sanctuary_stage_visible() -> str:
    return fold_bool(
        "And",
        [
            f"Not({reward_ready_visible()})",
            f"Not({custody_stage_visible()})",
            f"Not({any_row_failed_visible()})",
        ],
    )


def reward_branch_pending_visible() -> str:
    return fold_bool(
        "And",
        [
            f"Not({reward_ready_visible()})",
            f"Not({row_branch_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW)})",
            f"Not({row_branch_visible(DOME_OF_THE_ROCK_CUSTODY_ROW)})",
            f"Not({any_row_failed_visible()})",
        ],
    )


def reward_branch_recorded_visible() -> str:
    return fold_bool(
        "And",
        [
            f"Not({reward_ready_visible()})",
            f"Not({any_row_failed_visible()})",
            f"Or({row_branch_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW)}, {row_branch_visible(DOME_OF_THE_ROCK_CUSTODY_ROW)})",
        ],
    )


def dome_of_the_rock_chip(indent: int, *, visible: str, text_key: str, texture: str, alpha: str) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{visible}]"',
        f"{prefix}{T}layoutpolicy_horizontal = fixed",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {DOME_OF_THE_ROCK_CHIP_WIDTH} 22 }}",
        f"{prefix}{T}alwaystransparent = yes",
        f"{prefix}{T}background = {{",
        f"{prefix}{T}{T}using = {texture}",
        f"{prefix}{T}{T}alpha = {alpha}",
        f"{prefix}{T}}}",
        f"{prefix}{T}text_single = {{",
        f'{prefix}{T}{T}text = "{text_key}"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}max_width = {DOME_OF_THE_ROCK_CHIP_WIDTH - 10}",
        f"{prefix}{T}{T}fontsize = 12",
        f"{prefix}{T}{T}align = center|nobaseline",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def dome_of_the_rock_status_row(
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
        f"{prefix}{T}size = {{ {DOME_OF_THE_ROCK_ROW_WIDTH} {DOME_OF_THE_ROCK_ROW_HEIGHT} }}",
        f"{prefix}{T}spacing = 8",
        f"{prefix}{T}ignoreinvisible = yes",
        f"{prefix}{T}text_single = {{",
        f'{prefix}{T}{T}text = "{label_key}"',
        f"{prefix}{T}{T}size = {{ {DOME_OF_THE_ROCK_LABEL_WIDTH} 24 }}",
        f"{prefix}{T}{T}max_width = {DOME_OF_THE_ROCK_LABEL_WIDTH}",
        f"{prefix}{T}{T}fontsize = 13",
        f"{prefix}{T}{T}align = nobaseline|left",
        f"{prefix}{T}}}",
    ]
    lines.extend(
        dome_of_the_rock_chip(
            indent + 1,
            visible=failed_visible,
            text_key="TV_ENGINEERING_DOME_OF_THE_ROCK_STATUS_FAILED",
            texture="color_mid_red_texture",
            alpha="0.34",
        )
    )
    lines.extend(
        dome_of_the_rock_chip(
            indent + 1,
            visible=complete_visible,
            text_key="TV_ENGINEERING_DOME_OF_THE_ROCK_STATUS_COMPLETE",
            texture="color_market_green_texture",
            alpha="0.34",
        )
    )
    if branch_visible is not None:
        lines.extend(
            dome_of_the_rock_chip(
                indent + 1,
                visible=branch_visible,
                text_key="TV_ENGINEERING_DOME_OF_THE_ROCK_STATUS_BRANCH_RECORDED",
                texture="color_yellow_texture",
                alpha="0.30",
            )
        )
    lines.extend(
        dome_of_the_rock_chip(
            indent + 1,
            visible=active_visible,
            text_key="TV_ENGINEERING_DOME_OF_THE_ROCK_STATUS_ACTIVE",
            texture="color_yellow_texture",
            alpha="0.28",
        )
    )
    lines.extend(
        dome_of_the_rock_chip(
            indent + 1,
            visible=waiting_visible,
            text_key="TV_ENGINEERING_DOME_OF_THE_ROCK_STATUS_WAITING",
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
        f"{prefix}{T}size = {{ {DOME_OF_THE_ROCK_ROW_WIDTH} {DOME_OF_THE_ROCK_ROW_HEIGHT} }}",
        f"{prefix}{T}spacing = 8",
        f"{prefix}{T}ignoreinvisible = yes",
        f"{prefix}{T}text_single = {{ text = \"TV_ENGINEERING_DOME_OF_THE_ROCK_CURRENT_STAGE\" size = {{ {DOME_OF_THE_ROCK_LABEL_WIDTH} 24 }} max_width = {DOME_OF_THE_ROCK_LABEL_WIDTH} fontsize = 13 align = nobaseline|left }}",
    ]
    for visible, text_key, texture, alpha in (
        (any_row_failed_visible(), "TV_ENGINEERING_DOME_OF_THE_ROCK_STATUS_FAILED", "color_mid_red_texture", "0.34"),
        (reward_ready_visible(), "TV_ENGINEERING_DOME_OF_THE_ROCK_STAGE_REWARD", "color_market_green_texture", "0.34"),
        (custody_stage_visible(), "TV_ENGINEERING_DOME_OF_THE_ROCK_STAGE_CUSTODY_DUTIES", "color_yellow_texture", "0.28"),
        (sanctuary_stage_visible(), "TV_ENGINEERING_DOME_OF_THE_ROCK_STAGE_SANCTUARY_ACCESS_GROUPS", "color_yellow_texture", "0.20"),
    ):
        lines.extend(
            dome_of_the_rock_chip(
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
    return dome_of_the_rock_status_row(
        indent,
        label_key="TV_ENGINEERING_DOME_OF_THE_ROCK_REWARD_BRANCH_STATUS",
        waiting_visible=reward_branch_pending_visible(),
        active_visible="False",
        branch_visible=reward_branch_recorded_visible(),
        complete_visible=reward_ready_visible(),
        failed_visible=any_row_failed_visible(),
    )


def dome_of_the_rock_ritual_card(indent: int) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}widget = {{",
        f'{prefix}{T}visible = "[{dome_of_the_rock_visible()}]"',
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {DOME_OF_THE_ROCK_CARD_WIDTH} {DOME_OF_THE_ROCK_CARD_HEIGHT} }}",
        f"{prefix}{T}using = bg_text_mask_container_dark_blue",
        f"{prefix}{T}vbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}margin = {{ 8 8 }}",
        f"{prefix}{T}{T}spacing = 6",
        f"{prefix}{T}{T}ignoreinvisible = yes",
        f'{prefix}{T}{T}text_single = {{ text = "TV_ENGINEERING_DOME_OF_THE_ROCK_OPENING_TITLE" size = {{ {DOME_OF_THE_ROCK_ROW_WIDTH} 24 }} max_width = {DOME_OF_THE_ROCK_ROW_WIDTH} fontsize = 14 align = nobaseline|left }}',
    ]
    lines.extend(current_stage_row(indent + 2))
    lines.extend(
        dome_of_the_rock_status_row(
            indent + 2,
            label_key="TV_ENGINEERING_DOME_OF_THE_ROCK_SANCTUARY_ACCESS_GROUPS_STATUS",
            waiting_visible=row_waiting_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW),
            active_visible=row_active_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW),
            branch_visible=row_branch_recorded_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW),
            complete_visible=row_completed_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW),
            failed_visible=row_failed_visible(DOME_OF_THE_ROCK_SANCTUARY_ROW),
        )
    )
    lines.extend(
        dome_of_the_rock_status_row(
            indent + 2,
            label_key="TV_ENGINEERING_DOME_OF_THE_ROCK_CUSTODY_DUTIES_STATUS",
            waiting_visible=row_waiting_visible(DOME_OF_THE_ROCK_CUSTODY_ROW),
            active_visible=row_active_visible(DOME_OF_THE_ROCK_CUSTODY_ROW),
            branch_visible=row_branch_recorded_visible(DOME_OF_THE_ROCK_CUSTODY_ROW),
            complete_visible=row_completed_visible(DOME_OF_THE_ROCK_CUSTODY_ROW),
            failed_visible=row_failed_visible(DOME_OF_THE_ROCK_CUSTODY_ROW),
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
    lines.extend(dome_of_the_rock_ritual_card(indent))
