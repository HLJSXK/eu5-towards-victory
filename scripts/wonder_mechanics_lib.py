import sys
from copy import deepcopy
from pathlib import Path
import re

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
WONDERS_FILE = REPO_ROOT / "data" / "wonders.yaml"
MECHANICS_FILE = REPO_ROOT / "data" / "wonder_mechanics.yaml"
UNIQUE_WONDERS_FILE = REPO_ROOT / "data" / "unique_wonders.yaml"
GENERIC_WONDER_IMAGE_PROMPTS_FILE = REPO_ROOT / "data" / "wonder_image_prompts.yaml"
MANUAL_TV_GAME_CONCEPTS_FILE = REPO_ROOT / "src" / "main_menu" / "common" / "game_concepts" / "tv_game_concepts.txt"
ALL_WONDER_MIN_ID = 1
ALL_WONDER_MAX_ID = 40
UNIQUE_WONDER_MIN_ID = 101
UNIQUE_WONDER_MAX_ID = 140
WONDER_MECHANICS_MIN_ID = ALL_WONDER_MIN_ID
WONDER_MECHANICS_MAX_ID = UNIQUE_WONDER_MAX_ID
PARTS = ["foundation", "body", "function", "decoration"]
GAME_CONCEPT_DECL_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*\{$")
ROMAN_NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
}
SUPPORTED_RITUAL_COST_TYPES = {None, "artwork", "scaled_gold", "prestige"}
SUPPORTED_UNIQUE_RITUAL_MODES = {"immediate", "timed", "auxiliary_building"}
SUPPORTED_RITUAL_LISTENERS = {"monthly", "ruler_death", "pre_winning_war", "ending_war"}
SITE_RULES_SECTION = "site_rules"
RITUAL_AUXILIARY_ESTATE_POWER_BY_POP_TYPE = {
    "clergy": "local_clergy_estate_power",
    "nobles": "local_nobles_estate_power",
    "burghers": "local_burghers_estate_power",
    "laborers": "local_peasants_estate_power",
    "soldiers": "local_crown_estate_power",
}


class WonderYamlDumper(yaml.SafeDumper):
    pass


class StrictWonderYamlLoader(yaml.SafeLoader):
    pass


