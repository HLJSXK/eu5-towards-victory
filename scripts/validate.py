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
VALIDATED_SUFFIXES = {".txt", ".gui", ".yml", ".yaml", ".md", ".py"}

issues = []
warnings = []


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


def check_anti_patterns(path: Path, content: str, patterns: list[dict]):
    path_str = str(path).replace("\\", "/")
    for entry in patterns:
        regex = entry.get("pattern", "")
        detectability = entry.get("detectability")
        if detectability is None:
            detectability = "lint" if regex else "advisory"
        if detectability != "lint":
            continue
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
        except re.error as exc:
            warnings.append(
                f"[LINT_RULE] {entry.get('id', '<unknown>')} -- invalid regex skipped: {exc}"
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


def check_vanilla_copy_integrity() -> None:
    """Ensure generated vanilla-copy files preserve copied vanilla content."""
    pulse_files = {
        "src/in_game/common/on_action/country_monthly.txt":
            "reference_game_files/game/in_game/common/on_action/country_monthly.txt",
        "src/in_game/common/on_action/country_yearly.txt":
            "reference_game_files/game/in_game/common/on_action/country_yearly.txt",
        "src/in_game/common/on_action/character_death_pulses.txt":
            "reference_game_files/game/in_game/common/on_action/character_death_pulses.txt",
    }
    tv_pulse_block = re.compile(
        r"\n?\t\t# Towards Victory additions\n(?:\t\ttv_[^\n]+\n)+"
    )
    for out_rel, vanilla_rel in pulse_files.items():
        out_path = REPO_ROOT / out_rel
        vanilla_path = REPO_ROOT / vanilla_rel
        if not out_path.exists() or not vanilla_path.exists():
            continue
        copied = _strip_generated_header(_read_normalized_text(out_path))
        copied_without_tv = tv_pulse_block.sub("\n", copied, count=1)
        vanilla = _read_normalized_text(vanilla_path)
        if not _same_ignoring_final_newline(copied_without_tv, vanilla):
            issues.append(
                f"[VANILLA_COPY] {out_rel} -- copied vanilla content differs from "
                f"{vanilla_rel}; only the TV additions block may differ"
            )

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
        if (entry.get("detectability") == "lint") and not entry.get("pattern"):
            warnings.append(
                f"[KNOWLEDGE] anti_patterns.yaml:{entry.get('id', '<unknown>')} -- "
                "detectability is lint but pattern is empty"
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
    for card_name in domain_rule_cards:
        card = risk_cards_dir / card_name
        if not card.exists():
            warnings.append(
                f"[KNOWLEDGE] scripts/ai_context.py -- DOMAIN_RULES references missing risk card {card_name}"
            )


def _line_num(content: str, pos: int) -> int:
    return content[:pos].count("\n") + 1


def _find_matching_brace(content: str, open_pos: int) -> int | None:
    """Return the matching } for content[open_pos] == {, ignoring strings/comments."""
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
                return i
    return None


def _iter_top_level_blocks(content: str):
    for match in re.finditer(r"(?m)^([A-Za-z]\w*)\s*=\s*\{", content):
        open_pos = content.find("{", match.start())
        close_pos = _find_matching_brace(content, open_pos)
        if close_pos is None:
            continue
        yield match.group(1), open_pos, close_pos


def _iter_named_blocks(content: str, start: int, end: int, name: str):
    body = content[start + 1:end]
    for match in re.finditer(rf"(?m)^[ \t]*{re.escape(name)}\s*=\s*\{{", body):
        open_pos = content.find("{", start + 1 + match.start())
        close_pos = _find_matching_brace(content, open_pos)
        if close_pos is None or close_pos > end:
            continue
        yield open_pos, close_pos


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

            is_game_content = (
                path.is_relative_to(REPO_ROOT / "src")
                or path.is_relative_to(REPO_ROOT / "data")
            )
            if is_game_content:
                check_anti_patterns(path, content, anti_patterns)
                check_generic_action_pre_eval_risks(path, content)
                check_enums(path, content, enum_data)
                check_modifier_names(path, content, modifier_whitelist)

        check_loc_coverage()
        check_trigger_loc_coverage()
        check_autogenerated_staged()
        check_generated_headers()
        check_vanilla_copy_integrity()
        check_knowledge_maintenance(anti_patterns)

    if ai_report:
        def _is_autogen_warning(i: str) -> bool:
            return "[AUTOGEN]" in i or "[AUTOGEN_HEADER]" in i
        errors = [_parse_issue_structured(i) for i in issues if not _is_autogen_warning(i)]
        report_warnings = [_parse_issue_structured(i) for i in issues if _is_autogen_warning(i)]
        report_warnings.extend(_parse_issue_structured(i) for i in warnings)
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

    if warnings:
        print(f"[WARN] {len(warnings)} warning(s):\n")
        for warning in warnings:
            print(f"  {warning}")
        print("")

    if issues:
        print(f"[FAIL] {len(issues)} issue(s) found:\n")
        for issue in issues:
            print(f"  {issue}")
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
