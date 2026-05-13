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

REPO_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "knowledge"
MODIFIER_TYPES_FILE = (
    REPO_ROOT
    / "reference_game_files"
    / "game"
    / "main_menu"
    / "common"
    / "modifier_type_definitions"
    / "00_modifier_types.txt"
)
UTF8_BOM = b"\xef\xbb\xbf"

issues = []


def load_yaml(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_modifier_whitelist() -> set[str]:
    if not MODIFIER_TYPES_FILE.exists():
        return set()
    whitelist = set()
    pattern = re.compile(r"^(\w+)\s*=\s*\{")
    with MODIFIER_TYPES_FILE.open(encoding="utf-8-sig") as f:
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
        if p.exists() and p.suffix in {".txt", ".gui", ".yml"}:
            paths.append(p)
    return paths


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return [
        p
        for p in target.rglob("*")
        if p.suffix in {".txt", ".gui", ".yml"} and p.is_file()
    ]


def check_anti_patterns(path: Path, content: str, patterns: list[dict]):
    path_str = str(path).replace("\\", "/")
    for entry in patterns:
        regex = entry.get("pattern", "")
        if not regex:
            continue
        only_in = entry.get("only_in_paths", [])
        if only_in and not any(sub in path_str for sub in only_in):
            continue
        try:
            for m in re.finditer(regex, content, re.MULTILINE | re.IGNORECASE):
                line_num = content[: m.start()].count("\n") + 1
                issues.append(
                    f"[{entry.get('category', 'pattern').upper()}] "
                    f"{path.relative_to(REPO_ROOT)}:{line_num} -- "
                    f"Bad: \"{entry['bad']}\" -> {entry['correction']}"
                )
        except re.error:
            pass


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


def check_loc_coverage() -> None:
    """Verify every key in English localization also exists in simp_chinese."""
    en_dir = REPO_ROOT / "src" / "main_menu" / "localization" / "english"
    zh_dir = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese"
    if not en_dir.exists():
        return
    key_pat = re.compile(r"^\s+(\w+)\s*:")
    for en_file in sorted(en_dir.glob("*_l_english.yml")):
        stem = en_file.stem[: -len("_l_english")]
        zh_file = zh_dir / f"{stem}_l_simp_chinese.yml"
        en_keys = {m.group(1) for line in en_file.read_text(encoding="utf-8-sig").splitlines() if (m := key_pat.match(line))}
        if not zh_file.exists():
            issues.append(f"[LOC] Missing simp_chinese file: {zh_file.relative_to(REPO_ROOT)}")
            continue
        zh_keys = {m.group(1) for line in zh_file.read_text(encoding="utf-8-sig").splitlines() if (m := key_pat.match(line))}
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
        if not p.exists() or p.suffix not in {".txt", ".gui", ".yml"}:
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


# =============================================================================
# MAIN
# =============================================================================

def main():
    anti_patterns = load_yaml(KNOWLEDGE_DIR / "anti_patterns.yaml") or []
    enum_data = load_yaml(KNOWLEDGE_DIR / "valid_enums.yaml") or {}
    modifier_whitelist = load_modifier_whitelist()

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

            check_anti_patterns(path, content, anti_patterns)
            check_enums(path, content, enum_data)
            check_modifier_names(path, content, modifier_whitelist)

        check_loc_coverage()
        check_trigger_loc_coverage()
        check_autogenerated_staged()
        check_generated_headers()

    if ai_report:
        def _is_autogen_warning(i: str) -> bool:
            return "[AUTOGEN]" in i or "[AUTOGEN_HEADER]" in i
        errors = [_parse_issue_structured(i) for i in issues if not _is_autogen_warning(i)]
        warnings = [_parse_issue_structured(i) for i in issues if _is_autogen_warning(i)]
        print(json.dumps({
            "pass": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(files) if files else 0,
        }, ensure_ascii=False, indent=2))
        sys.exit(0 if len(errors) == 0 else 1)

    if fixed:
        for f in fixed:
            print(f"[FIXED] Added UTF-8 BOM: {f}")

    if issues:
        print(f"[FAIL] {len(issues)} issue(s) found:\n")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        if files:
            n = len(files)
            suffix = f", {len(fixed)} BOM(s) fixed" if fixed else ""
            print(f"[OK] Validated {n} file(s) -- no issues found{suffix}.")
        sys.exit(0)


if __name__ == "__main__":
    main()
