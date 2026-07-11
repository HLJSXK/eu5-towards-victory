"""Generate Wonder Construction random-event eligibility triggers."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_construction_event_lib import (
    build_events,
    format_noneng_magnitude,
    indent_lines,
    load_data,
    render_header,
)


OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_triggers" / "tv_wonder_construction_event_triggers.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_triggers/gen_tv_wonder_construction_event_triggers.py"
DATA_REL = "data/wonder_construction_events.yaml"


def eng_positive_trigger(token_id: str) -> list[str]:
    if token_id == "domestic_support":
        return ["tv_wonder_domestic_support_can_increase_trigger = yes"]
    if token_id == "scale_competence":
        return ["var:tv_wonder_scale_competence ?= { this < 100 }"]
    if token_id == "organization_competence":
        return ["var:tv_wonder_organization_competence ?= { this < 100 }"]
    if token_id == "logistics_competence":
        return ["var:tv_wonder_logistics_competence ?= { this < 100 }"]
    if token_id == "construction_progress":
        return ["tv_wonder_active_part_can_gain_progress_trigger = yes"]
    raise ValueError(f"Unhandled engineering token: {token_id}")


def eng_negative_trigger(token_id: str) -> list[str]:
    if token_id == "domestic_support":
        return ["tv_wonder_domestic_support_can_decrease_trigger = yes"]
    if token_id == "scale_competence":
        return ["var:tv_wonder_scale_competence ?= { this > 0 }"]
    if token_id == "organization_competence":
        return ["var:tv_wonder_organization_competence ?= { this > 0 }"]
    if token_id == "logistics_competence":
        return ["var:tv_wonder_logistics_competence ?= { this > 0 }"]
    if token_id == "construction_progress":
        return ["tv_wonder_active_part_has_progress_trigger = yes"]
    raise ValueError(f"Unhandled engineering token: {token_id}")


def noneng_loss_trigger(token: dict, units: int) -> list[str]:
    token_id = token["id"]
    if token_id == "nobles_satisfaction":
        return ["country_has_estate = estate_type:nobles_estate"]
    if token_id == "clergy_satisfaction":
        return ["country_has_estate = estate_type:clergy_estate"]
    if token_id == "burghers_satisfaction":
        return ["country_has_estate = estate_type:burghers_estate"]
    if token_id == "peasants_satisfaction":
        return ["country_has_estate = estate_type:peasants_estate"]
    if token_id == "site_development":
        value = format_noneng_magnitude(token_id, token["value"] * units)
        return [f"var:tv_wonder_site ?= {{ development >= {value} }}"]
    if token_id == "site_prosperity":
        value = format_noneng_magnitude(token_id, token["value"] * units)
        return [f"var:tv_wonder_site ?= {{ prosperity >= {value} }}"]
    if token_id == "capital_development":
        value = format_noneng_magnitude(token_id, token["value"] * units)
        return [f"capital ?= {{ development >= {value} }}"]
    if token_id == "capital_prosperity":
        value = format_noneng_magnitude(token_id, token["value"] * units)
        return [f"capital ?= {{ prosperity >= {value} }}"]
    if token_id == "site_laborers":
        return ["tv_wonder_site_has_laborer_pop_trigger = yes"]
    return []


def engineer_tier_trigger(kind: str) -> list[str]:
    if kind == "engineer_gain_engineering_2":
        return ["tv_great_engineer_effective_mil_above_80_trigger = yes"]
    if kind == "engineer_gain_engineering_1":
        return ["tv_great_engineer_effective_mil_above_50_trigger = yes"]
    if kind == "engineer_swing_engineering_1":
        return [
            "tv_great_engineer_effective_mil_at_least_20_trigger = yes",
            "tv_great_engineer_effective_mil_not_above_80_trigger = yes",
        ]
    if kind == "engineer_lose_noneng_1":
        return ["tv_great_engineer_effective_mil_below_50_trigger = yes"]
    if kind == "engineer_lose_noneng_2":
        return ["tv_great_engineer_effective_mil_below_20_trigger = yes"]
    return []


def event_trigger_lines(event: dict) -> list[str]:
    lines = ["tv_wonder_construction_random_events_active_trigger = yes"]
    kind = event["kind"]
    eng = event.get("eng")
    noneng = event.get("noneng")

    if kind in {"gain_engineering_2", "gain_engineering_1", "engineer_gain_engineering_2", "engineer_gain_engineering_1"}:
        lines.extend(eng_positive_trigger(eng["id"]))
    elif kind == "trade_noneng_for_eng":
        lines.extend(eng_positive_trigger(eng["id"]))
        lines.extend(noneng_loss_trigger(noneng, 1))
    elif kind in {"swing_engineering_1", "engineer_swing_engineering_1"}:
        lines.extend(eng_positive_trigger(eng["id"]))
        lines.extend(eng_negative_trigger(eng["id"]))
    elif kind == "choose_eng_or_noneng_loss":
        lines.extend(eng_negative_trigger(eng["id"]))
        lines.extend(noneng_loss_trigger(noneng, 1))
    elif kind in {"lose_noneng_1", "engineer_lose_noneng_1"}:
        lines.extend(noneng_loss_trigger(noneng, 1))
    elif kind in {"lose_noneng_2", "engineer_lose_noneng_2"}:
        lines.extend(noneng_loss_trigger(noneng, 2))
    else:
        raise ValueError(f"Unhandled kind: {kind}")

    lines.extend(engineer_tier_trigger(kind))
    return lines


def render_eligibility(event: dict) -> str:
    body = "\n".join(event_trigger_lines(event))
    return "\n".join(
        [
            f"tv_wonder_construction_event_{event['id']}_eligible_trigger = {{",
            indent_lines(body, 1),
            "}",
        ]
    )


def generate() -> str:
    events = build_events(load_data())
    header = render_header(
        SCRIPT_REL,
        DATA_REL,
        "# Towards Victory - generated Wonder Construction event eligibility triggers.",
    )
    return f"{header}\n" + "\n\n".join(render_eligibility(event) for event in events) + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
