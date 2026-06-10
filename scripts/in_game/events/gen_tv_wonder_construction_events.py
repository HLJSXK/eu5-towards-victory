"""Generate Wonder Construction monthly random event definitions."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_construction_event_lib import build_events, indent_lines, load_data, render_header


OUT_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_wonder_construction_events.txt"
SCRIPT_REL = "scripts/in_game/events/gen_tv_wonder_construction_events.py"
DATA_REL = "data/wonder_construction_events.yaml"
T = "\t"
WONDER_IMAGE_DIR = "gfx/interface/icons/towards_victory/wonders"
CONSTRUCTION_EVENT_IMAGE = f"{WONDER_IMAGE_DIR}/tv_wonder_construction.dds"


ENG_EFFECTS = {
    "domestic_support": "tv_change_wonder_domestic_support_effect = { value = VALUE }",
    "scale_competence": "tv_wonder_change_scale_competence_effect = { value = VALUE }",
    "organization_competence": "tv_wonder_change_organization_competence_effect = { value = VALUE }",
    "logistics_competence": "tv_wonder_change_logistics_competence_effect = { value = VALUE }",
    "construction_progress": "tv_wonder_change_construction_progress_effect = { value = VALUE }",
}

NONENG_EFFECTS = {
    "gold": "change_gold_effect = { scale = -1 }",
    "legitimacy": "add_legitimacy = -5",
    "stability": "add_stability = -7",
    "prestige": "add_prestige = -10",
    "nobles_satisfaction": "add_estate_satisfaction = { type = estate_type:nobles_estate value = -0.10 }",
    "clergy_satisfaction": "add_estate_satisfaction = { type = estate_type:clergy_estate value = -0.10 }",
    "burghers_satisfaction": "add_estate_satisfaction = { type = estate_type:burghers_estate value = -0.10 }",
    "peasants_satisfaction": "add_estate_satisfaction = { type = estate_type:peasants_estate value = -0.20 }",
    "site_development": "var:tv_wonder_site ?= { change_development = -0.25 }",
    "site_prosperity": "var:tv_wonder_site ?= { change_prosperity = -0.2 }",
    "capital_development": "capital ?= { change_development = -0.25 }",
    "capital_prosperity": "capital ?= { change_prosperity = -0.2 }",
    "site_laborers": "tv_wonder_site_laborer_casualty_effect = { value = 10 }",
}


def eng_effect(token: dict, units: int, sign: int) -> str:
    value = token["value"] * units * sign
    return ENG_EFFECTS[token["id"]].replace("VALUE", str(value))


def noneng_effect(token: dict, units: int) -> str:
    effect = NONENG_EFFECTS[token["id"]]
    if units == 1:
        return effect
    if token["id"] == "gold":
        return effect.replace("scale = -1", f"scale = -{units}")
    if token["id"] == "legitimacy":
        return f"add_legitimacy = -{5 * units}"
    if token["id"] == "stability":
        return f"add_stability = -{7 * units}"
    if token["id"] == "prestige":
        return f"add_prestige = -{10 * units}"
    if token["id"] == "nobles_satisfaction":
        return f"add_estate_satisfaction = {{ type = estate_type:nobles_estate value = -{0.10 * units:.2f} }}"
    if token["id"] == "clergy_satisfaction":
        return f"add_estate_satisfaction = {{ type = estate_type:clergy_estate value = -{0.10 * units:.2f} }}"
    if token["id"] == "burghers_satisfaction":
        return f"add_estate_satisfaction = {{ type = estate_type:burghers_estate value = -{0.10 * units:.2f} }}"
    if token["id"] == "peasants_satisfaction":
        return f"add_estate_satisfaction = {{ type = estate_type:peasants_estate value = -{0.20 * units:.2f} }}"
    if token["id"] == "site_development":
        return f"var:tv_wonder_site ?= {{ change_development = -{0.25 * units:.2f} }}"
    if token["id"] == "site_prosperity":
        return f"var:tv_wonder_site ?= {{ change_prosperity = -{0.2 * units:.1f} }}"
    if token["id"] == "capital_development":
        return f"capital ?= {{ change_development = -{0.25 * units:.2f} }}"
    if token["id"] == "capital_prosperity":
        return f"capital ?= {{ change_prosperity = -{0.2 * units:.1f} }}"
    if token["id"] == "site_laborers":
        return f"tv_wonder_site_laborer_casualty_effect = {{ value = {10 * units} }}"
    raise ValueError(f"Unhandled non-engineering token: {token['id']}")


def eligibility_effect_call(event: dict) -> str:
    return f"tv_wonder_construction_event_{event['id']}_eligible_trigger = yes"


def render_immediate() -> str:
    return "\n".join(
        [
            "immediate = {",
            T + "var:tv_great_engineer_char ?= { save_scope_as = tv_wonder_event_engineer }",
            T + "var:tv_wonder_site ?= { save_scope_as = tv_wonder_event_site }",
            "}",
        ]
    )


def guarded_effect(event: dict, body: str) -> str:
    return "\n".join(
        [
            "if = {",
            T + f"limit = {{ {eligibility_effect_call(event)} }}",
            indent_lines(body, 1),
            "}",
        ]
    )


def option(event: dict, suffix: str, body: str | None = None) -> str:
    lines = ["option = {", T + f"name = tv_engineering_department.{event['id']}.{suffix}"]
    if body:
        lines.append(indent_lines(guarded_effect(event, body), 1))
    lines.append("}")
    return "\n".join(lines)


def render_options(event: dict) -> list[str]:
    kind = event["kind"]
    eng = event.get("eng")
    noneng = event.get("noneng")
    if kind in {"gain_engineering_2", "engineer_gain_engineering_2"}:
        return [option(event, "a", eng_effect(eng, 2, 1))]
    if kind in {"gain_engineering_1", "engineer_gain_engineering_1"}:
        return [option(event, "a", eng_effect(eng, 1, 1))]
    if kind == "trade_noneng_for_eng":
        return [option(event, "a", f"{noneng_effect(noneng, 1)}\n{eng_effect(eng, 1, 1)}"), option(event, "b")]
    if kind in {"swing_engineering_1", "engineer_swing_engineering_1"}:
        body = "\n".join(
            [
                "random_list = {",
                T + f"50 = {{ {eng_effect(eng, 1, 1)} }}",
                T + f"50 = {{ {eng_effect(eng, 1, -1)} }}",
                "}",
            ]
        )
        return [option(event, "a", body)]
    if kind == "choose_eng_or_noneng_loss":
        return [option(event, "a", eng_effect(eng, 1, -1)), option(event, "b", noneng_effect(noneng, 1))]
    if kind in {"lose_noneng_1", "engineer_lose_noneng_1"}:
        return [option(event, "a", noneng_effect(noneng, 1))]
    if kind in {"lose_noneng_2", "engineer_lose_noneng_2"}:
        return [option(event, "a", noneng_effect(noneng, 2))]
    raise ValueError(f"Unhandled kind: {kind}")


def render_event(event: dict) -> str:
    event_id = event["id"]
    parts = [
        f"# -- tv_engineering_department.{event_id} ----------------------------------------------",
        f"tv_engineering_department.{event_id} = {{",
        T + "type = country_event",
        T + f"title = tv_engineering_department.{event_id}.t",
        T + f"desc = tv_engineering_department.{event_id}.d",
        T + f'image = "{CONSTRUCTION_EVENT_IMAGE}"',
        T + f"outcome = {event['outcome']}",
        "",
        T + "trigger = {",
        T * 2 + eligibility_effect_call(event),
        T + "}",
        "",
        indent_lines(render_immediate(), 1),
        "",
    ]
    parts.extend(indent_lines(opt, 1) for opt in render_options(event))
    parts.append("}")
    return "\n".join(parts)


def generate() -> str:
    data = load_data()
    header = render_header(
        SCRIPT_REL,
        DATA_REL,
        "namespace = tv_engineering_department\n",
    )
    events = "\n\n".join(render_event(event) for event in build_events(data))
    return f"{header}\n{events}\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
