#!/usr/bin/env python3
"""
EU5 Mod Static Validator
Catches common errors before game loading. Reads docs/knowledge/*.yaml for patterns.

Usage:
  python scripts/validate.py                   # validate entire src/
  python scripts/validate.py src/              # validate one directory
  python scripts/validate.py --changed         # validate only git-changed files
  python scripts/validate.py --ai-report       # JSON output for AI tools
"""

import json
import importlib.util
import re
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from wonder_unique_ritual_harness import validate_unique_ritual_specs_for_repo  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "knowledge"
VALIDATION_BASELINE_FILE = REPO_ROOT / "data" / "validation_baseline.yaml"
PULSE_REGISTRY_FILE = REPO_ROOT / "data" / "pulse_registry.yaml"
MODIFIER_TYPES_FILE = (
    REPO_ROOT
    / "reference_game_files"
    / "game"
    / "main_menu"
    / "common"
    / "modifier_type_definitions"
    / "00_modifier_types.txt"
)
MODIFIER_TYPE_FILES = [
    MODIFIER_TYPES_FILE,
    *(
        (REPO_ROOT / "src" / "main_menu" / "common" / "modifier_type_definitions").glob("*.txt")
        if (REPO_ROOT / "src" / "main_menu" / "common" / "modifier_type_definitions").exists()
        else []
    ),
]
HARD_CODED_ON_ACTIONS_FILE = (
    REPO_ROOT
    / "reference_game_files"
    / "game"
    / "in_game"
    / "common"
    / "on_action"
    / "_hardcoded.txt"
)
TV_IO_DIR = REPO_ROOT / "src" / "in_game" / "common" / "international_organizations"
TV_IO_ICON_DIR = (
    REPO_ROOT
    / "src"
    / "main_menu"
    / "gfx"
    / "interface"
    / "icons"
    / "international_organizations"
)
STATIC_MODIFIER_DIRS = (
    REPO_ROOT / "src" / "in_game" / "common" / "static_modifiers",
    REPO_ROOT / "src" / "main_menu" / "common" / "static_modifiers",
)
UNIQUE_RITUAL_HARNESS_FILES = {
    "data/unique_wonders.yaml",
    "data/unique_wonder_ritual_designs.yaml",
    "data/unique_wonder_ritual_prompts.yaml",
    "data/unique_wonder_ritual_specs.yaml",
    "data/unique_wonder_ritual_codegen_templates.yaml",
    "data/unique_wonder_ritual_capabilities.yaml",
    "data/unique_wonder_ritual_archetypes.yaml",
    "data/wonder_localization.yaml",
    "scripts/wonder_unique_ritual_harness.py",
    "scripts/gen_unique_wonder_ritual_specs.py",
    "scripts/gen_unique_wonder_ritual_code.py",
    "scripts/audit_unique_wonder_rituals.py",
    "scripts/allocate_unique_wonder_ritual_event_ids.py",
    "scripts/test_unique_wonder_ritual_harness.py",
    "docs/guides/Unique_Wonder_Ritual_Harness.md",
}
UNIQUE_RITUAL_HARNESS_PREFIXES = {
    "data/generated_fragments/unique_wonder_rituals/",
}
UTF8_BOM = b"\xef\xbb\xbf"
VALIDATED_SUFFIXES = {".txt", ".gui", ".yml", ".yaml", ".md", ".py"}
LOCALIZATION_KEY_PATTERN = re.compile(r"^\s+(\w+)\s*:(?:\d+)?")
LOCALIZATION_HEADER_PATTERN = re.compile(r"^l_[A-Za-z_]+:\s*$")
LOCALIZATION_ENTRY_LINE_PATTERN = re.compile(r"^\s+[A-Za-z0-9_.-]+:(?:\d+)?\s+")
GAME_CONCEPT_DECL_PATTERN = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*\{$")
TOP_LEVEL_BLOCK_PATTERN = re.compile(r"(?m)^([A-Za-z]\w*)\s*=\s*\{")
EVENT_ID_REFERENCE_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\.([1-9][0-9]{4,})\b")
MONTHLY_PULSE_EVENT_ID_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\.\d+)\b")
MONTHLY_PULSE_TRIGGER_EVENT_SIMPLE_RE = re.compile(
    r"\btrigger_event_(?:non_silently|silently)\s*=\s*([A-Za-z_][A-Za-z0-9_]*\.\d+)\b"
)
MONTHLY_PULSE_TRIGGER_EVENT_BLOCK_RE = re.compile(
    r"\btrigger_event_(?:non_silently|silently)\s*=\s*\{"
)
MONTHLY_PULSE_TV_CALL_RE = re.compile(
    r"(?<![\w.:])(tv_[A-Za-z0-9_]+)\s*=\s*(?:yes|\{)"
)
EFFECT_LOCALIZATION_NEGATIVE_COUNTERPARTS = (
    ("global_neg", "global"),
    ("first_neg", "first"),
    ("third_neg", "third"),
    ("global_past_neg", "global_past"),
    ("first_past_neg", "first_past"),
    ("third_past_neg", "third_past"),
)
EFFECT_LOCALIZATION_ASSIGNMENT_RE = re.compile(
    r"(?m)^[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*=[ \t]*\"?([A-Za-z_][A-Za-z0-9_.]*)\"?"
)
WONDER_ENGINE_SCALED_FIXED_MODIFIER_MAX = 0.5
WONDER_ENGINE_SCALED_FIXED_MODIFIERS = {
    # Fixed-value modifiers only. Percent *_modifier variants are intentionally excluded.
    "global_pop_assimilation_speed",
    "global_pop_conversion_speed",
    "local_manpower",
    "local_pop_assimilation_speed",
    "local_pop_conversion_speed",
    "local_sailors",
}
WONDER_ENGINE_SCALED_FIXED_MODIFIER_RE = re.compile(
    rf"^\s*(?P<key>{'|'.join(sorted(WONDER_ENGINE_SCALED_FIXED_MODIFIERS))})\s*[:=]\s*"
    r"(?P<quote>['\"]?)(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?P=quote)\s*(?:#.*)?$"
)
GENERIC_ACTION_HIDDEN_ONLY_EFFECTS = {
    "tv_governor_remove_effect": (
        "dismisses a regional governor by clearing variables/lists and rebuilding display state; "
        "wrap the call in `hidden_effect = { ... }` so action tooltip rendering does not evaluate the cleanup chain."
    ),
    "tv_governor_clear_assignment_effect": (
        "clears governor assignment variables and location modifiers; wrap the call in "
        "`hidden_effect = { ... }` when reached from a generic action."
    ),
}

issues = []
warnings = []
BRACE_MATCH_CACHE: dict[int, tuple[str, dict[int, int]]] = {}
LINT_PREFILTER_TOKEN_RE = re.compile(r"(?<!\\)[A-Za-z_][A-Za-z0-9_]{2,}")


def load_yaml(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_warning_baseline() -> list[dict]:
    data = load_yaml(VALIDATION_BASELINE_FILE) or {}
    return data.get("warnings", []) or []


def _literal_prefilter_tokens(regex: str) -> tuple[str, ...]:
    """Extract conservative literal substrings used to skip impossible regex scans."""
    cleaned: list[str] = []
    in_class = False
    escaped = False
    for ch in regex:
        if escaped:
            if ch in "AbBdDsSwWZ0123456789":
                cleaned.append(" ")
            else:
                cleaned.append(ch)
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == "[":
            in_class = True
            cleaned.append(" ")
            continue
        if ch == "]" and in_class:
            in_class = False
            cleaned.append(" ")
            continue
        cleaned.append(" " if in_class else ch)

    tokens: list[str] = []
    for match in LINT_PREFILTER_TOKEN_RE.finditer("".join(cleaned)):
        token = match.group(0).lower()
        if token in {"ms", "multiline", "dotall"}:
            continue
        if token not in tokens:
            tokens.append(token)
    return tuple(tokens)


def compile_anti_patterns(patterns: list[dict]) -> list[dict]:
    compiled: list[dict] = []
    for entry in patterns:
        regex = entry.get("pattern", "")
        detectability = entry.get("detectability")
        if detectability is None:
            detectability = "lint" if regex else "advisory"
        if detectability != "lint" or not regex:
            continue
        try:
            compiled.append({
                "entry": entry,
                "pattern": re.compile(regex, re.MULTILINE | re.IGNORECASE),
                "only_in": tuple(entry.get("only_in_paths", []) or []),
                "prefilter_tokens": _literal_prefilter_tokens(regex),
            })
        except re.error as exc:
            warnings.append(
                f"[LINT_RULE] {entry.get('id', '<unknown>')} -- invalid regex skipped: {exc}"
            )
    return compiled


def load_modifier_whitelist() -> set[str]:
    whitelist = set()
    pattern = re.compile(r"^(\w+)\s*=\s*\{")
    for path in MODIFIER_TYPE_FILES:
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig") as f:
            for line in f:
                m = pattern.match(line.strip())
                if m:
                    whitelist.add(m.group(1))
    return whitelist


def get_changed_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
    )
    staged = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
    )
    names = set()
    for r in [result, staged, untracked]:
        for name in r.stdout.splitlines():
            names.add(name.strip())
    paths = []
    for name in names:
        p = REPO_ROOT / name
        if p.exists() and p.suffix in VALIDATED_SUFFIXES:
            paths.append(p)
    return paths


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return [
        p
        for p in target.rglob("*")
        if p.suffix in VALIDATED_SUFFIXES and p.is_file()
    ]