def _represent_yaml_string(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


WonderYamlDumper.add_representer(str, _represent_yaml_string)


def _construct_yaml_mapping_no_duplicates(
    loader: StrictWonderYamlLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            source_name = getattr(loader, "source_name", "<yaml>")
            raise ValueError(f"Duplicate key {key!r} in {source_name}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictWonderYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_yaml_mapping_no_duplicates,
)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing YAML source file: {path}")
    loader = StrictWonderYamlLoader(path.read_text(encoding="utf-8"))
    loader.source_name = str(path)
    try:
        data = loader.get_single_data()
    finally:
        loader.dispose()
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a top-level mapping")
    return data


def dump_yaml_document(payload: object) -> str:
    return yaml.dump(
        payload,
        Dumper=WonderYamlDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )


def _expect_keys(mapping: dict, *, required: set[str], optional: set[str], context: str) -> None:
    missing = sorted(required - set(mapping))
    if missing:
        raise ValueError(f"Missing keys in {context}: {', '.join(missing)}")
    unexpected = sorted(set(mapping) - required - optional)
    if unexpected:
        raise ValueError(f"Unexpected keys in {context}: {', '.join(unexpected)}")


def _require_mapping(value: object, context: str) -> dict:
    if not isinstance(value, dict):
        raise TypeError(f"{context} must be a mapping, got {type(value).__name__}")
    return value


def _require_list(value: object, context: str) -> list:
    if not isinstance(value, list):
        raise TypeError(f"{context} must be a list, got {type(value).__name__}")
    return value


def _require_string(value: object, context: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{context} must be a string, got {type(value).__name__}")
    if not allow_empty and not value.strip():
        raise ValueError(f"{context} cannot be empty")
    return value


def _require_optional_string(value: object, context: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, context, allow_empty=True)


def _require_int(value: object, context: str, *, minimum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{context} must be an int, got {type(value).__name__}")
    if minimum is not None and value < minimum:
        raise ValueError(f"{context} must be >= {minimum}, got {value}")
    return value


def _require_bool(value: object, context: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{context} must be a bool, got {type(value).__name__}")
    return value


def _validate_localized_text_map(value: object, context: str) -> dict[str, str]:
    mapping = _require_mapping(value, context)
    _expect_keys(mapping, required={"en", "zh"}, optional=set(), context=context)
    return {
        "en": _require_string(mapping["en"], f"{context}.en", allow_empty=True),
        "zh": _require_string(mapping["zh"], f"{context}.zh", allow_empty=True),
    }


def _validate_script_text(value: object, context: str, *, allow_empty: bool = True) -> str:
    text = _require_string(value, context, allow_empty=allow_empty)
    return text.strip("\n")


def _validate_string_list(value: object, context: str) -> list[str]:
    items = _require_list(value, context)
    normalized: list[str] = []
    for index, item in enumerate(items, start=1):
        normalized_item = _require_string(item, f"{context}[{index}]")
        if normalized_item in normalized:
            raise ValueError(f"Duplicate value {normalized_item!r} in {context}")
        normalized.append(normalized_item)
    return normalized


def _validate_final_buildings(value: object, context: str) -> dict[int, str]:
    mapping = _require_mapping(value, context)
    if not mapping:
        raise ValueError(f"{context} cannot be empty")
    normalized: dict[int, str] = {}
    for style, building in mapping.items():
        if not isinstance(style, int) or isinstance(style, bool):
            raise TypeError(f"{context} keys must be ints, got {type(style).__name__}")
        if style in normalized:
            raise ValueError(f"Duplicate style {style} in {context}")
        normalized[style] = _require_string(building, f"{context}[{style}]")
    if len(set(normalized.values())) != len(normalized):
        raise ValueError(f"{context} cannot map multiple styles to the same final building")
    return normalized


def _validate_parts_section(value: object, context: str) -> list[dict[str, str]]:
    parts = _require_list(value, context)
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(parts, start=1):
        entry_context = f"{context}[{index}]"
        part = _require_mapping(item, entry_context)
        _expect_keys(part, required={"key"}, optional=set(), context=entry_context)
        key = _require_string(part["key"], f"{entry_context}.key")
        if key not in PARTS:
            raise ValueError(f"Unknown part key in {entry_context}: {key}")
        if key in seen:
            raise ValueError(f"Duplicate part key in {context}: {key}")
        seen.add(key)
        normalized.append({"key": key})
    missing = [key for key in PARTS if key not in seen]
    if missing:
        raise ValueError(f"Missing part entries in {context}: {', '.join(missing)}")
    return normalized


def _validate_sizes_section(value: object, context: str) -> dict[str, dict[str, int]]:
    sizes = _require_mapping(value, context)
    _expect_keys(sizes, required={"small", "medium", "large"}, optional=set(), context=context)
    normalized: dict[str, dict[str, int]] = {}
    for size_key in ("small", "medium", "large"):
        entry_context = f"{context}.{size_key}"
        entry = _require_mapping(sizes[size_key], entry_context)
        _expect_keys(entry, required={"progress"}, optional=set(), context=entry_context)
        normalized[size_key] = {
            "progress": _require_int(entry["progress"], f"{entry_context}.progress", minimum=1),
        }
    return normalized


def _validate_generic_wonder_record(raw: object) -> dict:
    context = "data/wonders.yaml wonder entry"
    wonder = _require_mapping(raw, context)
    _expect_keys(
        wonder,
        required={
            "id",
            "key",
            "concept",
            "size",
            "category",
            "pop_type",
            "maintenance",
            "final_buildings",
            "is_unique",
            "base_key",
            "mechanic_key",
            "base_effect_multiplier",
        },
        optional=set(),
        context=context,
    )

    key = _require_string(wonder["key"], f"{context}.key")
    if _require_bool(wonder["is_unique"], f"{context}.is_unique"):
        raise ValueError(f"{context}.is_unique must be false for generic wonders")
    if _require_string(wonder["base_key"], f"{context}.base_key") != key:
        raise ValueError(f"{context}.base_key must equal {key}")
    if _require_string(wonder["mechanic_key"], f"{context}.mechanic_key") != key:
        raise ValueError(f"{context}.mechanic_key must equal {key}")
    if _require_int(wonder["base_effect_multiplier"], f"{context}.base_effect_multiplier", minimum=1) != 1:
        raise ValueError(f"{context}.base_effect_multiplier must be 1 for generic wonders")

    return {
        **wonder,
        "id": _require_int(wonder["id"], f"{context}.id", minimum=1),
        "key": key,
        "concept": _require_string(wonder["concept"], f"{context}.concept"),
        "size": _require_string(wonder["size"], f"{context}.size"),
        "category": _require_string(wonder["category"], f"{context}.category"),
        "pop_type": _require_string(wonder["pop_type"], f"{context}.pop_type"),
        "maintenance": _require_string(wonder["maintenance"], f"{context}.maintenance"),
        "final_buildings": _validate_final_buildings(wonder["final_buildings"], f"{context}.final_buildings"),
        "is_unique": False,
        "base_key": key,
        "mechanic_key": key,
        "base_effect_multiplier": 1,
    }


def _validate_site_rules(raw: object, *, design_keys: set[str]) -> dict[str, dict[str, str]]:
    context = f"{MECHANICS_FILE}.site_rules"
    site_rules = _require_mapping(raw, context)
    missing = sorted(design_keys - set(site_rules))
    if missing:
        raise ValueError(f"Missing site_rules entries for: {', '.join(missing)}")
    extra = sorted(set(site_rules) - design_keys)
    if extra:
        raise ValueError(f"Unknown site_rules entries for: {', '.join(extra)}")

    normalized: dict[str, dict[str, str]] = {}
    for key in sorted(design_keys):
        entry_context = f"{context}.{key}"
        entry = _require_mapping(site_rules[key], entry_context)
        _expect_keys(
            entry,
            required={"trigger_script", "preference_script"},
            optional=set(),
            context=entry_context,
        )
        normalized[key] = {
            "trigger_script": _validate_script_text(entry["trigger_script"], f"{entry_context}.trigger_script", allow_empty=False),
            "preference_script": _validate_script_text(
                entry["preference_script"],
                f"{entry_context}.preference_script",
                allow_empty=False,
            ),
        }
    return normalized


def load_wonders_source_data(path: Path = WONDERS_FILE) -> dict:
    raw = load_yaml(path)
    _expect_keys(raw, required={"wonders"}, optional={"parts", "sizes"}, context=str(path))
    wonders_raw = _require_list(raw["wonders"], f"{path}.wonders")
    wonders: list[dict] = []
    wonder_ids: set[int] = set()
    wonder_keys: set[str] = set()
    for index, item in enumerate(wonders_raw, start=1):
        wonder = _validate_generic_wonder_record(item)
        if wonder["id"] in wonder_ids:
            raise ValueError(f"Duplicate wonder id in {path}: {wonder['id']}")
        if wonder["key"] in wonder_keys:
            raise ValueError(f"Duplicate wonder key in {path}: {wonder['key']}")
        wonder_ids.add(wonder["id"])
        wonder_keys.add(wonder["key"])
        wonders.append(wonder)
    normalized = {
        **raw,
        "wonders": wonders,
    }
    if "parts" in raw:
        normalized["parts"] = _validate_parts_section(raw["parts"], f"{path}.parts")
    if "sizes" in raw:
        normalized["sizes"] = _validate_sizes_section(raw["sizes"], f"{path}.sizes")
    return normalized


def load_mechanics_source_data(path: Path = MECHANICS_FILE) -> dict:
    raw = load_yaml(path)
    designs = _require_mapping(raw.get("designs"), f"{path}.designs")
    site_rules = _validate_site_rules(raw.get("site_rules"), design_keys=set(designs))
    return {
        **raw,
        "site_rules": site_rules,
    }


def load_unique_wonders_source_data(path: Path = UNIQUE_WONDERS_FILE) -> dict:
    raw = load_yaml(path)
    _expect_keys(raw, required={"unique_wonders"}, optional=set(), context=str(path))
    wonders_raw = _require_list(raw["unique_wonders"], f"{path}.unique_wonders")
    wonder_ids: set[int] = set()
    wonder_keys: set[str] = set()
    wonders: list[dict] = []
    for index, item in enumerate(wonders_raw, start=1):
        context = f"{path}.unique_wonders[{index}]"
        wonder = _require_mapping(item, context)
        _expect_keys(
            wonder,
            required={
                "id",
                "key",
                "base_key",
                "concept",
                "location",
                "image",
                "prompt",
                "is_unique",
                "mechanic_key",
                "base_effect_multiplier",
                "final_buildings",
                "ritual",
            },
            optional=set(),
            context=context,
        )

        wonder_id = _require_int(wonder["id"], f"{context}.id", minimum=1)
        if wonder_id in wonder_ids:
            raise ValueError(f"Duplicate unique wonder id in {path}: {wonder_id}")
        wonder_ids.add(wonder_id)

        key = _require_string(wonder["key"], f"{context}.key")
        if key in wonder_keys:
            raise ValueError(f"Duplicate unique wonder key in {path}: {key}")
        wonder_keys.add(key)

        if not _require_bool(wonder["is_unique"], f"{context}.is_unique"):
            raise ValueError(f"{context}.is_unique must be true for unique wonders")

        wonders.append(
            {
                **wonder,
                "id": wonder_id,
                "key": key,
                "base_key": _require_string(wonder["base_key"], f"{context}.base_key"),
                "concept": _require_string(wonder["concept"], f"{context}.concept"),
                "location": _require_string(wonder["location"], f"{context}.location"),
                "image": _require_string(wonder["image"], f"{context}.image"),
                "prompt": _require_string(wonder["prompt"], f"{context}.prompt"),
                "is_unique": True,
                "mechanic_key": _require_string(wonder["mechanic_key"], f"{context}.mechanic_key"),
                "base_effect_multiplier": _require_int(
                    wonder["base_effect_multiplier"],
                    f"{context}.base_effect_multiplier",
                    minimum=1,
                ),
                "final_buildings": _validate_final_buildings(wonder["final_buildings"], f"{context}.final_buildings"),
                "ritual": _require_mapping(wonder["ritual"], f"{context}.ritual"),
            }
        )
    return {
        "unique_wonders": wonders,
    }


def leading_comment_block(text: str) -> str:
    lines = text.splitlines()
    captured: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            captured.append(line.rstrip())
            continue
        break
    return "\n".join(captured).rstrip()


def save_yaml_document(path: Path, payload: object, *, preserve_leading_comments: bool = False) -> None:
    header = ""
    if preserve_leading_comments and path.exists():
        header = leading_comment_block(path.read_text(encoding="utf-8"))

    body = dump_yaml_document(payload).rstrip() + "\n"
    if header:
        path.write_text(f"{header}\n{body}", encoding="utf-8")
    else:
        path.write_text(body, encoding="utf-8")


def load_generic_wonder_image_prompts(path: Path = GENERIC_WONDER_IMAGE_PROMPTS_FILE) -> dict[str, str]:
    if not path.exists():
        return {}

    raw = load_yaml(path) or {}
    prompts = raw.get("generic_wonder_image_prompts", {})
    if not isinstance(prompts, dict):
        raise ValueError("generic_wonder_image_prompts must be a mapping")

    normalized: dict[str, str] = {}
    for key, prompt in prompts.items():
        normalized_key = str(key).strip()
        normalized_prompt = str(prompt).strip()
        if not normalized_key:
            raise ValueError("Wonder image prompt keys cannot be empty")
        if not normalized_prompt:
            raise ValueError(f"Wonder image prompt for {normalized_key} cannot be empty")
        normalized[normalized_key] = normalized_prompt
    return normalized


def load_manual_game_concept_ids(path: Path = MANUAL_TV_GAME_CONCEPTS_FILE) -> set[str]:
    if not path.exists():
        return set()

    concept_ids: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        match = GAME_CONCEPT_DECL_RE.match(raw_line.strip())
        if match:
            concept_ids.add(match.group(1))
    return concept_ids


def mechanic_key(wonder: dict) -> str:
    return _require_string(wonder["mechanic_key"], f"{wonder['key']}.mechanic_key")


def ceremony_styles(wonder: dict) -> list[int]:
    return sorted(int(style) for style in wonder["final_buildings"])


def normalize_loc_map(value: object) -> dict[str, str]:
    return _validate_localized_text_map(value, "localized text")


def normalize_script_text(value: object) -> str:
    return _validate_script_text(value, "script text")


def normalize_string_list(value: object) -> list[str]:
    return _validate_string_list(value, "string list")


def indent_script_block(script: str | None, indent: int) -> list[str]:
    if not script:
        return []
    prefix = "\t" * indent
    lines: list[str] = []
    for raw_line in script.splitlines():
        if raw_line.strip():
            lines.append(f"{prefix}{raw_line.rstrip()}")
        else:
            lines.append("")
    return lines


def ritual_has_custom_completion_trigger(ritual: dict) -> bool:
    return bool(ritual.get("completion_trigger_script", ""))


def ritual_listens_to(ritual: dict, listener: str) -> bool:
    return listener in ritual.get("listeners", [])


def ritual_uses_deferred_completion(ritual: dict) -> bool:
    return ritual.get("mode") != "immediate" or ritual_has_custom_completion_trigger(ritual) or bool(ritual.get("listeners", []))


def normalize_unique_ritual(wonder: dict) -> dict:
    raw = wonder.get("ritual")
    if not isinstance(raw, dict):
        raise TypeError(f"Unique wonder {wonder['key']} must define ritual as a mapping")
    _expect_keys(
        raw,
        required={
            "key",
            "mode",
            "cost_type",
            "listeners",
            "runtime_variables",
            "country_modifier",
            "reward",
            "confirmation_trigger_script",
            "start_effect_script",
            "snapshot_effect_script",
            "progress_effect_script",
            "completion_trigger_script",
            "completion_effect_script",
            "timed",
            "auxiliary_building",
        },
        optional=set(),
        context=f"unique wonder {wonder['key']}.ritual",
    )

    key = _require_string(raw["key"], f"unique wonder {wonder['key']}.ritual.key")
    mode = _require_string(raw["mode"], f"unique wonder {wonder['key']}.ritual.mode")
    if mode not in SUPPORTED_UNIQUE_RITUAL_MODES:
        raise ValueError(f"Unsupported unique ritual mode for {wonder['key']}: {mode}")

    cost_type = raw["cost_type"]
    if cost_type not in SUPPORTED_RITUAL_COST_TYPES:
        raise ValueError(f"Unsupported unique ritual cost_type for {wonder['key']}: {cost_type}")

    listeners = _validate_string_list(raw["listeners"], f"unique wonder {wonder['key']}.ritual.listeners")
    for listener in listeners:
        if listener not in SUPPORTED_RITUAL_LISTENERS:
            raise ValueError(f"Unsupported unique ritual listener for {wonder['key']}: {listener}")

    runtime_variables = _validate_string_list(
        raw["runtime_variables"], f"unique wonder {wonder['key']}.ritual.runtime_variables"
    )
    country_modifier = _require_mapping(raw["country_modifier"], f"unique wonder {wonder['key']}.ritual.country_modifier")
    reward = _require_list(raw["reward"], f"unique wonder {wonder['key']}.ritual.reward")
    confirmation_trigger_script = _validate_script_text(
        raw["confirmation_trigger_script"],
        f"unique wonder {wonder['key']}.ritual.confirmation_trigger_script",
    )
    start_effect_script = _validate_script_text(
        raw["start_effect_script"],
        f"unique wonder {wonder['key']}.ritual.start_effect_script",
    )
    snapshot_effect_script = _validate_script_text(
        raw["snapshot_effect_script"],
        f"unique wonder {wonder['key']}.ritual.snapshot_effect_script",
    )
    progress_effect_script = _validate_script_text(
        raw["progress_effect_script"],
        f"unique wonder {wonder['key']}.ritual.progress_effect_script",
    )
    completion_trigger_script = _validate_script_text(
        raw["completion_trigger_script"],
        f"unique wonder {wonder['key']}.ritual.completion_trigger_script",
    )
    completion_effect_script = _validate_script_text(
        raw["completion_effect_script"],
        f"unique wonder {wonder['key']}.ritual.completion_effect_script",
    )
    timed = _require_mapping(raw["timed"], f"unique wonder {wonder['key']}.ritual.timed")
    _expect_keys(
        timed,
        required={"years", "burden_modifier", "blessing_modifier"},
        optional=set(),
        context=f"unique wonder {wonder['key']}.ritual.timed",
    )
    auxiliary_building = _require_mapping(raw["auxiliary_building"], f"unique wonder {wonder['key']}.ritual.auxiliary_building")
    _expect_keys(
        auxiliary_building,
        required={
            "local_modifier",
            "maintenance",
            "build_time",
            "construction_demand",
            "price",
            "attributes",
            "max_levels",
        },
        optional=set(),
        context=f"unique wonder {wonder['key']}.ritual.auxiliary_building",
    )

    timed_normalized = {
        "years": _require_int(timed["years"], f"unique wonder {wonder['key']}.ritual.timed.years", minimum=1),
        "burden_modifier": _require_mapping(timed["burden_modifier"], f"unique wonder {wonder['key']}.ritual.timed.burden_modifier"),
        "blessing_modifier": _require_mapping(timed["blessing_modifier"], f"unique wonder {wonder['key']}.ritual.timed.blessing_modifier"),
    }
    auxiliary_normalized = {
        "local_modifier": _require_mapping(
            auxiliary_building["local_modifier"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.local_modifier",
        ),
        "maintenance": _require_optional_string(
            auxiliary_building["maintenance"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.maintenance",
        ),
        "build_time": _require_optional_string(
            auxiliary_building["build_time"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.build_time",
        ),
        "construction_demand": _require_optional_string(
            auxiliary_building["construction_demand"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.construction_demand",
        ),
        "price": _require_optional_string(
            auxiliary_building["price"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.price",
        ),
        "attributes": _require_mapping(
            auxiliary_building["attributes"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.attributes",
        ),
        "max_levels": _require_int(
            auxiliary_building["max_levels"],
            f"unique wonder {wonder['key']}.ritual.auxiliary_building.max_levels",
            minimum=1,
        ),
    }

    if mode == "immediate" and (listeners or snapshot_effect_script or progress_effect_script) and not completion_trigger_script:
        raise ValueError(
            f"Immediate unique ritual {wonder['key']} needs completion_trigger_script when it uses listeners or runtime progress hooks"
        )

    if mode == "auxiliary_building" and auxiliary_normalized["local_modifier"] == {}:
        raise ValueError(f"Auxiliary unique ritual {wonder['key']} needs a local_modifier")

    return {
        "key": key,
        "mode": mode,
        "cost_type": cost_type,
        "listeners": listeners,
        "runtime_variables": runtime_variables,
        "country_modifier": country_modifier,
        "reward": reward,
        "confirmation_trigger_script": confirmation_trigger_script,
        "start_effect_script": start_effect_script,
        "snapshot_effect_script": snapshot_effect_script,
        "progress_effect_script": progress_effect_script,
        "completion_trigger_script": completion_trigger_script,
        "completion_effect_script": completion_effect_script,
        "timed": timed_normalized,
        "auxiliary_building": auxiliary_normalized,
    }


def unique_ritual(wonder: dict) -> dict:
    if not wonder.get("is_unique"):
        raise ValueError(f"{wonder['key']} is not a unique wonder")
    return wonder["ritual"]


def ritual_plan_for_style(wonder: dict, mechanics: dict, style: int) -> dict:
    if wonder.get("is_unique"):
        if style != 1:
            raise ValueError(f"Unique wonder {wonder['key']} only supports style 1 ritual plans")
        return unique_ritual(wonder)

    ritual = generic_ritual_for_wonder(mechanics, wonder)
    if style == 1:
        return {
            "mode": "timed",
            "cost_type": None,
            "listeners": ["monthly"],
            "runtime_variables": [],
            "country_modifier": {},
            "reward": [],
            "confirmation_trigger_script": "",
            "start_effect_script": "",
            "snapshot_effect_script": "",
            "progress_effect_script": "",
            "completion_trigger_script": "",
            "completion_effect_script": "",
            "timed": {
                "years": 1,
                "burden_modifier": {},
                "blessing_modifier": deepcopy(ritual["style_1"]["country_modifier"]),
            },
            "auxiliary_building": {
                "local_modifier": {},
                "maintenance": None,
                "build_time": None,
                "construction_demand": None,
                "price": None,
                "attributes": {},
                "max_levels": 1,
            },
        }
    if style == 2:
        return {
            "mode": "auxiliary_building",
            "cost_type": None,
            "listeners": [],
            "runtime_variables": [],
            "country_modifier": {},
            "reward": [],
            "confirmation_trigger_script": "",
            "start_effect_script": "",
            "snapshot_effect_script": "",
            "progress_effect_script": "",
            "completion_trigger_script": "",
            "completion_effect_script": "",
            "timed": {
                "years": 1,
                "burden_modifier": {},
                "blessing_modifier": {},
            },
            "auxiliary_building": {
                "local_modifier": deepcopy(ritual["style_2"]["local_modifier"]),
                "maintenance": None,
                "build_time": None,
                "construction_demand": None,
                "price": None,
                "attributes": {},
                "max_levels": 1,
            },
        }
    if style == 3:
        return {
            "mode": "immediate",
            "cost_type": ritual["style_3"]["cost_type"],
            "listeners": [],
            "runtime_variables": [],
            "country_modifier": {},
            "reward": deepcopy(ritual["style_3"]["reward"]),
            "confirmation_trigger_script": "",
            "start_effect_script": "",
            "snapshot_effect_script": "",
            "progress_effect_script": "",
            "completion_trigger_script": "",
            "completion_effect_script": "",
            "timed": {
                "years": 1,
                "burden_modifier": {},
                "blessing_modifier": {},
            },
            "auxiliary_building": {
                "local_modifier": {},
                "maintenance": None,
                "build_time": None,
                "construction_demand": None,
                "price": None,
                "attributes": {},
                "max_levels": 1,
            },
        }
    raise ValueError(f"Unsupported ritual style for {wonder['key']}: {style}")


def load_wonder_data(
    min_id: int = ALL_WONDER_MIN_ID,
    max_id: int = ALL_WONDER_MAX_ID,
    *,
    require_designs: bool = True,
    require_buildings: bool = True,
    require_base_modifiers: bool = True,
) -> tuple[list[dict], dict]:
    wonders_data = load_wonders_source_data()
    mechanics = load_mechanics_source_data()
    wonders = [
        deepcopy(wonder)
        for wonder in wonders_data["wonders"]
        if min_id <= int(wonder["id"]) <= max_id
    ]
    for wonder in wonders:
        key = wonder["key"]
        if require_designs and key not in mechanics["designs"]:
            raise ValueError(f"Missing design data for {key}")
        if require_buildings and key not in mechanics["buildings"]:
            raise ValueError(f"Missing building data for {key}")
        if require_base_modifiers and key not in mechanics["base_modifiers"]:
            raise ValueError(f"Missing base modifier data for {key}")
    return wonders, mechanics


def load_generic_wonder_mechanics_data() -> tuple[list[dict], dict]:
    wonders, mechanics = load_wonder_data(
        ALL_WONDER_MIN_ID,
        ALL_WONDER_MAX_ID,
        require_designs=False,
        require_buildings=True,
        require_base_modifiers=True,
    )
    generic_rituals = mechanics.get("generic_rituals", {})
    for wonder in wonders:
        if wonder["key"] not in generic_rituals:
            raise ValueError(f"Missing generic ritual data for {wonder['key']}")
    return wonders, mechanics


def load_unique_wonders() -> list[dict]:
    wonders_data = load_wonders_source_data()
    mechanics = load_mechanics_source_data()
    unique_data = load_unique_wonders_source_data()
    base_by_key = {
        wonder["key"]: deepcopy(wonder)
        for wonder in wonders_data["wonders"]
    }
    unique_wonders: list[dict] = []
    for raw in unique_data["unique_wonders"]:
        base_key = raw["base_key"]
        if base_key not in base_by_key:
            raise ValueError(f"Unknown base wonder for unique wonder {raw['key']}: {base_key}")
        if base_key not in mechanics["buildings"]:
            raise ValueError(f"Missing building data for base wonder {base_key}")
        if base_key not in mechanics["base_modifiers"]:
            raise ValueError(f"Missing base modifier data for base wonder {base_key}")
        base = deepcopy(base_by_key[base_key])
        key = raw["key"]
        merged = {
            **base,
            **raw,
        }
        if merged["base_key"] != base_key:
            raise ValueError(f"Unique wonder {key} must keep base_key = {base_key}")
        if merged["mechanic_key"] != base_key:
            raise ValueError(f"Unique wonder {key} must keep mechanic_key = {base_key}")
        normalized = deepcopy(merged)
        normalized["ritual"] = normalize_unique_ritual(normalized)
        if ceremony_styles(normalized) != [1]:
            raise ValueError(f"Unique wonder {key} must currently expose exactly one ceremony style")
        unique_wonders.append(normalized)
    return unique_wonders


def load_all_wonder_mechanics_data(*, include_unique: bool = True) -> tuple[list[dict], dict]:
    wonders, mechanics = load_generic_wonder_mechanics_data()
    if include_unique:
        wonders.extend(load_unique_wonders())
    return wonders, mechanics


def load_generic_wonder_mechanics() -> tuple[list[dict], dict]:
    return load_generic_wonder_mechanics_data()


def load_all_wonder_mechanics(*, include_unique: bool = True) -> tuple[list[dict], dict]:
    return load_all_wonder_mechanics_data(include_unique=include_unique)


def legacy_site_trigger_lines(key: str, indent: int = 1) -> list[str]:
    raise RuntimeError("Legacy site trigger fallback has been removed; use data/wonder_mechanics.yaml site_rules")


def legacy_site_preference_lines(key: str, indent: int = 2) -> list[str]:
    raise RuntimeError("Legacy site preference fallback has been removed; use data/wonder_mechanics.yaml site_rules")


def site_rule_config(mechanics: dict, key: str) -> dict:
    site_rules = _require_mapping(mechanics.get(SITE_RULES_SECTION), f"{MECHANICS_FILE}.site_rules")
    if key not in site_rules:
        raise KeyError(f"Missing site_rules entry for {key}")
    entry = _require_mapping(site_rules[key], f"{MECHANICS_FILE}.site_rules.{key}")
    _expect_keys(
        entry,
        required={"trigger_script", "preference_script"},
        optional=set(),
        context=f"{MECHANICS_FILE}.site_rules.{key}",
    )
    return entry


def site_trigger_script_for_key(mechanics: dict, key: str) -> str:
    return _validate_script_text(
        site_rule_config(mechanics, key)["trigger_script"],
        f"{MECHANICS_FILE}.site_rules.{key}.trigger_script",
        allow_empty=False,
    )


def site_preference_script_for_key(mechanics: dict, key: str) -> str:
    return _validate_script_text(
        site_rule_config(mechanics, key)["preference_script"],
        f"{MECHANICS_FILE}.site_rules.{key}.preference_script",
        allow_empty=False,
    )


def site_trigger_lines_for_wonder(mechanics: dict, wonder: dict, indent: int = 1) -> list[str]:
    return indent_script_block(site_trigger_script_for_key(mechanics, mechanic_key(wonder)), indent)


def site_preference_lines_for_wonder(mechanics: dict, wonder: dict, indent: int = 2) -> list[str]:
    return indent_script_block(site_preference_script_for_key(mechanics, mechanic_key(wonder)), indent)


def render_header(script_rel: str, data_rel: str = "data/wonders.yaml + data/wonder_mechanics.yaml + data/unique_wonders.yaml") -> list[str]:
    return [
        f"# @Generated by {script_rel}",
        f"#   Data:    {data_rel}",
        f"#   Regen:   conda run --no-capture-output -n eu5 python {script_rel}",
        "# Do not edit directly - modify the data file and re-run the generator.",
        "",
    ]


def upper_key(key: str) -> str:
    return key.upper()


def q(text: str) -> str:
    return text.replace('"', '\\"')


def all_final_buildings(wonders: list[dict]) -> list[str]:
    buildings: list[str] = []
    for wonder in wonders:
        for building in wonder["final_buildings"].values():
            if building not in buildings:
                buildings.append(building)
    return buildings


def loc_line(key: str, value: str) -> str:
    return f' {key}:0 "{q(value)}"'


def level_static_modifier_loc(concept: str, level: int) -> str:
    numeral = ROMAN_NUMERALS.get(level)
    if numeral is None:
        raise ValueError(f"Unsupported wonder level for localization: {level}")
    return f"[{concept}|E] {numeral}"


def final_building_for_style(wonder: dict, style: int) -> str:
    if style not in wonder["final_buildings"]:
        raise KeyError(f"{wonder['key']} has no final building for ceremony style {style}")
    return wonder["final_buildings"][style]


def wonder_image_name(wonder: dict) -> str:
    return str(wonder.get("image") or f"tv_wonder_{wonder['key']}")


def wonder_image_prompt(wonder: dict, generic_prompts: dict[str, str] | None = None) -> str:
    prompt = str(wonder.get("prompt") or "").strip()
    if prompt:
        return prompt

    prompts = generic_prompts or {}
    if wonder.get("is_unique"):
        raise ValueError(f"Unique wonder {wonder['key']} is missing an image prompt")

    prompt = str(prompts.get(wonder["key"]) or "").strip()
    if not prompt:
        raise ValueError(f"Generic wonder {wonder['key']} is missing an image prompt")
    return prompt


def load_wonder_image_tasks(*, include_unique: bool = True) -> list[dict]:
    wonders, _ = load_all_wonder_mechanics_data(include_unique=include_unique)
    generic_prompts = load_generic_wonder_image_prompts()
    generic_keys = {wonder["key"] for wonder in wonders if not wonder.get("is_unique")}

    missing_generic_prompts = sorted(key for key in generic_keys if key not in generic_prompts)
    if missing_generic_prompts:
        raise ValueError(
            "Missing generic wonder image prompts for: "
            + ", ".join(missing_generic_prompts)
        )

    extra_generic_prompts = sorted(key for key in generic_prompts if key not in generic_keys)
    if extra_generic_prompts:
        raise ValueError(
            "Unknown generic wonder image prompt keys: "
            + ", ".join(extra_generic_prompts)
        )

    tasks: list[dict] = []
    for wonder in wonders:
        tasks.append(
            {
                "id": int(wonder["id"]),
                "key": wonder["key"],
                "name": wonder_image_name(wonder),
                "prompt": wonder_image_prompt(wonder, generic_prompts),
                "is_unique": bool(wonder.get("is_unique")),
            }
        )
    return tasks


def final_building_maintenance(wonder: dict, building_design: dict, building: str) -> str:
    return building_design.get("final_maintenance", {}).get(building, building_design.get("maintenance", wonder["maintenance"]))


def ceremony_modifier_for_building(wonder: dict, mechanics: dict, building: str) -> tuple[str, dict] | None:
    if wonder.get("is_unique"):
        modifier_data = unique_ritual(wonder).get("country_modifier", {})
        if not modifier_data:
            return None
        return f"tv_wonder_{wonder['key']}_ceremony_modifier", modifier_data
    modifier_name = mechanics.get("ceremony_modifier_names", {}).get(wonder["key"], {}).get(building, f"{building}_modifier")
    ceremony_modifiers = mechanics.get("ceremony_modifiers", {})
    if modifier_name in ceremony_modifiers:
        return modifier_name, ceremony_modifiers[modifier_name]
    if building in ceremony_modifiers:
        return modifier_name, ceremony_modifiers[building]
    return None


def ceremony_modifier_for_style(wonder: dict, mechanics: dict, style: int) -> tuple[str, dict] | None:
    if style not in wonder["final_buildings"]:
        return None
    return ceremony_modifier_for_building(wonder, mechanics, final_building_for_style(wonder, style))


def generic_ritual_for_wonder(mechanics: dict, wonder: dict) -> dict:
    return mechanics["generic_rituals"][wonder["key"]]


def ritual_auxiliary_building(wonder: dict) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_annex"


def ritual_auxiliary_display_modifier_name(wonder: dict) -> str:
    return f"{ritual_auxiliary_building(wonder)}_display_modifier"


def ritual_auxiliary_modifiers(wonder: dict, ritual_plan: dict) -> dict:
    modifiers = dict(ritual_plan["auxiliary_building"]["local_modifier"])
    estate_power_modifier = RITUAL_AUXILIARY_ESTATE_POWER_BY_POP_TYPE[wonder["pop_type"]]
    modifiers[estate_power_modifier] = modifiers.get(estate_power_modifier, 0) + 0.5
    return modifiers


def ritual_burden_modifier_name(wonder: dict) -> str:
    if wonder.get("is_unique"):
        return f"tv_wonder_{wonder['key']}_ritual_burden_modifier"
    return f"tv_wonder_{wonder['key']}_ritual_burden_modifier"


def ritual_blessing_modifier_name(wonder: dict) -> str:
    if wonder.get("is_unique"):
        return f"tv_wonder_{wonder['key']}_ritual_blessing_modifier"
    return f"tv_wonder_{wonder['key']}_ritual_blessing_modifier"
