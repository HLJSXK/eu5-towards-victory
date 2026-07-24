"""Surgically merge authored Unique Wonder Ceremony cost/option-text picks into
data/unique_wonders.yaml.

Input: a JSON file shaped {"wonders": [{"wonder_id": int, "stages": [{"stage_index": int,
"cost": [{"catalog": str, "type": str}, ...], "option_pay_en": str, "option_pay_zh": str,
"option_decline_en": str, "option_decline_zh": str}, ...8 entries...]}, ...]} -- the
authoring content pipeline (a per-wonder agent fan-out) only ever picks "catalog"+"type";
this script computes and stamps the actual numeric "value" via
wonder_mechanics.rituals.ceremony_cost_computed_value(), so the magnitude can never drift
from the deterministic stage-parity formula (see docs/knowledge/risk_cards/wonders.md rule
20).

Does NOT use a full YAML parse+dump round-trip: data/unique_wonders.yaml (14,000+ lines) has
never been round-tripped by any script in this repo, no format-preserving YAML library is
installed, and a plain re-dump would reformat the whole file (see the rework's approved
plan). Instead this performs anchored, line-based text splicing, exploiting the file's
verified-uniform structure: every wonder starts at a column-0 "- id: <n>" line, every stage
starts at a 4-space-indented "- title_en:" line, and every stage's authored fields end with
its "cost:" list (verified: the ceremony block is always the last field of a wonder entry,
and every stage's cost list is always immediately followed by either the next stage's
"- title_en:" or the next wonder's "- id:"). Reloads via load_all_wonder_mechanics() after
writing so any splicing mistake surfaces as a hard validation error, not silent corruption.

Usage:
    C:\\Users\\Hades\\anaconda3\\envs\\eu5\\python.exe scripts\\wonder_mechanics\\merge_ceremony_cost_options.py --input <path.json>
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_mechanics.rituals import ceremony_cost_computed_value  # noqa: E402

UNIQUE_WONDERS_FILE = REPO_ROOT / "data" / "unique_wonders.yaml"
WONDER_ID_RE = re.compile(r"^- id: (\d+)$")
STAGE_START_RE = re.compile(r"^    - title_en:")
COST_HEADER = "      cost:"
NULL_CEREMONY_RE = re.compile(r"^\s*ceremony: null\s*$")
STAGE_COUNT = 8


def format_number(value: object) -> str:
    value = float(value)
    if value.is_integer():
        return str(int(value))
    return repr(value)


def quote(text: str) -> str:
    collapsed = " ".join(str(text).split())
    escaped = collapsed.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_stage_cost_and_option_lines(stage_data: dict) -> list[str]:
    lines = [COST_HEADER]
    for item in stage_data["cost"]:
        catalog = item["catalog"]
        entry_id = item["type"]
        value = ceremony_cost_computed_value(catalog, entry_id, stage_data["stage_index"])
        lines.append(f"      - catalog: {catalog}")
        lines.append(f"        type: {entry_id}")
        lines.append(f"        value: {format_number(value)}")
    lines.append(f'      option_pay_en: {quote(stage_data["option_pay_en"])}')
    lines.append(f'      option_pay_zh: {quote(stage_data["option_pay_zh"])}')
    lines.append(f'      option_decline_en: {quote(stage_data["option_decline_en"])}')
    lines.append(f'      option_decline_zh: {quote(stage_data["option_decline_zh"])}')
    return lines


def split_stage_chunks(block_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    stage_start_indices = [i for i, line in enumerate(block_lines) if STAGE_START_RE.match(line)]
    if len(stage_start_indices) != STAGE_COUNT:
        raise ValueError(f"expected {STAGE_COUNT} stages, found {len(stage_start_indices)}")
    preamble = block_lines[: stage_start_indices[0]]
    chunks = []
    for index, start in enumerate(stage_start_indices):
        end = stage_start_indices[index + 1] if index + 1 < len(stage_start_indices) else len(block_lines)
        chunks.append(block_lines[start:end])
    return preamble, chunks


def rewrite_stage_chunk(chunk: list[str], stage_data: dict) -> list[str]:
    try:
        cost_header_index = chunk.index(COST_HEADER)
    except ValueError:
        raise ValueError(f"stage chunk has no {COST_HEADER!r} line: {chunk[:3]!r}...") from None
    kept = chunk[:cost_header_index]
    return kept + build_stage_cost_and_option_lines(stage_data)


def rewrite_wonder_block(block_lines: list[str], wonder_entry: dict, *, wonder_id: int) -> list[str]:
    preamble, chunks = split_stage_chunks(block_lines)
    stages_by_index = {s["stage_index"]: s for s in wonder_entry["stages"]}
    if sorted(stages_by_index) != list(range(1, STAGE_COUNT + 1)):
        raise ValueError(f"wonder {wonder_id}: stages must cover 1-{STAGE_COUNT} exactly, got {sorted(stages_by_index)}")
    new_chunks = [rewrite_stage_chunk(chunk, stages_by_index[i + 1]) for i, chunk in enumerate(chunks)]
    result = list(preamble)
    for new_chunk in new_chunks:
        result.extend(new_chunk)
    return result


def merge(text: str, wonders_by_id: dict[int, dict]) -> tuple[str, list[int], list[int]]:
    trailing_newline = text.endswith("\r\n")
    lines = text.split("\r\n")
    if trailing_newline:
        lines = lines[:-1]

    wonder_starts = [i for i, line in enumerate(lines) if WONDER_ID_RE.match(line)]
    if not wonder_starts:
        raise ValueError("no wonder entries found (no line matched '- id: <n>')")

    new_lines: list[str] = list(lines[: wonder_starts[0]])
    processed: list[int] = []
    missing: list[int] = []
    for idx, start in enumerate(wonder_starts):
        end = wonder_starts[idx + 1] if idx + 1 < len(wonder_starts) else len(lines)
        block = lines[start:end]
        wonder_id = int(WONDER_ID_RE.match(block[0]).group(1))
        if wonder_id in wonders_by_id:
            block = rewrite_wonder_block(block, wonders_by_id[wonder_id], wonder_id=wonder_id)
            processed.append(wonder_id)
        elif not any(NULL_CEREMONY_RE.match(line) for line in block):
            missing.append(wonder_id)
        new_lines.extend(block)

    output_text = "\r\n".join(new_lines) + ("\r\n" if trailing_newline else "")
    return output_text, processed, missing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to the authoring pipeline's aggregated JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print a summary but do not write the file")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    wonders_by_id = {int(w["wonder_id"]): w for w in payload["wonders"]}

    with UNIQUE_WONDERS_FILE.open(encoding="utf-8-sig", newline="") as f:
        original_text = f.read()
    output_text, processed, missing = merge(original_text, wonders_by_id)

    print(f"Processed {len(processed)} wonders.")
    if missing:
        print(f"WARNING: {len(missing)} ceremony wonders had no matching entry in {args.input}: {missing}")
    unmatched_input_ids = sorted(set(wonders_by_id) - set(processed))
    if unmatched_input_ids:
        print(f"WARNING: input JSON had wonder ids not found in {UNIQUE_WONDERS_FILE.name}: {unmatched_input_ids}")

    if args.dry_run:
        print("Dry run: not writing.")
        return

    with UNIQUE_WONDERS_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        f.write(output_text)
    print(f"Wrote {UNIQUE_WONDERS_FILE.relative_to(REPO_ROOT)}")

    from wonder_mechanics.io import load_all_wonder_mechanics

    load_all_wonder_mechanics()
    print("Validated: load_all_wonder_mechanics() succeeded.")


if __name__ == "__main__":
    main()