def _rel_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _paths_match(
    rels: set[str],
    *,
    prefixes: tuple[str, ...] = (),
    exact: tuple[str, ...] = (),
    contains: tuple[str, ...] = (),
) -> bool:
    return any(
        rel in exact
        or any(rel.startswith(prefix) for prefix in prefixes)
        or any(fragment in rel for fragment in contains)
        for rel in rels
    )


def check_anti_patterns(path: Path, content: str, patterns: list[dict]):
    path_str = str(path).replace("\\", "/")
    content_lower = content.lower()
    for compiled in patterns:
        entry = compiled["entry"]
        only_in = compiled["only_in"]
        if only_in and not any(sub in path_str for sub in only_in):
            continue
        prefilter_tokens = compiled["prefilter_tokens"]
        if prefilter_tokens and not any(token in content_lower for token in prefilter_tokens):
            continue
        for m in compiled["pattern"].finditer(content):
            line_num = content[: m.start()].count("\n") + 1
            issues.append(
                f"[{entry.get('category', 'pattern').upper()}] "
                f"{path.relative_to(REPO_ROOT)}:{line_num} -- "
                f"Bad: \"{entry['bad']}\" -> {entry['correction']}"
            )


def check_enums(path: Path, content: str, enums: dict):
    for enum_name, enum_data in enums.items():
        valid_values = set(enum_data.get("values", []))
        pattern = re.compile(
            rf"{re.escape(enum_name)}\s*\??\s*=\s*{re.escape(enum_name)}:(\w+)"
        )
        for m in pattern.finditer(content):
            val = m.group(1)
            if val not in valid_values:
                line_num = content[: m.start()].count("\n") + 1
                issues.append(
                    f"[ENUM] {path.relative_to(REPO_ROOT)}:{line_num} -- "
                    f"Invalid {enum_name}:{val}. Valid: {', '.join(sorted(valid_values))}"
                )


def check_modifier_names(path: Path, content: str, whitelist: set[str]):
    if not whitelist:
        return
    rel = str(path.relative_to(REPO_ROOT))
    if "auto_modifiers" not in rel and "static_modifiers" not in rel:
        return
    structural = {
        "category", "type", "icon", "requires_real", "potential_trigger",
        "scales_with", "limit", "hide_effects", "alert", "boolean", "percent",
        "already_percent", "decimals", "game_data", "min", "max",
        "cap_zero_to_one", "scale_with_pop", "format", "ai", "bias_type",
        "should_show_in_modifiers_tab", "color",
    }
    line_pattern = re.compile(r"^\s*(\w+)\s*=\s*[-\d.]+")
    for i, line in enumerate(content.splitlines(), 1):
        if line.strip().startswith("#"):
            continue
        m = line_pattern.match(line)
        if m:
            name = m.group(1)
            if name not in structural and name not in whitelist:
                issues.append(
                    f"[MODIFIER] {path.relative_to(REPO_ROOT)}:{i} -- "
                    f"Unknown modifier name '{name}'; verify in 00_modifier_types.txt"
                )


def _iter_yaml_localization_keys(path: Path):
    for line_num, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        match = LOCALIZATION_KEY_PATTERN.match(line)
        if match:
            yield match.group(1), line_num


