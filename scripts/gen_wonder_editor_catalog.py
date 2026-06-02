import re
import sys
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import STYLE_3_REWARD_EFFECTS

OUT_FILE = REPO_ROOT / "data" / "wonder_editor_catalog.yaml"
MODIFIER_TYPE_DEFINITION_DIR = (
    REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "common" / "modifier_type_definitions"
)
STATIC_MODIFIER_DIR = REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "common" / "static_modifiers"
EVENT_DIR = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "events"
MODIFIER_DECL_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{")
MODIFIER_CATEGORY_RE = re.compile(r"\bcategory\s*=\s*([A-Za-z0-9_]+)\b")
EFFECT_ASSIGN_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=")
DIRECT_ASSIGN_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=")
STATIC_MODIFIER_REFERENCE_RE = re.compile(r"\bmodifier\s*=\s*(?:static_modifier:)?([A-Za-z0-9_]+)(?!:)\b")


def strip_comment(line: str) -> str:
    return line.split("#", 1)[0]


def uncommented_text(path: Path) -> str:
    return "\n".join(
        strip_comment(line)
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    )


def jomini_blocks_for_key(text: str, key: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(key)}\s*=\s*\{{")
    blocks: list[str] = []
    cursor = 0
    while True:
        match = pattern.search(text, cursor)
        if match is None:
            return blocks
        start = match.start()
        brace_start = text.find("{", match.start())
        if brace_start < 0:
            cursor = match.end()
            continue
        depth = 0
        for index in range(brace_start, len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start : index + 1])
                    cursor = index + 1
                    break
        else:
            return blocks


def scan_modifier_type_categories() -> dict[str, str]:
    categories: dict[str, str] = {}
    if not MODIFIER_TYPE_DEFINITION_DIR.exists():
        raise FileNotFoundError(f"Missing vanilla modifier type directory: {MODIFIER_TYPE_DEFINITION_DIR}")

    for path in sorted(MODIFIER_TYPE_DEFINITION_DIR.glob("*.txt")):
        current_name: str | None = None
        current_category: str | None = None
        depth = 0

        for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            line = strip_comment(raw_line)
            if current_name is None:
                match = MODIFIER_DECL_RE.match(line)
                if not match:
                    continue
                current_name = match.group(1)
                current_category = None
                depth = 0

            category_match = MODIFIER_CATEGORY_RE.search(line)
            if category_match:
                current_category = category_match.group(1)

            depth += line.count("{") - line.count("}")
            if depth <= 0 and current_name is not None:
                if current_category:
                    categories[current_name] = current_category
                current_name = None
                current_category = None
                depth = 0

    return categories


def scan_event_static_modifier_names() -> dict[str, set[str]]:
    modifier_names: dict[str, set[str]] = {"country": set(), "local": set()}
    if not EVENT_DIR.exists():
        raise FileNotFoundError(f"Missing vanilla event directory: {EVENT_DIR}")

    for path in sorted(EVENT_DIR.rglob("*.txt")):
        text = uncommented_text(path)
        for block in jomini_blocks_for_key(text, "add_country_modifier"):
            modifier_names["country"].update(STATIC_MODIFIER_REFERENCE_RE.findall(block))
        for block in jomini_blocks_for_key(text, "add_location_modifier"):
            modifier_names["local"].update(STATIC_MODIFIER_REFERENCE_RE.findall(block))

    return modifier_names


def scan_event_static_modifier_effects(
    event_static_modifier_names: dict[str, set[str]],
    modifier_type_categories: dict[str, str],
) -> dict[str, list[str]]:
    modifiers: dict[str, set[str]] = {"country": set(), "local": set()}
    wanted_static_names = event_static_modifier_names["country"] | event_static_modifier_names["local"]
    if not STATIC_MODIFIER_DIR.exists():
        raise FileNotFoundError(f"Missing vanilla static modifier directory: {STATIC_MODIFIER_DIR}")

    for path in sorted(STATIC_MODIFIER_DIR.glob("*.txt")):
        current_name: str | None = None
        current_effect_keys: set[str] = set()
        depth = 0

        for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            line = strip_comment(raw_line)
            if current_name is None:
                match = MODIFIER_DECL_RE.match(line)
                if not match:
                    continue
                current_name = match.group(1)
                current_effect_keys = set()
                depth = 0

            if current_name in wanted_static_names and depth == 1:
                assign_match = DIRECT_ASSIGN_RE.match(line)
                if assign_match:
                    effect_key = assign_match.group(1)
                    if effect_key in modifier_type_categories:
                        current_effect_keys.add(effect_key)

            depth += line.count("{") - line.count("}")
            if depth <= 0 and current_name is not None:
                if current_name in event_static_modifier_names["country"]:
                    modifiers["country"].update(
                        key for key in current_effect_keys if modifier_type_categories.get(key) == "country"
                    )
                if current_name in event_static_modifier_names["local"]:
                    modifiers["local"].update(
                        key for key in current_effect_keys if modifier_type_categories.get(key) == "location"
                    )
                current_name = None
                current_effect_keys = set()
                depth = 0

    return {key: sorted(values) for key, values in modifiers.items()}


def scan_event_effects() -> set[str]:
    if not EVENT_DIR.exists():
        raise FileNotFoundError(f"Missing vanilla event directory: {EVENT_DIR}")

    effects: set[str] = set()
    for path in sorted(EVENT_DIR.rglob("*.txt")):
        for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = EFFECT_ASSIGN_RE.match(strip_comment(raw_line))
            if match:
                effects.add(match.group(1))
    return effects


def scan_style_3_reward_types(event_effects: set[str]) -> tuple[list[str], dict[str, str]]:
    reward_sources = {
        reward_type: str(spec["effect"])
        for reward_type, spec in sorted(STYLE_3_REWARD_EFFECTS.items())
        if str(spec["effect"]) in event_effects
    }
    return sorted(reward_sources), reward_sources


def build_catalog() -> dict[str, object]:
    modifier_type_categories = scan_modifier_type_categories()
    event_static_modifier_names = scan_event_static_modifier_names()
    modifier_types = scan_event_static_modifier_effects(event_static_modifier_names, modifier_type_categories)
    event_effects = scan_event_effects()
    reward_types, reward_sources = scan_style_3_reward_types(event_effects)
    return {
        "modifier_types": modifier_types,
        "style_3_reward_types": reward_types,
        "style_3_reward_sources": reward_sources,
        "scan_summary": {
            "event_country_static_modifier_count": len(event_static_modifier_names["country"]),
            "event_local_static_modifier_count": len(event_static_modifier_names["local"]),
            "country_modifier_count": len(modifier_types["country"]),
            "local_modifier_count": len(modifier_types["local"]),
            "style_3_reward_type_count": len(reward_types),
        },
    }


def main() -> None:
    payload = build_catalog()
    header = (
        "# @Generated by scripts/gen_wonder_editor_catalog.py\n"
        "#   Data:    reference_game_files/game/in_game/events + reference_game_files/game/main_menu/common/static_modifiers + reference_game_files/game/main_menu/common/modifier_type_definitions\n"
        "#   Regen:   conda run --no-capture-output -n eu5 python scripts/gen_wonder_editor_catalog.py\n"
        "# Do not edit directly - update the reference files and re-run the generator.\n\n"
    )
    OUT_FILE.write_text(
        header
        + yaml.safe_dump(
            payload,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=120,
        ),
        encoding="utf-8",
    )
    summary = payload["scan_summary"]
    print(
        "Generated data/wonder_editor_catalog.yaml "
        f"({summary['country_modifier_count']} country modifiers, "
        f"{summary['local_modifier_count']} local modifiers, "
        f"{summary['style_3_reward_type_count']} style 3 reward types)"
    )


if __name__ == "__main__":
    main()
