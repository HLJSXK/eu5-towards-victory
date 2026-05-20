#!/usr/bin/env python3
"""
Build a compact task context for AI coding tools.

Usage:
  python scripts/ai_context.py --changed
  python scripts/ai_context.py --files src/in_game/common/generic_actions/foo.txt
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

DOMAIN_RULES = [
    ("generic_actions", "src/in_game/common/generic_actions/", "generic_actions.md"),
    ("gui", "src/in_game/gui/", None),
    ("international_organizations", "src/in_game/common/international_organizations/", None),
    ("events", "src/in_game/events/", None),
    ("on_action", "src/in_game/common/on_action/", None),
]


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
        if path.endswith(".gui"):
            domains.add("gui")
    return domains


def relevant_rules(files: list[str], domains: set[str], limit: int = 12) -> list[dict]:
    patterns = load_yaml(KNOWLEDGE_DIR / "anti_patterns.yaml") or []
    normalized = [f.replace("\\", "/") for f in files]
    picked: list[dict] = []
    for entry in patterns:
        only_in = entry.get("only_in_paths", [])
        category = entry.get("category", "")
        matched_path = bool(only_in) and any(
            any(part in path for part in only_in) for path in normalized
        )
        matched_domain = category in domains or entry.get("scope") in domains
        if matched_path or matched_domain:
            picked.append(entry)
        if len(picked) >= limit:
            break
    return picked


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
    for domain, _prefix, card in DOMAIN_RULES:
        if domain in domains and card:
            print(f"- `docs/knowledge/risk_cards/{card}`")
    print("- `CLAUDE.md`")
    print("- `docs/knowledge/BRIEF.md` for broad project context")
    print("")

    for domain, _prefix, card in DOMAIN_RULES:
        if domain in domains and card:
            print_card(card)

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

    print("## Suggested Validation")
    print("```powershell")
    print("conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix --ai-report")
    print("```")


if __name__ == "__main__":
    main()
