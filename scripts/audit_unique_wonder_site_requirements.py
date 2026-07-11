#!/usr/bin/env python3
"""Check every unique wonder's fixed location against its base site-rule trigger_script.

Uses static vanilla map/setup data (topography, raw material, starting location rank,
ownership/capital, owner religion, continent) to evaluate whether the location assigned in
data/unique_wonders.yaml could ever satisfy data/wonder_site_rules.yaml's trigger_script for
that wonder's base_key. Some conditions (has_river, is_adjacent_to_lake, dominant_religion)
have no reliable static source in this repo and are reported as UNKNOWN rather than guessed.
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics._core import (  # noqa: E402
    WONDER_SITE_RULES_FILE,
    load_unique_wonders_source_data,
    load_yaml,
)

BASELINE_FILE = REPO_ROOT / "data" / "wonder_site_requirement_baseline.yaml"

MAP_DATA_DIR = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "map_data"
LOCATION_TEMPLATES_FILE = MAP_DATA_DIR / "location_templates.txt"
DEFINITIONS_FILE = MAP_DATA_DIR / "definitions.txt"
SETUP_START_DIR = REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "setup" / "start"
CITIES_AND_BUILDINGS_FILE = SETUP_START_DIR / "07_cities_and_buildings.txt"
COUNTRIES_FILE = SETUP_START_DIR / "10_countries.txt"
SETUP_COUNTRIES_DIR = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "setup" / "countries"

DEFAULT_LOCATION_RANK = "rural_settlement"

# ---------------------------------------------------------------------------
# Generic flat Jomini-block scanner (identifiers/blocks/bare tokens only - no
# quoted strings appear in any of the files this script reads).
# ---------------------------------------------------------------------------

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
_TOKEN_RE = re.compile(r"\S+")


def _strip_comments(text: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def _read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing reference file: {path}")
    return _strip_comments(path.read_text(encoding="utf-8-sig", errors="replace"))


def parse_level(content: str) -> list[tuple[str, str, str]]:
    """Parse one nesting level. Returns (key, kind, value) tuples.

    kind is 'block' (value is the unparsed inner text), 'scalar' (key = token),
    or 'bare' (a bare token with no following '=', e.g. a location key in a leaf list).
    """
    items: list[tuple[str, str, str]] = []
    i, n = 0, len(content)
    while i < n:
        if content[i].isspace():
            i += 1
            continue
        match = _IDENT_RE.match(content, i)
        if not match:
            i += 1
            continue
        key = match.group(0)
        j = match.end()
        while j < n and content[j].isspace():
            j += 1
        is_optional_eq = content[j : j + 2] == "?="
        is_assignment = is_optional_eq or (j < n and content[j] == "=")
        if is_assignment:
            j += 2 if is_optional_eq else 1
            while j < n and content[j].isspace():
                j += 1
            if j < n and content[j] == "{":
                depth = 1
                start = j + 1
                k = j + 1
                while k < n and depth > 0:
                    if content[k] == "{":
                        depth += 1
                    elif content[k] == "}":
                        depth -= 1
                    k += 1
                items.append((key, "block", content[start : k - 1]))
                i = k
            else:
                token_match = _TOKEN_RE.match(content, j)
                value = token_match.group(0) if token_match else ""
                items.append((key, "scalar", value))
                i = j + len(value)
        else:
            items.append((key, "bare", key))
            i = j
    return items


def _scalar(items: list[tuple[str, str, str]], key: str) -> str | None:
    for item_key, kind, value in items:
        if kind == "scalar" and item_key == key:
            return value
    return None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_location_templates() -> dict[str, dict[str, str | float | None]]:
    text = _read_text(LOCATION_TEMPLATES_FILE)
    out: dict[str, dict[str, str | float | None]] = {}
    for key, kind, value in parse_level(text):
        if kind != "block":
            continue
        fields = parse_level(value)
        suitability_raw = _scalar(fields, "natural_harbor_suitability")
        try:
            suitability = float(suitability_raw) if suitability_raw is not None else 0.0
        except ValueError:
            suitability = 0.0
        out[key] = {
            "topography": _scalar(fields, "topography"),
            "vegetation": _scalar(fields, "vegetation"),
            "raw_material": _scalar(fields, "raw_material"),
            "religion": _scalar(fields, "religion"),
            "natural_harbor_suitability": suitability,
        }
    return out


def load_location_ranks() -> dict[str, str]:
    text = _read_text(CITIES_AND_BUILDINGS_FILE)
    ranks: dict[str, str] = {}
    for key, kind, value in parse_level(text):
        if key != "locations" or kind != "block":
            continue
        for loc_key, loc_kind, loc_value in parse_level(value):
            if loc_kind != "block":
                continue
            rank = _scalar(parse_level(loc_value), "rank")
            if rank:
                ranks[loc_key] = rank
        break
    return ranks


def _find_country_tag_blocks(items: list[tuple[str, str, str]]) -> dict[str, list[tuple[str, str, str]]]:
    results: dict[str, list[tuple[str, str, str]]] = {}
    for key, kind, value in items:
        if kind != "block":
            continue
        sub_items = parse_level(value)
        if _scalar(sub_items, "capital") is not None:
            results[key] = sub_items
        else:
            results.update(_find_country_tag_blocks(sub_items))
    return results


def load_ownership_and_capitals() -> tuple[dict[str, str], dict[str, str]]:
    text = _read_text(COUNTRIES_FILE)
    tag_blocks = _find_country_tag_blocks(parse_level(text))

    capitals: dict[str, str] = {}
    owners: dict[str, str] = {}
    for tag, sub_items in tag_blocks.items():
        capital = _scalar(sub_items, "capital")
        if capital:
            capitals[tag] = capital
        for key, kind, value in sub_items:
            if kind == "block" and key.startswith("own_"):
                for loc_key, loc_kind, _ in parse_level(value):
                    if loc_kind == "bare":
                        owners[loc_key] = tag
    return owners, capitals


def load_country_religions() -> dict[str, str]:
    religions: dict[str, str] = {}
    if not SETUP_COUNTRIES_DIR.exists():
        raise FileNotFoundError(f"Missing reference directory: {SETUP_COUNTRIES_DIR}")
    for path in sorted(SETUP_COUNTRIES_DIR.glob("*.txt")):
        text = _read_text(path)
        for tag, kind, value in parse_level(text):
            if kind != "block":
                continue
            religion = _scalar(parse_level(value), "religion_definition")
            if religion:
                religions[tag] = religion
    return religions


def load_continents() -> dict[str, str]:
    text = _read_text(DEFINITIONS_FILE)
    out: dict[str, str] = {}

    def walk(items: list[tuple[str, str, str]], continent: str) -> None:
        for key, kind, value in items:
            if kind == "block":
                walk(parse_level(value), continent)
            elif kind == "bare":
                out[value] = continent

    for continent, kind, value in parse_level(text):
        if kind == "block":
            walk(parse_level(value), continent)
    return out


def load_baseline() -> dict[str, dict[str, str]]:
    if not BASELINE_FILE.exists():
        return {}
    raw = load_yaml(BASELINE_FILE)
    entries = raw.get("accepted") or []
    baseline: dict[str, dict[str, str]] = {}
    for index, entry in enumerate(entries, start=1):
        context = f"{BASELINE_FILE}.accepted[{index}]"
        key = entry.get("key")
        status = entry.get("status")
        rationale = entry.get("rationale")
        if not key:
            raise ValueError(f"{context}: missing 'key'")
        if status not in ("FAIL", "UNKNOWN"):
            raise ValueError(f"{context}: 'status' must be FAIL or UNKNOWN, got {status!r}")
        if not rationale or not str(rationale).strip():
            raise ValueError(f"{context}: missing 'rationale'")
        if key in baseline:
            raise ValueError(f"{context}: duplicate baseline entry for key '{key}'")
        baseline[key] = {"status": status, "rationale": str(rationale).strip()}
    return baseline


# ---------------------------------------------------------------------------
# Trigger evaluation (three-valued: True / False / None=UNKNOWN)
# ---------------------------------------------------------------------------


class Leaf:
    __slots__ = ("key", "value", "result", "detail", "effective_result")

    def __init__(self, key: str, value: str, result: bool | None, detail: str):
        self.key = key
        self.value = value
        self.result = result
        self.detail = detail
        self.effective_result = result


def _ternary_and(results: list[bool | None]) -> bool | None:
    if any(r is False for r in results):
        return False
    if any(r is None for r in results):
        return None
    return True


def _ternary_or(results: list[bool | None]) -> bool | None:
    if any(r is True for r in results):
        return True
    if any(r is None for r in results):
        return None
    return False


def evaluate_leaf(key: str, value: str, facts: dict) -> Leaf:
    key_lower = key.lower()
    if key_lower == "always":
        return Leaf(key, value, True, "always = yes")
    if key_lower == "is_port":
        return Leaf(key, value, facts["is_port"], f"is_port={facts['is_port']} (harbor_suitability={facts['natural_harbor_suitability']})")
    if key_lower == "is_capital":
        return Leaf(key, value, facts["is_capital"], f"is_capital={facts['is_capital']}")
    if key_lower == "has_owner":
        return Leaf(key, value, facts["owner_tag"] is not None, f"owner={facts['owner_tag']}")
    if key_lower == "has_river":
        return Leaf(key, value, None, "has_river: no static river data available in reference_game_files")
    if key_lower == "is_adjacent_to_lake":
        return Leaf(key, value, None, "is_adjacent_to_lake: no static lake-adjacency data available in reference_game_files")
    if key_lower == "location_rank":
        required = value.split(":", 1)[1] if ":" in value else value
        actual = facts["rank"]
        return Leaf(key, value, actual == required, f"location_rank={actual} (required {required})")
    if key_lower == "topography":
        actual = facts["topography"]
        return Leaf(key, value, actual == value, f"topography={actual} (required {value})")
    if key_lower == "vegetation":
        actual = facts["vegetation"]
        return Leaf(key, value, actual == value, f"vegetation={actual} (required {value})")
    if key_lower == "raw_material":
        required = value.split(":", 1)[1] if ":" in value else value
        actual = facts["raw_material"]
        return Leaf(key, value, actual == required, f"raw_material={actual} (required {required})")
    if key_lower == "dominant_religion" and value == "owner.religion":
        owner_religion = facts["owner_religion"]
        location_religion = facts["location_religion"]
        if owner_religion is None or location_religion is None:
            return Leaf(key, value, None, f"dominant_religion(approx)={location_religion} vs owner.religion={owner_religion}")
        return Leaf(
            key,
            value,
            owner_religion == location_religion,
            f"dominant_religion(approx)={location_religion} vs owner.religion={owner_religion}",
        )
    if key_lower == "continent" and value == "owner.capital.continent":
        continent = facts["continent"]
        capital_continent = facts["owner_capital_continent"]
        if capital_continent is None:
            return Leaf(key, value, None, f"continent={continent} vs owner.capital.continent=UNKNOWN (no owner/capital)")
        return Leaf(
            key,
            value,
            continent == capital_continent,
            f"continent={continent} vs owner.capital.continent={capital_continent}",
        )
    return Leaf(key, value, None, f"unsupported condition '{key} = {value}' - evaluator vocabulary gap")


def evaluate_statement(key: str, value, facts: dict, leaves: list[Leaf], negate: bool = False) -> bool | None:
    """Returns the RAW (non-negated) truth value, used by the parent combinator's ternary
    logic. `negate` only affects the effective_result recorded on leaves for reporting -
    it tracks the cumulative parity of enclosing NOT blocks so a leaf that is internally
    True but sits inside a failing NOT still shows up as the reported cause of failure."""
    key_lower = key.lower()
    if key_lower in ("and", "or", "not"):
        child_items = parse_level(value) if isinstance(value, str) else value
        child_negate = negate ^ (key_lower == "not")
        child_results = [
            evaluate_statement(k, v, facts, leaves, negate=child_negate) for k, kd, v in child_items
        ]
        if key_lower == "and":
            return _ternary_and(child_results)
        if key_lower == "or":
            return _ternary_or(child_results)
        inner = _ternary_and(child_results)
        return None if inner is None else (not inner)
    leaf = evaluate_leaf(key, value, facts)
    leaf.effective_result = leaf.result if not negate else (None if leaf.result is None else not leaf.result)
    leaves.append(leaf)
    return leaf.result


def evaluate_trigger_script(trigger_script: str, facts: dict) -> tuple[bool | None, list[Leaf]]:
    statements = parse_level(_strip_comments(trigger_script))
    leaves: list[Leaf] = []
    results = [evaluate_statement(key, value, facts, leaves) for key, kind, value in statements]
    return _ternary_and(results), leaves


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build_facts(
    location: str,
    templates: dict,
    ranks: dict,
    owners: dict,
    capitals: dict,
    religions: dict,
    continents: dict,
) -> dict:
    template = templates.get(location, {})
    owner_tag = owners.get(location)
    owner_capital = capitals.get(owner_tag) if owner_tag else None
    suitability = template.get("natural_harbor_suitability") or 0.0
    return {
        "location": location,
        "topography": template.get("topography"),
        "vegetation": template.get("vegetation"),
        "raw_material": template.get("raw_material"),
        "location_religion": template.get("religion"),
        "natural_harbor_suitability": suitability,
        "is_port": suitability > 0,
        "rank": ranks.get(location, DEFAULT_LOCATION_RANK),
        "owner_tag": owner_tag,
        "is_capital": bool(owner_tag) and capitals.get(owner_tag) == location,
        "owner_religion": religions.get(owner_tag) if owner_tag else None,
        "continent": continents.get(location),
        "owner_capital_continent": continents.get(owner_capital) if owner_capital else None,
    }


def audit() -> dict:
    templates = load_location_templates()
    ranks = load_location_ranks()
    owners, capitals = load_ownership_and_capitals()
    religions = load_country_religions()
    continents = load_continents()

    site_rules = load_yaml(WONDER_SITE_RULES_FILE)["site_rules"]
    unique_wonders = load_unique_wonders_source_data()["unique_wonders"]
    baseline = load_baseline()
    baseline_seen: set[str] = set()

    results = []
    drift: list[str] = []
    for wonder in sorted(unique_wonders, key=lambda w: w["id"]):
        location = wonder["location"]
        base_key = wonder["base_key"]
        rule = site_rules.get(base_key)
        if rule is None:
            results.append(
                {
                    "id": wonder["id"],
                    "key": wonder["key"],
                    "base_key": base_key,
                    "location": location,
                    "status": "ERROR",
                    "reasons": [f"base_key '{base_key}' not found in {WONDER_SITE_RULES_FILE}"],
                }
            )
            continue
        if location not in templates:
            results.append(
                {
                    "id": wonder["id"],
                    "key": wonder["key"],
                    "base_key": base_key,
                    "location": location,
                    "status": "ERROR",
                    "reasons": [f"location '{location}' not found in {LOCATION_TEMPLATES_FILE}"],
                }
            )
            continue

        facts = build_facts(location, templates, ranks, owners, capitals, religions, continents)
        result, leaves = evaluate_trigger_script(rule["trigger_script"], facts)

        if result is False:
            status = "FAIL"
            reasons = [leaf.detail for leaf in leaves if leaf.effective_result is False]
        elif result is None:
            status = "UNKNOWN"
            reasons = [leaf.detail for leaf in leaves if leaf.effective_result is None]
        else:
            status = "PASS"
            reasons = []

        rationale = None
        baseline_entry = baseline.get(wonder["key"])
        if baseline_entry is not None:
            baseline_seen.add(wonder["key"])
            if baseline_entry["status"] == status and status in ("FAIL", "UNKNOWN"):
                rationale = baseline_entry["rationale"]
                status = "INTENDED"
            elif status != "PASS":
                drift.append(
                    f"{wonder['key']}: baseline expects {baseline_entry['status']} but current "
                    f"result is {status} - baseline entry is stale, review data/wonder_site_requirement_baseline.yaml"
                )
            else:
                drift.append(
                    f"{wonder['key']}: baseline expects {baseline_entry['status']} but the wonder now "
                    f"PASSes - remove the stale entry from data/wonder_site_requirement_baseline.yaml"
                )

        row = {
            "id": wonder["id"],
            "key": wonder["key"],
            "base_key": base_key,
            "location": location,
            "owner": facts["owner_tag"],
            "status": status,
            "reasons": reasons,
        }
        if rationale is not None:
            row["rationale"] = rationale
        results.append(row)

    for key in baseline:
        if key not in baseline_seen:
            drift.append(f"{key}: baseline entry does not match any unique wonder key")

    return {"results": results, "baseline_drift": drift}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--fail-on-fail",
        action="store_true",
        help="Exit non-zero when any wonder is a confirmed FAIL (does not trigger on UNKNOWN).",
    )
    args = parser.parse_args()

    summary = audit()
    results = summary["results"]
    drift = summary["baseline_drift"]
    counts = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0, "ERROR": 0, "INTENDED": 0}
    for row in results:
        counts[row["status"]] += 1

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("# Unique Wonder Site-Requirement Audit")
        print(f"Total unique wonders: {len(results)}")
        print(
            f"PASS: {counts['PASS']}  FAIL: {counts['FAIL']}  UNKNOWN: {counts['UNKNOWN']}  "
            f"INTENDED: {counts['INTENDED']}  ERROR: {counts['ERROR']}"
        )
        print("")

        for status in ("ERROR", "FAIL", "UNKNOWN", "INTENDED"):
            rows = [row for row in results if row["status"] == status]
            if not rows:
                continue
            print(f"## {status} ({len(rows)})")
            for row in rows:
                owner = row.get("owner")
                owner_part = f" owner={owner}" if owner else ""
                print(f"- [{row['id']}] {row['key']} (base_key={row['base_key']}, location={row['location']}{owner_part})")
                for reason in row["reasons"]:
                    print(f"    - {reason}")
                if row.get("rationale"):
                    print(f"    rationale: {row['rationale']}")
            print("")

        if drift:
            print(f"## BASELINE DRIFT ({len(drift)})")
            for message in drift:
                print(f"- {message}")
            print("")

    if args.fail_on_fail and counts["FAIL"] > 0:
        sys.exit(1)
    if drift:
        sys.exit(1)


if __name__ == "__main__":
    main()
