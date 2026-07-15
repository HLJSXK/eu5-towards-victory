#!/usr/bin/env python3
r"""
Build a compact task context for AI coding tools.

Usage:
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --changed
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --files src/in_game/common/generic_actions/foo.txt
"""

import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml")
    raise SystemExit(1)

REPO_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "knowledge"
RISK_CARDS_DIR = KNOWLEDGE_DIR / "risk_cards"
GENERATED_REGISTRY = REPO_ROOT / "data" / "generated_files.yaml"
MANAGED_SANDBOX_PYTHON = r"C:\Users\Hades\anaconda3\envs\eu5\python.exe"

# Two deployable mod roots: the main "Towards Victory" mod and the split-out,
# standalone "Engineering Department" mod. Path-prefix domain routing below
# is expanded across both so a moved file keeps matching its generic domain
# card (e.g. "gui.md") in addition to whatever FILENAME_DOMAIN_RULES match.
MOD_ROOT_NAMES = ("src", "src_engineering_department")


def _mod_prefixes(subpath: str) -> tuple[str, ...]:
    return tuple(f"{root_name}/{subpath}" for root_name in MOD_ROOT_NAMES)


DOMAIN_RULES = [
    ("generic_actions", _mod_prefixes("in_game/common/generic_actions/"), "generic_actions.md"),
    ("gui", _mod_prefixes("in_game/gui/"), "gui.md"),
    ("international_organizations", _mod_prefixes("in_game/common/international_organizations/"), "international_organizations.md"),
    ("international_organizations", _mod_prefixes("in_game/common/laws/"), "international_organizations.md"),
    ("international_organizations", _mod_prefixes("in_game/common/country_interactions/"), "international_organizations.md"),
    ("events", _mod_prefixes("in_game/events/"), "events.md"),
    ("on_action", _mod_prefixes("in_game/common/on_action/"), "on_action.md"),
    ("localization", _mod_prefixes("main_menu/localization/"), "localization.md"),
]

# Some task domains are not isolated in their own directory: their files are
# interspersed by filename across common/scripted_effects, static_modifiers,
# building_types, generic_actions, gui, and localization. Route those by
# filename substring instead of path prefix.
FILENAME_DOMAIN_RULES = [
    ("wonders", ("wonder", "engineering_department"), "wonders.md"),
    ("philosophy_debate", ("philosophy_debate", "world_debate", "academy_debate"), "philosophy_debate.md"),
    ("trade_league", ("trade_league", "trade_chain"), "trade_league.md"),
    ("europedia", ("encyclopedia_lateralview",), "europedia.md"),
]


def domain_cards() -> list[tuple[str, str]]:
    pairs = [(domain, card) for domain, _prefix, card in DOMAIN_RULES]
    pairs += [(domain, card) for domain, _substrings, card in FILENAME_DOMAIN_RULES]
    return pairs

CONTENT_DOMAIN_MARKERS = {
    "variable_map": (
        "variable_map(",
        "global_variable_map(",
        "local_variable_map(",
        "add_to_variable_map",
        "add_to_global_variable_map",
        "add_to_local_variable_map",
        "is_key_in_variable_map",
        "is_key_in_global_variable_map",
        "random_key_in_variable_map",
    ),
}


