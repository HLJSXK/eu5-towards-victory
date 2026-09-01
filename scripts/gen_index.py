#!/usr/bin/env python3
"""
Build fast-lookup symbol and localization indexes for AI coding sessions.

Scans reference and source files and writes indexes to data/index/:
  icons.txt                  — all @icon_name! entries from font_icons.gui
  scripted_triggers.txt      — all scripted_trigger names (vanilla + mod)
  scripted_effects.txt       — all scripted_effect names (vanilla + mod)
  static_modifiers.txt       — all modifier names from modifier type definitions
  modifier_localization.json — EN/ZH modifier labels, descriptions, and value metadata
  trigger_localization.json  — EN/ZH trigger text variants
  loc_keys_en.txt            — all English localization keys in src/

Usage:
  conda run -n eu5 python scripts/gen_index.py
  conda run -n eu5 python scripts/gen_index.py --verbose

Called automatically by gen_brief.py before generating BRIEF.md.
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = REPO_ROOT / "data" / "index"

# Four deployable mod roots feed these indexes: the main "Towards Victory"
# mod and the standalone Engineering Department, Court Positions, and Eureka mods.
MOD_ROOTS = [REPO_ROOT / "src", REPO_ROOT / "src_engineering_department", REPO_ROOT / "src_court_positions", REPO_ROOT / "src_eureka"]

FONT_ICONS_FILE = (
    REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "gui" / "shared" / "font_icons.gui"
)
MODIFIER_TYPES_FILE = (
    REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "common"
    / "modifier_type_definitions" / "00_modifier_types.txt"
)
MODIFIER_TYPE_FILES = [
    MODIFIER_TYPES_FILE,
    *(
        f
        for mod_dir in (root / "main_menu" / "common" / "modifier_type_definitions" for root in MOD_ROOTS)
        if mod_dir.exists()
        for f in mod_dir.glob("*.txt")
    ),
]
REFERENCE_LOC_DIRS = {
    "en": REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "localization" / "english",
    "zh": REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "localization" / "simp_chinese",
}
MOD_LOC_DIRS = {
    "en": [root / "main_menu" / "localization" / "english" for root in MOD_ROOTS],
    "zh": [root / "main_menu" / "localization" / "simp_chinese" for root in MOD_ROOTS],
}
VANILLA_TRIGGERS_DIR = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "common" / "scripted_triggers"
VANILLA_EFFECTS_DIR  = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "common" / "scripted_effects"
MOD_TRIGGERS_DIRS = [root / "in_game" / "common" / "scripted_triggers" for root in MOD_ROOTS]
MOD_EFFECTS_DIRS = [root / "in_game" / "common" / "scripted_effects" for root in MOD_ROOTS]
LOC_EN_DIRS = [root / "main_menu" / "localization" / "english" for root in MOD_ROOTS]


def _write_index(path: Path, entries: list[str], verbose: bool, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(set(entries))) + "\n", encoding="utf-8")
    if verbose:
        print(f"[index] {path.relative_to(REPO_ROOT)}: {len(set(entries))} entries")


def _write_json_index(path: Path, payload: dict, verbose: bool, label: str, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if verbose:
        print(f"[index] {path.relative_to(REPO_ROOT)}: {count} entries")


def _localization_files_for_language(language: str) -> list[Path]:
    files: list[Path] = []
    loc_dirs = [REFERENCE_LOC_DIRS.get(language), *MOD_LOC_DIRS.get(language, [])]
    for loc_dir in loc_dirs:
        if loc_dir and loc_dir.exists():
            files.extend(sorted(loc_dir.rglob("*.yml")))
    return files


LOC_LINE_RE = re.compile(r'^\s*([A-Za-z0-9_.-]+):(?:\d+)?\s+"(.*)"\s*$')


def _parse_localization_file(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return entries
    for line in lines:
        match = LOC_LINE_RE.match(line)
        if not match:
            continue
        entries[match.group(1)] = match.group(2).replace(r"\"", '"').replace(r"\n", "\n")
    return entries


def _resolve_loc_references(entries: dict[str, str]) -> dict[str, str]:
    ref_re = re.compile(r"\$([A-Za-z0-9_.-]+)\$")
    resolved_cache: dict[str, str] = {}

    def resolve_key(key: str, stack: tuple[str, ...] = ()) -> str:
        if key in resolved_cache:
            return resolved_cache[key]
        value = entries.get(key, "")
        if key in stack:
            return value

        def replace(match: re.Match[str]) -> str:
            ref_key = match.group(1)
            if ref_key not in entries:
                return match.group(0)
            return resolve_key(ref_key, (*stack, key))

        resolved = ref_re.sub(replace, value)
        resolved_cache[key] = resolved
        return resolved

    return {key: resolve_key(key) for key in entries}


def _load_localization_entries(language: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for path in _localization_files_for_language(language):
        entries.update(_parse_localization_file(path))
    return _resolve_loc_references(entries)


def build_icons_index(verbose: bool) -> None:
    """Extract all @icon_name! names from font_icons.gui."""
    if not FONT_ICONS_FILE.exists():
        print(f"[WARN] font_icons.gui not found: {FONT_ICONS_FILE}")
        return
    text = FONT_ICONS_FILE.read_text(encoding="utf-8-sig")
    # texticon blocks use `icon = <name>` at depth 1
    icon_pat = re.compile(r"^\s+icon\s*=\s*(\w+)", re.MULTILINE)
    names = [f"@{m.group(1)}!" for m in icon_pat.finditer(text)]
    _write_index(INDEX_DIR / "icons.txt", names, verbose, "GUI icons")


def _extract_top_level_names(txt_files: list[Path]) -> list[str]:
    """Extract top-level `name = {` block definitions from a list of .txt files."""
    names = []
    # Top-level block: starts at column 0, word chars, `=`, `{`; not a comment
    top_pat = re.compile(r"^([a-zA-Z_]\w*)\s*=\s*\{", re.MULTILINE)
    for path in txt_files:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        for m in top_pat.finditer(text):
            # Skip known structural keys that are not definitions
            name = m.group(1)
            if name not in {"category", "color", "method", "ai", "potential", "on_valid"}:
                names.append(name)
    return names


def build_scripted_triggers_index(verbose: bool) -> None:
    dirs = [VANILLA_TRIGGERS_DIR] + MOD_TRIGGERS_DIRS
    files = []
    for d in dirs:
        if d.exists():
            files.extend(d.glob("*.txt"))
    names = _extract_top_level_names(files)
    _write_index(INDEX_DIR / "scripted_triggers.txt", names, verbose, "scripted triggers")


def build_scripted_effects_index(verbose: bool) -> None:
    dirs = [VANILLA_EFFECTS_DIR] + MOD_EFFECTS_DIRS
    files = []
    for d in dirs:
        if d.exists():
            files.extend(d.glob("*.txt"))
    names = _extract_top_level_names(files)
    _write_index(INDEX_DIR / "scripted_effects.txt", names, verbose, "scripted effects")


def build_static_modifiers_index(verbose: bool) -> None:
    """Extract modifier names from 00_modifier_types.txt (same source as validate.py whitelist)."""
    whitelist = []
    for path in MODIFIER_TYPE_FILES:
        whitelist.extend(_extract_top_level_blocks(path))
    _write_index(INDEX_DIR / "static_modifiers.txt", whitelist, verbose, "static modifiers")


def _extract_top_level_blocks(path: Path) -> dict[str, str]:
    blocks: dict[str, str] = {}
    if not path.exists():
        return blocks
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return blocks
    current_name: str | None = None
    current_lines: list[str] = []
    depth = 0
    start_re = re.compile(r"^(\w+)\s*=\s*\{")
    for line in lines:
        if current_name is None:
            match = start_re.match(line.strip())
            if not match:
                continue
            current_name = match.group(1)
            current_lines = [line]
            depth = line.count("{") - line.count("}")
            if depth <= 0:
                blocks[current_name] = "\n".join(current_lines)
                current_name = None
            continue
        current_lines.append(line)
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            blocks[current_name] = "\n".join(current_lines)
            current_name = None
    return blocks


def _modifier_definition_metadata() -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    for path in MODIFIER_TYPE_FILES:
        for name, block in _extract_top_level_blocks(path).items():
            def bool_prop(prop: str) -> bool:
                return bool(re.search(rf"\b{re.escape(prop)}\s*=\s*yes\b", block))

            decimals_match = re.search(r"\bdecimals\s*=\s*(-?\d+)\b", block)
            category_match = re.search(r"\bcategory\s*=\s*([A-Za-z0-9_]+)", block)
            color_match = re.search(r"\bcolor\s*=\s*([A-Za-z0-9_]+)", block)
            if bool_prop("boolean"):
                value_kind = "boolean"
            elif bool_prop("already_percent"):
                value_kind = "already_percent"
            elif bool_prop("percent"):
                value_kind = "percent"
            else:
                value_kind = "number"
            metadata[name] = {
                "value_kind": value_kind,
                "decimals": int(decimals_match.group(1)) if decimals_match else 2,
                "category": category_match.group(1) if category_match else "all",
                "color": color_match.group(1) if color_match else "good",
            }
    return metadata


def build_modifier_localization_index(verbose: bool) -> None:
    entries_by_language = {
        language: _load_localization_entries(language)
        for language in ("en", "zh")
    }
    metadata = _modifier_definition_metadata()
    modifiers: dict[str, dict[str, object]] = {}
    for modifier in sorted(metadata):
        record: dict[str, object] = dict(metadata[modifier])
        for language, entries in entries_by_language.items():
            record[language] = {
                "name": entries.get(f"MODIFIER_TYPE_NAME_{modifier}", ""),
                "description": entries.get(f"MODIFIER_TYPE_DESC_{modifier}", ""),
            }
        modifiers[modifier] = record
    payload = {
        "version": 1,
        "languages": ["en", "zh"],
        "modifiers": modifiers,
    }
    _write_json_index(
        INDEX_DIR / "modifier_localization.json",
        payload,
        verbose,
        "modifier localization",
        len(modifiers),
    )


def _trigger_loc_key_to_index_key(loc_key: str) -> tuple[str, str] | None:
    key = loc_key
    variant = "text"
    prefix_variants = (
        ("NOT_THIRD_", "not_third"),
        ("THIRD_NOT_", "not_third"),
        ("NOT_FIRST_", "not_first"),
        ("FIRST_", "first"),
        ("THIRD_", "third"),
        ("NOT_", "not"),
    )
    upper = key.upper()
    for prefix, candidate_variant in prefix_variants:
        if upper.startswith(prefix):
            key = key[len(prefix):]
            variant = candidate_variant
            break
    if key.upper().endswith("_TRIGGER"):
        key = key[:-8]
    if not key:
        return None
    if variant == "text" and not (
        loc_key.upper().endswith("_TRIGGER")
        or "_equal" in loc_key
        or loc_key in {"always", "or", "calc_true_if", "weighted_calc_true_if"}
    ):
        return None
    return key.lower(), variant


def _trigger_source_files(language: str) -> list[Path]:
    files: list[Path] = []
    loc_dirs = [REFERENCE_LOC_DIRS.get(language), *MOD_LOC_DIRS.get(language, [])]
    for loc_dir in loc_dirs:
        if not loc_dir or not loc_dir.exists():
            continue
        files.extend(sorted(loc_dir.rglob("triggers_l_*.yml")))
        files.extend(sorted(loc_dir.rglob("scripted_triggers_l_*.yml")))
    return files


def build_trigger_localization_index(verbose: bool) -> None:
    triggers: dict[str, dict[str, dict[str, str]]] = {}
    for language in ("en", "zh"):
        all_entries = _load_localization_entries(language)
        source_keys: set[str] = set()
        for path in _trigger_source_files(language):
            source_keys.update(_parse_localization_file(path))
        for loc_key in sorted(source_keys):
            normalized = _trigger_loc_key_to_index_key(loc_key)
            if normalized is None:
                continue
            trigger_key, variant = normalized
            triggers.setdefault(trigger_key, {}).setdefault(language, {})[variant] = all_entries.get(loc_key, "")

    payload = {
        "version": 1,
        "languages": ["en", "zh"],
        "triggers": {
            key: {
                language: variants
                for language, variants in sorted(language_payload.items())
            }
            for key, language_payload in sorted(triggers.items())
        },
    }
    _write_json_index(
        INDEX_DIR / "trigger_localization.json",
        payload,
        verbose,
        "trigger localization",
        len(triggers),
    )


def build_loc_keys_en_index(verbose: bool) -> None:
    """Extract all English localization key names from src/."""
    key_pat = re.compile(r"^\s+(\w+)\s*:", re.MULTILINE)
    keys = []
    for loc_dir in LOC_EN_DIRS:
        if not loc_dir.exists():
            continue
        for yml in loc_dir.glob("*_l_english.yml"):
            try:
                text = yml.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                continue
            for m in key_pat.finditer(text):
                keys.append(m.group(1))
    _write_index(INDEX_DIR / "loc_keys_en.txt", keys, verbose, "English loc keys")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", "-v", action="store_true", help="Print entry counts per index")
    args = ap.parse_args()

    build_icons_index(args.verbose)
    build_scripted_triggers_index(args.verbose)
    build_scripted_effects_index(args.verbose)
    build_static_modifiers_index(args.verbose)
    build_modifier_localization_index(args.verbose)
    build_trigger_localization_index(args.verbose)
    build_loc_keys_en_index(args.verbose)

    if not args.verbose:
        counts = {f.name: sum(1 for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip())
                  for f in sorted(INDEX_DIR.glob("*.txt")) if f.exists()}
        summary = ", ".join(f"{n}: {c}" for n, c in counts.items())
        print(f"[OK] Indexes written to {INDEX_DIR.relative_to(REPO_ROOT)}/ — {summary}")


if __name__ == "__main__":
    main()