def check_loc_physical_lines() -> None:
    """Catch localization values split across real physical lines."""
    loc_root = REPO_ROOT / "src" / "main_menu" / "localization"
    if not loc_root.exists():
        return

    for loc_file in sorted(loc_root.rglob("*.yml")):
        for line_num, line in enumerate(loc_file.read_text(encoding="utf-8-sig").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if LOCALIZATION_HEADER_PATTERN.match(line):
                continue
            if LOCALIZATION_ENTRY_LINE_PATTERN.match(line):
                continue
            issues.append(
                f"[LOCALIZATION] {loc_file.relative_to(REPO_ROOT)}:{line_num} -- "
                "Malformed localization physical line; keep each key/value on one line and "
                "escape intentional line breaks as \\n inside the quoted value."
            )


def _iter_game_concept_keys(path: Path):
    for line_num, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        match = GAME_CONCEPT_DECL_PATTERN.match(line.strip())
        if match:
            yield match.group(1), line_num


def check_game_concept_duplicate_keys() -> None:
    """Verify each main-menu game concept key is declared only once."""
    concepts_dir = REPO_ROOT / "src" / "main_menu" / "common" / "game_concepts"
    if not concepts_dir.exists():
        return

    key_defs: dict[str, list[tuple[Path, int]]] = {}
    for concept_file in sorted(concepts_dir.rglob("*.txt")):
        for key, line_num in _iter_game_concept_keys(concept_file):
            key_defs.setdefault(key, []).append((concept_file, line_num))

    for key, definitions in sorted(key_defs.items()):
        if len(definitions) < 2:
            continue
        locations = ", ".join(
            f"{path.relative_to(REPO_ROOT)}:{line_num}"
            for path, line_num in definitions
        )
        issues.append(
            f"[GAME_CONCEPT] Duplicate game concept key '{key}' in main_menu/common/game_concepts: {locations}"
        )


def check_loc_duplicate_keys() -> None:
    """Verify each main-menu localization key is defined only once per language."""
    loc_root = REPO_ROOT / "src" / "main_menu" / "localization"
    if not loc_root.exists():
        return
    for language_dir in sorted(path for path in loc_root.iterdir() if path.is_dir()):
        key_defs: dict[str, list[tuple[Path, int]]] = {}
        for loc_file in sorted(language_dir.rglob("*.yml")):
            for key, line_num in _iter_yaml_localization_keys(loc_file):
                key_defs.setdefault(key, []).append((loc_file, line_num))
        for key, definitions in sorted(key_defs.items()):
            if len(definitions) < 2:
                continue
            locations = ", ".join(
                f"{path.relative_to(REPO_ROOT)}:{line_num}"
                for path, line_num in definitions
            )
            issues.append(
                f"[LOCALIZATION] Duplicate localization key '{key}' in {language_dir.name}: {locations}"
            )


def check_loc_coverage() -> None:
    """Verify every key in English localization also exists in simp_chinese."""
    en_dir = REPO_ROOT / "src" / "main_menu" / "localization" / "english"
    zh_dir = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese"
    if not en_dir.exists():
        return
    for en_file in sorted(en_dir.glob("*_l_english.yml")):
        stem = en_file.stem[: -len("_l_english")]
        zh_file = zh_dir / f"{stem}_l_simp_chinese.yml"
        en_keys = {key for key, _ in _iter_yaml_localization_keys(en_file)}
        if not zh_file.exists():
            issues.append(f"[LOC] Missing simp_chinese file: {zh_file.relative_to(REPO_ROOT)}")
            continue
        zh_keys = {key for key, _ in _iter_yaml_localization_keys(zh_file)}
        missing = sorted(en_keys - zh_keys)
        if missing:
            issues.append(
                f"[LOC] {zh_file.relative_to(REPO_ROOT)}: "
                f"{len(missing)} key(s) missing from simp_chinese: "
                + ", ".join(missing)
            )


def check_trigger_loc_coverage() -> None:
    """Verify every custom_description text key in scripted_triggers has an entry in trigger_localization/."""
    triggers_dir = REPO_ROOT / "src" / "in_game" / "common" / "scripted_triggers"
    trig_loc_dir = REPO_ROOT / "src" / "in_game" / "common" / "trigger_localization"
    if not triggers_dir.exists():
        return

    # Collect all registered trigger loc keys from trigger_localization/ files
    registered: set[str] = set()
    if trig_loc_dir.exists():
        key_pat = re.compile(r"^(\w+)\s*=\s*\{")
        for f in trig_loc_dir.glob("*.txt"):
            for line in f.read_text(encoding="utf-8-sig").splitlines():
                m = key_pat.match(line.strip())
                if m:
                    registered.add(m.group(1))

    # Check each scripted_trigger file for custom_description text keys
    cd_pat = re.compile(r"custom_description\s*=\s*\{[^}]*?text\s*=\s*(\w+)", re.DOTALL)
    for f in triggers_dir.glob("*.txt"):
        content = f.read_text(encoding="utf-8-sig")
        for m in cd_pat.finditer(content):
            key = m.group(1)
            if key not in registered:
                line_num = content[: m.start()].count("\n") + 1
                issues.append(
                    f"[LOCALIZATION] {f.relative_to(REPO_ROOT)}:{line_num} -- "
                    f"custom_description text key '{key}' not registered in "
                    f"src/in_game/common/trigger_localization/ (engine error: 'No trigger loc {key}')"
                )


def check_effect_loc_coverage() -> None:
    """Verify every custom_description text key in scripted_effects has an effect_localization entry."""
    effects_dir = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects"
    effect_loc_dirs = (
        REPO_ROOT / "reference_game_files" / "game" / "in_game" / "common" / "effect_localization",
        REPO_ROOT / "src" / "in_game" / "common" / "effect_localization",
    )
    if not effects_dir.exists():
        return

    registered: set[str] = set()
    key_pat = re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*=\s*\{")
    for loc_dir in effect_loc_dirs:
        if not loc_dir.exists():
            continue
        for f in loc_dir.glob("*.txt"):
            for line in f.read_text(encoding="utf-8-sig").splitlines():
                m = key_pat.match(line.strip())
                if m:
                    registered.add(m.group(1))

    cd_pat = re.compile(
        r"custom_description\s*=\s*\{[^}]*?text\s*=\s*\"?([A-Za-z_][A-Za-z0-9_.]*)\"?",
        re.DOTALL,
    )
    for f in effects_dir.glob("*.txt"):
        content = f.read_text(encoding="utf-8-sig")
        for m in cd_pat.finditer(content):
            key = m.group(1)
            if key not in registered:
                line_num = content[: m.start()].count("\n") + 1
                issues.append(
                    f"[LOCALIZATION] {f.relative_to(REPO_ROOT)}:{line_num} -- "
                    f"custom_description text key '{key}' not registered in "
                    f"src/in_game/common/effect_localization/ (engine error: 'No effect loc {key}')"
                )


def check_effect_loc_positive_negative_pairs(path: Path, content: str) -> None:
    """Verify effect loc negative perspectives do not reuse the positive loc key."""
    for effect_key, open_pos, close_pos in _iter_top_level_blocks(content) or []:
        body = content[open_pos + 1:close_pos]
        assignments: dict[str, tuple[str, int]] = {}
        for match in EFFECT_LOCALIZATION_ASSIGNMENT_RE.finditer(body):
            perspective = match.group(1)
            loc_key = match.group(2)
            assignments[perspective] = (loc_key, open_pos + 1 + match.start())
        for negative, positive in EFFECT_LOCALIZATION_NEGATIVE_COUNTERPARTS:
            if negative not in assignments or positive not in assignments:
                continue
            negative_key, negative_pos = assignments[negative]
            positive_key, _positive_pos = assignments[positive]
            if negative_key == positive_key:
                issues.append(
                    f"[LOCALIZATION] {_rel_path(path)}:{_line_num(content, negative_pos)} -- "
                    f"effect loc '{effect_key}' maps {negative} to the same localization key "
                    f"as {positive} ('{negative_key}'); use a distinct negative loc key "
                    f"(engine error: 'Negative and positive version share loc')"
                )


def check_effect_loc_negative_perspectives() -> None:
    """Verify effect_localization positive/negative perspectives use distinct loc keys."""
    effect_loc_dir = REPO_ROOT / "src" / "in_game" / "common" / "effect_localization"
    if not effect_loc_dir.exists():
        return
    for f in sorted(effect_loc_dir.glob("*.txt")):
        check_effect_loc_positive_negative_pairs(f, f.read_text(encoding="utf-8-sig"))


def check_static_modifier_name_loc_coverage() -> None:
    """Verify every static modifier has a STATIC_MODIFIER_NAME_<id> localization key."""
    loc_root = REPO_ROOT / "src" / "main_menu" / "localization"
    if not loc_root.exists():
        return

    loc_keys_by_language: dict[str, set[str]] = {}
    for language_dir in sorted(path for path in loc_root.iterdir() if path.is_dir()):
        keys: set[str] = set()
        for loc_file in sorted(language_dir.rglob("*.yml")):
            for key, _loc_line_num in _iter_yaml_localization_keys(loc_file):
                if key.startswith("STATIC_MODIFIER_NAME_"):
                    keys.add(key)
        loc_keys_by_language[language_dir.name] = keys

    if not loc_keys_by_language:
        return

    for modifier_dir in STATIC_MODIFIER_DIRS:
        if not modifier_dir.exists():
            continue
        for modifier_file in sorted(modifier_dir.glob("*.txt")):
            content = modifier_file.read_text(encoding="utf-8-sig")
            for modifier_id, open_pos, _close_pos in _iter_top_level_blocks(content):
                if not modifier_id or modifier_id == "TRY_REPLACE":
                    continue
                expected_key = f"STATIC_MODIFIER_NAME_{modifier_id}"
                missing_languages = [
                    language
                    for language, keys in loc_keys_by_language.items()
                    if expected_key not in keys
                ]
                if missing_languages:
                    issues.append(
                        f"[LOCALIZATION] {modifier_file.relative_to(REPO_ROOT)}:{_line_num(content, open_pos)} -- "
                        f"static modifier '{modifier_id}' missing {expected_key} localization in "
                        f"{', '.join(missing_languages)}"
                    )


def check_autogenerated_staged() -> None:
    """Warn if any staged file contains the @AUTOGENERATED marker (generated output, not source)."""
    staged = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        cwd=REPO_ROOT,
    )
    for name in staged.stdout.splitlines():
        name = name.strip()
        if not name:
            continue
        p = REPO_ROOT / name
        if not p.exists() or p.suffix not in VALIDATED_SUFFIXES:
            continue
        try:
            first_line = p.read_text(encoding="utf-8-sig").splitlines()[0]
        except (IndexError, UnicodeDecodeError):
            continue
        if "@AUTOGENERATED" in first_line:
            issues.append(
                f"[AUTOGEN] {name} is auto-generated — edit its source script/data instead "
                f"(see first-line comment for the generator)"
            )


def check_generated_headers() -> None:
    """Warn if any script-managed file (in data/generated_files.yaml) is missing its @Generated header."""
    registry_path = REPO_ROOT / "data" / "generated_files.yaml"
    if not registry_path.exists():
        return
    registry = load_yaml(registry_path)
    if not registry or "generated" not in registry:
        return
    seen_outputs: set[str] = set()
    for entry in registry["generated"]:
        output = entry.get("output", "")
        if not output or output in seen_outputs:
            continue
        seen_outputs.add(output)
        out_path = REPO_ROOT / output
        if not out_path.exists():
            continue
        try:
            first_lines = out_path.read_text(encoding="utf-8-sig").splitlines()[:5]
        except UnicodeDecodeError:
            continue
        if not any("# @Generated by" in ln for ln in first_lines):
            issues.append(
                f"[AUTOGEN_HEADER] {output} is listed in data/generated_files.yaml but "
                f"missing '# @Generated by' header — re-run its generator or add the header"
            )


def _read_normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def _strip_generated_header(text: str) -> str:
    return re.sub(r"^# @Generated by .*?\n\n", "", text, count=1, flags=re.DOTALL)


def _same_ignoring_final_newline(left: str, right: str) -> bool:
    return left.rstrip("\r\n") == right.rstrip("\r\n")


def _load_generator_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path.relative_to(REPO_ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check_generated_output_fresh(
    *,
    output: Path,
    generator: Path,
    module_name: str,
    label: str,
) -> None:
    if not output.exists() or not generator.exists():
        return
    try:
        module = _load_generator_module(module_name, generator)
        expected = module.generate()
        actual = _read_normalized_text(output)
    except Exception as exc:
        issues.append(
            f"[GENERATED_FRESHNESS] {output.relative_to(REPO_ROOT)} -- "
            f"could not regenerate expected {label} output from "
            f"{generator.relative_to(REPO_ROOT)}: {exc}"
        )
        return
    if not _same_ignoring_final_newline(actual, expected):
        issues.append(
            f"[GENERATED_FRESHNESS] {output.relative_to(REPO_ROOT)} -- "
            f"generated {label} output is stale; run "
            f"`conda run --no-capture-output -n eu5 python {generator.relative_to(REPO_ROOT)}`"
        )


def check_location_window_generated_freshness() -> None:
    """Ensure generated location-window GUI files match current reference/data inputs."""
    gui_scripts_dir = REPO_ROOT / "scripts" / "in_game" / "gui"
    if str(gui_scripts_dir) not in sys.path:
        sys.path.insert(0, str(gui_scripts_dir))

    _check_generated_output_fresh(
        output=REPO_ROOT / "src" / "in_game" / "gui" / "location_window.gui",
        generator=REPO_ROOT / "scripts" / "in_game" / "gui" / "gen_location_window.py",
        module_name="validate_gen_location_window",
        label="location_window.gui",
    )
    _check_generated_output_fresh(
        output=REPO_ROOT / "submods" / "tv_meiou_and_taxes_compat" / "in_game" / "gui" / "location_window.gui",
        generator=REPO_ROOT / "scripts" / "compat" / "gen_tv_meiou_and_taxes_location_window.py",
        module_name="validate_gen_tv_meiou_and_taxes_location_window",
        label="M&T compatibility location_window.gui",
    )


def check_vanilla_copy_integrity() -> None:
    """Ensure generated vanilla-copy files preserve copied vanilla content."""
    character_out = REPO_ROOT / "src/in_game/common/customizable_localization/character_title.txt"
    character_vanilla = REPO_ROOT / "reference_game_files/game/in_game/common/customizable_localization/character_title.txt"
    if character_out.exists() and character_vanilla.exists():
        copied = _strip_generated_header(_read_normalized_text(character_out))
        copied_without_tv = re.sub(
            r"\n\t# Towards Victory IO leader titles\n\n[\s\S]*?\n(?=\})",
            "",
            copied,
            count=1,
        )
        vanilla = _read_normalized_text(character_vanilla)
        if not _same_ignoring_final_newline(copied_without_tv, vanilla):
            issues.append(
                "[VANILLA_COPY] src/in_game/common/customizable_localization/character_title.txt "
                "-- copied vanilla content differs from "
                "reference_game_files/game/in_game/common/customizable_localization/character_title.txt; "
                "only the TV leader title entries may differ"
            )

    message_out = REPO_ROOT / "src/main_menu/gui/messagetypes.txt"
    message_vanilla = REPO_ROOT / "reference_game_files/game/main_menu/gui/messagetypes.txt"
    if message_out.exists() and message_vanilla.exists():
        copied = _read_normalized_text(message_out)
        vanilla = _read_normalized_text(message_vanilla)
        if not copied.startswith(vanilla):
            issues.append(
                "[VANILLA_COPY] src/main_menu/gui/messagetypes.txt -- copied vanilla "
                "prefix differs from reference_game_files/game/main_menu/gui/messagetypes.txt; "
                "only appended TV message type entries may differ"
            )


def check_tv_io_icon_assets() -> None:
    """Every mod-defined IO type needs the matching GetIcon DDS asset."""
    if not TV_IO_DIR.exists():
        return

    io_decl = re.compile(r"^(tv_[A-Za-z0-9_]+)\s*=\s*\{")
    for path in sorted(TV_IO_DIR.glob("*.txt")):
        try:
            content = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        for match in io_decl.finditer(content):
            io_type = match.group(1)
            icon = TV_IO_ICON_DIR / f"{io_type}.dds"
            if not icon.exists():
                line_num = _line_num(content, match.start())
                issues.append(
                    f"[GUI] {path.relative_to(REPO_ROOT)}:{line_num} -- "
                    f"Missing GetIcon asset {icon.relative_to(REPO_ROOT)} for IO type {io_type}"
                )


def check_tv_io_monthly_effect_blocks() -> None:
    """Ban IO monthly_effect blocks; use monthly_change or country pulses instead."""
    if not TV_IO_DIR.exists():
        return

    monthly_effect_re = re.compile(r"\bmonthly_effect\s*=")
    for path in sorted(TV_IO_DIR.rglob("*.txt")):
        try:
            content = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as exc:
            issues.append(f"[IO_MONTHLY_EFFECT] Cannot read {path.relative_to(REPO_ROOT)}: {exc}")
            continue

        for line_num, raw_line in enumerate(content.splitlines(), 1):
            line = raw_line.split("#", 1)[0]
            if not monthly_effect_re.search(line):
                continue
            issues.append(
                f"[IO_MONTHLY_EFFECT] {path.relative_to(REPO_ROOT)}:{line_num} -- "
                "TV international_organization types must not define `monthly_effect` blocks; "
                "IO monthly effects have severe performance costs. Keep visible variable arithmetic "
                "in IO variable `monthly_change`, and move maintenance/completion side effects to "
                "registered country monthly pulses or explicit lifecycle hooks."
            )


def check_event_id_numeric_range(path: Path, content: str) -> None:
    """Catch event IDs whose numeric part exceeds Jomini's four-digit limit."""
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if not (
        rel.startswith("src/")
        or rel.startswith("scripts/")
        or rel.startswith("data/")
    ):
        return
    for match in EVENT_ID_REFERENCE_PATTERN.finditer(content):
        event_id = f"{match.group(1)}.{match.group(2)}"
        issues.append(
            f"[EVENT_ID] {path.relative_to(REPO_ROOT)}:{_line_num(content, match.start())} -- "
            f"{event_id} is invalid; EU5 event numeric IDs must be < 10000. "
            "Keep extra dimensions in pre-trigger dispatch or event-local non-wonder branches instead of encoding them into the event ID."
        )


def check_event_option_effect_blocks(path: Path, content: str) -> None:
    """Event options execute effects directly; `effect = {}` is parsed as an unknown effect."""
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if not (rel.startswith("src/in_game/events/") and path.suffix == ".txt"):
        return

    for match in re.finditer(r"(?m)^[ \t]*option\s*=\s*\{", content):
        open_pos = content.find("{", match.start())
        close_pos = _find_matching_brace(content, open_pos)
        if open_pos == -1 or close_pos is None:
            continue
        for effect_open, _ in _iter_direct_child_blocks(content, open_pos, close_pos, "effect"):
            issues.append(
                f"[EVENT_OPTION_EFFECT_BLOCK] {path.relative_to(REPO_ROOT)}:{_line_num(content, effect_open)} -- "
                "Event option effects must be written directly inside `option = { ... }`; "
                "`effect = { ... }` is parsed as an unknown effect named `effect`."
            )


def check_gui_parentanchor_under_hbox_vbox(path: Path, content: str) -> None:
    """Catch direct hbox/vbox children trying to position themselves."""
    if path.suffix != ".gui":
        return

    for box_name in ("hbox", "vbox"):
        for box_open, box_close in _iter_named_blocks(content, -1, len(content), box_name):
            for child_name, child_open, child_close in _iter_direct_child_blocks_any(
                content,
                box_open,
                box_close,
            ):
                parentanchor_pos = _find_direct_property(
                    content,
                    child_open,
                    child_close,
                    "parentanchor",
                )
                if parentanchor_pos is None:
                    continue
                issues.append(
                    f"[GUI] {path.relative_to(REPO_ROOT)}:{_line_num(content, parentanchor_pos)} -- "
                    f"`parentanchor` is unsupported on direct {box_name} child `{child_name}`; "
                    "hboxes/vboxes arrange their children automatically. Use layout policies, "
                    "expand spacers, or a nested wrapper for centering."
                )


def check_wonder_engine_scaled_fixed_modifiers(path: Path, content: str) -> None:
    """Catch wonder modifier values that EU5 displays 1000x larger than written."""
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if "wonder" not in rel or path.suffix not in {".txt", ".yaml", ".yml"}:
        return

    for line_num, line in enumerate(content.splitlines(), 1):
        match = WONDER_ENGINE_SCALED_FIXED_MODIFIER_RE.match(line)
        if not match:
            continue
        value = float(match.group("value"))
        if value <= WONDER_ENGINE_SCALED_FIXED_MODIFIER_MAX:
            continue
        key = match.group("key")
        issues.append(
            f"[WONDER_MODIFIER_SCALE] {path.relative_to(REPO_ROOT)}:{line_num} -- "
            f"{key} = {match.group('value')} exceeds {WONDER_ENGINE_SCALED_FIXED_MODIFIER_MAX}. "
            "EU5 multiplies this fixed-value modifier by 1000 in game; use a small fixed value, "
            "or use the matching *_modifier percent modifier when a percentage is intended."
        )


def check_knowledge_maintenance(anti_patterns: list[dict]) -> None:
    """Warn when AI-maintained knowledge/workflow files drift out of sync."""
    valid_detectability = {"lint", "needs_parser", "advisory"}
    for entry in anti_patterns:
        detectability = entry.get("detectability")
        if detectability is not None and detectability not in valid_detectability:
            warnings.append(
                f"[KNOWLEDGE] anti_patterns.yaml:{entry.get('id', '<unknown>')} -- "
                f"invalid detectability '{detectability}'; use lint, needs_parser, or advisory"
            )
        if (entry.get("detectability") == "lint") and not entry.get("pattern") and not entry.get("validator"):
            warnings.append(
                f"[KNOWLEDGE] anti_patterns.yaml:{entry.get('id', '<unknown>')} -- "
                "detectability is lint but both pattern and validator are empty"
            )

    ai_context = REPO_ROOT / "scripts" / "ai_context.py"
    ai_context_text = ai_context.read_text(encoding="utf-8") if ai_context.exists() else ""
    risk_cards_dir = KNOWLEDGE_DIR / "risk_cards"
    if risk_cards_dir.exists():
        for card in sorted(risk_cards_dir.glob("*.md")):
            if card.name.upper() in {"README.MD", "MAINTENANCE.MD"}:
                continue
            if card.name not in ai_context_text:
                warnings.append(
                    f"[KNOWLEDGE] docs/knowledge/risk_cards/{card.name} -- "
                    "risk card is not registered in scripts/ai_context.py DOMAIN_RULES"
                )

    domain_rule_cards = re.findall(
        r'\("[^"]+",\s*"[^"]+",\s*"([^"]+\.md)"\)',
        ai_context_text,
    )
    domain_rule_cards += re.findall(
        r'\("[^"]+",\s*\([^()]*\),\s*"([^"]+\.md)"\)',
        ai_context_text,
    )
    for card_name in domain_rule_cards:
        card = risk_cards_dir / card_name
        if not card.exists():
            warnings.append(
                f"[KNOWLEDGE] scripts/ai_context.py -- DOMAIN_RULES references missing risk card {card_name}"
            )

    baseline = load_yaml(VALIDATION_BASELINE_FILE) or {}
    for idx, entry in enumerate(baseline.get("warnings", []) or [], 1):
        if not entry.get("rule"):
            warnings.append(
                f"[KNOWLEDGE] data/validation_baseline.yaml:warnings[{idx}] -- missing rule"
            )
        if not entry.get("message") and not entry.get("message_contains"):
            warnings.append(
                f"[KNOWLEDGE] data/validation_baseline.yaml:warnings[{idx}] -- missing message or message_contains"
            )
        if not entry.get("rationale"):
            warnings.append(
                f"[KNOWLEDGE] data/validation_baseline.yaml:warnings[{idx}] -- missing rationale"
            )


def check_unique_wonder_ritual_harness(files: list[Path]) -> None:
    rels = {str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in files}
    if not rels.intersection(UNIQUE_RITUAL_HARNESS_FILES) and not any(
        rel.startswith(prefix)
        for rel in rels
        for prefix in UNIQUE_RITUAL_HARNESS_PREFIXES
    ):
        return
    for error in validate_unique_ritual_specs_for_repo():
        issues.append(f"[UNIQUE_RITUAL_HARNESS] {error}")


def run_global_checks(files: list[Path], use_changed: bool, anti_patterns: list[dict]) -> None:
    rels = {_rel_path(path) for path in files}

    if not use_changed or _paths_match(rels, prefixes=("src/main_menu/common/game_concepts/",)):
        check_game_concept_duplicate_keys()
    if not use_changed or _paths_match(rels, prefixes=("src/main_menu/localization/",)):
        check_loc_physical_lines()
        check_loc_duplicate_keys()
        check_loc_coverage()
    if not use_changed or _paths_match(
        rels,
        exact=("scripts/validate.py",),
        prefixes=(
            "src/in_game/common/static_modifiers/",
            "src/main_menu/common/static_modifiers/",
            "src/main_menu/localization/",
        ),
    ):
        check_static_modifier_name_loc_coverage()
    if not use_changed or _paths_match(
        rels,
        prefixes=(
            "src/in_game/common/scripted_triggers/",
            "src/in_game/common/trigger_localization/",
        ),
    ):
        check_trigger_loc_coverage()
    if not use_changed or _paths_match(
        rels,
        exact=("scripts/validate.py",),
        prefixes=(
            "src/in_game/common/scripted_effects/",
            "src/in_game/common/effect_localization/",
        ),
    ):
        check_effect_loc_coverage()
        check_effect_loc_negative_perspectives()

    check_autogenerated_staged()

    check_generated_headers()
    if not use_changed or _paths_match(
        rels,
        exact=(
            "src/in_game/common/customizable_localization/character_title.txt",
            "src/main_menu/gui/messagetypes.txt",
            "reference_game_files/game/in_game/common/customizable_localization/character_title.txt",
            "reference_game_files/game/main_menu/gui/messagetypes.txt",
        ),
    ):
        check_vanilla_copy_integrity()
    if not use_changed or _paths_match(
        rels,
        exact=(
            "src/in_game/gui/location_window.gui",
            "submods/tv_meiou_and_taxes_compat/in_game/gui/location_window.gui",
            "scripts/in_game/gui/gen_location_window.py",
            "scripts/compat/gen_tv_meiou_and_taxes_location_window.py",
        ),
    ):
        check_location_window_generated_freshness()
    if not use_changed or _paths_match(
        rels,
        prefixes=(
            "src/in_game/common/international_organizations/",
            "src/main_menu/gfx/interface/icons/international_organizations/",
        ),
    ):
        check_tv_io_icon_assets()
        check_tv_io_monthly_effect_blocks()
    if not use_changed or _paths_match(
        rels,
        exact=("data/pulse_registry.yaml",),
        prefixes=(
            "src/in_game/common/on_action/",
            "src/in_game/common/scripted_effects/",
        ),
    ):
        check_monthly_country_pulse_event_delay()

    if not use_changed or _paths_match(
        rels,
        exact=(
            "docs/knowledge/anti_patterns.yaml",
            "data/validation_baseline.yaml",
            "scripts/ai_context.py",
        ),
        prefixes=("docs/knowledge/risk_cards/",),
    ):
        check_knowledge_maintenance(anti_patterns)
    check_unique_wonder_ritual_harness(files)


def _line_num(content: str, pos: int) -> int:
    return content[:pos].count("\n") + 1


def _find_matching_brace(content: str, open_pos: int) -> int | None:
    """Return the matching } for content[open_pos] == {, ignoring strings/comments."""
    cache_key = id(content)
    cached = BRACE_MATCH_CACHE.get(cache_key)
    if cached is not None and cached[0] is content and open_pos in cached[1]:
        return cached[1][open_pos]
    depth = 0
    in_string = False
    in_comment = False
    escaped = False
    for i in range(open_pos, len(content)):
        ch = content[i]
        if in_comment:
            if ch == "\n":
                in_comment = False
            continue
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == "#":
            in_comment = True
        elif ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                if cached is None or cached[0] is not content:
                    cached = (content, {})
                    BRACE_MATCH_CACHE[cache_key] = cached
                cached[1][open_pos] = i
                return i
    return None


def _iter_top_level_blocks(content: str):
    candidates = {
        content.find("{", match.start(), match.end()): match.group(1)
        for match in TOP_LEVEL_BLOCK_PATTERN.finditer(content)
    }
    if not candidates:
        return

    depth = 0
    active: tuple[str, int] | None = None
    in_string = False
    in_comment = False
    escaped = False
    for i, ch in enumerate(content):
        if in_comment:
            if ch == "\n":
                in_comment = False
            continue
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == "#":
            in_comment = True
        elif ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 0:
                name = candidates.get(i)
                active = (name, i) if name else None
            depth += 1
        elif ch == "}":
            if depth <= 0:
                continue
            depth -= 1
            if depth == 0 and active is not None:
                name, open_pos = active
                BRACE_MATCH_CACHE.setdefault(id(content), (content, {}))[1][open_pos] = i
                yield name, open_pos, i
                active = None


def _iter_named_blocks(content: str, start: int, end: int, name: str):
    body = content[start + 1:end]
    for match in re.finditer(rf"(?m)^[ \t]*{re.escape(name)}\s*=\s*\{{", body):
        open_pos = content.find("{", start + 1 + match.start())
        close_pos = _find_matching_brace(content, open_pos)
        if close_pos is None or close_pos > end:
            continue
        yield open_pos, close_pos


def _brace_delta(line: str) -> int:
    """Return brace depth delta for a single line, ignoring comments."""
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def _has_direct_child_block(body: str, name: str) -> bool:
    """True when body contains a direct child block with the given name."""
    depth = 0
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*=\s*\{{")
    for line in body.splitlines():
        if depth == 0 and pattern.match(line):
            return True
        depth += _brace_delta(line)
        if depth < 0:
            depth = 0
    return False


def _is_comment_position(content: str, pos: int) -> bool:
    line_start = content.rfind("\n", 0, pos) + 1
    prefix = content[line_start:pos]
    return "#" in prefix and prefix.split("#", 1)[0].strip() == ""


def _iter_direct_child_blocks(content: str, start: int, end: int, name: str):
    """Yield direct child blocks named `name` inside content[start:end]."""
    depth = 0
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*=\s*\{{")
    segment = content[start + 1:end]
    abs_line_start = start + 1
    for line in segment.splitlines(keepends=True):
        code = line.split("#", 1)[0]
        if depth == 0:
            match = pattern.match(code)
            if match:
                open_pos = content.find("{", abs_line_start + match.start(), abs_line_start + len(line))
                close_pos = _find_matching_brace(content, open_pos) if open_pos != -1 else None
                if close_pos is not None and close_pos <= end:
                    yield open_pos, close_pos
        depth += _brace_delta(line)
        if depth < 0:
            depth = 0
        abs_line_start += len(line)


def _iter_direct_child_blocks_any(content: str, start: int, end: int):
    """Yield direct child blocks of any simple GUI/script block name."""
    depth = 0
    pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{")
    segment = content[start + 1:end]
    abs_line_start = start + 1
    for line in segment.splitlines(keepends=True):
        code = line.split("#", 1)[0]
        if depth == 0:
            match = pattern.match(code)
            if match:
                open_pos = content.find("{", abs_line_start + match.start(), abs_line_start + len(line))
                close_pos = _find_matching_brace(content, open_pos) if open_pos != -1 else None
                if close_pos is not None and close_pos <= end:
                    yield match.group(1), open_pos, close_pos
        depth += _brace_delta(line)
        if depth < 0:
            depth = 0
        abs_line_start += len(line)


def _find_direct_property(content: str, start: int, end: int, name: str) -> int | None:
    """Return the first direct property assignment position inside a block."""
    depth = 0
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*=")
    segment = content[start + 1:end]
    abs_line_start = start + 1
    for line in segment.splitlines(keepends=True):
        code = line.split("#", 1)[0]
        if depth == 0:
            match = pattern.match(code)
            if match:
                return abs_line_start + match.start()
        depth += _brace_delta(line)
        if depth < 0:
            depth = 0
        abs_line_start += len(line)
    return None


def _iter_direct_on_action_event_entries(content: str, start: int, end: int):
    """Yield direct event ids inside native events/random_events blocks."""
    depth = 0
    segment = content[start + 1:end]
    abs_line_start = start + 1
    weighted_event = re.compile(
        r"^\s*(?:\d+|[A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*\.\d+)\b"
    )
    bare_event = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*\.\d+)\b")
    for line in segment.splitlines(keepends=True):
        code = line.split("#", 1)[0]
        if depth == 0:
            match = weighted_event.match(code) or bare_event.match(code)
            if match:
                event_id = match.group(1)
                yield event_id, abs_line_start + code.find(event_id)
        depth += _brace_delta(line)
        if depth < 0:
            depth = 0
        abs_line_start += len(line)


def _direct_delay_days(content: str, start: int, end: int) -> list[tuple[int, int | None]]:
    delays = []
    for delay_open, delay_close in _iter_direct_child_blocks(content, start, end, "delay"):
        body = content[delay_open + 1:delay_close]
        days_match = re.search(r"\bdays\s*=\s*(-?\d+)\b", body)
        days = int(days_match.group(1)) if days_match else None
        delays.append((delay_open, days))
    return delays


def _load_monthly_country_pulse_config() -> tuple[list[str], int]:
    registry = load_yaml(PULSE_REGISTRY_FILE) or {}
    settings = registry.get("settings", {}) or {}
    delay = int(settings.get("monthly_country_pulse_event_delay_days", 1))
    pulses = registry.get("pulses", {}) or {}
    callbacks = [str(name) for name in (pulses.get("monthly_country_pulse", []) or [])]
    return callbacks, delay


def _load_tv_on_action_and_effect_blocks() -> dict[str, dict]:
    blocks: dict[str, dict] = {}
    roots = [
        REPO_ROOT / "src" / "in_game" / "common" / "on_action",
        REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.txt")):
            try:
                content = path.read_text(encoding="utf-8-sig")
            except OSError:
                continue
            for name, open_pos, close_pos in _iter_top_level_blocks(content):
                if name.startswith("tv_"):
                    blocks[name] = {
                        "path": path,
                        "content": content,
                        "open": open_pos,
                        "close": close_pos,
                    }
    return blocks


def _iter_tv_block_calls(content: str, start: int, end: int):
    body = content[start + 1:end]
    for match in MONTHLY_PULSE_TV_CALL_RE.finditer(body):
        absolute_pos = start + 1 + match.start()
        if _is_comment_position(content, absolute_pos):
            continue
        yield match.group(1)


def _monthly_delay_issue(path: Path, content: str, pos: int, event_id: str, expected_days: int, detail: str) -> None:
    issues.append(
        f"[MONTHLY_PULSE_EVENT_DELAY] {path.relative_to(REPO_ROOT)}:{_line_num(content, pos)} -- "
        f"{event_id} is reachable from monthly_country_pulse; {detail}. "
        f"Use days = {expected_days} for trigger_event_* calls or "
        f"`delay = {{ days = {expected_days} }}` for native events/random_events blocks."
    )


def _check_trigger_event_delays_in_block(block: dict, expected_days: int) -> None:
    path = block["path"]
    content = block["content"]
    start = block["open"]
    end = block["close"]
    body = content[start + 1:end]

    for match in MONTHLY_PULSE_TRIGGER_EVENT_SIMPLE_RE.finditer(body):
        absolute_pos = start + 1 + match.start()
        if _is_comment_position(content, absolute_pos):
            continue
        _monthly_delay_issue(
            path,
            content,
            absolute_pos,
            match.group(1),
            expected_days,
            "simple trigger_event_* form has no delay",
        )

    for match in MONTHLY_PULSE_TRIGGER_EVENT_BLOCK_RE.finditer(body):
        absolute_pos = start + 1 + match.start()
        if _is_comment_position(content, absolute_pos):
            continue
        open_pos = content.find("{", absolute_pos, end)
        if open_pos == -1:
            continue
        close_pos = _find_matching_brace(content, open_pos)
        if close_pos is None or close_pos > end:
            continue
        trigger_body = content[open_pos + 1:close_pos]
        id_match = re.search(r"\bid\s*=\s*([A-Za-z_][A-Za-z0-9_]*\.\d+)\b", trigger_body)
        if not id_match:
            continue
        event_id = id_match.group(1)
        days_match = re.search(r"\bdays\s*=\s*(-?\d+)\b", trigger_body)
        if not days_match or int(days_match.group(1)) != expected_days:
            _monthly_delay_issue(
                path,
                content,
                open_pos + 1 + id_match.start(),
                event_id,
                expected_days,
                "trigger_event_* object is missing the required one-day delay",
            )


def _check_native_on_action_event_delays_in_block(block: dict, expected_days: int) -> None:
    path = block["path"]
    content = block["content"]
    for block_name in ("events", "random_events"):
        for events_open, events_close in _iter_named_blocks(content, block["open"], block["close"], block_name):
            event_entries = list(_iter_direct_on_action_event_entries(content, events_open, events_close))
            if not event_entries:
                continue
            first_event_id, first_event_pos = event_entries[0]
            valid_delay = any(
                delay_open < first_event_pos and days == expected_days
                for delay_open, days in _direct_delay_days(content, events_open, events_close)
            )
            if not valid_delay:
                _monthly_delay_issue(
                    path,
                    content,
                    first_event_pos,
                    first_event_id,
                    expected_days,
                    f"{block_name} block is missing a preceding delay",
                )


def check_monthly_country_pulse_event_delay() -> None:
    """Ensure monthly_country_pulse-triggered events fire one day later."""
    if not PULSE_REGISTRY_FILE.exists():
        return
    callbacks, expected_days = _load_monthly_country_pulse_config()
    if not callbacks:
        return

    blocks = _load_tv_on_action_and_effect_blocks()
    queue = list(callbacks)
    visited: set[str] = set()
    reachable: list[dict] = []
    while queue:
        name = queue.pop(0)
        if name in visited:
            continue
        visited.add(name)
        block = blocks.get(name)
        if not block:
            continue
        reachable.append(block)
        for called in _iter_tv_block_calls(block["content"], block["open"], block["close"]):
            if called in blocks and called not in visited:
                queue.append(called)

    for block in reachable:
        _check_trigger_event_delays_in_block(block, expected_days)
        _check_native_on_action_event_delays_in_block(block, expected_days)


def load_hardcoded_on_actions() -> set[str]:
    """Return the vanilla hardcoded on_action names that should not gain a second effect block."""
    if not HARD_CODED_ON_ACTIONS_FILE.exists():
        return set()
    content = HARD_CODED_ON_ACTIONS_FILE.read_text(encoding="utf-8-sig")
    return {name for name, _, _ in _iter_top_level_blocks(content)}


def _generic_action_warning(path: Path, line: int, action: str, code: str, message: str) -> None:
    warnings.append(
        f"[GENERIC_ACTION_RISK] {path.relative_to(REPO_ROOT)}:{line} -- "
        f"{code}: {action}: {message}"
    )


def check_generic_action_pre_eval_risks(path: Path, content: str) -> None:
    """Heuristic, brace-aware checks for hover/tooltip pre-evaluation hazards."""
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if "src/in_game/common/generic_actions/" not in rel:
        return

    hover_blocks = ["allow", "select_trigger"]
    for action, action_open, action_close in _iter_top_level_blocks(content):
        action_body = content[action_open + 1:action_close]

        for block_name in hover_blocks:
            for block_open, block_close in _iter_named_blocks(content, action_open, action_close, block_name):
                block_body = content[block_open + 1:block_close]
                guarded = set(re.findall(r"\bhas_variable\s*=\s*(\w+)", block_body))
                for var_name in sorted(guarded):
                    direct = re.search(rf"\bvar:{re.escape(var_name)}\s*=", block_body)
                    if direct:
                        _generic_action_warning(
                            path,
                            _line_num(content, block_open + 1 + direct.start()),
                            action,
                            "generic_action_pre_eval",
                            f"`has_variable = {var_name}` and direct `var:{var_name} =` appear in the same {block_name} block; use `var:{var_name} ?=` for nullable hover-time reads.",
                        )

        target_flags = re.findall(r"\btarget_flag\s*=\s*(\w+)", action_body)
        allowed_flags = {"target", "recipient"} | {f"target_{i}" for i in range(1, 10)}
        for flag in target_flags:
            if flag not in allowed_flags:
                m = re.search(rf"\btarget_flag\s*=\s*{re.escape(flag)}\b", action_body)
                _generic_action_warning(
                    path,
                    _line_num(content, action_open + 1 + (m.start() if m else 0)),
                    action,
                    "target_flag_name",
                    f"`target_flag = {flag}` is not one of target/target_1/target_2; vanilla-shaped names are safest.",
                )

        seen_target_flags: set[str] = set()
        for block_open, block_close in _iter_named_blocks(content, action_open, action_close, "select_trigger"):
            block_body = content[block_open + 1:block_close]
            prior_refs = [
                flag
                for flag in sorted(seen_target_flags)
                if re.search(rf"\bscope:{re.escape(flag)}\b", block_body)
            ]
            if prior_refs and re.search(r"\bsource\s*=\s*world\b", block_body):
                source_match = re.search(r"\bsource\s*=\s*world\b", block_body)
                _generic_action_warning(
                    path,
                    _line_num(content, block_open + 1 + (source_match.start() if source_match else 0)),
                    action,
                    "world_source_reads_previous_target",
                    "`source = world` appears in a later select_trigger that reads "
                    f"previous target flag(s) {', '.join(prior_refs)}; keep the selector in the same "
                    "interaction-target chooser by omitting source or using a non-world source.",
                )
            flag_match = re.search(r"\btarget_flag\s*=\s*(\w+)", block_body)
            if flag_match:
                seen_target_flags.add(flag_match.group(1))

        effect_blocks = list(_iter_named_blocks(content, action_open, action_close, "effect"))
        if target_flags and effect_blocks:
            effect_text = "\n".join(content[o + 1:c] for o, c in effect_blocks)
            for flag in sorted(set(target_flags)):
                if re.search(rf"\bscope:{re.escape(flag)}\b", effect_text) and not re.search(
                    rf"\bexists\s*=\s*scope:{re.escape(flag)}\b", effect_text
                ):
                    _generic_action_warning(
                        path,
                        _line_num(content, effect_blocks[0][0]),
                        action,
                        "missing_target_guard",
                        f"effect reads `scope:{flag}` but no `exists = scope:{flag}` guard was found.",
                    )

        for effect_open, effect_close in effect_blocks:
            effect_body = content[effect_open + 1:effect_close]
            hidden_ranges = list(_iter_named_blocks(content, effect_open, effect_close, "hidden_effect"))
            for effect_name, reason in GENERIC_ACTION_HIDDEN_ONLY_EFFECTS.items():
                for cleanup_match in re.finditer(rf"\b{re.escape(effect_name)}\s*=\s*yes\b", effect_body):
                    absolute_pos = effect_open + 1 + cleanup_match.start()
                    line_start = effect_body.rfind("\n", 0, cleanup_match.start()) + 1
                    line_prefix = effect_body[line_start:cleanup_match.start()]
                    if line_prefix.lstrip().startswith("#"):
                        continue
                    if any(hidden_open < absolute_pos < hidden_close for hidden_open, hidden_close in hidden_ranges):
                        continue
                    issues.append(
                        f"[GENERIC_ACTION_HIDDEN_EFFECT] {path.relative_to(REPO_ROOT)}:{_line_num(content, absolute_pos)} -- "
                        f"{action}: `{effect_name}` is a state-cleanup helper called from a visible generic action effect; {reason}"
                    )

            for set_match in re.finditer(
                r"set_variable\s*=\s*\{[^{}]*\bname\s*=\s*(\w+)",
                effect_body,
                re.MULTILINE,
            ):
                var_name = set_match.group(1)
                tail = effect_body[set_match.end():]
                direct = re.search(
                    rf"\bvar:{re.escape(var_name)}\s*(?:[<>]=?|=)",
                    tail,
                )
                if direct:
                    _generic_action_warning(
                        path,
                        _line_num(content, effect_open + 1 + set_match.end() + direct.start()),
                        action,
                        "visible_effect_reads_new_value",
                        f"effect sets `{var_name}` and later reads `var:{var_name}` directly; action tooltip pre-evaluation may not commit the earlier write.",
                    )


def check_io_policy_ai_scope_recipient_guard(path: Path, content: str) -> None:
    """Catch IO policy AI math that can be evaluated without a recipient IO target."""
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if "src/in_game/common/laws/" not in rel:
        return

    ai_math_blocks = [
        "wants_this_policy_bias",
        "wants_propose_policy",
        "wants_keep_policy",
        "reasons_to_join",
        "diplomatic_capacity_cost",
    ]
    for block_name in ai_math_blocks:
        for block_open, block_close in _iter_named_blocks(content, 0, len(content) - 1, block_name):
            block_body = content[block_open + 1:block_close]
            if "scope:recipient" not in block_body:
                continue
            has_unsafe_recipient = re.search(r"\bscope:recipient(?!\s*\?=)\b", block_body)
            if has_unsafe_recipient and not re.search(r"\bexists\s*=\s*scope:recipient\b", block_body):
                issues.append(
                    f"[IO_POLICY_AI_SCOPE] {path.relative_to(REPO_ROOT)}:{_line_num(content, block_open)} -- "
                    f"{block_name} uses `scope:recipient` without `exists = scope:recipient`; "
                    "IO policy AI math may be pre-evaluated without a recipient event target."
                )


def check_on_action_singleton_effect_delegate(path: Path, content: str, hardcoded_on_actions: set[str]) -> None:
    """Catch additive mod files that stack a second direct effect onto a vanilla hardcoded on_action."""
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if "src/in_game/common/on_action/" not in rel:
        return
    for block_name, open_pos, close_pos in _iter_top_level_blocks(content):
        if block_name not in hardcoded_on_actions:
            continue
        body = content[open_pos + 1:close_pos]
        if _has_direct_child_block(body, "effect"):
            issues.append(
                f"[ON_ACTION] {path.relative_to(REPO_ROOT)}:{_line_num(content, open_pos)} -- "
                f"{block_name} defines a direct top-level effect block; extend hardcoded vanilla hooks via `on_actions = {{ tv_* }}` delegation instead of stacking another `effect`."
            )


def _parse_issue_structured(raw: str) -> dict:
    """Parse a raw issue string into a structured dict for --ai-report output."""
    m = re.match(r"^\[(\w+)\]\s+([^:]+):(\d+)\s+--\s+Bad:\s+\"([^\"]*)\"\s+->\s+(.+)$", raw)
    if m:
        return {"rule": m.group(1).lower(), "file": m.group(2), "line": int(m.group(3)),
                "bad": m.group(4), "fix": m.group(5).strip()}
    m = re.match(r"^\[(\w+)\]\s+([^:]+):(\d+)\s+--\s+(.+)$", raw)
    if m:
        return {"rule": m.group(1).lower(), "file": m.group(2), "line": int(m.group(3)),
                "message": m.group(4).strip()}
    m = re.match(r"^\[(\w+)\]\s+(.+)$", raw, re.DOTALL)
    if m:
        return {"rule": m.group(1).lower(), "message": m.group(2).strip()}
    return {"raw": raw}


def _normalize_report_path(path: str) -> str:
    return path.replace("\\", "/")


def _warning_message(parsed: dict) -> str:
    if "message" in parsed:
        return str(parsed["message"])
    if "raw" in parsed:
        return str(parsed["raw"])
    return json.dumps(parsed, ensure_ascii=False, sort_keys=True)


def _warning_matches_baseline(parsed: dict, baseline: list[dict]) -> bool:
    rule = str(parsed.get("rule", ""))
    file_name = _normalize_report_path(str(parsed.get("file", "")))
    message = _warning_message(parsed)
    for entry in baseline:
        if str(entry.get("rule", "")) != rule:
            continue
        entry_file = _normalize_report_path(str(entry.get("file", "")))
        if entry_file and entry_file != file_name:
            continue
        expected_message = entry.get("message")
        if expected_message is not None and str(expected_message) != message:
            continue
        expected_contains = entry.get("message_contains")
        if expected_contains is not None and str(expected_contains) not in message:
            continue
        return True
    return False


def split_warning_baseline(raw_warnings: list[str], baseline: list[dict]) -> tuple[list[dict], list[dict]]:
    baselined: list[dict] = []
    new_warnings: list[dict] = []
    for raw in raw_warnings:
        parsed = _parse_issue_structured(raw)
        parsed["baselined"] = _warning_matches_baseline(parsed, baseline)
        if parsed["baselined"]:
            baselined.append(parsed)
        else:
            new_warnings.append(parsed)
    return baselined, new_warnings


# =============================================================================
# MAIN
# =============================================================================

def main():
    anti_patterns = load_yaml(KNOWLEDGE_DIR / "anti_patterns.yaml") or []
    lint_patterns = compile_anti_patterns(anti_patterns)
    enum_data = load_yaml(KNOWLEDGE_DIR / "valid_enums.yaml") or {}
    modifier_whitelist = load_modifier_whitelist()
    hardcoded_on_actions = load_hardcoded_on_actions()
    warning_baseline = load_warning_baseline()

    use_changed = "--changed" in sys.argv
    ai_report = "--ai-report" in sys.argv
    use_fix = "--fix" in sys.argv
    targets = [a for a in sys.argv[1:] if not a.startswith("-")]
    fixed: list[str] = []

    if use_changed:
        files = get_changed_files()
        if not files:
            if ai_report:
                print(json.dumps({"pass": True, "errors": [], "warnings": [], "files_checked": 0}))
            else:
                print("[OK] No changed mod files to validate.")
            sys.exit(0)
    elif targets:
        files = []
        for t in targets:
            files.extend(collect_files(REPO_ROOT / t))
    else:
        files = collect_files(REPO_ROOT / "src")

    if files:
        for path in files:
            try:
                raw = path.read_bytes()
            except OSError as e:
                issues.append(f"[ENCODING] Cannot read {path.relative_to(REPO_ROOT)}: {e}")
                continue

            if not raw.startswith(UTF8_BOM) and path.is_relative_to(REPO_ROOT / "src"):
                if use_fix:
                    path.write_bytes(UTF8_BOM + raw)
                    fixed.append(str(path.relative_to(REPO_ROOT)))
                else:
                    issues.append(
                        f"[ENCODING] {path.relative_to(REPO_ROOT)} -- missing UTF-8 BOM "
                        f"(EU5 will warn on load; save as UTF-8 with BOM)"
                    )

            try:
                content = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                issues.append(f"[ENCODING] Cannot decode as UTF-8: {path.relative_to(REPO_ROOT)}")
                continue

            if KNOWLEDGE_DIR in path.parents:
                continue

            check_event_id_numeric_range(path, content)
            check_event_option_effect_blocks(path, content)

            is_game_content = (
                path.is_relative_to(REPO_ROOT / "src")
                or path.is_relative_to(REPO_ROOT / "data")
            )
            if is_game_content:
                check_anti_patterns(path, content, lint_patterns)
                check_gui_parentanchor_under_hbox_vbox(path, content)
                check_wonder_engine_scaled_fixed_modifiers(path, content)
                check_generic_action_pre_eval_risks(path, content)
                check_io_policy_ai_scope_recipient_guard(path, content)
                check_on_action_singleton_effect_delegate(path, content, hardcoded_on_actions)
                check_enums(path, content, enum_data)
                check_modifier_names(path, content, modifier_whitelist)

        run_global_checks(files, use_changed, anti_patterns)

    if ai_report:
        def _is_autogen_warning(i: str) -> bool:
            return "[AUTOGEN]" in i or "[AUTOGEN_HEADER]" in i
        errors = [_parse_issue_structured(i) for i in issues if not _is_autogen_warning(i)]
        report_warnings = [_parse_issue_structured(i) for i in issues if _is_autogen_warning(i)]
        baselined_warnings, new_warnings = split_warning_baseline(warnings, warning_baseline)
        report_warnings.extend(baselined_warnings)
        for warning in new_warnings:
            errors.append({
                "rule": "new_warning",
                "message": "Warning is not listed in data/validation_baseline.yaml; fix it or explicitly add a baseline entry with rationale.",
                "warning": warning,
            })
            report_warnings.append(warning)
        print(json.dumps({
            "pass": len(errors) == 0,
            "errors": errors,
            "warnings": report_warnings,
            "files_checked": len(files) if files else 0,
        }, ensure_ascii=False, indent=2))
        sys.exit(0 if len(errors) == 0 else 1)

    if fixed:
        for f in fixed:
            print(f"[FIXED] Added UTF-8 BOM: {f}")

    baselined_warnings, new_warnings = split_warning_baseline(warnings, warning_baseline)
    if warnings:
        print(f"[WARN] {len(warnings)} warning(s):\n")
        for warning in baselined_warnings:
            print(f"  [BASELINE] {_warning_message(warning)}")
        for warning in new_warnings:
            print(f"  [NEW] {_warning_message(warning)}")
        print("")

    if issues or new_warnings:
        fail_count = len(issues) + len(new_warnings)
        print(f"[FAIL] {fail_count} issue(s) found:\n")
        for issue in issues:
            print(f"  {issue}")
        for warning in new_warnings:
            file_part = f"{warning.get('file')}:{warning.get('line')} -- " if warning.get("file") else ""
            print(
                "  [NEW_WARNING] "
                + file_part
                + _warning_message(warning)
                + " (fix it or add a baseline entry with rationale)"
            )
        sys.exit(1)
    else:
        if files:
            n = len(files)
            suffix = f", {len(fixed)} BOM(s) fixed" if fixed else ""
            warning_suffix = f", {len(warnings)} warning(s)" if warnings else ""
            print(f"[OK] Validated {n} file(s) -- no issues found{suffix}{warning_suffix}.")
        sys.exit(0)


if __name__ == "__main__":
    main()
