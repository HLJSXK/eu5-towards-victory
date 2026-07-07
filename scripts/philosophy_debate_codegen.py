"""Shared code generation helpers for Academy philosophy debate files."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "philosophy_debates.yaml"
RANDOM_EVENTS_DIR = REPO_ROOT / "data" / "philosophy_debate_random_events"
PHILOSOPHY_DEBATE_DATA_SOURCES = "data/philosophy_debates.yaml + data/philosophy_debate_random_events/*.yaml"
RANDOM_EVENT_ID_BASE = 2000

EVENT_NS = "tv_academy_debate"
LOCAL_ACTION_POSITIVE_EVENT = 116
LOCAL_ACTION_NEGATIVE_EVENT = 117
WORLD_DEBATE_START_EVENT = 118
WORLD_DEBATE_PROGRESSIVE_EVENT = 119
WORLD_DEBATE_CONSERVATIVE_EVENT = 120
WORLD_DEBATE_NEUTRAL_EVENT = 121
AUTO_STANCE_SUPPORT_EVENT = 122
AUTO_STANCE_OPPOSE_EVENT = 123
AUTO_STANCE_NEUTRAL_EVENT = 124
AUTO_SEAT_VACATED_EVENT = 125
SEATS = range(1, 6)
WORLD_SEATS = range(1, 51)
STANCE_SUPPORT = 1
STANCE_OPPOSE = 2
STANCE_NEUTRAL = 3
WORLD_RESULT_PROGRESSIVE = 1
WORLD_RESULT_CONSERVATIVE = 2
WORLD_RESULT_NEUTRAL = 3

WORLD_PARTICIPANTS_LIST = "tv_academy_world_debate_participants"
WORLD_ACTIVE_VAR = "tv_academy_world_debate_active"
WORLD_ISSUE_VAR = "tv_academy_world_debate_issue"
WORLD_NODE_VAR = "tv_academy_world_debate_node"
WORLD_PROGRESS_VAR = "tv_academy_world_debate_progress"
WORLD_STRENGTH_VAR = "tv_academy_world_debate_strength"
WORLD_MONTHS_VAR = "tv_academy_world_debate_months"
WORLD_SUPPORT_SEATS_VAR = "tv_academy_world_debate_support_seats"
WORLD_OPPOSE_SEATS_VAR = "tv_academy_world_debate_oppose_seats"
WORLD_NEUTRAL_SEATS_VAR = "tv_academy_world_debate_neutral_seats"
WORLD_SEAT_COUNT_VAR = "tv_academy_world_debate_seat_count"
WORLD_RESULT_VAR = "tv_academy_world_debate_result"
WORLD_DELTA_VAR = "tv_academy_world_debate_delta"
WORLD_NEXT_SEAT_VAR = "tv_academy_world_debate_next_seat"
WORLD_DECISIVE_SEATS_VAR = "tv_academy_world_debate_decisive_seats"
WORLD_COUNTRY_STANCE_VAR = "tv_academy_world_debate_stance"
WORLD_PARTICIPANT_VAR = "tv_academy_world_debate_participant"
WORLD_NUMERIC_VARS = [
    WORLD_ACTIVE_VAR,
    WORLD_ISSUE_VAR,
    WORLD_NODE_VAR,
    WORLD_PROGRESS_VAR,
    WORLD_STRENGTH_VAR,
    WORLD_MONTHS_VAR,
    WORLD_SUPPORT_SEATS_VAR,
    WORLD_OPPOSE_SEATS_VAR,
    WORLD_NEUTRAL_SEATS_VAR,
    WORLD_SEAT_COUNT_VAR,
    WORLD_RESULT_VAR,
]

EVENT_GROUP = "tv_academy_debate_event_group"
EVENT_GROUP_2 = "tv_academy_debate_event_group_2"
EVENT_STANCE = "tv_academy_debate_event_stance"
EVENT_STANCE_2 = "tv_academy_debate_event_stance_2"
EVENT_SEAT = "tv_academy_debate_event_seat"
EVENT_SEAT_2 = "tv_academy_debate_event_seat_2"
EVENT_PRICE = "tv_academy_debate_event_price"
MONTHLY_DELTA = "tv_academy_philosophy_monthly_delta"
SEAT_CONTRIB = "tv_academy_debate_seat_contribution"
LOCAL_DEBATE_PROGRESS_VAR = "tv_academy_philosophy_debate_position"
LOCAL_DEBATE_PROGRESS_DELTA_LOCAL = "tv_academy_debate_local_progress_delta"
SELECTED_ARTIST_SCOPE = "tv_academy_debate_selected_artist"
SELECTED_FOREIGN_SCOPE = "tv_academy_debate_selected_foreign_country"
SELECTED_SCIENTIST_SCOPE = "tv_academy_debate_selected_scientist"

PENDING_RESULT_VAR = "tv_academy_philosophy_result_pending"
PENDING_ISSUE_VAR = "tv_academy_philosophy_result_issue"
PENDING_KIND_VAR = "tv_academy_philosophy_result_kind"
AUTO_STANCE_SUPPORT_VAR = "tv_academy_debate_auto_stance_support_pending"
AUTO_STANCE_OPPOSE_VAR = "tv_academy_debate_auto_stance_oppose_pending"
AUTO_STANCE_NEUTRAL_VAR = "tv_academy_debate_auto_stance_neutral_pending"
AUTO_SEAT_VACATED_VAR = "tv_academy_debate_auto_seat_vacated_pending"

GROUP_ESTATE_MAP = "tv_academy_debate_group_to_estate"
RESULT_GROUP_LOCAL = "tv_academy_debate_result_group"
RESULT_ESTATE_LOCAL = "tv_academy_debate_result_estate"

RANDOM_EVENT_EFFECT_TYPES = {
    "artist_skill",
    "estate_satisfaction",
    "foreign_prestige",
    "resource",
    "scientist_attribute",
    "seat_cooldown",
    "seat_stance",
    "temporary_country_modifier",
}
RANDOM_EVENT_RESOURCES = {"gold", "legitimacy", "prestige", "stability"}
RANDOM_EVENT_STANCES = {"support", "oppose", "neutral"}
RANDOM_EVENT_PROGRESS_DELTAS = {-10, -5, 5, 10}


def load_data() -> dict:
    with DATA_FILE.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    load_random_event_data(data)
    validate_data(data)
    return data


def load_random_event_data(data: dict) -> None:
    random_events: list[dict] = []
    excluded_events: list[dict] = []
    if RANDOM_EVENTS_DIR.exists():
        for path in sorted(RANDOM_EVENTS_DIR.glob("*.yaml")):
            with path.open(encoding="utf-8-sig") as file:
                fragment = yaml.safe_load(file) or {}
            for event in fragment.get("random_events") or []:
                entry = dict(event)
                entry["source_file"] = path.relative_to(REPO_ROOT).as_posix()
                random_events.append(entry)
            for event in fragment.get("excluded_events") or []:
                entry = dict(event)
                entry["source_file"] = path.relative_to(REPO_ROOT).as_posix()
                excluded_events.append(entry)
    for idx, event in enumerate(random_events):
        event["event_num"] = RANDOM_EVENT_ID_BASE + idx
    data["random_events"] = random_events
    data["excluded_random_events"] = sorted(excluded_events, key=lambda event: event["design_id"])


def validate_data(data: dict) -> None:
    missing: list[str] = []
    for field in ("settings", "event_weights", "prices", "issues", "groups", "debate_positions"):
        if field not in data:
            missing.append(field)
    issue_keys = {issue["key"] for issue in data.get("issues", [])}
    group_keys = {group["key"] for group in data.get("groups", [])}
    for group in data.get("groups", []):
        for field in ("id", "key", "type", "icon", "loc"):
            if field not in group:
                missing.append(f"groups.{group.get('key', '<unknown>')}.{field}")
    for group_key, positions in (data.get("debate_positions") or {}).items():
        if group_key not in group_keys:
            missing.append(f"debate_positions.{group_key}")
            continue
        if positions.get("dynamic"):
            continue
        for stance in ("support", "oppose", "neutral"):
            if stance not in positions:
                missing.append(f"debate_positions.{group_key}.{stance}")
                continue
            for issue_key in positions[stance]:
                if issue_key not in issue_keys:
                    missing.append(f"debate_positions.{group_key}.{stance}.{issue_key}")
    for issue_key, trigger_groups in (data.get("action_triggers") or {}).items():
        if issue_key not in issue_keys:
            missing.append(f"action_triggers.{issue_key}")
            continue
        for direction in ("positive", "negative"):
            for idx, trigger in enumerate(trigger_groups.get(direction, []), start=1):
                for field in ("hook", "condition", "chance", "delta"):
                    if field not in trigger:
                        missing.append(f"action_triggers.{issue_key}.{direction}.{idx}.{field}")
    validate_random_event_data(data, missing)
    if missing:
        raise ValueError("Missing/invalid philosophy debate fields:\n  " + "\n  ".join(missing))


def validate_random_event_data(data: dict, missing: list[str]) -> None:
    random_event_entries = data.get("random_events") or []
    excluded_entries = data.get("excluded_random_events") or []
    issue_keys = {issue["key"] for issue in data.get("issues", [])}
    group_keys = {group["key"] for group in data.get("groups", [])}
    seen_ids: set[str] = set()
    excluded_ids = {entry.get("design_id") for entry in excluded_entries}
    if random_event_entries or excluded_entries:
        if len(random_event_entries) != 198:
            missing.append(f"random_events.expected_198_found_{len(random_event_entries)}")
        if len(excluded_entries) != 2:
            missing.append(f"excluded_random_events.expected_2_found_{len(excluded_entries)}")
        if excluded_ids != {"G09", "G12"}:
            missing.append(f"excluded_random_events.expected_G09_G12_found_{sorted(excluded_ids)}")
    for idx, event in enumerate(random_event_entries, start=1):
        path = f"random_events.{event.get('design_id', idx)}"
        design_id = event.get("design_id")
        if not design_id:
            missing.append(f"{path}.design_id")
        elif design_id in seen_ids:
            missing.append(f"{path}.duplicate_design_id")
        else:
            seen_ids.add(design_id)
        if design_id in {"G09", "G12"}:
            missing.append(f"{path}.excluded_id_in_random_events")
        event_num = event.get("event_num")
        if event_num is None or int(event_num) >= 10000:
            missing.append(f"{path}.event_num")
        if event.get("pool") == "general":
            if event.get("issue") is not None:
                missing.append(f"{path}.general_issue_must_be_null")
        elif event.get("issue") not in issue_keys:
            missing.append(f"{path}.issue")
        for loc_field in ("title", "desc"):
            loc = event.get(loc_field) or {}
            for lang in ("english", "simp_chinese"):
                if not loc.get(lang):
                    missing.append(f"{path}.{loc_field}.{lang}")
        options = event.get("options") or {}
        if set(options) != {"a", "b"}:
            missing.append(f"{path}.options.expected_a_b")
            continue
        for opt_key in ("a", "b"):
            option_data = options.get(opt_key) or {}
            opt_path = f"{path}.options.{opt_key}"
            text = option_data.get("text") or {}
            rationale = option_data.get("rationale") or {}
            for lang in ("english", "simp_chinese"):
                if not text.get(lang):
                    missing.append(f"{opt_path}.text.{lang}")
                if not rationale.get(lang):
                    missing.append(f"{opt_path}.rationale.{lang}")
            if option_data.get("progress_delta") not in RANDOM_EVENT_PROGRESS_DELTAS:
                missing.append(f"{opt_path}.progress_delta")
            for block_idx, block in enumerate(option_data.get("effect_blocks") or [], start=1):
                validate_random_effect_block(block, f"{opt_path}.effect_blocks.{block_idx}", missing, group_keys)


def validate_random_effect_block(block: dict, path: str, missing: list[str], group_keys: set[str]) -> None:
    effect_type = block.get("type")
    if effect_type not in RANDOM_EVENT_EFFECT_TYPES:
        missing.append(f"{path}.type")
        return
    if effect_type == "seat_stance":
        if block.get("group") not in group_keys:
            missing.append(f"{path}.group")
        if block.get("stance") not in RANDOM_EVENT_STANCES:
            missing.append(f"{path}.stance")
        if not isinstance(block.get("cooldown_months"), int):
            missing.append(f"{path}.cooldown_months")
    elif effect_type == "seat_cooldown":
        if block.get("group") not in group_keys:
            missing.append(f"{path}.group")
        if not isinstance(block.get("cooldown_months"), int):
            missing.append(f"{path}.cooldown_months")
    elif effect_type == "estate_satisfaction":
        if not str(block.get("estate", "")).endswith("_estate"):
            missing.append(f"{path}.estate")
        if not isinstance(block.get("value"), (int, float)):
            missing.append(f"{path}.value")
    elif effect_type == "resource":
        if block.get("resource") not in RANDOM_EVENT_RESOURCES:
            missing.append(f"{path}.resource")
        if not isinstance(block.get("amount", block.get("scale")), (int, float)):
            missing.append(f"{path}.amount")
    elif effect_type == "temporary_country_modifier":
        if not str(block.get("key", "")).startswith("tv_"):
            missing.append(f"{path}.key")
        if not isinstance(block.get("months"), int):
            missing.append(f"{path}.months")
        if not block.get("effects"):
            missing.append(f"{path}.effects")
    elif effect_type == "artist_skill":
        if not isinstance(block.get("amount"), (int, float)):
            missing.append(f"{path}.amount")
    elif effect_type == "scientist_attribute":
        if "adm" not in block and "dip" not in block:
            missing.append(f"{path}.adm_or_dip")
    elif effect_type == "foreign_prestige":
        if not isinstance(block.get("amount"), (int, float)):
            missing.append(f"{path}.amount")


def emit(lines: list[str], level: int = 0, text: str = "") -> None:
    lines.append("\t" * level + text if text else "")


def header(script_rel: str, data_rel: str = "data/philosophy_debates.yaml") -> str:
    return (
        f"# @Generated by {script_rel}\n"
        f"#   Data:    {data_rel}\n"
        f"#   Regen:   conda run --no-capture-output -n eu5 python {script_rel}\n"
        "# Do not edit directly - modify the data file and re-run the generator.\n"
    )


def groups(data: dict) -> list[dict]:
    return sorted(data["groups"], key=lambda g: int(g["id"]))


def issues(data: dict) -> list[dict]:
    return sorted(data["issues"], key=lambda i: int(i["id"]))


def random_events(data: dict) -> list[dict]:
    return sorted(data.get("random_events") or [], key=lambda event: int(event["event_num"]))


def group_by_key(data: dict) -> dict[str, dict]:
    return {g["key"]: g for g in data["groups"]}


def issue_by_key(data: dict) -> dict[str, dict]:
    return {i["key"]: i for i in data["issues"]}


def random_event_loc_key(event: dict, suffix: str) -> str:
    return f"{EVENT_NS}.{event['event_num']}.{suffix}"


def group_seated_tooltip_key(group: dict) -> str:
    return f"tv_academy_debate_group_{group['key']}_seated_text"


def group_left_tooltip_key(group: dict) -> str:
    return f"tv_academy_debate_group_{group['key']}_left_text"


def random_event_reason_hint(data: dict, event: dict, lang: str) -> str:
    """Single trailing line explaining why this random debate event appeared.

    Mirrors the concentrated-research great-scientist attribute hint: separated
    from the flavor text by a blank line and wrapped in a neutral #Y ... #! span.
    Issue-locked events name the current debate issue; general-pool events note
    that they can surface under any issue.
    """
    zh = lang == "simp_chinese"
    issue_key = event.get("issue")
    if issue_key:
        issue_name = issue_by_key(data)[issue_key]["loc"][lang]
        if zh:
            body = f"本事件出现是因为当前辩论议题为【{issue_name}】。"
        else:
            body = f"This event appeared because the current debate issue is {issue_name}."
    else:
        if zh:
            body = "本事件出现是因为一场本地辩论正在进行，且适用于任何辩论议题。"
        else:
            body = "This event appeared because a local debate is under way, and it can surface under any debate issue."
    return f"\n\n#Y {body}#!"


def random_event_desc_with_hint(data: dict, event: dict, lang: str) -> str:
    return event["desc"][lang] + random_event_reason_hint(data, event, lang)


def random_event_modifier_name(block: dict) -> str:
    return block["key"]


def group_var(key: str, suffix: str) -> str:
    return f"tv_academy_debate_group_{key}_{suffix}"


def seat_group(seat: int | str) -> str:
    return f"tv_academy_debate_seat_{seat}_group"


def seat_stance(seat: int | str) -> str:
    return f"tv_academy_debate_seat_{seat}_stance"


def seat_cooldown(seat: int | str) -> str:
    return f"tv_academy_debate_seat_{seat}_cooldown"


def seat_artist(seat: int | str) -> str:
    return f"tv_academy_debate_seat_{seat}_artist"


def seat_foreign(seat: int | str) -> str:
    return f"tv_academy_debate_seat_{seat}_foreign_country"


def seat_scientist(seat: int | str) -> str:
    return f"tv_academy_debate_seat_{seat}_scientist"


def world_seat_country(seat: int | str) -> str:
    return f"tv_academy_world_debate_seat_{seat}_country"


def world_seat_stance(seat: int | str) -> str:
    return f"tv_academy_world_debate_seat_{seat}_stance"


def group_condition(group: dict, status: str, *, negated: bool = False) -> str:
    text = f"has_variable = {group_var(group['key'], status)}"
    return f"NOT = {{ {text} }}" if negated else text


def var_eq(name: str, value: int | str) -> str:
    return f"var:{name} ?= {value}"


def if_group(lines: list[str], level: int, group: dict, *, first: bool = False) -> None:
    emit(lines, level, ("if" if first else "else_if") + " = {")
    emit(lines, level + 1, f"limit = {{ {var_eq(EVENT_GROUP, group['id'])} }}")


def close(lines: list[str], level: int) -> None:
    emit(lines, level, "}")


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8-sig")


def loc_key(prefix: str, key: str) -> str:
    return f"{prefix}_{key.upper()}"


def issue_match_lines(data: dict, issue_keys: list[str]) -> list[str]:
    by_key = issue_by_key(data)
    return [f"var:tv_academy_philosophy_current ?= {by_key[key]['id']}" for key in issue_keys]


def current_issue_or_block(data: dict, issue_keys: list[str]) -> list[str]:
    if not issue_keys:
        return ["always = no"]
    checks = issue_match_lines(data, issue_keys)
    if len(checks) == 1:
        return checks
    return ["OR = {", *[f"\t{line}" for line in checks], "}"]


def emit_current_issue_or(lines: list[str], level: int, data: dict, issue_keys: list[str]) -> None:
    block = current_issue_or_block(data, issue_keys)
    for raw in block:
        indent = raw.count("\t")
        emit(lines, level + indent, raw.lstrip("\t"))


def group_positions(data: dict, group_key: str) -> dict:
    return data["debate_positions"].get(group_key, {})


def static_group_stance(data: dict, group_key: str, issue_key: str) -> int:
    pos = group_positions(data, group_key)
    if pos.get("dynamic"):
        return STANCE_NEUTRAL
    if issue_key in pos.get("support", []):
        return STANCE_SUPPORT
    if issue_key in pos.get("oppose", []):
        return STANCE_OPPOSE
    return STANCE_NEUTRAL


def stance_name(stance: int) -> str:
    return {STANCE_SUPPORT: "support", STANCE_OPPOSE: "oppose", STANCE_NEUTRAL: "neutral"}[stance]


def base_estate_group_keys(data: dict, base_group: str) -> list[str]:
    return [g["key"] for g in groups(data) if g.get("base_group") == base_group]


def is_variant(group: dict) -> bool:
    return group["type"] == "variant"


def is_estate_or_variant(group: dict) -> bool:
    return group["type"] in {"estate", "variant"}


def estate_modifier_name(group: dict) -> str:
    return f"tv_academy_debate_royal_{group['key']}_modifier"


def price_loc_key(price: dict) -> str:
    return loc_key("TV_ACADEMY_DEBATE_PRICE", price["key"])


def price_option_loc_key(event_num: int, opt: str, price: dict) -> str:
    return f"{EVENT_NS}.{event_num}.{opt}_{price['key']}"


def group_loc_key(group: dict) -> str:
    return loc_key("TV_ACADEMY_DEBATE_GROUP", group["key"])


def group_tt_key(group: dict) -> str:
    return loc_key("TV_ACADEMY_DEBATE_GROUP", group["key"]) + "_TT"


def issue_progressive_var(issue: dict) -> str:
    return f"tv_academy_debate_{issue['key']}_progressive"


def issue_conservative_var(issue: dict) -> str:
    return f"tv_academy_debate_{issue['key']}_conservative"


def sanitize_id(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value).strip("_")


def action_triggers(data: dict) -> list[dict]:
    by_key = issue_by_key(data)
    result: list[dict] = []
    for issue_key, trigger_groups in (data.get("action_triggers") or {}).items():
        issue = by_key[issue_key]
        for direction in ("positive", "negative"):
            for idx, trigger in enumerate(trigger_groups.get(direction, []), start=1):
                entry = dict(trigger)
                entry["issue_key"] = issue_key
                entry["issue_id"] = int(issue["id"])
                entry["direction"] = direction
                entry["idx"] = idx
                entry["context"] = action_trigger_context(entry)
                result.append(entry)
    return result


def action_trigger_context(trigger: dict) -> str:
    hook = trigger["hook"]
    condition = trigger["condition"]
    if hook in {"on_work_of_art_created", "on_work_of_art_destroyed"}:
        return f"{hook}_owner"
    if hook == "on_work_of_art_looted":
        return f"{hook}_old_owner"
    if hook in {"on_location_occupied", "on_siege_won"}:
        return f"{hook}_owner"
    if hook == "on_took_location_in_peace_treaty":
        if condition.startswith("gain_"):
            return f"{hook}_winner"
        if condition.startswith("lose_"):
            return f"{hook}_loser"
    if hook == "on_war_declared":
        return f"{hook}_actor"
    return hook


def action_contexts(data: dict) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for trigger in action_triggers(data):
        context = trigger["context"]
        if context not in seen:
            seen.add(context)
            result.append(context)
    return result


def action_trigger_effect_name(trigger: dict) -> str:
    parts = [
        "tv_academy_debate_action_trigger",
        trigger["issue_key"],
        trigger["direction"],
        sanitize_id(trigger["hook"]),
        str(trigger["idx"]),
    ]
    return "_".join(parts) + "_effect"


def action_context_effect_name(context: str) -> str:
    return f"tv_academy_debate_action_triggers_{sanitize_id(context)}_effect"


def generate_triggers(data: dict) -> str:
    script = "scripts/in_game/common/scripted_triggers/gen_tv_academy_philosophy_debate_triggers.py"
    lines: list[str] = [header(script).rstrip(), ""]

    emit(lines, 0, "tv_academy_debate_has_empty_seat_trigger = {")
    emit(lines, 1, "OR = {")
    for seat in SEATS:
        emit(lines, 2, f"NOT = {{ has_variable = {seat_group(seat)} }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_has_two_empty_seats_trigger = {")
    emit(lines, 1, "OR = {")
    for first in SEATS:
        for second in SEATS:
            if second <= first:
                continue
            emit(lines, 2, "AND = {")
            emit(lines, 3, f"NOT = {{ has_variable = {seat_group(first)} }}")
            emit(lines, 3, f"NOT = {{ has_variable = {seat_group(second)} }}")
            emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_has_neutral_seated_group_trigger = {")
    emit(lines, 1, "OR = {")
    for seat in SEATS:
        emit(lines, 2, f"{var_eq(seat_stance(seat), STANCE_NEUTRAL)}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_has_seated_group_that_can_leave_trigger = {")
    emit(lines, 1, "OR = {")
    for seat in SEATS:
        emit(lines, 2, "AND = {")
        emit(lines, 3, f"has_variable = {seat_group(seat)}")
        emit(lines, 3, f"NOT = {{ {var_eq(seat_group(seat), 18)} }}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for group in groups(data):
        key = group["key"]
        emit(lines, 0, f"tv_academy_debate_group_{key}_not_in_current_debate_trigger = {{")
        emit(lines, 1, group_condition(group, "seated", negated=True))
        emit(lines, 1, group_condition(group, "left", negated=True))
        if group["type"] == "estate":
            for variant_key in base_estate_group_keys(data, key):
                emit(lines, 1, f"NOT = {{ has_variable = {group_var(variant_key, 'seated')} }}")
                emit(lines, 1, f"NOT = {{ has_variable = {group_var(variant_key, 'left')} }}")
        elif is_variant(group):
            base = group.get("base_group")
            if base and base != "mixed_minor_estates":
                emit(lines, 1, f"NOT = {{ has_variable = {group_var(base, 'seated')} }}")
                emit(lines, 1, f"NOT = {{ has_variable = {group_var(base, 'left')} }}")
        emit(lines, 0, "}")
        emit(lines)

        emit(lines, 0, f"tv_academy_debate_group_{key}_available_trigger = {{")
        emit(lines, 1, f"tv_academy_debate_group_{key}_not_in_current_debate_trigger = yes")
        gtype = group["type"]
        if gtype == "estate":
            emit(lines, 1, f"country_has_estate = estate_type:{group['estate']}")
        elif key == "scholarly_community":
            emit(lines, 1, "country_has_estate = estate_type:burghers_estate")
            emit(lines, 1, "average_country_literacy > 50")
        elif key == "public_opinion":
            emit(lines, 1, "country_has_estate = estate_type:peasants_estate")
            emit(lines, 1, "has_policy = no_censorship")
        elif key == "court_bureaucrats":
            emit(lines, 1, "country_has_estate = estate_type:nobles_estate")
            emit(lines, 1, "any_current_bureaucracy = { always = yes }")
        elif key == "maritime_merchants":
            emit(lines, 1, "country_has_estate = estate_type:burghers_estate")
            emit(lines, 1, "societal_value:land_vs_naval > 50")
        elif key == "professional_military":
            emit(lines, 1, "country_has_estate = estate_type:nobles_estate")
            emit(lines, 1, "societal_value:quality_vs_quantity < -50")
        elif key == "religious_reformers":
            emit(lines, 1, "country_has_estate = estate_type:clergy_estate")
            emit(lines, 1, "religion.group = religion_group:christian")
            emit(lines, 1, "is_situation_active = situation:reformation")
        elif key == "local_autonomy":
            emit(lines, 1, "country_has_estate = estate_type:peasants_estate")
            emit(lines, 1, "societal_value:centralization_vs_decentralization > 50")
        elif key == "minorities":
            emit(lines, 1, "OR = {")
            for base_key, estate in (("tribes", "tribes_estate"), ("dhimmi", "dhimmi_estate"), ("cossacks", "cossacks_estate")):
                emit(lines, 2, "AND = {")
                emit(lines, 3, f"country_has_estate = estate_type:{estate}")
                emit(lines, 3, f"tv_academy_debate_group_{base_key}_not_in_current_debate_trigger = yes")
                emit(lines, 2, "}")
            emit(lines, 1, "}")
            emit(lines, 1, "any_owned_location = { dominant_culture = { is_accepted_in = root } }")
        elif key == "artists":
            emit(lines, 1, "any_character = { is_alive = yes is_artist = yes }")
        elif key == "foreign_power":
            emit(lines, 1, "any_country = {")
            emit(lines, 2, "OR = {")
            emit(lines, 3, "is_allied_with = { target = root }")
            emit(lines, 3, "is_neighbor_of = root")
            emit(lines, 3, "is_rival_of = root")
            emit(lines, 3, "is_at_war_with = root")
            emit(lines, 2, "}")
            emit(lines, 1, "}")
        elif key == "great_scientist":
            emit(lines, 1, "tv_academy_debate_great_scientist_available_for_seat_trigger = yes")
        emit(lines, 0, "}")
        emit(lines)

        for stance, value in (("supports", STANCE_SUPPORT), ("opposes", STANCE_OPPOSE), ("neutral_on", STANCE_NEUTRAL)):
            emit(lines, 0, f"tv_academy_debate_group_{key}_{stance}_current_issue_trigger = {{")
            if group_positions(data, key).get("dynamic"):
                emit(lines, 1, "always = no")
            else:
                stance_key = {"supports": "support", "opposes": "oppose", "neutral_on": "neutral"}[stance]
                emit_current_issue_or(lines, 1, data, group_positions(data, key).get(stance_key, []))
            emit(lines, 0, "}")
            emit(lines)

    emit(lines, 0, "tv_academy_debate_great_scientist_exists_trigger = {")
    emit(lines, 1, "has_variable = tv_academy_leader_char")
    emit(lines, 1, "var:tv_academy_leader_char ?= {")
    emit(lines, 2, "is_alive = yes")
    emit(lines, 2, "OR = {")
    for trait in ("tv_great_scientist_1", "tv_great_scientist_2", "tv_great_scientist_3"):
        emit(lines, 3, f"has_trait = {trait}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_great_scientist_available_for_seat_trigger = {")
    emit(lines, 1, "tv_academy_debate_great_scientist_exists_trigger = yes")
    emit(lines, 1, "NOT = { has_variable = tv_academy_debate_great_scientist_seated }")
    emit(lines, 1, "tv_academy_debate_has_empty_seat_trigger = yes")
    emit(lines, 0, "}")
    emit(lines)

    for name, expr in (
        ("dip_at_least_80", "dip >= 80"),
        ("dip_at_most_30", "dip <= 30"),
        ("dip_between_30_and_80", "dip > 30\n\t\tdip < 80"),
    ):
        emit(lines, 0, f"tv_academy_debate_great_scientist_{name}_trigger = {{")
        emit(lines, 1, "tv_academy_debate_great_scientist_exists_trigger = yes")
        emit(lines, 1, "var:tv_academy_leader_char ?= {")
        for part in expr.splitlines():
            emit(lines, 2, part.strip())
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)

    gen_defection_condition_triggers(lines, data)
    gen_world_debate_triggers(lines, data)

    return "\n".join(lines).rstrip() + "\n"


def gen_defection_condition_triggers(lines: list[str], data: dict) -> None:
    for group in groups(data):
        key = group["key"]
        emit(lines, 0, f"tv_academy_debate_group_{key}_positive_defection_condition_trigger = {{")
        emit_defection_condition(lines, 1, group, positive=True)
        emit(lines, 0, "}")
        emit(lines)
        emit(lines, 0, f"tv_academy_debate_group_{key}_negative_defection_condition_trigger = {{")
        emit_defection_condition(lines, 1, group, positive=False)
        emit(lines, 0, "}")
        emit(lines)


def gen_world_debate_triggers(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_world_debate_country_has_academy_trigger = {")
    emit(lines, 1, "has_variable = tv_academy_io_member")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_country_can_participate_trigger = {")
    emit(lines, 1, "tv_academy_world_debate_country_has_academy_trigger = yes")
    emit(lines, 1, "var:tv_academy_debate_current_node_type ?= 2")
    emit(lines, 1, "tv_academy_philosophy_has_current_issue_trigger = yes")
    emit(lines, 1, "situation:tv_academy_world_debate_situation = {")
    emit(lines, 2, f"has_variable = {WORLD_ACTIVE_VAR}")
    emit(lines, 2, f"has_variable = {WORLD_ISSUE_VAR}")
    emit(lines, 1, "}")
    emit(lines, 1, f"var:tv_academy_philosophy_current ?= situation:tv_academy_world_debate_situation.var:{WORLD_ISSUE_VAR}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_country_supports_current_issue_trigger = {")
    emit(lines, 1, "OR = {")
    for issue in issues(data):
        emit(lines, 2, "AND = {")
        emit(lines, 3, f"situation:tv_academy_world_debate_situation = {{ var:{WORLD_ISSUE_VAR} ?= {issue['id']} }}")
        emit(lines, 3, f"has_embraced_institution = institution:{issue['institution']}")
        emit(lines, 2, "}")
        emit(lines, 2, "AND = {")
        emit(lines, 3, f"situation:tv_academy_world_debate_situation = {{ var:{WORLD_ISSUE_VAR} ?= {issue['id']} }}")
        emit(lines, 3, f"has_variable = {issue_progressive_var(issue)}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_country_opposes_current_issue_trigger = {")
    emit(lines, 1, "OR = {")
    for issue in issues(data):
        emit(lines, 2, "AND = {")
        emit(lines, 3, f"situation:tv_academy_world_debate_situation = {{ var:{WORLD_ISSUE_VAR} ?= {issue['id']} }}")
        emit(lines, 3, f"has_variable = {issue_conservative_var(issue)}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def gen_remove_group_seated(lines: list[str], level: int, group_id_expr: str, data: dict) -> None:
    for idx, group in enumerate(groups(data)):
        emit(lines, level, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, level + 1, f"limit = {{ {group_id_expr} ?= {group['id']} }}")
        emit(lines, level + 1, f"remove_variable = {group_var(group['key'], 'seated')}")
        if group["key"] == "great_scientist":
            emit(lines, level + 1, "remove_variable = tv_academy_debate_great_scientist_seated")
        emit(lines, level, "}")


def gen_set_group_seated(lines: list[str], level: int, data: dict) -> None:
    for idx, group in enumerate(groups(data)):
        emit(lines, level, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, level + 1, f"limit = {{ {var_eq(EVENT_GROUP, group['id'])} }}")
        emit(lines, level + 1, f"set_variable = {{ name = {group_var(group['key'], 'seated')} value = 1 }}")
        if group["key"] == "great_scientist":
            emit(lines, level + 1, "set_variable = { name = tv_academy_debate_great_scientist_seated value = 1 }")
        emit(lines, level, "}")


def gen_group_change_tooltip(lines: list[str], level: int, data: dict, change: str) -> None:
    key_fn = group_seated_tooltip_key if change == "seated" else group_left_tooltip_key
    for idx, group in enumerate(groups(data)):
        emit(lines, level, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, level + 1, f"limit = {{ {var_eq(EVENT_GROUP, group['id'])} }}")
        emit(lines, level + 1, "custom_description = {")
        emit(lines, level + 2, f"text = {key_fn(group)}")
        emit(lines, level + 1, "}")
        emit(lines, level, "}")


def emit_owned_academy_io_limit(lines: list[str], level: int, leader_expr: str = "root") -> None:
    emit(lines, level, "limit = {")
    emit(lines, level + 1, "international_organization_type = international_organization_type:tv_academy_of_sciences")
    emit(lines, level + 1, f"leader_country ?= {leader_expr}")
    emit(lines, level, "}")


def emit_owned_academy_io_trigger(lines: list[str], level: int) -> None:
    emit(lines, level, "any_international_organizations_member_of = {")
    emit(lines, level + 1, "international_organization_type = international_organization_type:tv_academy_of_sciences")
    emit(lines, level + 1, "leader_country ?= root")
    emit(lines, level, "}")


def emit_local_debate_progress_threshold(lines: list[str], level: int, operator: str, value: int) -> None:
    emit(lines, level, "any_international_organizations_member_of = {")
    emit(lines, level + 1, "international_organization_type = international_organization_type:tv_academy_of_sciences")
    emit(lines, level + 1, "leader_country ?= root")
    emit(lines, level + 1, f"var:{LOCAL_DEBATE_PROGRESS_VAR} {operator} {value}")
    emit(lines, level, "}")


def emit_change_local_debate_progress_effect(lines: list[str], level: int, value_expr: str) -> None:
    emit(lines, level, f"tv_academy_debate_change_local_progress_effect = {{ value = {value_expr} }}")


def gen_local_debate_progress_effects(lines: list[str]) -> None:
    emit(lines, 0, "tv_academy_debate_change_local_progress_effect = {")
    emit(lines, 1, "save_scope_as = tv_academy_debate_progress_owner")
    emit(lines, 1, "custom_description = {")
    emit(lines, 2, "text = tv_academy_debate_change_local_progress_text")
    emit(lines, 2, "value = $value$")
    emit(lines, 2, "every_international_organizations_member_of = {")
    emit_owned_academy_io_limit(lines, 3, leader_expr="scope:tv_academy_debate_progress_owner")
    emit(lines, 3, f"change_variable = {{ name = {LOCAL_DEBATE_PROGRESS_VAR} add = $value$ }}")
    emit(lines, 3, f"clamp_variable = {{ name = {LOCAL_DEBATE_PROGRESS_VAR} min = 0 max = 100 }}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_set_local_progress_effect = {")
    emit(lines, 1, "save_scope_as = tv_academy_debate_progress_owner")
    emit(lines, 1, "every_international_organizations_member_of = {")
    emit_owned_academy_io_limit(lines, 2, leader_expr="scope:tv_academy_debate_progress_owner")
    emit(lines, 2, f"set_local_variable = {{ name = {LOCAL_DEBATE_PROGRESS_DELTA_LOCAL} value = $value$ }}")
    emit(lines, 2, f"change_local_variable = {{ name = {LOCAL_DEBATE_PROGRESS_DELTA_LOCAL} subtract = var:{LOCAL_DEBATE_PROGRESS_VAR} }}")
    emit(lines, 2, "leader_country ?= {")
    emit_change_local_debate_progress_effect(lines, 3, f"local_var:{LOCAL_DEBATE_PROGRESS_DELTA_LOCAL}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def generate_effects(data: dict) -> str:
    script = "scripts/in_game/common/scripted_effects/gen_tv_academy_philosophy_debate_effects.py"
    lines: list[str] = [header(script, PHILOSOPHY_DEBATE_DATA_SOURCES).rstrip(), ""]
    settings = data["settings"]

    gen_cleanup_effects(lines, data)
    gen_issue_accept_effects(lines, data)
    gen_stance_effects(lines, data)
    gen_selection_effects(lines, data)
    gen_seat_effects(lines, data)
    gen_monthly_tick_effects(lines, data)
    gen_defection_effects(lines, data)
    gen_result_effects(lines, data)
    gen_endpoint_effects(lines, data)
    gen_action_trigger_effects(lines, data)
    gen_world_debate_effects(lines, data)

    emit(lines, 0, "tv_academy_philosophy_apply_monthly_debate_drift_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = {")
    emit(lines, 3, "var:tv_academy_philosophy_phase ?= 1")
    emit(lines, 3, "var:tv_academy_debate_current_node_type ?= 1")
    emit(lines, 3, "tv_academy_philosophy_has_current_issue_trigger = yes")
    emit(lines, 3, "NOT = { tv_academy_philosophy_current_issue_embraced_trigger = yes }")
    emit(lines, 3, f"NOT = {{ has_variable = {PENDING_RESULT_VAR} }}")
    emit(lines, 3, "NOT = { has_variable = tv_academy_philosophy_recess_notice_pending }")
    emit(lines, 2, "}")
    emit(lines, 2, f"trigger_event_silently = {{ id = {EVENT_NS}.1 days = 1 }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    return "\n".join(lines).rstrip() + "\n"


def gen_cleanup_effects(lines: list[str], data: dict) -> None:
    settings = data["settings"]
    runtime_vars = [
        EVENT_GROUP, EVENT_GROUP_2, EVENT_STANCE, EVENT_STANCE_2, EVENT_SEAT, EVENT_SEAT_2, EVENT_PRICE,
        MONTHLY_DELTA, SEAT_CONTRIB,
        AUTO_STANCE_SUPPORT_VAR, AUTO_STANCE_OPPOSE_VAR, AUTO_STANCE_NEUTRAL_VAR, AUTO_SEAT_VACATED_VAR,
        "tv_academy_debate_left_count", "tv_academy_debate_right_count",
        "tv_academy_debate_royal_option_1_group",
        "tv_academy_debate_royal_option_2_group",
        "tv_academy_debate_royal_option_3_group",
        "tv_academy_debate_recent_war_won",
        "tv_academy_debate_recent_war_lost",
    ]
    emit(lines, 0, "tv_academy_debate_clear_event_state_effect = {")
    for var in runtime_vars:
        emit(lines, 1, f"remove_variable = {var}")
    emit(lines, 0, "}")
    emit(lines)

    gen_local_debate_progress_effects(lines)

    emit(lines, 0, "tv_academy_debate_clear_all_seats_effect = {")
    for seat in SEATS:
        emit(lines, 1, f"tv_academy_debate_clear_seat_{seat}_effect = yes")
    for group in groups(data):
        for suffix in ("seated", "left"):
            emit(lines, 1, f"remove_variable = {group_var(group['key'], suffix)}")
    emit(lines, 1, "remove_variable = tv_academy_debate_great_scientist_seated")
    emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_initialize_global_maps_effect = {")
    for group in groups(data):
        if not is_estate_or_variant(group):
            continue
        emit(lines, 1, f"remove_from_global_variable_map = {{ name = {GROUP_ESTATE_MAP} key = {group['id']} }}")
        emit(lines, 1, f"add_to_global_variable_map = {{ name = {GROUP_ESTATE_MAP} key = {group['id']} value = estate_type:{group['base_estate']} }}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_initialize_debate_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_all_seats_effect = yes")
    emit(lines, 1, f"tv_academy_debate_set_local_progress_effect = {{ value = {settings['initial_progress']} }}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_cleanup_debate_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_all_seats_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_remove_group_seated_by_id_effect = {")
    gen_remove_group_seated(lines, 1, "$group$", data)
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_mark_selected_group_seated_effect = {")
    gen_set_group_seated(lines, 1, data)
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_selected_group_seated_tooltip_effect = {")
    gen_group_change_tooltip(lines, 1, data, "seated")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_selected_group_left_tooltip_effect = {")
    gen_group_change_tooltip(lines, 1, data, "left")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_clear_seat_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {seat_group('$seat$')} }}")
    emit(lines, 2, f"tv_academy_debate_remove_group_seated_by_id_effect = {{ group = var:{seat_group('$seat$')} }}")
    emit(lines, 1, "}")
    for var in (seat_group("$seat$"), seat_stance("$seat$"), seat_cooldown("$seat$"), seat_artist("$seat$"), seat_foreign("$seat$"), seat_scientist("$seat$")):
        emit(lines, 1, f"remove_variable = {var}")
    emit(lines, 0, "}")
    emit(lines)

    for seat in SEATS:
        emit(lines, 0, f"tv_academy_debate_clear_seat_{seat}_effect = {{")
        emit(lines, 1, f"tv_academy_debate_clear_seat_effect = {{ seat = {seat} }}")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "tv_academy_debate_mark_selected_group_left_effect = {")
    for idx, group in enumerate(groups(data)):
        emit(lines, 1, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, group['id'])} }}")
        emit(lines, 2, f"set_variable = {{ name = {group_var(group['key'], 'left')} value = 1 }}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_clear_selected_seat_effect = {")
    for seat in SEATS:
        emit(lines, 1, "if = {" if seat == 1 else "else_if = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_SEAT, seat)} }}")
        emit(lines, 2, f"tv_academy_debate_clear_seat_{seat}_effect = yes")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def gen_issue_accept_effects(lines: list[str], data: dict) -> None:
    for issue in issues(data):
        key = issue["key"]
        emit(lines, 0, f"tv_academy_philosophy_accept_{key}_effect = {{")
        emit(lines, 1, f"every_owned_location = {{ change_institution_progress = {{ type = institution:{issue['institution']} value = 100 }} }}")
        emit(lines, 1, f"research_advance = advance_type:{issue['advance']}")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "tv_academy_philosophy_apply_pending_acceptance_effect = {")
    for idx, issue in enumerate(issues(data)):
        emit(lines, 1, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, 2, f"limit = {{ var:{PENDING_ISSUE_VAR} ?= {issue['id']} }}")
        emit(lines, 2, f"tv_academy_philosophy_accept_{issue['key']}_effect = yes")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_philosophy_clear_debate_result_effect = {")
    for var in (PENDING_RESULT_VAR, PENDING_ISSUE_VAR, PENDING_KIND_VAR, MONTHLY_DELTA, SEAT_CONTRIB):
        emit(lines, 1, f"remove_variable = {var}")
    emit(lines, 0, "}")
    emit(lines)


def gen_stance_effects(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_debate_set_stance_for_selected_group_effect = {")
    emit(lines, 1, f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_NEUTRAL} }}")
    for idx, group in enumerate(groups(data)):
        emit(lines, 1, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, group['id'])} }}")
        if group["key"] == "foreign_power":
            emit(lines, 2, "tv_academy_debate_set_selected_foreign_stance_effect = yes")
        else:
            pos = group_positions(data, group["key"])
            for stance_key, stance_value in (("support", STANCE_SUPPORT), ("oppose", STANCE_OPPOSE), ("neutral", STANCE_NEUTRAL)):
                issue_keys = pos.get(stance_key, [])
                if not issue_keys:
                    continue
                emit(lines, 2, "if = {")
                emit(lines, 3, "limit = {")
                emit_current_issue_or(lines, 4, data, issue_keys)
                emit(lines, 3, "}")
                emit(lines, 3, f"set_variable = {{ name = {EVENT_STANCE} value = {stance_value} }}")
                emit(lines, 2, "}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_set_selected_foreign_stance_effect = {")
    emit(lines, 1, f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_NEUTRAL} }}")
    emit(lines, 1, f"scope:{SELECTED_FOREIGN_SCOPE} = {{")
    emit(lines, 2, "if = {")
    emit(lines, 3, "limit = { is_rival_of = root }")
    emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_OPPOSE} }} }}")
    emit(lines, 2, "}")
    for issue in issues(data):
        emit(lines, 2, "else_if = {")
        emit(lines, 3, "limit = {")
        emit(lines, 4, f"root = {{ var:tv_academy_philosophy_current ?= {issue['id']} }}")
        emit(lines, 4, f"has_embraced_institution = institution:{issue['institution']}")
        emit(lines, 3, "}")
        emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }} }}")
        emit(lines, 2, "}")
    for issue in issues(data):
        emit(lines, 2, "else_if = {")
        emit(lines, 3, "limit = {")
        emit(lines, 4, f"root = {{ var:tv_academy_philosophy_current ?= {issue['id']} }}")
        emit(lines, 4, f"has_variable = {issue_conservative_var(issue)}")
        emit(lines, 3, "}")
        emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_OPPOSE} }} }}")
        emit(lines, 2, "}")
    for issue in issues(data):
        emit(lines, 2, "else_if = {")
        emit(lines, 3, "limit = {")
        emit(lines, 4, f"root = {{ var:tv_academy_philosophy_current ?= {issue['id']} }}")
        emit(lines, 4, f"has_variable = {issue_progressive_var(issue)}")
        emit(lines, 3, "}")
        emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }} }}")
        emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, "limit = { is_allied_with = { target = root } }")
    emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }} }}")
    emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, "limit = { opinion = { target = root value >= 1 } }")
    emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }} }}")
    emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, "limit = { opinion = { target = root value < 0 } }")
    emit(lines, 3, f"root = {{ set_variable = {{ name = {EVENT_STANCE} value = {STANCE_OPPOSE} }} }}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def gen_selection_effects(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_debate_pick_price_effect = {")
    emit(lines, 1, "random_list = {")
    for price in data["prices"]:
        emit(lines, 2, f"1 = {{ set_variable = {{ name = {EVENT_PRICE} value = {data['prices'].index(price) + 1} }} }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for mode, trigger_suffix in (
        ("any", "available"),
        ("support", "supports_current_issue"),
        ("oppose", "opposes_current_issue"),
        ("neutral", "neutral_on_current_issue"),
        ("royal_support", "supports_current_issue"),
    ):
        emit(lines, 0, f"tv_academy_debate_pick_unseated_{mode}_group_effect = {{")
        emit(lines, 1, "random_list = {")
        for group in groups(data):
            if group["key"] == "great_scientist":
                continue
            if mode == "royal_support" and not is_estate_or_variant(group):
                continue
            if mode in {"support", "oppose", "neutral", "royal_support"} and group["key"] == "foreign_power":
                continue
            emit(lines, 2, "1 = {")
            emit(lines, 3, "trigger = {")
            emit(lines, 4, f"tv_academy_debate_group_{group['key']}_available_trigger = yes")
            if mode != "any":
                emit(lines, 4, f"tv_academy_debate_group_{group['key']}_{trigger_suffix}_trigger = yes")
            emit(lines, 3, "}")
            emit(lines, 3, f"set_variable = {{ name = {EVENT_GROUP} value = {group['id']} }}")
            emit(lines, 2, "}")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "tv_academy_debate_pick_seated_group_effect = {")
    emit(lines, 1, "random_list = {")
    for seat in SEATS:
        emit(lines, 2, "1 = {")
        emit(lines, 3, f"trigger = {{ has_variable = {seat_group(seat)} NOT = {{ {var_eq(seat_group(seat), 18)} }} }}")
        emit(lines, 3, f"set_variable = {{ name = {EVENT_SEAT} value = {seat} }}")
        emit(lines, 3, f"set_variable = {{ name = {EVENT_GROUP} value = var:{seat_group(seat)} }}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_pick_neutral_seated_group_effect = {")
    emit(lines, 1, "random_list = {")
    for seat in SEATS:
        emit(lines, 2, "1 = {")
        emit(lines, 3, f"trigger = {{ {var_eq(seat_stance(seat), STANCE_NEUTRAL)} }}")
        emit(lines, 3, f"set_variable = {{ name = {EVENT_SEAT} value = {seat} }}")
        emit(lines, 3, f"set_variable = {{ name = {EVENT_GROUP} value = var:{seat_group(seat)} }}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    gen_prepare_event_effects(lines, data)


def gen_prepare_event_effects(lines: list[str], data: dict) -> None:
    prep_specs = [
        ("join", "tv_academy_debate_pick_unseated_any_group_effect", f"{EVENT_NS}.100", False, None),
        ("support_price_join", "tv_academy_debate_pick_unseated_support_group_effect", f"{EVENT_NS}.102", True, None),
        ("oppose_price_stay_out", "tv_academy_debate_pick_unseated_oppose_group_effect", f"{EVENT_NS}.103", True, None),
        ("scientist_sways_support", "tv_academy_debate_pick_unseated_support_group_effect", f"{EVENT_NS}.105", False, "tv_academy_debate_great_scientist_dip_at_least_80_trigger = yes"),
        ("scientist_angers_oppose", "tv_academy_debate_pick_unseated_oppose_group_effect", f"{EVENT_NS}.106", False, "tv_academy_debate_great_scientist_dip_at_most_30_trigger = yes"),
        ("scientist_bargain_support", "tv_academy_debate_pick_unseated_support_group_effect", f"{EVENT_NS}.107", True, "tv_academy_debate_great_scientist_dip_between_30_and_80_trigger = yes"),
        ("neutral_price_support", "tv_academy_debate_pick_neutral_seated_group_effect", f"{EVENT_NS}.111", True, None),
        ("neutral_price_not_oppose", "tv_academy_debate_pick_neutral_seated_group_effect", f"{EVENT_NS}.112", True, None),
        ("scientist_sways_neutral", "tv_academy_debate_pick_neutral_seated_group_effect", f"{EVENT_NS}.113", False, "tv_academy_debate_great_scientist_dip_at_least_80_trigger = yes"),
        ("scientist_angers_neutral", "tv_academy_debate_pick_neutral_seated_group_effect", f"{EVENT_NS}.114", False, "tv_academy_debate_great_scientist_dip_at_most_30_trigger = yes"),
        ("scientist_bargain_neutral", "tv_academy_debate_pick_neutral_seated_group_effect", f"{EVENT_NS}.115", True, "tv_academy_debate_great_scientist_dip_between_30_and_80_trigger = yes"),
    ]
    for key, picker, event_id, price, extra_trigger in prep_specs:
        emit(lines, 0, f"tv_academy_debate_prepare_{key}_event_effect = {{")
        emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
        if extra_trigger:
            emit(lines, 1, "if = {")
            emit(lines, 2, f"limit = {{ {extra_trigger} }}")
            emit(lines, 2, f"{picker} = yes")
            emit(lines, 1, "}")
        else:
            emit(lines, 1, f"{picker} = yes")
        if price:
            emit(lines, 1, "if = {")
            emit(lines, 2, f"limit = {{ has_variable = {EVENT_GROUP} }}")
            emit(lines, 2, "tv_academy_debate_pick_price_effect = yes")
            emit(lines, 1, "}")
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {EVENT_GROUP} }}")
        if picker.startswith("tv_academy_debate_pick_neutral"):
            emit(lines, 2, f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_NEUTRAL} }}")
        else:
            emit(lines, 2, "tv_academy_debate_prepare_selected_special_scope_effect = yes")
            emit(lines, 2, "tv_academy_debate_set_stance_for_selected_group_effect = yes")
            emit(lines, 2, "tv_academy_debate_pick_seat_for_selected_stance_effect = yes")
        emit(lines, 2, f"trigger_event_non_silently = {{ id = {event_id} days = 1 }}")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "tv_academy_debate_prepare_leave_event_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
    emit(lines, 1, "tv_academy_debate_pick_seated_group_effect = yes")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {EVENT_GROUP} has_variable = {EVENT_SEAT} }}")
    emit(lines, 2, f"trigger_event_non_silently = {{ id = {EVENT_NS}.101 days = 1 }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_prepare_neutral_decides_event_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
    emit(lines, 1, "tv_academy_debate_pick_neutral_seated_group_effect = yes")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {EVENT_GROUP} has_variable = {EVENT_SEAT} }}")
    emit(lines, 2, f"trigger_event_non_silently = {{ id = {EVENT_NS}.110 days = 1 }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_prepare_great_scientist_requests_seat_event_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = { tv_academy_debate_great_scientist_available_for_seat_trigger = yes }")
    great = next(g for g in groups(data) if g["key"] == "great_scientist")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_GROUP} value = {great['id']} }}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }}")
    emit(lines, 2, "tv_academy_debate_prepare_selected_special_scope_effect = yes")
    emit(lines, 2, "tv_academy_debate_pick_seat_for_selected_stance_effect = yes")
    emit(lines, 2, f"trigger_event_non_silently = {{ id = {EVENT_NS}.108 days = 1 }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_prepare_royal_appointment_event_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
    for slot in range(1, 4):
        emit(lines, 1, "random_list = {")
        for group in groups(data):
            if not is_estate_or_variant(group):
                continue
            emit(lines, 2, "1 = {")
            emit(lines, 3, "trigger = {")
            emit(lines, 4, f"tv_academy_debate_group_{group['key']}_available_trigger = yes")
            emit(lines, 4, f"tv_academy_debate_group_{group['key']}_supports_current_issue_trigger = yes")
            for prev in range(1, slot):
                emit(lines, 4, f"NOT = {{ var:tv_academy_debate_royal_option_{prev}_group ?= {group['id']} }}")
            emit(lines, 3, "}")
            emit(lines, 3, f"set_variable = {{ name = tv_academy_debate_royal_option_{slot}_group value = {group['id']} }}")
            emit(lines, 2, "}")
        emit(lines, 1, "}")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = { has_variable = tv_academy_debate_royal_option_1_group }")
    emit(lines, 2, f"trigger_event_non_silently = {{ id = {EVENT_NS}.109 days = 1 }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_prepare_quarrel_event_effect = {")
    emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
    emit(lines, 1, "tv_academy_debate_pick_unseated_support_group_effect = yes")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {EVENT_GROUP} }}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_GROUP_2} value = var:{EVENT_GROUP} }}")
    emit(lines, 2, f"remove_variable = {EVENT_GROUP}")
    emit(lines, 2, "tv_academy_debate_pick_unseated_oppose_group_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {EVENT_GROUP} has_variable = {EVENT_GROUP_2} }}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_SEAT_2} value = var:{EVENT_GROUP} }}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_GROUP} value = var:{EVENT_GROUP_2} }}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_GROUP_2} value = var:{EVENT_SEAT_2} }}")
    emit(lines, 2, f"remove_variable = {EVENT_SEAT_2}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }}")
    emit(lines, 2, f"set_variable = {{ name = {EVENT_STANCE_2} value = {STANCE_SUPPORT} }}")
    emit(lines, 2, f"trigger_event_non_silently = {{ id = {EVENT_NS}.104 days = 1 }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def gen_seat_effects(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_debate_prepare_selected_special_scope_effect = {")
    emit(lines, 1, f"clear_saved_scope = {SELECTED_ARTIST_SCOPE}")
    emit(lines, 1, f"clear_saved_scope = {SELECTED_FOREIGN_SCOPE}")
    emit(lines, 1, f"clear_saved_scope = {SELECTED_SCIENTIST_SCOPE}")
    artists = next(g for g in groups(data) if g["key"] == "artists")
    foreign = next(g for g in groups(data) if g["key"] == "foreign_power")
    great = next(g for g in groups(data) if g["key"] == "great_scientist")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, artists['id'])} }}")
    emit(lines, 2, "random_character = {")
    emit(lines, 3, "limit = { is_alive = yes is_artist = yes }")
    emit(lines, 3, f"save_scope_as = {SELECTED_ARTIST_SCOPE}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 1, "else_if = {")
    emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, foreign['id'])} }}")
    emit(lines, 2, "ordered_country = {")
    emit(lines, 3, "limit = {")
    emit(lines, 4, "OR = {")
    emit(lines, 5, "is_allied_with = { target = root }")
    emit(lines, 5, "is_neighbor_of = root")
    emit(lines, 5, "is_rival_of = root")
    emit(lines, 5, "is_at_war_with = root")
    emit(lines, 4, "}")
    emit(lines, 3, "}")
    emit(lines, 3, "order_by = great_power_score")
    emit(lines, 3, "max = 1")
    emit(lines, 3, "check_range_bounds = no")
    emit(lines, 3, f"save_scope_as = {SELECTED_FOREIGN_SCOPE}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 1, "else_if = {")
    emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, great['id'])} }}")
    emit(lines, 2, f"var:tv_academy_leader_char ?= {{ save_scope_as = {SELECTED_SCIENTIST_SCOPE} }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_count_seated_sides_effect = {")
    emit(lines, 1, "set_variable = { name = tv_academy_debate_left_count value = 0 }")
    emit(lines, 1, "set_variable = { name = tv_academy_debate_right_count value = 0 }")
    for seat, side in ((2, "left"), (4, "left"), (3, "right"), (5, "right")):
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {seat_group(seat)} }}")
        emit(lines, 2, f"change_variable = {{ name = tv_academy_debate_{side}_count add = 1 }}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    def emit_empty_seat_random_list(level: int, seat_order: list[int]) -> None:
        emit(lines, level, "random_list = {")
        for seat in seat_order:
            emit(lines, level + 1, "1 = {")
            emit(lines, level + 2, f"trigger = {{ NOT = {{ has_variable = {seat_group(seat)} }} }}")
            emit(lines, level + 2, f"set_variable = {{ name = {EVENT_SEAT} value = {seat} }}")
            emit(lines, level + 1, "}")
        emit(lines, level, "}")

    def emit_any_empty_seat_limit(level: int, seat_order: list[int]) -> None:
        emit(lines, level, "OR = {")
        for seat in seat_order:
            emit(lines, level + 1, f"NOT = {{ has_variable = {seat_group(seat)} }}")
        emit(lines, level, "}")

    def pick_effect(name: str, preferred_seats: list[int], fallback_seats: list[int] | None = None) -> None:
        emit(lines, 0, f"{name} = {{")
        if fallback_seats:
            emit(lines, 1, "if = {")
            emit(lines, 2, "limit = {")
            emit_any_empty_seat_limit(3, preferred_seats)
            emit(lines, 2, "}")
            emit_empty_seat_random_list(2, preferred_seats)
            emit(lines, 1, "}")
            emit(lines, 1, "else = {")
            emit_empty_seat_random_list(2, fallback_seats)
            emit(lines, 1, "}")
        else:
            emit_empty_seat_random_list(1, preferred_seats)
        emit(lines, 0, "}")
        emit(lines)

    pick_effect("tv_academy_debate_pick_empty_right_seat_effect", [3, 5], [1, 2, 4])
    pick_effect("tv_academy_debate_pick_empty_left_seat_effect", [2, 4], [1, 3, 5])
    pick_effect("tv_academy_debate_pick_any_empty_seat_effect", [1, 2, 3, 4, 5])

    emit(lines, 0, "tv_academy_debate_pick_seat_for_selected_stance_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ {var_eq(EVENT_STANCE, STANCE_SUPPORT)} }}")
    emit(lines, 2, "tv_academy_debate_pick_empty_right_seat_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 1, "else_if = {")
    emit(lines, 2, f"limit = {{ {var_eq(EVENT_STANCE, STANCE_OPPOSE)} }}")
    emit(lines, 2, "tv_academy_debate_pick_empty_left_seat_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 1, "else = {")
    emit(lines, 2, "tv_academy_debate_count_seated_sides_effect = yes")
    emit(lines, 2, "if = {")
    emit(lines, 3, "limit = { var:tv_academy_debate_left_count < var:tv_academy_debate_right_count }")
    emit(lines, 3, "tv_academy_debate_pick_empty_left_seat_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, "limit = { var:tv_academy_debate_right_count < var:tv_academy_debate_left_count }")
    emit(lines, 3, "tv_academy_debate_pick_empty_right_seat_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, f"limit = {{ NOT = {{ has_variable = {seat_group(1)} }} }}")
    emit(lines, 3, f"set_variable = {{ name = {EVENT_SEAT} value = 1 }}")
    emit(lines, 2, "}")
    emit(lines, 2, "else = {")
    emit(lines, 3, "tv_academy_debate_pick_any_empty_seat_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_assign_selected_group_to_seat_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, foreign['id'])} }}")
    emit(lines, 2, "if = {")
    emit(lines, 3, f"limit = {{ NOT = {{ exists = scope:{SELECTED_FOREIGN_SCOPE} }} }}")
    emit(lines, 3, "tv_academy_debate_prepare_selected_special_scope_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 2, "tv_academy_debate_set_selected_foreign_stance_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ NOT = {{ has_variable = {EVENT_SEAT} }} }}")
    emit(lines, 2, "tv_academy_debate_pick_seat_for_selected_stance_effect = yes")
    emit(lines, 1, "}")
    for seat in SEATS:
        emit(lines, 1, "if = {" if seat == 1 else "else_if = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_SEAT, seat)} NOT = {{ has_variable = {seat_group(seat)} }} }}")
        emit(lines, 2, f"tv_academy_debate_assign_selected_group_to_specific_seat_effect = {{ seat = {seat} }}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_assign_selected_group_to_specific_seat_effect = {")
    emit(lines, 1, f"set_variable = {{ name = {seat_group('$seat$')} value = var:{EVENT_GROUP} }}")
    emit(lines, 1, f"set_variable = {{ name = {seat_stance('$seat$')} value = var:{EVENT_STANCE} }}")
    emit(lines, 1, f"set_variable = {{ name = {seat_cooldown('$seat$')} value = {data['settings']['defection_cooldown_months']} }}")
    emit(lines, 1, f"if = {{ limit = {{ exists = scope:{SELECTED_ARTIST_SCOPE} }} set_variable = {{ name = {seat_artist('$seat$')} value = scope:{SELECTED_ARTIST_SCOPE} }} }}")
    emit(lines, 1, f"if = {{ limit = {{ exists = scope:{SELECTED_FOREIGN_SCOPE} }} set_variable = {{ name = {seat_foreign('$seat$')} value = scope:{SELECTED_FOREIGN_SCOPE} }} }}")
    emit(lines, 1, f"if = {{ limit = {{ exists = scope:{SELECTED_SCIENTIST_SCOPE} }} set_variable = {{ name = {seat_scientist('$seat$')} value = scope:{SELECTED_SCIENTIST_SCOPE} }} }}")
    emit(lines, 1, "tv_academy_debate_mark_selected_group_seated_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_set_selected_neutral_stance_effect = {")
    emit(lines, 1, f"set_variable = {{ name = {EVENT_STANCE} value = $stance$ }}")
    for seat in SEATS:
        emit(lines, 1, ("if" if seat == 1 else "else_if") + " = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_SEAT, seat)} }}")
        emit(lines, 2, f"set_variable = {{ name = {seat_stance(seat)} value = $stance$ }}")
        emit(lines, 2, f"set_variable = {{ name = {seat_cooldown(seat)} value = {data['settings']['defection_cooldown_months']} }}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_set_selected_neutral_to_support_effect = {")
    emit(lines, 1, f"tv_academy_debate_set_selected_neutral_stance_effect = {{ stance = {STANCE_SUPPORT} }}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_set_selected_neutral_to_oppose_effect = {")
    emit(lines, 1, f"tv_academy_debate_set_selected_neutral_stance_effect = {{ stance = {STANCE_OPPOSE} }}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_apply_selected_price_effect = {")
    for idx, price in enumerate(data["prices"], 1):
        emit(lines, 1, ("if" if idx == 1 else "else_if") + " = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_PRICE, idx)} }}")
        for effect in price["effect"]:
            emit(lines, 2, effect)
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_apply_selected_royal_modifier_effect = {")
    for idx, group in enumerate(groups(data)):
        if not is_estate_or_variant(group):
            continue
        emit(lines, 1, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, 2, f"limit = {{ {var_eq(EVENT_GROUP, group['id'])} }}")
        emit(lines, 2, "add_country_modifier = {")
        emit(lines, 3, f"modifier = {estate_modifier_name(group)}")
        emit(lines, 3, "years = 5")
        emit(lines, 3, "mode = add_and_extend")
        emit(lines, 2, "}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for slot in range(1, 4):
        emit(lines, 0, f"tv_academy_debate_accept_royal_option_{slot}_effect = {{")
        emit(lines, 1, f"set_variable = {{ name = {EVENT_GROUP} value = var:tv_academy_debate_royal_option_{slot}_group }}")
        emit(lines, 1, f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }}")
        emit(lines, 1, "tv_academy_debate_apply_selected_royal_modifier_effect = yes")
        emit(lines, 1, "tv_academy_debate_pick_seat_for_selected_stance_effect = yes")
        emit(lines, 1, "tv_academy_debate_selected_group_seated_tooltip_effect = yes")
        emit(lines, 1, "tv_academy_debate_assign_selected_group_to_seat_effect = yes")
        emit(lines, 1, "tv_academy_debate_clear_event_state_effect = yes")
        emit(lines, 0, "}")
        emit(lines)


def contribution_value(group: dict, settings: dict) -> list[str]:
    base = settings["base_group_contribution"]
    if group["type"] == "estate":
        return [
            "value = {",
            f"\tvalue = {base}",
            "\tadd = {",
            f"\t\tvalue = \"estate_power(estate_type:{group['estate']})\"",
            f"\t\tmultiply = {settings['estate_power_multiplier']}",
            "\t}",
            "}",
        ]
    if group["type"] == "variant":
        return [
            "value = {",
            f"\tvalue = {base}",
            "\tadd = {",
            f"\t\tvalue = \"estate_power(estate_type:{group['base_estate']})\"",
            f"\t\tmultiply = {settings['variant_power_multiplier']}",
            "\t}",
            "}",
        ]
    if group["type"] == "artists":
        return [
            "value = {",
            f"\tvalue = {base}",
            "\tadd = {",
            "\t\tvalue = var:CURRENT_SEAT_ARTIST.artist_skill",
            f"\t\tmultiply = {settings['artist_skill_multiplier']}",
            "\t}",
            "}",
        ]
    if group["type"] == "foreign_power":
        return [
            "value = {",
            f"\tvalue = {base}",
            "\tadd = {",
            "\t\tvalue = var:CURRENT_SEAT_FOREIGN.great_power_score",
            "\t\tdivide = { value = great_power_score min = 1 }",
            f"\t\tmultiply = {settings['foreign_power_multiplier']}",
            "\t}",
            "}",
        ]
    if group["type"] == "great_scientist":
        return [
            "value = {",
            f"\tvalue = {base}",
            "\tadd = {",
            "\t\tvalue = var:tv_scientist_effective_adm",
            "\t\tdivide = 100",
            f"\t\tmultiply = {settings['great_scientist_adm_multiplier']}",
            "\t}",
            "}",
        ]
    return [f"value = {base}"]


def gen_monthly_tick_effects(lines: list[str], data: dict) -> None:
    settings = data["settings"]
    emit(lines, 0, "tv_academy_debate_monthly_tick_effect = {")
    for var in (AUTO_STANCE_SUPPORT_VAR, AUTO_STANCE_OPPOSE_VAR, AUTO_STANCE_NEUTRAL_VAR, AUTO_SEAT_VACATED_VAR):
        emit(lines, 1, f"remove_variable = {var}")
    emit(lines, 1, "tv_update_chief_scientist_effective_adm_effect = yes")
    emit(lines, 1, "tv_academy_debate_cleanup_invalid_special_seats_effect = yes")
    emit(lines, 1, "tv_academy_debate_decrement_cooldowns_effect = yes")
    emit(lines, 1, "tv_academy_debate_apply_monthly_progress_effect = yes")
    emit(lines, 1, "tv_academy_debate_apply_defections_effect = yes")
    emit(lines, 1, "random_list = {")
    emit(lines, 2, f"{settings['monthly_no_event_weight']} = {{ }}")
    emit(lines, 2, f"{settings['monthly_event_chance_weight']} = {{ tv_academy_debate_dispatch_monthly_seat_event_effect = yes }}")
    emit(lines, 1, "}")
    emit(lines, 1, "random_list = {")
    emit(lines, 2, f"{settings['monthly_no_event_weight']} = {{ }}")
    emit(lines, 2, f"{settings['monthly_event_chance_weight']} = {{ tv_academy_debate_dispatch_monthly_progress_event_effect = yes }}")
    emit(lines, 1, "}")
    emit(lines, 1, "tv_academy_philosophy_check_debate_endpoint_effect = yes")
    emit(lines, 1, "tv_academy_debate_dispatch_auto_stance_notifications_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_cleanup_invalid_special_seats_effect = {")
    for seat in SEATS:
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {seat_artist(seat)} NOT = {{ var:{seat_artist(seat)} ?= {{ is_alive = yes }} }} }}")
        emit(lines, 2, f"set_variable = {{ name = {AUTO_SEAT_VACATED_VAR} value = 1 }}")
        emit(lines, 2, f"tv_academy_debate_clear_seat_{seat}_effect = yes")
        emit(lines, 1, "}")
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {seat_scientist(seat)} NOT = {{ var:{seat_scientist(seat)} ?= {{ is_alive = yes }} }} }}")
        emit(lines, 2, f"set_variable = {{ name = {AUTO_SEAT_VACATED_VAR} value = 1 }}")
        emit(lines, 2, f"tv_academy_debate_clear_seat_{seat}_effect = yes")
        emit(lines, 1, "}")
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {seat_foreign(seat)} NOT = {{ country_exists = var:{seat_foreign(seat)} }} }}")
        emit(lines, 2, f"set_variable = {{ name = {AUTO_SEAT_VACATED_VAR} value = 1 }}")
        emit(lines, 2, f"tv_academy_debate_clear_seat_{seat}_effect = yes")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_decrement_cooldowns_effect = {")
    for seat in SEATS:
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ var:{seat_cooldown(seat)} > 0 }}")
        emit(lines, 2, f"change_variable = {{ name = {seat_cooldown(seat)} add = -1 }}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_apply_monthly_progress_effect = {")
    emit(lines, 1, "set_variable = { name = tv_academy_philosophy_monthly_delta value = 0 }")
    emit(lines, 1, "set_variable = {")
    emit(lines, 2, "name = tv_academy_debate_seat_contribution")
    emit(lines, 2, "value = {")
    emit(lines, 3, f"value = \"estate_power(estate_type:crown_estate)\"")
    emit(lines, 3, f"multiply = {settings['crown_contribution_multiplier']}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 1, "change_variable = { name = tv_academy_philosophy_monthly_delta add = var:tv_academy_debate_seat_contribution }")
    for seat in SEATS:
        emit(lines, 1, f"tv_academy_debate_apply_seat_{seat}_monthly_progress_effect = yes")
    emit_change_local_debate_progress_effect(lines, 1, f"var:{MONTHLY_DELTA}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_apply_seat_monthly_progress_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {seat_group('$seat$')} NOT = {{ {var_eq(seat_stance('$seat$'), STANCE_NEUTRAL)} }} }}")
    for idx, group in enumerate(groups(data)):
        emit(lines, 2, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, 3, f"limit = {{ {var_eq(seat_group('$seat$'), group['id'])} }}")
        value_lines = contribution_value(group, settings)
        emit(lines, 3, "set_variable = {")
        emit(lines, 4, f"name = {SEAT_CONTRIB}")
        for raw in value_lines:
            raw = raw.replace("CURRENT_SEAT_ARTIST", seat_artist("$seat$")).replace("CURRENT_SEAT_FOREIGN", seat_foreign("$seat$"))
            emit(lines, 4 + raw.count("\t"), raw.lstrip("\t"))
        emit(lines, 3, "}")
        emit(lines, 2, "}")
    emit(lines, 2, "if = {")
    emit(lines, 3, f"limit = {{ {var_eq(seat_stance('$seat$'), STANCE_OPPOSE)} }}")
    emit(lines, 3, f"change_variable = {{ name = {SEAT_CONTRIB} multiply = -1 }}")
    emit(lines, 2, "}")
    emit(lines, 2, f"change_variable = {{ name = {MONTHLY_DELTA} add = var:{SEAT_CONTRIB} }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for seat in SEATS:
        emit(lines, 0, f"tv_academy_debate_apply_seat_{seat}_monthly_progress_effect = {{")
        emit(lines, 1, f"tv_academy_debate_apply_seat_monthly_progress_effect = {{ seat = {seat} }}")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "tv_academy_debate_dispatch_monthly_seat_event_effect = {")
    emit(lines, 1, "random_list = {")
    for key, weight in data["event_weights"].items():
        prep = f"tv_academy_debate_prepare_{key}_event_effect"
        emit(lines, 2, f"{weight} = {{")
        emit(lines, 3, "trigger = {")
        if key in {"join", "support_price_join", "oppose_price_stay_out", "quarrel", "scientist_sways_support", "scientist_angers_oppose", "scientist_bargain_support", "great_scientist_requests_seat", "royal_appointment"}:
            emit(lines, 4, "tv_academy_debate_has_empty_seat_trigger = yes")
        if key == "quarrel":
            emit(lines, 4, "tv_academy_debate_has_two_empty_seats_trigger = yes")
        if key == "leave":
            emit(lines, 4, "tv_academy_debate_has_seated_group_that_can_leave_trigger = yes")
        if key.startswith("neutral") or key in {"scientist_sways_neutral", "scientist_angers_neutral", "scientist_bargain_neutral"}:
            emit(lines, 4, "tv_academy_debate_has_neutral_seated_group_trigger = yes")
        if key == "great_scientist_requests_seat":
            emit(lines, 4, "tv_academy_debate_great_scientist_available_for_seat_trigger = yes")
        if key == "scientist_sways_support":
            emit(lines, 4, "tv_academy_debate_great_scientist_dip_at_least_80_trigger = yes")
        if key == "scientist_angers_oppose":
            emit(lines, 4, "tv_academy_debate_great_scientist_dip_at_most_30_trigger = yes")
        if key == "scientist_bargain_support":
            emit(lines, 4, "tv_academy_debate_great_scientist_dip_between_30_and_80_trigger = yes")
        if key == "scientist_sways_neutral":
            emit(lines, 4, "tv_academy_debate_great_scientist_dip_at_least_80_trigger = yes")
        if key == "scientist_angers_neutral":
            emit(lines, 4, "tv_academy_debate_great_scientist_dip_at_most_30_trigger = yes")
        if key == "scientist_bargain_neutral":
            emit(lines, 4, "tv_academy_debate_great_scientist_dip_between_30_and_80_trigger = yes")
        emit(lines, 3, "}")
        emit(lines, 3, f"{prep} = yes")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_dispatch_monthly_progress_event_effect = {")
    emit(lines, 1, "random_list = {")
    for event in random_events(data):
        emit(lines, 2, f"{event['weight']} = {{")
        emit(lines, 3, "trigger = {")
        gen_random_event_guard(lines, 4, data, event)
        emit(lines, 3, "}")
        emit(lines, 3, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{event['event_num']} days = 1 }}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def gen_random_event_guard(lines: list[str], level: int, data: dict, event: dict) -> None:
    emit(lines, level, "var:tv_academy_philosophy_phase ?= 1")
    emit(lines, level, "var:tv_academy_debate_current_node_type ?= 1")
    emit(lines, level, "tv_academy_philosophy_has_current_issue_trigger = yes")
    emit(lines, level, "NOT = { tv_academy_philosophy_current_issue_embraced_trigger = yes }")
    emit(lines, level, f"NOT = {{ has_variable = {PENDING_RESULT_VAR} }}")
    emit(lines, level, "NOT = { has_variable = tv_academy_philosophy_recess_notice_pending }")
    if event.get("issue"):
        issue = issue_by_key(data)[event["issue"]]
        emit(lines, level, f"var:tv_academy_philosophy_current ?= {issue['id']}")


def gen_random_event_effects(lines: list[str], level: int, data: dict, event: dict, opt_key: str) -> None:
    option_data = event["options"][opt_key]
    emit(lines, level, "if = {")
    emit(lines, level + 1, "limit = {")
    gen_random_event_guard(lines, level + 2, data, event)
    emit(lines, level + 1, "}")
    emit_change_local_debate_progress_effect(lines, level + 1, option_data["progress_delta"])
    for block in option_data.get("effect_blocks") or []:
        gen_random_event_effect_block(lines, level + 1, data, block)
    emit(lines, level + 1, "tv_academy_philosophy_check_debate_endpoint_effect = yes")
    emit(lines, level, "}")


def gen_random_event_effect_block(lines: list[str], level: int, data: dict, block: dict) -> None:
    effect_type = block["type"]
    if effect_type == "seat_stance":
        group_id = group_by_key(data)[block["group"]]["id"]
        stance_value = {"support": STANCE_SUPPORT, "oppose": STANCE_OPPOSE, "neutral": STANCE_NEUTRAL}[block["stance"]]
        for seat in SEATS:
            emit(lines, level, "if = {")
            emit(lines, level + 1, f"limit = {{ {var_eq(seat_group(seat), group_id)} }}")
            emit(lines, level + 1, f"set_variable = {{ name = {seat_stance(seat)} value = {stance_value} }}")
            emit(lines, level + 1, f"set_variable = {{ name = {seat_cooldown(seat)} value = {block['cooldown_months']} }}")
            emit(lines, level, "}")
    elif effect_type == "seat_cooldown":
        group_id = group_by_key(data)[block["group"]]["id"]
        for seat in SEATS:
            emit(lines, level, "if = {")
            emit(lines, level + 1, f"limit = {{ {var_eq(seat_group(seat), group_id)} }}")
            emit(lines, level + 1, f"set_variable = {{ name = {seat_cooldown(seat)} value = {block['cooldown_months']} }}")
            emit(lines, level, "}")
    elif effect_type == "estate_satisfaction":
        emit(lines, level, f"add_estate_satisfaction = {{ type = estate_type:{block['estate']} value = {format_number(block['value'])} }}")
    elif effect_type == "resource":
        amount = block.get("scale", block.get("amount"))
        resource = block["resource"]
        if resource == "gold":
            emit(lines, level, f"change_gold_effect = {{ scale = {format_number(amount)} }}")
        elif resource == "prestige":
            emit(lines, level, f"add_prestige = {format_number(amount)}")
        elif resource == "legitimacy":
            emit(lines, level, f"add_legitimacy = {format_number(amount)}")
        elif resource == "stability":
            emit(lines, level, f"add_stability = {format_number(amount)}")
    elif effect_type == "temporary_country_modifier":
        emit(lines, level, "add_country_modifier = {")
        emit(lines, level + 1, f"modifier = {random_event_modifier_name(block)}")
        emit(lines, level + 1, f"months = {block['months']}")
        emit(lines, level + 1, "mode = add_and_extend")
        emit(lines, level, "}")
    elif effect_type == "artist_skill":
        emit(lines, level, "random_character = {")
        emit(lines, level + 1, "limit = { is_alive = yes is_artist = yes }")
        emit(lines, level + 1, f"add_artist_skill = {format_number(block['amount'])}")
        emit(lines, level, "}")
    elif effect_type == "scientist_attribute":
        emit(lines, level, "var:tv_academy_leader_char ?= {")
        if block.get("adm"):
            emit(lines, level + 1, f"add_adm = {format_number(block['adm'])}")
        if block.get("dip"):
            emit(lines, level + 1, f"add_dip = {format_number(block['dip'])}")
        emit(lines, level, "}")
    elif effect_type == "foreign_prestige":
        for seat in SEATS:
            emit(lines, level, "if = {")
            emit(lines, level + 1, f"limit = {{ {var_eq(seat_group(seat), group_by_key(data)['foreign_power']['id'])} has_variable = {seat_foreign(seat)} }}")
            emit(lines, level + 1, f"var:{seat_foreign(seat)} ?= {{ add_prestige = {format_number(block['amount'])} }}")
            emit(lines, level, "}")


def format_number(value: int | float) -> str:
    if isinstance(value, int):
        return str(value)
    return f"{value:.4f}".rstrip("0").rstrip(".")


def random_event_modifier_entries(data: dict) -> list[dict]:
    by_key: dict[str, dict] = {}
    for event in random_events(data):
        for opt_key in ("a", "b"):
            option_data = event["options"][opt_key]
            for block in option_data.get("effect_blocks") or []:
                if block.get("type") != "temporary_country_modifier":
                    continue
                key = random_event_modifier_name(block)
                entry = by_key.setdefault(
                    key,
                    {
                        "key": key,
                        "english_name": f"{event['title']['english']}: {option_data['text']['english']}",
                        "simp_chinese_name": f"{event['title']['simp_chinese']}：{option_data['text']['simp_chinese']}",
                        "english_desc": option_data["rationale"]["english"],
                        "simp_chinese_desc": option_data["rationale"]["simp_chinese"],
                        "value": 0.0,
                    },
                )
                for value in (block.get("effects") or {}).values():
                    entry["value"] += float(value)
    result = sorted(by_key.values(), key=lambda entry: entry["key"])
    for entry in result:
        if entry["value"] == 0:
            entry["value"] = 0.01
        entry["modifier_value"] = max(-0.03, min(0.03, entry["value"]))
    return result


def gen_defection_effects(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_debate_apply_defections_effect = {")
    for seat in SEATS:
        emit(lines, 1, f"tv_academy_debate_apply_seat_{seat}_defection_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_dispatch_auto_stance_notifications_effect = {")
    for var, event_num in (
        (AUTO_STANCE_SUPPORT_VAR, AUTO_STANCE_SUPPORT_EVENT),
        (AUTO_STANCE_OPPOSE_VAR, AUTO_STANCE_OPPOSE_EVENT),
        (AUTO_STANCE_NEUTRAL_VAR, AUTO_STANCE_NEUTRAL_EVENT),
        (AUTO_SEAT_VACATED_VAR, AUTO_SEAT_VACATED_EVENT),
    ):
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {var} NOT = {{ has_variable = {PENDING_RESULT_VAR} }} }}")
        emit(lines, 2, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{event_num} days = 1 }}")
        emit(lines, 1, "}")
        emit(lines, 1, f"remove_variable = {var}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_debate_apply_seat_defection_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {seat_group('$seat$')} var:{seat_cooldown('$seat$')} <= 0 NOT = {{ {var_eq(seat_group('$seat$'), 18)} }} }}")
    for idx, group in enumerate(groups(data)):
        if group["key"] == "great_scientist":
            continue
        emit(lines, 2, ("if" if idx == 0 else "else_if") + " = {")
        emit(lines, 3, f"limit = {{ {var_eq(seat_group('$seat$'), group['id'])} }}")
        if group["key"] == "foreign_power":
            emit(lines, 3, f"set_variable = {{ name = {EVENT_STANCE} value = var:{seat_stance('$seat$')} }}")
            emit(lines, 3, f"var:{seat_foreign('$seat$')} ?= {{ save_scope_as = {SELECTED_FOREIGN_SCOPE} }}")
            emit(lines, 3, "tv_academy_debate_set_selected_foreign_stance_effect = yes")
            emit(lines, 3, "if = {")
            emit(lines, 4, f"limit = {{ NOT = {{ var:{EVENT_STANCE} ?= var:{seat_stance('$seat$')} }} }}")
            emit(lines, 4, "if = {")
            emit(lines, 5, f"limit = {{ var:{EVENT_STANCE} ?= {STANCE_SUPPORT} }}")
            emit(lines, 5, f"set_variable = {{ name = {AUTO_STANCE_SUPPORT_VAR} value = 1 }}")
            emit(lines, 4, "}")
            emit(lines, 4, "else_if = {")
            emit(lines, 5, f"limit = {{ var:{EVENT_STANCE} ?= {STANCE_OPPOSE} }}")
            emit(lines, 5, f"set_variable = {{ name = {AUTO_STANCE_OPPOSE_VAR} value = 1 }}")
            emit(lines, 4, "}")
            emit(lines, 4, "else_if = {")
            emit(lines, 5, f"limit = {{ var:{EVENT_STANCE} ?= {STANCE_NEUTRAL} }}")
            emit(lines, 5, f"set_variable = {{ name = {AUTO_STANCE_NEUTRAL_VAR} value = 1 }}")
            emit(lines, 4, "}")
            emit(lines, 4, f"set_variable = {{ name = {seat_stance('$seat$')} value = var:{EVENT_STANCE} }}")
            emit(lines, 4, f"set_variable = {{ name = {seat_cooldown('$seat$')} value = {data['settings']['defection_cooldown_months']} }}")
            emit(lines, 3, "}")
        else:
            emit(lines, 3, "if = {")
            emit(lines, 4, f"limit = {{ {var_eq(seat_stance('$seat$'), STANCE_SUPPORT)} tv_academy_debate_group_{group['key']}_negative_defection_condition_trigger = yes }}")
            emit(lines, 4, f"set_variable = {{ name = {AUTO_STANCE_OPPOSE_VAR} value = 1 }}")
            emit(lines, 4, f"set_variable = {{ name = {seat_stance('$seat$')} value = {STANCE_OPPOSE} }}")
            emit(lines, 4, f"set_variable = {{ name = {seat_cooldown('$seat$')} value = {data['settings']['defection_cooldown_months']} }}")
            emit(lines, 3, "}")
            emit(lines, 3, "else_if = {")
            emit(lines, 4, f"limit = {{ {var_eq(seat_stance('$seat$'), STANCE_OPPOSE)} tv_academy_debate_group_{group['key']}_positive_defection_condition_trigger = yes }}")
            emit(lines, 4, f"set_variable = {{ name = {AUTO_STANCE_SUPPORT_VAR} value = 1 }}")
            emit(lines, 4, f"set_variable = {{ name = {seat_stance('$seat$')} value = {STANCE_SUPPORT} }}")
            emit(lines, 4, f"set_variable = {{ name = {seat_cooldown('$seat$')} value = {data['settings']['defection_cooldown_months']} }}")
            emit(lines, 3, "}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for seat in SEATS:
        emit(lines, 0, f"tv_academy_debate_apply_seat_{seat}_defection_effect = {{")
        emit(lines, 1, f"tv_academy_debate_apply_seat_defection_effect = {{ seat = {seat} }}")
        emit(lines, 0, "}")
        emit(lines)


def emit_defection_condition(lines: list[str], level: int, group: dict, *, positive: bool) -> None:
    key = group["key"]
    if key in {"nobility", "tribes"}:
        estate = "nobles_estate" if key == "nobility" else "tribes_estate"
        emit(lines, level, f"estate_satisfaction:{estate} {'>' if positive else '<'} {0.8 if positive else 0.2}")
    elif key == "clergy":
        emit(lines, level, f"religious_unity {'>' if positive else '<'} {0.9 if positive else 0.5}")
    elif key == "burghers":
        op = ">" if positive else "<"
        mult = 0.5 if positive else 0.2
        emit(lines, level, f"monthly_trade_income {op} {{ value = monthly_income_total multiply = {mult} }}")
    elif key == "peasants":
        emit(lines, level, f"stability {'>' if positive else '<'} {30 if positive else -30}")
    elif key == "dhimmi":
        emit(lines, level, f"modifier:tolerance_heathen {'>' if positive else '<'} {3 if positive else -3}")
    elif key == "cossacks":
        emit(lines, level, "army_size_percentage >= 0.5" if positive else "regular_army_size <= 0")
    elif key == "scholarly_community":
        emit(lines, level, f"average_country_literacy {'>' if positive else '<'} {50 if positive else 20}")
    elif key == "public_opinion":
        emit(lines, level, "has_policy = no_censorship" if positive else "has_policy = strict_censorship")
    elif key == "court_bureaucrats":
        emit(lines, level, f"government_power {'>' if positive else '<'} {90 if positive else 50}")
    elif key == "maritime_merchants":
        emit(lines, level, "societal_value:land_vs_naval > 50" if positive else "societal_value:land_vs_naval < -1")
    elif key == "professional_military":
        emit(lines, level, "has_variable = tv_academy_debate_recent_war_won" if positive else "has_variable = tv_academy_debate_recent_war_lost")
    elif key == "religious_reformers":
        emit(lines, level, f"modifier:tolerance_heretic {'>' if positive else '<'} {3 if positive else -3}")
    elif key == "local_autonomy":
        emit(lines, level, f"average_control_in_home_region {'>' if positive else '<'} {0.5 if positive else 0.2}")
    elif key == "minorities":
        emit(lines, level, "any_owned_location = { dominant_culture = { is_accepted_in = root } }" if positive else "NOT = { any_owned_location = { dominant_culture = { is_accepted_in = root } } }")
    elif key == "artists":
        emit(lines, level, "any_international_organizations_member_of = { international_organization_type = international_organization_type:tv_arts_exhibition international_organization_has_policy = policy:tv_arts_free_creation_policy }" if positive else "any_international_organizations_member_of = { international_organization_type = international_organization_type:tv_arts_exhibition international_organization_has_policy = policy:tv_arts_strict_censorship_policy }")
    elif key == "foreign_power":
        emit(lines, level, "always = yes")
    else:
        emit(lines, level, "always = no")


def gen_result_effects(lines: list[str], data: dict) -> None:
    for accepted, name in ((True, "acceptance"), (False, "rejection")):
        emit(lines, 0, f"tv_academy_debate_apply_{name}_seat_results_effect = {{")
        for issue in issues(data):
            emit(lines, 1, "if = {")
            emit(lines, 2, f"limit = {{ var:{PENDING_ISSUE_VAR} ?= {issue['id']} }}")
            emit(lines, 2, f"set_variable = {{ name = {issue_progressive_var(issue) if accepted else issue_conservative_var(issue)} value = 1 }}")
            emit(lines, 2, f"remove_variable = {issue_conservative_var(issue) if accepted else issue_progressive_var(issue)}")
            emit(lines, 1, "}")
        for seat in SEATS:
            emit(lines, 1, f"tv_academy_debate_apply_seat_{seat}_{name}_result_effect = yes")
        emit(lines, 0, "}")
        emit(lines)
        for seat in SEATS:
            emit(lines, 0, f"tv_academy_debate_apply_seat_{seat}_{name}_result_effect = {{")
            emit(lines, 1, "if = {")
            emit(lines, 2, f"limit = {{ has_variable = {seat_group(seat)} NOT = {{ {var_eq(seat_stance(seat), STANCE_NEUTRAL)} }} }}")
            win_stance = STANCE_SUPPORT if accepted else STANCE_OPPOSE
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ {var_eq(seat_stance(seat), win_stance)} }}")
            emit(lines, 3, f"tv_academy_debate_apply_seat_{seat}_winner_effect = yes")
            emit(lines, 2, "}")
            emit(lines, 2, "else = {")
            emit(lines, 3, f"tv_academy_debate_apply_seat_{seat}_loser_effect = yes")
            emit(lines, 2, "}")
            emit(lines, 1, "}")
            emit(lines, 0, "}")
            emit(lines)

    for win, suffix in ((True, "winner"), (False, "loser")):
        emit(lines, 0, f"tv_academy_debate_apply_seat_{suffix}_effect = {{")
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ has_variable = {seat_group('$seat$')} }}")
        emit(lines, 2, f"set_local_variable = {{ name = {RESULT_GROUP_LOCAL} value = var:{seat_group('$seat$')} }}")
        emit(lines, 2, "if = {")
        emit(lines, 3, f"limit = {{ has_global_variable_map = {GROUP_ESTATE_MAP} is_key_in_global_variable_map = {{ name = {GROUP_ESTATE_MAP} target = local_var:{RESULT_GROUP_LOCAL} }} }}")
        emit(lines, 3, f"set_local_variable = {{ name = {RESULT_ESTATE_LOCAL} value = \"global_variable_map({GROUP_ESTATE_MAP}|local_var:{RESULT_GROUP_LOCAL})\" }}")
        emit(lines, 3, f"add_estate_satisfaction = {{ type = local_var:{RESULT_ESTATE_LOCAL} value = {0.10 * (1 if win else -1):.2f} }}")
        emit(lines, 2, "}")
        for group in groups(data):
            if is_estate_or_variant(group):
                continue
            emit(lines, 2, "else_if = {")
            emit(lines, 3, f"limit = {{ {var_eq(seat_group('$seat$'), group['id'])} }}")
            apply_result_for_group(lines, 3, group, "$seat$", win)
            emit(lines, 2, "}")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)

    for seat in SEATS:
        for _, suffix in ((True, "winner"), (False, "loser")):
            emit(lines, 0, f"tv_academy_debate_apply_seat_{seat}_{suffix}_effect = {{")
            emit(lines, 1, f"tv_academy_debate_apply_seat_{suffix}_effect = {{ seat = {seat} }}")
            emit(lines, 0, "}")
            emit(lines)


def apply_result_for_group(lines: list[str], level: int, group: dict, seat: int | str, win: bool) -> None:
    sign = 1 if win else -1
    if is_estate_or_variant(group):
        return
    elif group["type"] == "artists":
        if win:
            emit(lines, level, f"var:{seat_artist(seat)} ?= {{ add_artist_skill = 0.20 }}")
        else:
            emit(lines, level, f"var:{seat_artist(seat)} ?= {{ kill_character = this }}")
    elif group["type"] == "foreign_power":
        emit(lines, level, f"var:{seat_foreign(seat)} ?= {{ add_prestige = {10 * sign} }}")
    elif group["type"] == "great_scientist":
        emit(lines, level, f"var:{seat_scientist(seat)} ?= {{ add_adm = {10 * sign} add_dip = {10 * sign} }}")


def gen_endpoint_effects(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_philosophy_check_debate_endpoint_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = {")
    emit(lines, 3, "var:tv_academy_philosophy_phase ?= 1")
    emit(lines, 3, f"NOT = {{ has_variable = {PENDING_RESULT_VAR} }}")
    emit_local_debate_progress_threshold(lines, 3, ">=", 100)
    emit(lines, 2, "}")
    emit(lines, 2, f"set_variable = {{ name = {PENDING_RESULT_VAR} value = 1 }}")
    emit(lines, 2, f"set_variable = {{ name = {PENDING_ISSUE_VAR} value = var:tv_academy_philosophy_current }}")
    emit(lines, 2, f"set_variable = {{ name = {PENDING_KIND_VAR} value = 1 }}")
    emit(lines, 2, "set_variable = { name = tv_academy_philosophy_phase value = 0 }")
    emit(lines, 2, "trigger_event_non_silently = { id = tv_research.43 days = 1 }")
    emit(lines, 1, "}")
    emit(lines, 1, "else_if = {")
    emit(lines, 2, "limit = {")
    emit(lines, 3, "var:tv_academy_philosophy_phase ?= 1")
    emit(lines, 3, f"NOT = {{ has_variable = {PENDING_RESULT_VAR} }}")
    emit_local_debate_progress_threshold(lines, 3, "<=", 0)
    emit(lines, 2, "}")
    emit(lines, 2, f"set_variable = {{ name = {PENDING_RESULT_VAR} value = 1 }}")
    emit(lines, 2, f"set_variable = {{ name = {PENDING_ISSUE_VAR} value = var:tv_academy_philosophy_current }}")
    emit(lines, 2, f"set_variable = {{ name = {PENDING_KIND_VAR} value = 2 }}")
    emit(lines, 2, "set_variable = { name = tv_academy_philosophy_phase value = 0 }")
    emit(lines, 2, "trigger_event_non_silently = { id = tv_research.44 days = 1 }")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for accepted, kind in ((True, "acceptance"), (False, "rejection")):
        result_kind = 1 if accepted else 2
        emit(lines, 0, f"tv_academy_philosophy_resolve_pending_{kind}_effect = {{")
        emit(lines, 1, "if = {")
        emit(lines, 2, "limit = {")
        emit(lines, 3, f"var:{PENDING_RESULT_VAR} ?= 1")
        emit(lines, 3, f"var:{PENDING_KIND_VAR} ?= {result_kind}")
        emit(lines, 3, "tv_academy_philosophy_has_current_issue_trigger = yes")
        emit(lines, 3, f"var:tv_academy_philosophy_current ?= var:{PENDING_ISSUE_VAR}")
        emit(lines, 2, "}")
        emit(lines, 2, f"tv_academy_debate_apply_{kind}_seat_results_effect = yes")
        if accepted:
            emit(lines, 2, "tv_academy_philosophy_apply_pending_acceptance_effect = yes")
        emit(lines, 2, "tv_academy_philosophy_advance_current_issue_effect = yes")
        emit(lines, 2, "tv_academy_philosophy_enter_recess_effect = yes")
        emit(lines, 2, "tv_academy_philosophy_clear_debate_result_effect = yes")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)


def gen_action_trigger_effects(lines: list[str], data: dict) -> None:
    triggers = action_triggers(data)
    if not triggers:
        return

    for trigger in triggers:
        chance = int(trigger["chance"])
        miss_chance = max(0, 100 - chance)
        delta = int(trigger["delta"])
        emit(lines, 0, f"{action_trigger_effect_name(trigger)} = {{")
        emit(lines, 1, f"# Semantic condition: {trigger['condition']}")
        emit(lines, 1, "if = {")
        emit(lines, 2, "limit = {")
        emit(lines, 3, "var:tv_academy_philosophy_phase ?= 1")
        emit(lines, 3, "var:tv_academy_debate_current_node_type ?= 1")
        emit(lines, 3, "tv_academy_philosophy_has_current_issue_trigger = yes")
        emit_owned_academy_io_trigger(lines, 3)
        emit(lines, 3, f"var:tv_academy_philosophy_current ?= {trigger['issue_id']}")
        emit(lines, 3, "NOT = { tv_academy_philosophy_current_issue_embraced_trigger = yes }")
        emit(lines, 3, f"NOT = {{ has_variable = {PENDING_RESULT_VAR} }}")
        emit(lines, 3, "NOT = { has_variable = tv_academy_philosophy_recess_notice_pending }")
        emit(lines, 2, "}")
        emit(lines, 2, "random_list = {")
        emit(lines, 3, f"{chance} = {{")
        emit_change_local_debate_progress_effect(lines, 4, delta)
        emit(lines, 4, "tv_academy_philosophy_check_debate_endpoint_effect = yes")
        emit(lines, 4, "if = {")
        emit(lines, 5, f"limit = {{ NOT = {{ has_variable = {PENDING_RESULT_VAR} }} }}")
        event_num = LOCAL_ACTION_POSITIVE_EVENT if delta > 0 else LOCAL_ACTION_NEGATIVE_EVENT
        emit(lines, 5, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{event_num} days = 1 }}")
        emit(lines, 4, "}")
        emit(lines, 3, "}")
        if miss_chance > 0:
            emit(lines, 3, f"{miss_chance} = {{ }}")
        emit(lines, 2, "}")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)

    for context in action_contexts(data):
        emit(lines, 0, f"{action_context_effect_name(context)} = {{")
        for trigger in triggers:
            if trigger["context"] == context:
                emit(lines, 1, f"{action_trigger_effect_name(trigger)} = yes")
        emit(lines, 0, "}")
        emit(lines)


def gen_world_debate_effects(lines: list[str], data: dict) -> None:
    emit(lines, 0, "tv_academy_world_debate_initialize_effect = {")
    for var in (WORLD_ACTIVE_VAR, WORLD_ISSUE_VAR, WORLD_NODE_VAR, WORLD_RESULT_VAR, WORLD_DELTA_VAR, WORLD_NEXT_SEAT_VAR, WORLD_DECISIVE_SEATS_VAR):
        emit(lines, 1, f"remove_variable = {var}")
    emit(lines, 1, f"set_variable = {{ name = {WORLD_PROGRESS_VAR} value = 50 }}")
    emit(lines, 1, f"set_variable = {{ name = {WORLD_STRENGTH_VAR} value = 50 }}")
    emit(lines, 1, f"set_variable = {{ name = {WORLD_MONTHS_VAR} value = 0 }}")
    emit(lines, 1, "tv_academy_world_debate_clear_seats_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_clear_country_participants_effect = {")
    emit(lines, 1, f"if = {{")
    emit(lines, 2, f"limit = {{ has_global_variable_list = {WORLD_PARTICIPANTS_LIST} }}")
    emit(lines, 2, "every_in_global_list = {")
    emit(lines, 3, f"variable = {WORLD_PARTICIPANTS_LIST}")
    emit(lines, 3, f"remove_variable = {WORLD_PARTICIPANT_VAR}")
    emit(lines, 3, f"remove_variable = {WORLD_COUNTRY_STANCE_VAR}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_clear_seats_effect = {")
    emit(lines, 1, "tv_academy_world_debate_clear_country_participants_effect = yes")
    emit(lines, 1, f"clear_global_variable_list = {WORLD_PARTICIPANTS_LIST}")
    for seat in WORLD_SEATS:
        emit(lines, 1, f"remove_variable = {world_seat_country(seat)}")
        emit(lines, 1, f"remove_variable = {world_seat_stance(seat)}")
    for var in (WORLD_SUPPORT_SEATS_VAR, WORLD_OPPOSE_SEATS_VAR, WORLD_NEUTRAL_SEATS_VAR, WORLD_SEAT_COUNT_VAR):
        emit(lines, 1, f"set_variable = {{ name = {var} value = 0 }}")
    emit(lines, 1, f"remove_variable = {WORLD_NEXT_SEAT_VAR}")
    emit(lines, 1, f"remove_variable = {WORLD_DECISIVE_SEATS_VAR}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_try_begin_for_country_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = {")
    emit(lines, 3, "tv_academy_world_debate_country_has_academy_trigger = yes")
    emit(lines, 3, "var:tv_academy_debate_current_node_type ?= 2")
    emit(lines, 3, "tv_academy_philosophy_has_current_issue_trigger = yes")
    emit(lines, 3, "situation:tv_academy_world_debate_situation = {")
    emit(lines, 4, f"NOT = {{ has_variable = {WORLD_ACTIVE_VAR} }}")
    emit(lines, 3, "}")
    emit(lines, 2, "}")
    emit(lines, 2, "situation:tv_academy_world_debate_situation = {")
    emit(lines, 3, "tv_academy_world_debate_initialize_effect = yes")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_ACTIVE_VAR} value = 1 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_ISSUE_VAR} value = prev.var:tv_academy_philosophy_current }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_NODE_VAR} value = prev.var:tv_academy_debate_current_node }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_PROGRESS_VAR} value = 50 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_STRENGTH_VAR} value = 50 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_MONTHS_VAR} value = 0 }}")
    emit(lines, 3, "tv_academy_world_debate_refresh_seats_effect = yes")
    emit(lines, 3, "tv_academy_world_debate_mirror_all_countries_effect = yes")
    emit(lines, 3, f"if = {{")
    emit(lines, 4, f"limit = {{ has_global_variable_list = {WORLD_PARTICIPANTS_LIST} }}")
    emit(lines, 4, "every_in_global_list = {")
    emit(lines, 5, f"variable = {WORLD_PARTICIPANTS_LIST}")
    emit(lines, 5, "limit = {")
    emit(lines, 6, "tv_academy_world_debate_country_has_academy_trigger = yes")
    emit(lines, 6, f"var:tv_academy_philosophy_current ?= prev.var:{WORLD_ISSUE_VAR}")
    emit(lines, 5, "}")
    emit(lines, 5, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{WORLD_DEBATE_START_EVENT} days = 1 }}")
    emit(lines, 4, "}")
    emit(lines, 3, "}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_monthly_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {WORLD_ACTIVE_VAR} }}")
    emit(lines, 2, "tv_academy_world_debate_refresh_seats_effect = yes")
    emit(lines, 2, f"change_variable = {{ name = {WORLD_MONTHS_VAR} add = 1 }}")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_DELTA_VAR} value = var:{WORLD_STRENGTH_VAR} }}")
    emit(lines, 2, f"change_variable = {{ name = {WORLD_DELTA_VAR} add = -50 }}")
    emit(lines, 2, f"change_variable = {{ name = {WORLD_DELTA_VAR} divide = 100 }}")
    emit(lines, 2, f"change_variable = {{ name = {WORLD_DELTA_VAR} multiply = 5 }}")
    emit(lines, 2, f"change_variable = {{ name = {WORLD_PROGRESS_VAR} add = var:{WORLD_DELTA_VAR} }}")
    emit(lines, 2, f"clamp_variable = {{ name = {WORLD_PROGRESS_VAR} min = 0 max = 100 }}")
    emit(lines, 2, "if = {")
    emit(lines, 3, f"limit = {{ var:{WORLD_PROGRESS_VAR} <= 0 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_RESULT_VAR} value = {WORLD_RESULT_CONSERVATIVE} }}")
    emit(lines, 3, "tv_academy_world_debate_resolve_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, f"limit = {{ var:{WORLD_PROGRESS_VAR} >= 100 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_RESULT_VAR} value = {WORLD_RESULT_PROGRESSIVE} }}")
    emit(lines, 3, "tv_academy_world_debate_resolve_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 2, "else_if = {")
    emit(lines, 3, f"limit = {{ var:{WORLD_MONTHS_VAR} >= 120 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_RESULT_VAR} value = {WORLD_RESULT_NEUTRAL} }}")
    emit(lines, 3, "tv_academy_world_debate_resolve_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 1, "tv_academy_world_debate_mirror_all_countries_effect = yes")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_refresh_seats_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ NOT = {{ has_variable = {WORLD_ACTIVE_VAR} }} }}")
    emit(lines, 2, "tv_academy_world_debate_clear_seats_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {WORLD_ACTIVE_VAR} }}")
    emit(lines, 2, "tv_academy_world_debate_clear_seats_effect = yes")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_NEXT_SEAT_VAR} value = 1 }}")
    emit(lines, 2, "every_country = {")
    emit(lines, 3, "limit = { tv_academy_world_debate_country_can_participate_trigger = yes }")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_PARTICIPANT_VAR} value = 1 }}")
    emit(lines, 3, f"add_to_global_variable_list = {{ name = {WORLD_PARTICIPANTS_LIST} target = this }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_COUNTRY_STANCE_VAR} value = {STANCE_NEUTRAL} }}")
    emit(lines, 3, "if = {")
    emit(lines, 4, "limit = { tv_academy_world_debate_country_supports_current_issue_trigger = yes }")
    emit(lines, 4, f"set_variable = {{ name = {WORLD_COUNTRY_STANCE_VAR} value = {STANCE_SUPPORT} }}")
    emit(lines, 3, "}")
    emit(lines, 3, "else_if = {")
    emit(lines, 4, "limit = { tv_academy_world_debate_country_opposes_current_issue_trigger = yes }")
    emit(lines, 4, f"set_variable = {{ name = {WORLD_COUNTRY_STANCE_VAR} value = {STANCE_OPPOSE} }}")
    emit(lines, 3, "}")
    for stance_value, count_var in (
        (STANCE_SUPPORT, WORLD_SUPPORT_SEATS_VAR),
        (STANCE_OPPOSE, WORLD_OPPOSE_SEATS_VAR),
        (STANCE_NEUTRAL, WORLD_NEUTRAL_SEATS_VAR),
    ):
        emit(lines, 3, "if = {")
        emit(lines, 4, f"limit = {{ {var_eq(WORLD_COUNTRY_STANCE_VAR, stance_value)} }}")
        emit(lines, 4, f"situation:tv_academy_world_debate_situation = {{ change_variable = {{ name = {count_var} add = 1 }} }}")
        emit(lines, 3, "}")
    emit(lines, 3, f"situation:tv_academy_world_debate_situation = {{ change_variable = {{ name = {WORLD_SEAT_COUNT_VAR} add = 1 }} }}")
    gen_world_seat_assignment_branches(lines, 3)
    emit(lines, 2, "}")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_DECISIVE_SEATS_VAR} value = var:{WORLD_SUPPORT_SEATS_VAR} }}")
    emit(lines, 2, f"change_variable = {{ name = {WORLD_DECISIVE_SEATS_VAR} add = var:{WORLD_OPPOSE_SEATS_VAR} }}")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_STRENGTH_VAR} value = 50 }}")
    emit(lines, 2, "if = {")
    emit(lines, 3, f"limit = {{ var:{WORLD_DECISIVE_SEATS_VAR} > 0 }}")
    emit(lines, 3, f"set_variable = {{ name = {WORLD_STRENGTH_VAR} value = var:{WORLD_SUPPORT_SEATS_VAR} }}")
    emit(lines, 3, f"change_variable = {{ name = {WORLD_STRENGTH_VAR} divide = var:{WORLD_DECISIVE_SEATS_VAR} }}")
    emit(lines, 3, f"change_variable = {{ name = {WORLD_STRENGTH_VAR} multiply = 100 }}")
    emit(lines, 3, f"clamp_variable = {{ name = {WORLD_STRENGTH_VAR} min = 0 max = 100 }}")
    emit(lines, 2, "}")
    emit(lines, 2, f"remove_variable = {WORLD_NEXT_SEAT_VAR}")
    emit(lines, 2, f"remove_variable = {WORLD_DECISIVE_SEATS_VAR}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_resolve_effect = {")
    emit(lines, 1, f"if = {{")
    emit(lines, 2, f"limit = {{ has_variable = {WORLD_ACTIVE_VAR} has_variable = {WORLD_RESULT_VAR} }}")
    emit(lines, 2, f"if = {{")
    emit(lines, 3, f"limit = {{ has_global_variable_list = {WORLD_PARTICIPANTS_LIST} }}")
    emit(lines, 3, "every_in_global_list = {")
    emit(lines, 4, f"variable = {WORLD_PARTICIPANTS_LIST}")
    emit(lines, 4, "limit = {")
    emit(lines, 5, "tv_academy_world_debate_country_has_academy_trigger = yes")
    emit(lines, 5, f"var:tv_academy_philosophy_current ?= root.var:{WORLD_ISSUE_VAR}")
    emit(lines, 4, "}")
    emit(lines, 4, "tv_academy_world_debate_apply_country_result_effect = yes")
    emit(lines, 3, "}")
    emit(lines, 2, "}")
    emit(lines, 2, f"remove_variable = {WORLD_ACTIVE_VAR}")
    emit(lines, 2, f"remove_variable = {WORLD_ISSUE_VAR}")
    emit(lines, 2, f"remove_variable = {WORLD_NODE_VAR}")
    emit(lines, 2, f"remove_variable = {WORLD_RESULT_VAR}")
    emit(lines, 2, f"remove_variable = {WORLD_DELTA_VAR}")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_PROGRESS_VAR} value = 50 }}")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_STRENGTH_VAR} value = 50 }}")
    emit(lines, 2, f"set_variable = {{ name = {WORLD_MONTHS_VAR} value = 0 }}")
    emit(lines, 2, "tv_academy_world_debate_clear_seats_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_apply_country_result_effect = {")
    for issue in issues(data):
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ root = {{ var:{WORLD_ISSUE_VAR} ?= {issue['id']} }} }}")
        emit(lines, 2, "if = {")
        emit(lines, 3, f"limit = {{ root = {{ var:{WORLD_RESULT_VAR} ?= {WORLD_RESULT_PROGRESSIVE} }} }}")
        emit(lines, 3, f"set_variable = {{ name = {issue_progressive_var(issue)} value = 1 }}")
        emit(lines, 3, f"remove_variable = {issue_conservative_var(issue)}")
        emit(lines, 3, f"tv_academy_philosophy_accept_{issue['key']}_effect = yes")
        emit(lines, 2, "}")
        emit(lines, 2, "else_if = {")
        emit(lines, 3, f"limit = {{ root = {{ var:{WORLD_RESULT_VAR} ?= {WORLD_RESULT_CONSERVATIVE} }} NOT = {{ has_embraced_institution = institution:{issue['institution']} }} }}")
        emit(lines, 3, f"set_variable = {{ name = {issue_conservative_var(issue)} value = 1 }}")
        emit(lines, 3, f"remove_variable = {issue_progressive_var(issue)}")
        emit(lines, 2, "}")
        emit(lines, 2, "tv_academy_philosophy_advance_current_issue_effect = yes")
        emit(lines, 2, "tv_academy_philosophy_enter_recess_effect = yes")
        emit(lines, 2, "if = {")
        emit(lines, 3, f"limit = {{ root = {{ var:{WORLD_RESULT_VAR} ?= {WORLD_RESULT_PROGRESSIVE} }} }}")
        emit(lines, 3, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT} days = 1 }}")
        emit(lines, 2, "}")
        emit(lines, 2, "else_if = {")
        emit(lines, 3, f"limit = {{ root = {{ var:{WORLD_RESULT_VAR} ?= {WORLD_RESULT_CONSERVATIVE} }} }}")
        emit(lines, 3, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT} days = 1 }}")
        emit(lines, 2, "}")
        emit(lines, 2, "else_if = {")
        emit(lines, 3, f"limit = {{ root = {{ var:{WORLD_RESULT_VAR} ?= {WORLD_RESULT_NEUTRAL} }} }}")
        emit(lines, 3, f"trigger_event_non_silently = {{ id = {EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT} days = 1 }}")
        emit(lines, 2, "}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_academy_world_debate_mirror_all_countries_effect = {")
    emit(lines, 1, "every_country = {")
    emit(lines, 2, "limit = { tv_academy_world_debate_country_has_academy_trigger = yes }")
    gen_world_mirror_variable_branches(lines, 2)
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def gen_world_seat_assignment_branches(lines: list[str], level: int) -> None:
    for seat in WORLD_SEATS:
        emit(lines, level, ("if" if seat == 1 else "else_if") + " = {")
        emit(lines, level + 1, f"limit = {{ situation:tv_academy_world_debate_situation = {{ var:{WORLD_NEXT_SEAT_VAR} ?= {seat} }} }}")
        emit(lines, level + 1, "situation:tv_academy_world_debate_situation = {")
        emit(lines, level + 2, f"set_variable = {{ name = {world_seat_country(seat)} value = prev }}")
        emit(lines, level + 2, f"set_variable = {{ name = {world_seat_stance(seat)} value = prev.var:{WORLD_COUNTRY_STANCE_VAR} }}")
        emit(lines, level + 2, f"change_variable = {{ name = {WORLD_NEXT_SEAT_VAR} add = 1 }}")
        emit(lines, level + 1, "}")
        emit(lines, level, "}")


def gen_world_mirror_variable_branches(lines: list[str], level: int) -> None:
    variables = [*WORLD_NUMERIC_VARS]
    for seat in WORLD_SEATS:
        variables.append(world_seat_country(seat))
        variables.append(world_seat_stance(seat))
    for var in variables:
        emit(lines, level, "if = {")
        emit(lines, level + 1, f"limit = {{ prev = {{ has_variable = {var} }} }}")
        emit(lines, level + 1, f"set_variable = {{ name = {var} value = prev.var:{var} }}")
        emit(lines, level, "}")
        emit(lines, level, "else = {")
        emit(lines, level + 1, f"remove_variable = {var}")
        emit(lines, level, "}")


def generate_events(data: dict) -> str:
    script = "scripts/in_game/events/gen_tv_academy_philosophy_debate_events.py"
    lines: list[str] = [header(script, PHILOSOPHY_DEBATE_DATA_SOURCES).rstrip(), "", f"namespace = {EVENT_NS}", ""]
    emit(lines, 0, f"{EVENT_NS}.1 = {{")
    emit(lines, 1, "type = country_event")
    emit(lines, 1, f"title = {EVENT_NS}.1.t")
    emit(lines, 1, "hidden = yes")
    emit(lines, 1, "immediate = { tv_academy_debate_monthly_tick_effect = yes }")
    emit(lines, 0, "}")
    emit(lines)

    event_specs = {
        100: ("join", "neutral"),
        101: ("leave", "neutral"),
        102: ("support_price_join", "good"),
        103: ("oppose_price_stay_out", "bad"),
        104: ("quarrel", "bad"),
        105: ("scientist_sways_support", "good"),
        106: ("scientist_angers_oppose", "bad"),
        107: ("scientist_bargain_support", "good"),
        108: ("great_scientist_requests_seat", "neutral"),
        109: ("royal_appointment", "good"),
        110: ("neutral_decides", "neutral"),
        111: ("neutral_price_support", "good"),
        112: ("neutral_price_not_oppose", "bad"),
        113: ("scientist_sways_neutral", "good"),
        114: ("scientist_angers_neutral", "bad"),
        115: ("scientist_bargain_neutral", "good"),
    }
    for event_num, (key, outcome) in event_specs.items():
        emit(lines, 0, f"{EVENT_NS}.{event_num} = {{")
        emit(lines, 1, "type = country_event")
        emit(lines, 1, f"title = {EVENT_NS}.{event_num}.t")
        emit_desc(lines, 1, data, event_num, key)
        emit(lines, 1, f"outcome = {outcome}")
        emit(lines)
        emit(lines, 1, "trigger = {")
        if event_num == 109:
            emit(lines, 2, "has_variable = tv_academy_debate_royal_option_1_group")
        else:
            emit(lines, 2, f"has_variable = {EVENT_GROUP}")
        emit(lines, 1, "}")
        emit_event_options(lines, 1, data, event_num, key)
        emit(lines, 0, "}")
        emit(lines)

    notification_specs = {
        LOCAL_ACTION_POSITIVE_EVENT: "good",
        LOCAL_ACTION_NEGATIVE_EVENT: "bad",
        WORLD_DEBATE_START_EVENT: "neutral",
        WORLD_DEBATE_PROGRESSIVE_EVENT: "good",
        WORLD_DEBATE_CONSERVATIVE_EVENT: "bad",
        WORLD_DEBATE_NEUTRAL_EVENT: "neutral",
        AUTO_STANCE_SUPPORT_EVENT: "good",
        AUTO_STANCE_OPPOSE_EVENT: "bad",
        AUTO_STANCE_NEUTRAL_EVENT: "neutral",
        AUTO_SEAT_VACATED_EVENT: "neutral",
    }
    for event_num, outcome in notification_specs.items():
        emit(lines, 0, f"{EVENT_NS}.{event_num} = {{")
        emit(lines, 1, "type = country_event")
        emit(lines, 1, f"title = {EVENT_NS}.{event_num}.t")
        emit(lines, 1, f"desc = {EVENT_NS}.{event_num}.d")
        emit(lines, 1, f"outcome = {outcome}")
        emit(lines)
        option(lines, 1, f"{EVENT_NS}.{event_num}.a", [])
        emit(lines, 0, "}")
        emit(lines)

    for event in random_events(data):
        emit(lines, 0, f"{EVENT_NS}.{event['event_num']} = {{")
        emit(lines, 1, "type = country_event")
        emit(lines, 1, f"title = {random_event_loc_key(event, 't')}")
        emit(lines, 1, f"desc = {random_event_loc_key(event, 'd')}")
        emit(lines, 1, "outcome = neutral")
        emit(lines)
        emit(lines, 1, "trigger = {")
        gen_random_event_guard(lines, 2, data, event)
        emit(lines, 1, "}")
        for opt_key in ("a", "b"):
            emit(lines, 1, "option = {")
            emit(lines, 2, f"name = {random_event_loc_key(event, opt_key)}")
            gen_random_event_effects(lines, 2, data, event, opt_key)
            emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)
    return "\n".join(lines).rstrip() + "\n"


def emit_desc(lines: list[str], level: int, data: dict, event_num: int, key: str) -> None:
    emit(lines, level, "desc = {")
    emit(lines, level + 1, "first_valid = {")
    for group in groups(data):
        emit(lines, level + 2, "triggered_desc = {")
        emit(lines, level + 3, f"trigger = {{ {var_eq(EVENT_GROUP, group['id'])} }}")
        emit(lines, level + 3, f"desc = {EVENT_NS}.{event_num}.d_{group['key']}")
        emit(lines, level + 2, "}")
    emit(lines, level + 2, "triggered_desc = {")
    emit(lines, level + 3, "trigger = { always = yes }")
    emit(lines, level + 3, f"desc = {EVENT_NS}.{event_num}.d")
    emit(lines, level + 2, "}")
    emit(lines, level + 1, "}")
    emit(lines, level, "}")


def emit_event_options(lines: list[str], level: int, data: dict, event_num: int, key: str) -> None:
    if key == "join":
        option(lines, level, f"{EVENT_NS}.{event_num}.a", ["tv_academy_debate_selected_group_seated_tooltip_effect = yes", "tv_academy_debate_assign_selected_group_to_seat_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
    elif key == "leave":
        option(lines, level, f"{EVENT_NS}.{event_num}.a", ["tv_academy_debate_selected_group_left_tooltip_effect = yes", "tv_academy_debate_mark_selected_group_left_effect = yes", "tv_academy_debate_clear_selected_seat_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
    elif key in {"support_price_join", "scientist_bargain_support"}:
        priced_option(lines, level, data, event_num, "a", ["tv_academy_debate_apply_selected_price_effect = yes", "tv_academy_debate_selected_group_seated_tooltip_effect = yes", "tv_academy_debate_assign_selected_group_to_seat_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
        option(lines, level, f"{EVENT_NS}.{event_num}.b", ["tv_academy_debate_clear_event_state_effect = yes"])
    elif key == "oppose_price_stay_out":
        priced_option(lines, level, data, event_num, "a", ["tv_academy_debate_apply_selected_price_effect = yes", "tv_academy_debate_selected_group_left_tooltip_effect = yes", "tv_academy_debate_mark_selected_group_left_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
        option(lines, level, f"{EVENT_NS}.{event_num}.b", ["tv_academy_debate_selected_group_seated_tooltip_effect = yes", "tv_academy_debate_assign_selected_group_to_seat_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
    elif key == "quarrel":
        option(lines, level, f"{EVENT_NS}.{event_num}.a", [
            f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_SUPPORT} }}",
            "tv_academy_debate_prepare_selected_special_scope_effect = yes",
            "tv_academy_debate_selected_group_seated_tooltip_effect = yes",
            "tv_academy_debate_assign_selected_group_to_seat_effect = yes",
            f"set_variable = {{ name = {EVENT_GROUP} value = var:{EVENT_GROUP_2} }}",
            f"set_variable = {{ name = {EVENT_STANCE} value = {STANCE_OPPOSE} }}",
            f"remove_variable = {EVENT_SEAT}",
            "tv_academy_debate_prepare_selected_special_scope_effect = yes",
            "tv_academy_debate_selected_group_seated_tooltip_effect = yes",
            "tv_academy_debate_assign_selected_group_to_seat_effect = yes",
            "tv_academy_debate_clear_event_state_effect = yes",
        ])
    elif key in {"scientist_sways_support", "scientist_angers_oppose"}:
        option(lines, level, f"{EVENT_NS}.{event_num}.a", ["tv_academy_debate_selected_group_seated_tooltip_effect = yes", "tv_academy_debate_assign_selected_group_to_seat_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
    elif key == "great_scientist_requests_seat":
        option(lines, level, f"{EVENT_NS}.{event_num}.a", ["tv_academy_debate_selected_group_seated_tooltip_effect = yes", "tv_academy_debate_assign_selected_group_to_seat_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
        option(lines, level, f"{EVENT_NS}.{event_num}.b", ["tv_academy_debate_clear_event_state_effect = yes"])
    elif key == "royal_appointment":
        for slot in range(1, 4):
            emit(lines, level, "option = {")
            emit(lines, level + 1, f"name = {EVENT_NS}.{event_num}.{chr(96 + slot)}")
            emit(lines, level + 1, f"trigger = {{ has_variable = tv_academy_debate_royal_option_{slot}_group }}")
            emit(lines, level + 1, f"tv_academy_debate_accept_royal_option_{slot}_effect = yes")
            emit(lines, level, "}")
        option(lines, level, f"{EVENT_NS}.{event_num}.d", ["tv_academy_debate_clear_event_state_effect = yes"])
    elif key == "neutral_decides":
        option(lines, level, f"{EVENT_NS}.{event_num}.a", ["tv_academy_debate_set_selected_neutral_to_support_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
        option(lines, level, f"{EVENT_NS}.{event_num}.b", ["tv_academy_debate_set_selected_neutral_to_oppose_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
    elif key in {"neutral_price_support", "scientist_sways_neutral", "scientist_bargain_neutral"}:
        effects = []
        if "price" in key or key == "scientist_bargain_neutral":
            effects.append("tv_academy_debate_apply_selected_price_effect = yes")
        effects.extend(["tv_academy_debate_set_selected_neutral_to_support_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])
        if key in {"neutral_price_support", "scientist_bargain_neutral"}:
            priced_option(lines, level, data, event_num, "a", effects)
        else:
            option(lines, level, f"{EVENT_NS}.{event_num}.a", effects)
        option(lines, level, f"{EVENT_NS}.{event_num}.b", ["tv_academy_debate_clear_event_state_effect = yes"])
    elif key in {"neutral_price_not_oppose", "scientist_angers_neutral"}:
        effects = []
        if key == "neutral_price_not_oppose":
            effects.append("tv_academy_debate_apply_selected_price_effect = yes")
        effects.append("tv_academy_debate_clear_event_state_effect = yes")
        if key == "neutral_price_not_oppose":
            priced_option(lines, level, data, event_num, "a", effects)
        else:
            option(lines, level, f"{EVENT_NS}.{event_num}.a", effects)
        option(lines, level, f"{EVENT_NS}.{event_num}.b", ["tv_academy_debate_set_selected_neutral_to_oppose_effect = yes", "tv_academy_debate_clear_event_state_effect = yes"])


def priced_option(lines: list[str], level: int, data: dict, event_num: int, opt: str, effects: list[str]) -> None:
    for idx, price in enumerate(data["prices"], 1):
        emit(lines, level, "option = {")
        emit(lines, level + 1, f"name = {price_option_loc_key(event_num, opt, price)}")
        emit(lines, level + 1, f"trigger = {{ {var_eq(EVENT_PRICE, idx)} }}")
        for effect in effects:
            emit(lines, level + 1, effect)
        emit(lines, level, "}")


def option(lines: list[str], level: int, name: str, effects: list[str]) -> None:
    emit(lines, level, "option = {")
    emit(lines, level + 1, f"name = {name}")
    for effect in effects:
        emit(lines, level + 1, effect)
    emit(lines, level, "}")


def generate_modifiers(data: dict) -> str:
    script = "scripts/in_game/common/static_modifiers/gen_tv_academy_philosophy_debate_modifiers.py"
    lines = [header(script, PHILOSOPHY_DEBATE_DATA_SOURCES).rstrip(), ""]
    seen: set[str] = set()
    for group in groups(data):
        if not is_estate_or_variant(group):
            continue
        name = estate_modifier_name(group)
        if name in seen:
            continue
        seen.add(name)
        emit(lines, 0, f"{name} = {{")
        emit(lines, 1, f"{group['base_estate']}_target_satisfaction = 0.025")
        emit(lines, 1, f"global_{group['base_estate']}_power = 0.50")
        emit(lines, 0, "}")
        emit(lines)
    for entry in random_event_modifier_entries(data):
        emit(lines, 0, f"{entry['key']} = {{")
        emit(lines, 1, f"legislative_efficiency = {format_number(entry['modifier_value'])}")
        emit(lines, 0, "}")
        emit(lines)
    return "\n".join(lines).rstrip() + "\n"


def generate_loc(data: dict, language: str) -> str:
    lang_header = "l_english" if language == "english" else "l_simp_chinese"
    script = f"scripts/main_menu/localization/{language}/gen_tv_academy_philosophy_debate_l_{'english' if language == 'english' else 'simp_chinese'}.py"
    loc_lang = "english" if language == "english" else "simp_chinese"
    entries: dict[str, str] = {}
    for group in groups(data):
        entries[group_loc_key(group)] = group["loc"][loc_lang]
        entries[group_tt_key(group)] = f"{group['icon']} {group['loc'][loc_lang]}"
        if loc_lang == "simp_chinese":
            entries[group_seated_tooltip_key(group)] = f"{group['loc'][loc_lang]}已入席"
            entries[group_left_tooltip_key(group)] = f"{group['loc'][loc_lang]}已离席"
        else:
            entries[group_seated_tooltip_key(group)] = f"Seat filled: {group['loc'][loc_lang]}"
            entries[group_left_tooltip_key(group)] = f"Seat vacated: {group['loc'][loc_lang]}"
    for price in data["prices"]:
        entries[price_loc_key(price)] = price["loc"][loc_lang]
    entries[f"{EVENT_NS}.1.t"] = "Academy Debate Monthly Tick" if language == "english" else "科学院辩论月度刻"
    entries.update(generic_loc_entries(data, loc_lang))
    for duplicate_key in (
        "TV_ACADEMY_DEBATE_LOCAL_PROGRESS_TT",
        "TV_ACADEMY_DEBATE_LOCAL_EMPTY_SEAT_TT",
        "TV_ACADEMY_DEBATE_LOCAL_CROWN_SEAT_TT",
    ):
        entries.pop(duplicate_key, None)
    for event in random_events(data):
        entries[random_event_loc_key(event, "t")] = event["title"][loc_lang]
        entries[random_event_loc_key(event, "d")] = random_event_desc_with_hint(data, event, loc_lang)
        for opt_key in ("a", "b"):
            entries[random_event_loc_key(event, opt_key)] = event["options"][opt_key]["text"][loc_lang]
    for entry in random_event_modifier_entries(data):
        entries[f"STATIC_MODIFIER_NAME_{entry['key']}"] = entry[f"{loc_lang}_name"]
        entries[f"STATIC_MODIFIER_DESC_{entry['key']}"] = entry[f"{loc_lang}_desc"]
    lines = [header(script, PHILOSOPHY_DEBATE_DATA_SOURCES).rstrip(), f"{lang_header}:"]
    for key in sorted(entries):
        value = entries[key].replace('"', '\\"').replace("\n", "\\n")
        lines.append(f' {key}: "{value}"')
    return "\n".join(lines).rstrip() + "\n"


def add_world_debate_loc_entries(entries: dict[str, str], zh: bool) -> None:
    entries["tv_academy_world_debate_situation"] = "科学院世界辩论" if zh else "Academy World Debate"
    entries["tv_academy_world_debate_situation_desc"] = "拥有科学院的国家会在世界辩论阶段围绕同一思潮展开辩论。" if zh else "Countries with an Academy of Sciences enter the world debate stage around the same philosophy."
    entries["TV_ACADEMY_WORLD_DEBATE_TITLE"] = "世界辩论" if zh else "World Debate"
    entries["TV_ACADEMY_WORLD_DEBATE_EMPTY"] = "尚无世界辩论" if zh else "No active world debate"
    entries["TV_ACADEMY_WORLD_DEBATE_EMPTY_SEAT_TT"] = "一个空置的世界辩论席位。" if zh else "An empty world debate seat."
    entries["TV_ACADEMY_WORLD_DEBATE_SEAT_TT"] = "该国家在世界辩论中拥有一个席位。绿色支持，红色反对，黄色中立。" if zh else "This country has one seat in the world debate. Green supports, red opposes, and yellow is neutral."
    entries["TV_ACADEMY_WORLD_DEBATE_STRENGTH_TT"] = "世界辩论实力对比：支持席数 /（支持席数 + 反对席数）。中立席位不计入该比例。" if zh else "World debate strength: support seats divided by support plus opposition seats. Neutral seats are excluded."
    entries["TV_ACADEMY_WORLD_DEBATE_PROGRESS_TT"] = "世界辩论从50进度开始；每月变化为（实力对比 - 50%）×5。达到0为保守结局，达到100为进步结局，10年未结束为中立结局。" if zh else "World debate starts at 50 progress. Each month changes by (strength - 50%) x 5. Reaching 0 gives the conservative result, reaching 100 gives the progressive result, and ten years without a result gives the neutral result."


def notification_loc_entries(zh: bool) -> dict[str, str]:
    if zh:
        return {
            f"{EVENT_NS}.{LOCAL_ACTION_POSITIVE_EVENT}.t": "辩论渐占上风",
            f"{EVENT_NS}.{LOCAL_ACTION_POSITIVE_EVENT}.d": "这个月的政策和公众行动，都替当前议题攒了几分说服力。辩论的风向，正慢慢往接纳那头吹。",
            f"{EVENT_NS}.{LOCAL_ACTION_POSITIVE_EVENT}.a": "圆桌记下这一笔。",
            f"{EVENT_NS}.{LOCAL_ACTION_NEGATIVE_EVENT}.t": "辩论渐落下风",
            f"{EVENT_NS}.{LOCAL_ACTION_NEGATIVE_EVENT}.d": "这个月的政策和公众行动，反倒削弱了当前议题的说服力。辩论的风向，正慢慢往排斥那头吹。",
            f"{EVENT_NS}.{LOCAL_ACTION_NEGATIVE_EVENT}.a": "圆桌记下这一笔。",
            f"{EVENT_NS}.{WORLD_DEBATE_START_EVENT}.t": "世界辩论开场",
            f"{EVENT_NS}.{WORLD_DEBATE_START_EVENT}.d": "各国的科学院，都围着同一个哲学议题坐了下来。我们的科学院也会派人上场，看这场争论最后落在哪一边。",
            f"{EVENT_NS}.{WORLD_DEBATE_START_EVENT}.a": "派我们的代表入席。",
            f"{EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT}.t": "世界辩论，接纳了",
            f"{EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT}.d": "世界辩论有了结论：这个议题，被接纳了。我们的科学院就此推进哲学序列，让相关思潮在国内扎下根。",
            f"{EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT}.a": "记下这个结论。",
            f"{EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT}.t": "世界辩论，否了",
            f"{EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT}.d": "世界辩论有了结论：这个议题，被否了。我们的科学院就此收起这个议题，继续往哲学序列的下一步走。",
            f"{EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT}.a": "记下这个结论。",
            f"{EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT}.t": "世界辩论，不了了之",
            f"{EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT}.d": "世界辩论没能吵出个结果。我们的科学院把这个议题归了档，继续往哲学序列的下一步走。",
            f"{EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT}.a": "把档案封起来。",
            f"{EVENT_NS}.{AUTO_STANCE_SUPPORT_EVENT}.t": "有人倒向了支持",
            f"{EVENT_NS}.{AUTO_STANCE_SUPPORT_EVENT}.d": "这个月的政局和民情，悄悄挪动了圆桌上几张椅子。至少有一个辩论席，已经转而支持当前议题了。",
            f"{EVENT_NS}.{AUTO_STANCE_SUPPORT_EVENT}.a": "记下这次转向。",
            f"{EVENT_NS}.{AUTO_STANCE_OPPOSE_EVENT}.t": "有人倒向了反对",
            f"{EVENT_NS}.{AUTO_STANCE_OPPOSE_EVENT}.d": "这个月的政局和民情，悄悄挪动了圆桌上几张椅子。至少有一个辩论席，已经转而反对当前议题了。",
            f"{EVENT_NS}.{AUTO_STANCE_OPPOSE_EVENT}.a": "记下这次转向。",
            f"{EVENT_NS}.{AUTO_STANCE_NEUTRAL_EVENT}.t": "有人不表态了",
            f"{EVENT_NS}.{AUTO_STANCE_NEUTRAL_EVENT}.d": "这个月的政局和民情，悄悄挪动了圆桌上几张椅子。至少有一个辩论席，已经不再明确支持或反对当前议题了。",
            f"{EVENT_NS}.{AUTO_STANCE_NEUTRAL_EVENT}.a": "记下这次转向。",
            f"{EVENT_NS}.{AUTO_SEAT_VACATED_EVENT}.t": "一个席位空了下来",
            f"{EVENT_NS}.{AUTO_SEAT_VACATED_EVENT}.d": "圆桌上一位特殊的常客，已经没法再来了。这个月的清点，把对应的辩论席空了出来。",
            f"{EVENT_NS}.{AUTO_SEAT_VACATED_EVENT}.a": "记下这次空缺。",
        }
    return {
        f"{EVENT_NS}.{LOCAL_ACTION_POSITIVE_EVENT}.t": "The Debate Tips Our Way",
        f"{EVENT_NS}.{LOCAL_ACTION_POSITIVE_EVENT}.d": "This month's policies and public deeds have added real weight to the current issue. The debate is leaning toward acceptance.",
        f"{EVENT_NS}.{LOCAL_ACTION_POSITIVE_EVENT}.a": "The table takes note.",
        f"{EVENT_NS}.{LOCAL_ACTION_NEGATIVE_EVENT}.t": "The Debate Tips Against Us",
        f"{EVENT_NS}.{LOCAL_ACTION_NEGATIVE_EVENT}.d": "This month's policies and public deeds have taken weight away from the current issue. The debate is leaning toward rejection.",
        f"{EVENT_NS}.{LOCAL_ACTION_NEGATIVE_EVENT}.a": "The table takes note.",
        f"{EVENT_NS}.{WORLD_DEBATE_START_EVENT}.t": "The World Takes Its Seats",
        f"{EVENT_NS}.{WORLD_DEBATE_START_EVENT}.d": "Every country with an Academy of Sciences has gathered around the same philosophical issue. Our Academy will send its own delegation and watch where the argument leads.",
        f"{EVENT_NS}.{WORLD_DEBATE_START_EVENT}.a": "Send our delegation.",
        f"{EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT}.t": "The World Debate Says Yes",
        f"{EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT}.d": "The world debate has a verdict: the issue is accepted. Our Academy advances the philosophy sequence and lets the idea take root at home.",
        f"{EVENT_NS}.{WORLD_DEBATE_PROGRESSIVE_EVENT}.a": "Record the verdict.",
        f"{EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT}.t": "The World Debate Says No",
        f"{EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT}.d": "The world debate has a verdict: the issue is rejected. Our Academy closes the file and moves on to the next step in the sequence.",
        f"{EVENT_NS}.{WORLD_DEBATE_CONSERVATIVE_EVENT}.a": "Record the verdict.",
        f"{EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT}.t": "The World Debate Fizzles Out",
        f"{EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT}.d": "The world debate never reached a verdict. Our Academy files the issue away and moves on to the next step in the sequence.",
        f"{EVENT_NS}.{WORLD_DEBATE_NEUTRAL_EVENT}.a": "Seal the file.",
        f"{EVENT_NS}.{AUTO_STANCE_SUPPORT_EVENT}.t": "A Chair Slides Toward Support",
        f"{EVENT_NS}.{AUTO_STANCE_SUPPORT_EVENT}.d": "This month's politics and public mood have shifted a few chairs at the table. At least one debate seat now backs the current issue.",
        f"{EVENT_NS}.{AUTO_STANCE_SUPPORT_EVENT}.a": "Note the shift.",
        f"{EVENT_NS}.{AUTO_STANCE_OPPOSE_EVENT}.t": "A Chair Slides Toward Opposition",
        f"{EVENT_NS}.{AUTO_STANCE_OPPOSE_EVENT}.d": "This month's politics and public mood have shifted a few chairs at the table. At least one debate seat now stands against the current issue.",
        f"{EVENT_NS}.{AUTO_STANCE_OPPOSE_EVENT}.a": "Note the shift.",
        f"{EVENT_NS}.{AUTO_STANCE_NEUTRAL_EVENT}.t": "A Chair Slides to the Fence",
        f"{EVENT_NS}.{AUTO_STANCE_NEUTRAL_EVENT}.d": "This month's politics and public mood have shifted a few chairs at the table. At least one debate seat no longer clearly backs or opposes the current issue.",
        f"{EVENT_NS}.{AUTO_STANCE_NEUTRAL_EVENT}.a": "Note the shift.",
        f"{EVENT_NS}.{AUTO_SEAT_VACATED_EVENT}.t": "A Chair Sits Empty",
        f"{EVENT_NS}.{AUTO_SEAT_VACATED_EVENT}.d": "A regular at the table can no longer attend. This month's tally leaves the corresponding seat vacant.",
        f"{EVENT_NS}.{AUTO_SEAT_VACATED_EVENT}.a": "Note the vacancy.",
    }


def generic_loc_entries(data: dict, lang: str) -> dict[str, str]:
    zh = lang == "simp_chinese"
    entries: dict[str, str] = {}
    entries[LOCAL_DEBATE_PROGRESS_VAR] = "本地辩论进度" if zh else "Local Debate Progress"
    entries[f"{LOCAL_DEBATE_PROGRESS_VAR}_desc"] = (
        "衡量科学院本地哲学辩论对当前议题的接纳或排斥程度。达到100时议题被接纳，达到0时议题被否决。"
        if zh
        else "Measures the Academy's local philosophy debate movement toward acceptance or rejection of the current issue. Reaching 100 accepts the issue; reaching 0 rejects it."
    )
    entries["TV_ACADEMY_DEBATE_POSITION_FORMAT"] = "$VAL|0$/100"
    entries["TV_ACADEMY_DEBATE_POSITION_CHANGE_FORMAT"] = "$KEY$: $VALUE|+=2$"
    if zh:
        entries.update({
            "TV_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "获得$VALUE|+$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "我们获得$VALUE|+$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "获得$VALUE|+$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_PAST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "已获得$VALUE|+$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_PAST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "我们已获得$VALUE|+$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_PAST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "已获得$VALUE|+$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "失去$VALUE|-$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "我们失去$VALUE|-$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "失去$VALUE|-$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_PAST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "已失去$VALUE|-$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_PAST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "我们已失去$VALUE|-$#Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_PAST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "已失去$VALUE|-$#Y $tv_academy_philosophy_debate_position$#!",
        })
    else:
        entries.update({
            "TV_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "Gains $VALUE|+$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "We gain $VALUE|+$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "Gains $VALUE|+$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_PAST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "Gained $VALUE|+$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_PAST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "We gained $VALUE|+$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_PAST_ADD_ACADEMY_DEBATE_LOCAL_PROGRESS": "Gained $VALUE|+$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "Loses $VALUE|-$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "We lose $VALUE|-$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "Loses $VALUE|-$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_PAST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "Lost $VALUE|-$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_FIRST_PAST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "We lost $VALUE|-$ #Y $tv_academy_philosophy_debate_position$#!",
            "TV_THIRD_PAST_SUBTRACT_ACADEMY_DEBATE_LOCAL_PROGRESS": "Lost $VALUE|-$ #Y $tv_academy_philosophy_debate_position$#!",
        })
    entries["TV_ACADEMY_DEBATE_STANCE_SUPPORT"] = "支持" if zh else "Support"
    entries["TV_ACADEMY_DEBATE_STANCE_OPPOSE"] = "反对" if zh else "Oppose"
    entries["TV_ACADEMY_DEBATE_STANCE_NEUTRAL"] = "中立" if zh else "Neutral"
    entries["TV_ACADEMY_DEBATE_SEAT_FILLED_TT"] = "该辩论席已有团体入座。绿色表示支持，红色表示反对，黄色表示中立。" if zh else "This debate seat is occupied. Green supports the proposal, red opposes it, and yellow is neutral."
    entries["TV_ACADEMY_DEBATE_LOCAL_PROGRESS_TT"] = "本地辩论进度现在完全由辩论席上的团体通过月度事件推动：支持方增加进度，反对方降低进度，中立方暂不影响进度。" if zh else "Local debate progress is now event-driven by seated debate groups. Supporters increase progress, opponents reduce it, and neutral groups do not move it yet."
    entries["TV_ACADEMY_DEBATE_LOCAL_EMPTY_SEAT_TT"] = "一个空置的[tv_debate_seat|E]。" if zh else "An empty [tv_debate_seat|E]."
    entries["TV_ACADEMY_DEBATE_LOCAL_CROWN_SEAT_TT"] = "王室固定主持本国辩论，并始终支持当前议题。" if zh else "The Crown permanently presides over the domestic debate and always supports the current issue."
    add_world_debate_loc_entries(entries, zh)
    templates = event_loc_templates(zh)
    for group in groups(data):
        name = group["loc"][lang]
        for num, template in templates.items():
            entries[f"{EVENT_NS}.{num}.d_{group['key']}"] = template["desc"].format(group=name)
    price_option_events = {102: "a", 103: "a", 107: "a", 111: "a", 112: "a", 115: "a"}
    for num, template in templates.items():
        entries[f"{EVENT_NS}.{num}.t"] = template["title"]
        group_label = "某个[tv_debate_group|E]" if zh else "a [tv_debate_group|E]"
        entries[f"{EVENT_NS}.{num}.d"] = template["desc"].format(group=group_label)
        for opt, text in template["options"].items():
            entries[f"{EVENT_NS}.{num}.{opt}"] = text
        if num in price_option_events:
            opt = price_option_events[num]
            base_text = template["options"][opt]
            for price in data["prices"]:
                entries[price_option_loc_key(num, opt, price)] = f"{base_text}: {price['loc'][lang]}"
    entries.update(notification_loc_entries(zh))
    for group in groups(data):
        if is_estate_or_variant(group):
            entries[f"STATIC_MODIFIER_NAME_{estate_modifier_name(group)}"] = ("王室钦点：" if zh else "Royal Appointment: ") + group["loc"][lang]
            entries[f"STATIC_MODIFIER_DESC_{estate_modifier_name(group)}"] = "该阶层因王室在哲学辩论中公开抬举其代表而更加满意，也拥有更高影响力。" if zh else "This estate is more satisfied and influential after the Crown publicly elevated its representative in a philosophy debate."
    return entries


def event_loc_templates(zh: bool) -> dict[int, dict]:
    if zh:
        return {
            100: {"title": "又添一位客人", "desc": "#Y {group}#!推门而入，要在[tv_debate_seat|E]上占一个位置。他们的立场，早由当前议题和国内的风气定下了，用不着再问。", "options": {"a": "给他们让个座"}},
            101: {"title": "有人拂袖而去", "desc": "#R {group}#!觉得话不投机，径直退出了这场辩论。走了的[tv_debate_group|E]，这场辩论里就不会再回来了。", "options": {"a": "记下他们的离席"}},
            102: {"title": "支持是有价的", "desc": "#G {group}#!愿意站到我们这边，但先得开个价。天下没有白来的掌声。", "options": {"a": "答应这个价", "b": "拒绝"}},
            103: {"title": "反对派想要封口费", "desc": "#R {group}#!眼看就要坐上反对席；给点好处，倒也能让他们打消这个念头。", "options": {"a": "付这笔钱", "b": "让他们上场"}},
            104: {"title": "一场口角闹大了", "desc": "#Y {group}#!为着当前议题跟另一个团体吵得不可开交，谁也不肯先松口，两边索性都坐上了辩论席。", "options": {"a": "给他们各留一席"}},
            105: {"title": "大科学家说动了人心", "desc": "#G 大科学家外交能力不低于80#!，一番游说下来，#G {group}#!站到了我们这边。", "options": {"a": "欢迎他们入席"}},
            106: {"title": "大科学家说错了话", "desc": "#R 大科学家外交能力不高于30#!，一句话没说对，私下惹恼了#R {group}#!。", "options": {"a": "他们要公开唱反调了"}},
            107: {"title": "一笔私下的交易", "desc": "#Y 大科学家外交能力介于30与80之间#!，跟#G {group}#!谈出了一份有条件的支持。", "options": {"a": "接受这笔交易", "b": "拒绝"}},
            108: {"title": "大科学家想亲自上场", "desc": "#Y 大科学家#!想放下手头的研究，亲自上桌辩论几句。一旦同意，他就要一直忙到这场辩论收场为止。", "options": {"a": "准他入席", "b": "婉言谢绝"}},
            109: {"title": "王室金口一开", "desc": "#G 王室#!有意从支持当前议题的阶层或其变体里挑一位代表入席，还会给对方的基础阶层加五年的影响力。", "options": {"a": "钦点第一候选", "b": "钦点第二候选", "c": "钦点第三候选", "d": "这次不点了"}},
            110: {"title": "墙头草也得站队", "desc": "#Y {group}#!发现自己再骑墙下去也不是办法，只好在支持和反对之间挑一个。", "options": {"a": "站过来支持我们", "b": "转身站到对面"}},
            111: {"title": "中立方也想讨点好处", "desc": "#Y {group}#!表示，只要给点甜头，公开支持这事不是不能谈。", "options": {"a": "答应这个价", "b": "拒绝"}},
            112: {"title": "不表态,也是一种威胁", "desc": "#Y {group}#!话里有话：要是什么好处都不给，他们保不齐会转去反对。", "options": {"a": "给出让步", "b": "什么都不给"}},
            113: {"title": "大科学家把墙头草劝了过来", "desc": "#G 大科学家外交能力不低于80#!，说得原本中立的#G {group}#!点了头，站到我们这边。", "options": {"a": "这下好了", "b": "先缓一缓"}},
            114: {"title": "大科学家把墙头草惹恼了", "desc": "#R 大科学家外交能力不高于30#!，原本还中立的#R {group}#!，被这么一激，转头站到了对面。", "options": {"a": "这下麻烦了", "b": "赶紧安抚"}},
            115: {"title": "跟墙头草的私下交易", "desc": "#Y 大科学家外交能力介于30与80之间#!，跟原本中立的#Y {group}#!谈出了一份有条件的支持。", "options": {"a": "接受这笔交易", "b": "拒绝"}},
        }
    return {
        100: {"title": "Another Chair Fills Up", "desc": "#Y {group}#! walks in and claims a [tv_debate_seat|E]. Their stance is already settled by the current issue and the mood back home, no need to ask.", "options": {"a": "Make room for them"}},
        101: {"title": "A Chair Empties Out", "desc": "#R {group}#! has heard enough and walks out of this debate. Once a [tv_debate_group|E] leaves, it will not come back before the debate ends.", "options": {"a": "Note their departure"}},
        102: {"title": "Support Has a Price Tag", "desc": "#G {group}#! will stand with us, but only after naming a price. Nothing at this table comes free.", "options": {"a": "Pay the price", "b": "Refuse"}},
        103: {"title": "The Opposition Wants Hush Money", "desc": "#R {group}#! is about to take an opposition seat, but the right favor might change their mind.", "options": {"a": "Pay them off", "b": "Let them speak"}},
        104: {"title": "A Quarrel Gets Out of Hand", "desc": "#Y {group}#! and another group are trading words over the current issue, and neither will back down. Both end up taking a seat.", "options": {"a": "Seat them both"}},
        105: {"title": "The Great Scientist Wins Them Over", "desc": "#G Great Scientist Diplomacy is at least 80#!, and some careful persuading has brought #G {group}#! to our side.", "options": {"a": "Welcome them in"}},
        106: {"title": "The Great Scientist Puts a Foot Wrong", "desc": "#R Great Scientist Diplomacy is no more than 30#!, and one careless remark has left #R {group}#! quietly furious.", "options": {"a": "They'll speak against us now"}},
        107: {"title": "A Quiet Arrangement", "desc": "#Y Great Scientist Diplomacy is between 30 and 80#!, enough to talk #G {group}#! into a conditional support.", "options": {"a": "Take the deal", "b": "Refuse"}},
        108: {"title": "The Great Scientist Wants a Seat", "desc": "#Y The Great Scientist#! wants to set the research aside and argue this one in person. Say yes, and they'll be tied up here until the debate ends.", "options": {"a": "Grant the seat", "b": "Politely decline"}},
        109: {"title": "The Crown Makes Its Choice", "desc": "#G The Crown#! may name one supportive estate or variant group to a seat, and grant its base estate five years of added influence.", "options": {"a": "Name the first nominee", "b": "Name the second nominee", "c": "Name the third nominee", "d": "Make no appointment"}},
        110: {"title": "The Fence-Sitters Pick a Side", "desc": "#Y {group}#! has decided that sitting on the fence forever isn't an option, and must choose a side.", "options": {"a": "They side with us", "b": "They side against us"}},
        111: {"title": "Neutral, for the Right Price", "desc": "#Y {group}#! hints that public support isn't out of reach, given a small sweetener.", "options": {"a": "Pay the price", "b": "Refuse"}},
        112: {"title": "Silence Has Its Own Threat", "desc": "#Y {group}#! makes it plain: without some concession, they might not stay neutral for long.", "options": {"a": "Offer a concession", "b": "Offer nothing"}},
        113: {"title": "The Great Scientist Wins the Fence-Sitters", "desc": "#G Great Scientist Diplomacy is at least 80#!, and the once-neutral #G {group}#! has nodded along and come to our side.", "options": {"a": "Well done", "b": "Hold off for now"}},
        114: {"title": "The Great Scientist Loses the Fence-Sitters", "desc": "#R Great Scientist Diplomacy is no more than 30#!, and the once-neutral #R {group}#! has been pushed straight into opposition.", "options": {"a": "That's unfortunate", "b": "Try to smooth it over"}},
        115: {"title": "A Quiet Word with the Fence-Sitters", "desc": "#Y Great Scientist Diplomacy is between 30 and 80#!, enough to talk the once-neutral #Y {group}#! into a conditional support.", "options": {"a": "Take the deal", "b": "Refuse"}},
    }