def _git_names(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files() -> list[str]:
    names: set[str] = set()
    for args in [
        ["diff", "--name-only", "HEAD"],
        ["diff", "--name-only", "--cached"],
        ["ls-files", "--others", "--exclude-standard"],
    ]:
        names.update(_git_names(args))
    return sorted(names)


def load_yaml(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def generated_map() -> dict[str, dict]:
    registry = load_yaml(GENERATED_REGISTRY) or {}
    mapping: dict[str, dict] = {}
    for entry in registry.get("generated", []):
        output = entry.get("output")
        if output:
            mapping[output.replace("\\", "/")] = entry
    return mapping


def detect_domains(files: list[str]) -> set[str]:
    domains: set[str] = set()
    normalized = [f.replace("\\", "/") for f in files]
    for path in normalized:
        for domain, prefix, _card in DOMAIN_RULES:
            if path.startswith(prefix):
                domains.add(domain)
        name = Path(path).name.lower()
        for domain, substrings, _card in FILENAME_DOMAIN_RULES:
            if any(substring in name for substring in substrings):
                domains.add(domain)
        if path.endswith(".gui"):
            domains.add("gui")
        full_path = REPO_ROOT / path
        if full_path.exists() and full_path.is_file():
            try:
                with full_path.open(encoding="utf-8", errors="replace") as f:
                    for line in f:
                        for domain, markers in CONTENT_DOMAIN_MARKERS.items():
                            if any(marker in line for marker in markers):
                                domains.add(domain)
                        if domains.issuperset(CONTENT_DOMAIN_MARKERS):
                            break
            except OSError:
                pass
    return domains


def relevant_rules(files: list[str], domains: set[str], limit: int = 12) -> list[dict]:
    patterns = load_yaml(KNOWLEDGE_DIR / "anti_patterns.yaml") or []
    normalized = [f.replace("\\", "/") for f in files]
    domain_matches: list[dict] = []
    path_matches: list[dict] = []
    for entry in patterns:
        only_in = entry.get("only_in_paths", [])
        category = entry.get("category", "")
        matched_path = bool(only_in) and any(
            any(part in path for part in only_in) for path in normalized
        )
        matched_domain = category in domains or entry.get("scope") in domains
        if matched_domain:
            domain_matches.append(entry)
        elif matched_path:
            path_matches.append(entry)
    return [*domain_matches, *path_matches][:limit]


def maintenance_notes(files: list[str]) -> list[str]:
    notes: list[str] = []
    file_set = set(files)
    touches_knowledge = any(
        path.startswith("docs/knowledge/")
        or path in {"CLAUDE.md", "docs/guides/AI_Tool_Workflow_Prompt.md"}
        for path in files
    )
    if touches_knowledge:
        notes.append(
            f"After changing knowledge/workflow docs in a managed sandbox, run `{MANAGED_SANDBOX_PYTHON} scripts\\gen_brief.py`."
        )
    if "docs/knowledge/anti_patterns.yaml" in file_set:
        notes.append(
            "For each new anti-pattern, set `detectability` to `lint`, `needs_parser`, or `advisory`; use `lint` only for narrow, tested static checks."
        )
        notes.append(
            "For new or changed `detectability: lint` rules, add/update fixtures under `tests/fixtures/anti_patterns/<rule_id>/` and run `scripts/test_lint_rules.py`."
        )
        notes.append(
            "If a new anti-pattern belongs to an existing task domain, update that domain risk card in `docs/knowledge/risk_cards/`."
        )
    if "data/validation_baseline.yaml" in file_set:
        notes.append(
            "Validation baseline changed; ensure every accepted warning has a rationale and that new warnings were not baselined instead of fixed."
        )
    if any(path.startswith("docs/knowledge/risk_cards/") for path in files):
        notes.append(
            "If a risk card covers a new task domain, register it in `DOMAIN_RULES` inside `scripts/ai_context.py`."
        )
        notes.append(
            "Keep risk cards short and operational: required checks, safe skeletons, and validation commands rather than full history."
        )
    if "scripts/ai_context.py" in file_set:
        notes.append(
            "If `ai_context.py` behavior or domain coverage changes, update `CLAUDE.md`, `AI_Tool_Workflow_Prompt.md`, and the script table in `PROJECT_OVERVIEW.md`."
        )
    if "scripts/validate.py" in file_set:
        notes.append(
            "If `validate.py` implements a parser/check for a `needs_parser` anti-pattern, update that anti-pattern's `detectability` when it becomes a reliable lint."
        )
    if "docs/knowledge/PROJECT_OVERVIEW.md" in file_set:
        notes.append(
            "`PROJECT_OVERVIEW.md` changed; regenerate `docs/knowledge/BRIEF.md` before finishing."
        )
    return notes


def print_card(card_name: str) -> None:
    card = RISK_CARDS_DIR / card_name
    if not card.exists():
        return
    print(f"## Risk Card: {card_name}")
    print("")
    print(card.read_text(encoding="utf-8").strip())
    print("")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed", action="store_true", help="Use git changed files")
    parser.add_argument("--files", nargs="*", default=[], help="Explicit files")
    args = parser.parse_args()

    files = changed_files() if args.changed else args.files
    files = sorted({f.replace("\\", "/") for f in files if f})
    gen = generated_map()
    domains = detect_domains(files)

    print("# AI Task Context")
    print("")
    if not files:
        print("No files detected. Pass --changed or --files.")
        return

    print("## Files")
    for path in files:
        marker = ""
        if path in gen:
            marker = f" [generated: edit {gen[path].get('data', gen[path].get('script', 'source'))}]"
        print(f"- `{path}`{marker}")
    print("")

    print("## Domains")
    if domains:
        for domain in sorted(domains):
            print(f"- `{domain}`")
    else:
        print("- none detected")
    print("")

    print("## Required Reads")
    printed_cards: set[str] = set()
    for domain, card in domain_cards():
        if domain in domains and card and card not in printed_cards:
            print(f"- `docs/knowledge/risk_cards/{card}`")
            printed_cards.add(card)
    if "variable_map" in domains:
        print("- `docs/technical/EU5_Modding_Knowledge_Base.md` section 5.2 `Variable maps`")
        print("- `docs/knowledge/anti_patterns.yaml` rule `variable_map_scope_link_used_direct_rhs`")
    print("- `CLAUDE.md`")
    print("- `docs/knowledge/BRIEF.md` for broad project context")
    print("")

    printed_cards = set()
    for domain, card in domain_cards():
        if domain in domains and card and card not in printed_cards:
            print_card(card)
            printed_cards.add(card)

    rules = relevant_rules(files, domains)
    if rules:
        print("## Relevant Anti-Patterns")
        for entry in rules:
            detectability = entry.get("detectability") or (
                "lint" if entry.get("pattern") else "advisory"
            )
            print(
                f"- `{entry.get('id')}` [{detectability}]: "
                f"{entry.get('bad')} -> {entry.get('correction')}"
            )
        print("")

    notes = maintenance_notes(files)
    if notes:
        print("## Knowledge Maintenance")
        for note in notes:
            print(f"- {note}")
        print("")

    print("## Suggested Validation")
    print("```powershell")
    print("# Managed sandbox default; do not use conda run here.")
    print(f"{MANAGED_SANDBOX_PYTHON} scripts\\validate.py --changed --fix --ai-report")
    print(f"{MANAGED_SANDBOX_PYTHON} scripts\\test_lint_rules.py")
    print("```")


if __name__ == "__main__":
    main()
