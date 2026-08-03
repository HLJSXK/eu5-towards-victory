#!/usr/bin/env python3
r"""
Build task-scoped AI context without dumping every long-form knowledge file.

Usage:
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --changed
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --files src/in_game/common/generic_actions/foo.txt
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --full --files src_engineering_department/in_game/common/building_types/foo.txt
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --json --changed
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

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
ROUTES_FILE = KNOWLEDGE_DIR / "context_routes.yaml"
GENERATED_REGISTRY = REPO_ROOT / "data" / "generated_files.yaml"
MANAGED_SANDBOX_PYTHON = r"C:\Users\Hades\anaconda3\envs\eu5\python.exe"


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def generated_map() -> dict[str, dict[str, Any]]:
    registry = _load_yaml(GENERATED_REGISTRY) or {}
    mapping: dict[str, dict[str, Any]] = {}
    for entry in registry.get("generated", []):
        output = entry.get("output")
        if output:
            mapping[_norm(output)] = entry
    return mapping


def load_routes() -> dict[str, Any]:
    routes = _load_yaml(ROUTES_FILE)
    if not isinstance(routes, dict):
        raise SystemExit(f"[ERROR] Missing or invalid route config: {_rel(ROUTES_FILE)}")
    routes.setdefault("mod_roots", ["src", "src_engineering_department", "src_court_positions"])
    routes.setdefault("core_reads", [])
    routes.setdefault("domain_routes", [])
    routes.setdefault("filename_routes", [])
    routes.setdefault("content_routes", [])
    routes.setdefault("object_alerts", [])
    routes.setdefault("maintenance_routes", [])
    return routes


def _split_generated_sources(entry: dict[str, Any] | None) -> list[str]:
    if not entry:
        return []
    paths: list[str] = []
    script = entry.get("script")
    if script:
        paths.append(_norm(script))
    data = entry.get("data")
    if data:
        for part in str(data).split("+"):
            candidate = _norm(part).strip()
            if candidate and "*" not in candidate:
                paths.append(candidate)
    return paths


def route_paths(files: list[str], gen: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for path in files:
        normalized = _norm(path)
        paths = [normalized, *_split_generated_sources(gen.get(normalized))]
        result[normalized] = sorted(dict.fromkeys(paths))
    return result


def _expanded_prefixes(route: dict[str, Any], routes: dict[str, Any]) -> list[str]:
    prefixes = [_norm(p) for p in route.get("path_prefixes", []) or []]
    if route.get("expand_mod_roots"):
        expanded: list[str] = list(prefixes)
        for root_name in routes.get("mod_roots", []):
            root = _norm(root_name).rstrip("/")
            for prefix in prefixes:
                expanded.append(f"{root}/{prefix.lstrip('/')}")
        prefixes = expanded
    return prefixes


def _path_matches_route(path: str, route: dict[str, Any], routes: dict[str, Any]) -> bool:
    normalized = _norm(path)
    lower = normalized.lower()
    prefixes = _expanded_prefixes(route, routes)
    substrings = [str(s).lower() for s in route.get("filename_substrings", []) or []]
    suffixes = [str(s).lower() for s in route.get("file_suffixes", []) or []]
    path_ok = not prefixes or any(normalized.startswith(prefix) for prefix in prefixes)
    name_ok = not substrings or any(s in Path(normalized).name.lower() for s in substrings)
    suffix_ok = not suffixes or any(lower.endswith(s) for s in suffixes)
    return path_ok and name_ok and suffix_ok


def _content_excluded(path: str, route: dict[str, Any]) -> bool:
    normalized = _norm(path)
    excluded = [_norm(p) for p in route.get("excluded_prefixes", []) or []]
    exact = {_norm(p) for p in route.get("excluded_paths", []) or []}
    return normalized in exact or any(normalized.startswith(prefix) for prefix in excluded)


def _file_contains_marker(path: str, markers: tuple[str, ...]) -> bool:
    full_path = REPO_ROOT / path
    if not full_path.exists() or not full_path.is_file():
        return False
    try:
        with full_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if any(marker in line for marker in markers):
                    return True
    except OSError:
        return False
    return False


def _add_unique(items: list[dict[str, str]], item: dict[str, str], key: str) -> None:
    if item.get(key) and not any(existing.get(key) == item.get(key) for existing in items):
        items.append(item)


def build_context(files: list[str], routes: dict[str, Any]) -> dict[str, Any]:
    files = sorted({_norm(f) for f in files if f})
    gen = generated_map()
    routed_paths = route_paths(files, gen)

    domains: dict[str, dict[str, str]] = {}
    cards: list[dict[str, str]] = []
    reads: list[dict[str, str]] = []
    alerts: list[dict[str, str]] = []

    for entry in routes.get("core_reads", []):
        _add_unique(reads, {"path": entry["path"], "reason": entry.get("reason", "")}, "path")

    for original, paths in routed_paths.items():
        for path in paths:
            for route in routes.get("domain_routes", []):
                if _path_matches_route(path, route, routes):
                    domains[route["id"]] = {"id": route["id"], "reason": route.get("reason", "")}
                    if route.get("card"):
                        card = {
                            "path": f"docs/knowledge/risk_cards/{route['card']}",
                            "domain": route["id"],
                            "reason": route.get("reason", ""),
                            "summary": route.get("summary", ""),
                        }
                        _add_unique(cards, card, "path")
            filename = Path(path).name.lower()
            for route in routes.get("filename_routes", []):
                if any(str(s).lower() in filename for s in route.get("substrings", []) or []):
                    domains[route["id"]] = {"id": route["id"], "reason": route.get("reason", "")}
                    if route.get("card"):
                        card = {
                            "path": f"docs/knowledge/risk_cards/{route['card']}",
                            "domain": route["id"],
                            "reason": route.get("reason", ""),
                            "summary": route.get("summary", ""),
                        }
                        _add_unique(cards, card, "path")

            for route in routes.get("content_routes", []):
                if _content_excluded(path, route):
                    continue
                markers = tuple(str(m) for m in route.get("markers", []) or [])
                if markers and _file_contains_marker(path, markers):
                    domains[route["id"]] = {"id": route["id"], "reason": route.get("reason", "")}
                    for read in route.get("reads", []) or []:
                        _add_unique(reads, {"path": read["path"], "reason": read.get("reason", "")}, "path")
                    if route.get("card"):
                        card = {
                            "path": f"docs/knowledge/risk_cards/{route['card']}",
                            "domain": route["id"],
                            "reason": route.get("reason", ""),
                            "summary": route.get("summary", ""),
                        }
                        _add_unique(cards, card, "path")

            for route in routes.get("object_alerts", []):
                if _content_excluded(path, route):
                    continue
                if not _path_matches_route(path, route, routes):
                    continue
                markers = tuple(str(m) for m in route.get("markers", []) or [])
                if markers and _file_contains_marker(path, markers):
                    alert = {
                        "id": route["id"],
                        "severity": route.get("severity", "high"),
                        "path": original,
                        "source": path,
                        "message": route.get("message", ""),
                        "card": f"docs/knowledge/risk_cards/{route['card']}" if route.get("card") else "",
                    }
                    _add_unique(alerts, alert, "id")
                    if route.get("card"):
                        _add_unique(
                            cards,
                            {
                                "path": f"docs/knowledge/risk_cards/{route['card']}",
                                "domain": route["id"],
                                "reason": route.get("reason", route.get("message", "")),
                                "summary": route.get("summary", ""),
                            },
                            "path",
                        )

        for route in routes.get("maintenance_routes", []):
            if any(_path_matches_route(path, route, routes) for path in paths):
                domains[route["id"]] = {"id": route["id"], "reason": route.get("reason", "")}
                for read in route.get("reads", []) or []:
                    _add_unique(reads, {"path": read["path"], "reason": read.get("reason", "")}, "path")

    return {
        "files": files,
        "generated": {path: gen[path] for path in files if path in gen},
        "routed_paths": routed_paths,
        "domains": sorted(domains.values(), key=lambda item: item["id"]),
        "cards": sorted(cards, key=lambda item: item["path"]),
        "reads": reads,
        "alerts": alerts,
        "anti_patterns": relevant_rules(files, {d["id"] for d in domains.values()}),
        "maintenance": maintenance_notes(files, routes),
    }


def relevant_rules(files: list[str], domains: set[str], limit: int = 10) -> list[dict[str, str]]:
    patterns = _load_yaml(KNOWLEDGE_DIR / "anti_patterns.yaml") or []
    normalized = [_norm(f) for f in files]
    matches: list[dict[str, str]] = []
    for entry in patterns:
        category = entry.get("category", "")
        scope = entry.get("scope", "")
        only_in = entry.get("only_in_paths", []) or []
        matched_domain = category in domains or scope in domains
        matched_path = bool(only_in) and any(any(part in path for part in only_in) for path in normalized)
        if matched_domain or matched_path:
            detectability = entry.get("detectability") or ("lint" if entry.get("pattern") else "advisory")
            matches.append(
                {
                    "id": entry.get("id", ""),
                    "detectability": detectability,
                    "bad": entry.get("bad", ""),
                    "correction": entry.get("correction", ""),
                }
            )
    return matches[:limit]


def maintenance_notes(files: list[str], routes: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    file_set = set(files)
    if any(path.startswith("docs/knowledge/") or path in {"CLAUDE.md", "docs/guides/AI_Tool_Workflow_Prompt.md"} for path in files):
        notes.append(f"After changing knowledge/workflow docs, run `{MANAGED_SANDBOX_PYTHON} scripts\\gen_brief.py`.")
    if "docs/knowledge/context_routes.yaml" in file_set or "scripts/ai_context.py" in file_set:
        notes.append("Route behavior changed; run `scripts/test_ai_context.py` and update workflow docs.")
    if "docs/knowledge/anti_patterns.yaml" in file_set:
        notes.append("For new `detectability: lint` anti-patterns, add fixtures and run `scripts/test_lint_rules.py`.")
    if "data/validation_baseline.yaml" in file_set:
        notes.append("Validation baseline changed; every accepted warning needs a rationale.")
    if any(path.startswith("docs/knowledge/risk_cards/") for path in files):
        notes.append("Risk cards changed; keep them operational and ensure `context_routes.yaml` routes them.")
    if "docs/knowledge/PROJECT_OVERVIEW.md" in file_set:
        notes.append("Project overview changed; regenerate `docs/knowledge/BRIEF.md`.")
    return notes


def _short(text: str, limit: int = 260) -> str:
    collapsed = " ".join(str(text).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3].rstrip() + "..."


def print_card(card_path: str) -> None:
    path = REPO_ROOT / card_path
    if path.exists():
        print(f"## Risk Card: {card_path}")
        print("")
        print(path.read_text(encoding="utf-8").strip())
        print("")


def print_markdown(context: dict[str, Any], full: bool) -> None:
    print("# AI Task Context")
    print("")
    if not context["files"]:
        print("No files detected. Pass --changed or --files.")
        return

    print("## Core Bootstrap")
    print("- Read `CLAUDE.md` for the compact mandatory workflow.")
    print("- Read `docs/knowledge/BRIEF.md` for project-wide gotchas; use routed cards for details.")
    print("- In managed sandboxes, run project scripts with the direct `eu5` interpreter, not `conda run`.")
    print("")

    print("## Files")
    for path in context["files"]:
        marker = ""
        generated = context["generated"].get(path)
        if generated:
            source = generated.get("data", generated.get("script", "source"))
            marker = f" [generated: edit {source}]"
        print(f"- `{path}`{marker}")
    print("")

    if context["alerts"]:
        print("## Immediate Risk Alerts")
        for alert in context["alerts"]:
            card_suffix = f" Read `{alert['card']}`." if alert.get("card") else ""
            print(f"- `{alert['id']}` [{alert['severity']}]: {alert['message']}{card_suffix}")
        print("")

    print("## Domains")
    if context["domains"]:
        for domain in context["domains"]:
            reason = f" - {domain['reason']}" if domain.get("reason") else ""
            print(f"- `{domain['id']}`{reason}")
    else:
        print("- none detected")
    print("")

    print("## Context Routes")
    if context["cards"]:
        for card in context["cards"]:
            summary = f" - {card['summary']}" if card.get("summary") else ""
            print(f"- `{card['path']}` ({card['domain']}){summary}")
    else:
        print("- no risk card routes")
    print("")

    print("## Required Reads")
    printed: set[str] = set()
    for read in context["reads"]:
        path = read["path"]
        if path in printed:
            continue
        reason = f" - {read['reason']}" if read.get("reason") else ""
        print(f"- `{path}`{reason}")
        printed.add(path)
    for card in context["cards"]:
        path = card["path"]
        if path not in printed:
            reason = f" - {card['reason']}" if card.get("reason") else ""
            print(f"- `{path}`{reason}")
            printed.add(path)
    print("")

    if full:
        printed_cards: set[str] = set()
        for card in context["cards"]:
            if card["path"] not in printed_cards:
                print_card(card["path"])
                printed_cards.add(card["path"])

    if context["anti_patterns"]:
        print("## Relevant Anti-Patterns")
        for entry in context["anti_patterns"]:
            print(
                f"- `{entry['id']}` [{entry['detectability']}]: "
                f"{_short(entry['bad'], 180)} -> {_short(entry['correction'], 220)}"
            )
        print("")

    if context["maintenance"]:
        print("## Knowledge Maintenance")
        for note in context["maintenance"]:
            print(f"- {note}")
        print("")

    print("## Suggested Validation")
    print("```powershell")
    print("# Managed sandbox default; do not use conda run here.")
    print(f"{MANAGED_SANDBOX_PYTHON} scripts\\validate.py --changed --fix --ai-report")
    print("```")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed", action="store_true", help="Use git changed files")
    parser.add_argument("--files", nargs="*", default=[], help="Explicit files")
    parser.add_argument("--full", action="store_true", help="Inline full routed risk card text")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable route data")
    args = parser.parse_args()

    files = changed_files() if args.changed else args.files
    routes = load_routes()
    context = build_context(files, routes)

    if args.json:
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print_markdown(context, args.full)


if __name__ == "__main__":
    main()
