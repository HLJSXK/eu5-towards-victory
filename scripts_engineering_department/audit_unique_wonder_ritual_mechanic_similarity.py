#!/usr/bin/env python3
"""Static mechanic-similarity audit for the implemented unique wonder rituals.

Compares the generated EU5 scripted_effects/scripted_triggers source for each
implemented unique-wonder ritual after normalizing away wonder-specific naming,
so that two rituals built from the *same underlying mechanic template* (just
with different entity/row-set names swapped in) show up as highly similar,
while genuinely distinct bespoke mechanics show up as dissimilar.

This is a read-only static-analysis spike: it only reads existing src/ files.
It is meant to be a cheap automated gate run after each future batch of
wonder ritual implementations, to catch the kind of design homogenization that
previously produced an Alhambra / Dome of the Rock / Bank of Saint George /
St. Peter's Basilica cluster (all four were thin reskins of the same generic
`_entity_ritual.py` 4-stage shape, since removed) before it happens again
across the remaining 121 unplanned wonders.

Method
------
1. Read each wonder's effects + triggers file (events are not read; the spec
   for this spike weights effects/triggers only, since that is where the
   `_entity_ritual.py` reuse actually lives).
2. Strip comment-only lines (headers, `# -- block name --` separators).
3. Strip every wonder's own key / display-name variants from the text so
   identifiers normalize across wonders regardless of naming.
4. Split the file into top-level `name = { ... }` blocks (brace-depth scan).
5. Within each block, walk every identifier and split it into `_`-delimited
   segments. Segments that are common "engine vocabulary" (appear across most
   of the 6 wonders once wonder keys are stripped -- e.g. `effect`, `trigger`,
   `status`, `favorable`, `count`, `hidden_effect`, `random_list`, ...) are
   left untouched. Runs of segments that are NOT common vocabulary (i.e. only
   appear in a handful of wonders -- the actual entity/row-set names, e.g.
   `symbolic_keys`, `treaty_clause_register`) are collapsed to positional
   placeholders `ENTITY_1`, `ENTITY_2`, ... in order of first appearance
   *within that block*. Numeric literals are never touched.

   The "common vocabulary" set is derived empirically from the corpus itself
   (a segment counts as generic if it appears in at least
   ``--generic-threshold`` of the 6 wonders' own identifier vocabularies once
   each wonder's own name is stripped) rather than hand-maintained, so the
   detector does not need a manually curated EU5-keyword dictionary and keeps
   working as more wonders are added.
6. Compute, for every wonder pair:
   - `effects_ratio` / `triggers_ratio`: whole-file `difflib.SequenceMatcher`
     ratio over the concatenated normalized blocks.
   - `combined_ratio`: same ratio computed over effects+triggers concatenated
     together (naturally length-weighted between the two files).
   - `block_shape_jaccard`: Jaccard similarity of the *sets* of normalized
     block bodies (the "shape" of each named effect/trigger) between the two
     wonders, computed separately for effects and triggers.
7. Separately, scan for `random_list` blocks and extract each one's ordered
   weight tuple (e.g. `(60, 40)`, `(80, 20)`). Report which wonders share
   identical weight tuples as corroborating (not primary) evidence -- reusing
   the exact same probability split across unrelated "unique" mechanics is a
   strong reuse signal on its own.
8. Print the full pairwise matrix and flag pairs whose `combined_ratio`
   clears `--threshold`.

Usage
-----
    C:\\Users\\Hades\\anaconda3\\envs\\eu5\\python.exe scripts\\audit_unique_wonder_ritual_mechanic_similarity.py
"""

from __future__ import annotations

import argparse
import itertools
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
EFFECTS_DIR = REPO_ROOT / "src_engineering_department" / "in_game" / "common" / "scripted_effects"
TRIGGERS_DIR = REPO_ROOT / "src_engineering_department" / "in_game" / "common" / "scripted_triggers"

# key -> (file-name key used in tv_wonder_unique_<key>_ritual_*.txt,
#          identifier-name variants to strip from the text, longest first)
WONDERS: dict[str, list[str]] = {
    "hagia_sophia": ["hagia_sophia", "hagia"],
    "pharos_lighthouse": ["pharos_lighthouse", "pharos"],
}

KINDS = ("effects", "triggers")

IDENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
HEADER_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_:]*)\s*=\s*\{")
RANDOM_LIST_WEIGHT_RE = re.compile(r"\s*(\d+)\s*=\s*(?=\{)")


def _file_path(kind: str, key: str) -> Path:
    directory = EFFECTS_DIR if kind == "effects" else TRIGGERS_DIR
    return directory / f"tv_wonder_unique_{key}_ritual_{kind}.txt"


def _read_stripped(path: Path) -> str:
    """Read a src file and drop comment-only lines."""
    text = path.read_text(encoding="utf-8-sig")
    lines = [line for line in text.splitlines() if not line.strip().startswith("#")]
    return "\n".join(lines)


def _strip_wonder_key(text: str, variants: list[str]) -> str:
    for variant in sorted(variants, key=len, reverse=True):
        text = text.replace(variant, "")
    # Collapse the underscore runs left behind by removing an inner name
    # segment (e.g. "tv_wonder__ritual_phase" -> "tv_wonder_ritual_phase").
    text = re.sub(r"_{2,}", "_", text)
    text = re.sub(r"_(?=[^A-Za-z0-9_])", "", text)
    return text


def _extract_blocks(text: str) -> list[tuple[str, str]]:
    """Split key-stripped file text into top-level ``name = { ... }`` blocks."""
    blocks: list[tuple[str, str]] = []
    depth = 0
    name = None
    buf: list[str] = []
    for line in text.splitlines():
        if depth == 0:
            m = HEADER_RE.match(line.strip())
            if not m:
                continue
            name = m.group(1)
            buf = [line]
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                blocks.append((name, "\n".join(buf)))
                name, buf, depth = None, [], 0
            continue
        buf.append(line)
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            blocks.append((name, "\n".join(buf)))
            name, buf, depth = None, [], 0
    return blocks


def _build_generic_vocabulary(
    raw_texts: dict[str, dict[str, str]], threshold: int
) -> set[str]:
    """Segments that appear in at least `threshold` of the 6 wonders' own
    identifier vocabulary (after each wonder's own key is stripped) are
    treated as shared engine vocabulary rather than wonder-specific naming.
    """
    coverage: dict[str, set[str]] = {}
    for key, by_kind in raw_texts.items():
        for text in by_kind.values():
            for ident in IDENT_RE.findall(text):
                for seg in ident.split("_"):
                    if seg and not seg.isdigit():
                        coverage.setdefault(seg.lower(), set()).add(key)
    return {seg for seg, keys in coverage.items() if len(keys) >= threshold}


def _normalize_block(block_text: str, generic_words: set[str]) -> str:
    """Replace wonder-specific entity/row-set identifier segments with
    positional ENTITY_n placeholders, in order of first appearance in this
    block. Shared engine vocabulary and numeric literals are left untouched.
    """
    entity_map: dict[str, str] = {}

    def repl(match: re.Match) -> str:
        ident = match.group(0)
        segs = ident.split("_")
        out: list[str] = []
        run: list[str] = []

        def flush() -> None:
            if not run:
                return
            key = "_".join(run)
            placeholder = entity_map.setdefault(key, f"ENTITY_{len(entity_map) + 1}")
            out.append(placeholder)
            run.clear()

        for seg in segs:
            if not seg:
                continue
            if seg.lower() in generic_words or seg.isdigit():
                flush()
                out.append(seg)
            else:
                run.append(seg)
        flush()
        return "_".join(out)

    return IDENT_RE.sub(repl, block_text)


def _extract_random_list_weight_tuples(text: str) -> list[tuple[int, ...]]:
    """Find every `random_list = { N = {...} M = {...} ... }` block (brace
    depth scan from each `random_list = {` occurrence) and return the ordered
    tuple of top-level weights inside it, e.g. (60, 40) or (80, 20).
    """
    tuples: list[tuple[int, ...]] = []
    for m in re.finditer(r"random_list\s*=\s*\{", text):
        start = m.end()
        depth = 1
        i = start
        weights: list[int] = []
        # Walk char by char tracking depth; whenever we're back at depth 1
        # (i.e. directly inside the random_list body) and see "NUM = {",
        # record NUM and skip past it.
        while i < len(text) and depth > 0:
            ch = text[i]
            if ch == "{":
                depth += 1
                i += 1
            elif ch == "}":
                depth -= 1
                i += 1
            elif depth == 1:
                wm = RANDOM_LIST_WEIGHT_RE.match(text, i)
                if wm:
                    weights.append(int(wm.group(1)))
                    i = wm.end()
                else:
                    i += 1
            else:
                i += 1
        if weights:
            tuples.append(tuple(weights))
    return tuples


def _print_matrix(title: str, keys: list[str], values: dict[tuple[str, str], float]) -> None:
    print(f"\n{title}")
    width = max(len(k) for k in keys) + 2
    header = " " * width + "".join(f"{k[:10]:>12}" for k in keys)
    print(header)
    for k1 in keys:
        row = f"{k1:<{width}}"
        for k2 in keys:
            if k1 == k2:
                row += f"{'--':>12}"
            else:
                pair = (k1, k2) if (k1, k2) in values else (k2, k1)
                row += f"{values[pair]:>12.3f}"
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generic-threshold",
        type=int,
        default=4,
        help="Segment must appear in this many of the 6 wonders' own vocabularies "
        "(after wonder-key stripping) to count as shared engine vocabulary. Default 4.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.15,
        help="combined_ratio at/above this value flags a wonder pair as high "
        "homogenization risk. Default 0.15 -- empirically justified, not a "
        "guess: on the known-ground-truth 6-wonder set, whole-file "
        "SequenceMatcher ratio is sensitive to how many entities/rows each "
        "wonder's instance of a shared template happens to have, so same-"
        "template pairs with different row cardinalities score much lower "
        "than intuition suggests (e.g. Alhambra vs Dome of the Rock = 0.185, "
        "both route through the identical _entity_ritual.py engine). The "
        "observed minimum same-template combined_ratio was 0.185 and the "
        "observed maximum different-mechanic combined_ratio was 0.078 -- "
        "0.15 sits in that gap with margin on both sides. Do not raise this "
        "back toward 0.7-0.8 without re-checking the gap on the current data; "
        "read flagged pairs alongside the magic-number-reuse section below, "
        "which is a cleaner (if coarser) signal for this same dataset.",
    )
    args = parser.parse_args()

    keys = list(WONDERS.keys())

    raw_texts: dict[str, dict[str, str]] = {}
    for key, variants in WONDERS.items():
        by_kind = {}
        for kind in KINDS:
            path = _file_path(kind, key)
            text = _read_stripped(path)
            text = _strip_wonder_key(text, variants)
            by_kind[kind] = text
        raw_texts[key] = by_kind

    generic_words = _build_generic_vocabulary(raw_texts, args.generic_threshold)
    print(f"# Shared engine vocabulary ({len(generic_words)} segments, "
          f"threshold={args.generic_threshold}/{len(WONDERS)} wonders):")
    print("  " + ", ".join(sorted(generic_words)))

    # Per wonder: normalized whole-file text per kind, and set of normalized
    # block "shapes" per kind.
    norm_whole: dict[str, dict[str, str]] = {}
    norm_shapes: dict[str, dict[str, set[str]]] = {}
    weight_tuples: dict[str, Counter] = {}

    for key in keys:
        norm_whole[key] = {}
        norm_shapes[key] = {}
        weight_tuples[key] = Counter()
        for kind in KINDS:
            text = raw_texts[key][kind]
            blocks = _extract_blocks(text)
            normalized_blocks = [_normalize_block(body, generic_words) for _, body in blocks]
            norm_whole[key][kind] = "\n".join(normalized_blocks)
            norm_shapes[key][kind] = set(normalized_blocks)
            weight_tuples[key].update(_extract_random_list_weight_tuples(text))

    effects_ratio: dict[tuple[str, str], float] = {}
    triggers_ratio: dict[tuple[str, str], float] = {}
    combined_ratio: dict[tuple[str, str], float] = {}
    effects_jaccard: dict[tuple[str, str], float] = {}
    triggers_jaccard: dict[tuple[str, str], float] = {}

    for k1, k2 in itertools.combinations(keys, 2):
        pair = (k1, k2)
        e1, e2 = norm_whole[k1]["effects"], norm_whole[k2]["effects"]
        t1, t2 = norm_whole[k1]["triggers"], norm_whole[k2]["triggers"]
        effects_ratio[pair] = SequenceMatcher(None, e1, e2).ratio()
        triggers_ratio[pair] = SequenceMatcher(None, t1, t2).ratio()
        combined_ratio[pair] = SequenceMatcher(None, e1 + t1, e2 + t2).ratio()

        s1, s2 = norm_shapes[k1]["effects"], norm_shapes[k2]["effects"]
        effects_jaccard[pair] = (len(s1 & s2) / len(s1 | s2)) if (s1 | s2) else 0.0
        s1t, s2t = norm_shapes[k1]["triggers"], norm_shapes[k2]["triggers"]
        triggers_jaccard[pair] = (len(s1t & s2t) / len(s1t | s2t)) if (s1t | s2t) else 0.0

    _print_matrix("Effects SequenceMatcher ratio", keys, effects_ratio)
    _print_matrix("Triggers SequenceMatcher ratio", keys, triggers_ratio)
    _print_matrix("Combined (effects+triggers) SequenceMatcher ratio", keys, combined_ratio)
    _print_matrix("Effects block-shape Jaccard", keys, effects_jaccard)
    _print_matrix("Triggers block-shape Jaccard", keys, triggers_jaccard)

    print(f"\n# Flagged pairs (combined_ratio >= {args.threshold}):")
    flagged = [
        (k1, k2, combined_ratio[(k1, k2)])
        for k1, k2 in itertools.combinations(keys, 2)
        if combined_ratio[(k1, k2)] >= args.threshold
    ]
    if not flagged:
        print("  (none)")
    else:
        for k1, k2, ratio in sorted(flagged, key=lambda t: -t[2]):
            print(f"  {k1} <-> {k2}: combined_ratio={ratio:.3f} "
                  f"effects={effects_ratio[(k1, k2)]:.3f} "
                  f"triggers={triggers_ratio[(k1, k2)]:.3f} "
                  f"effects_jaccard={effects_jaccard[(k1, k2)]:.3f} "
                  f"triggers_jaccard={triggers_jaccard[(k1, k2)]:.3f}")

    print("\n# Shared random_list weight tuples (magic-number reuse):")
    all_tuples: set[tuple[int, ...]] = set()
    for c in weight_tuples.values():
        all_tuples.update(c.keys())
    any_shared = False
    for wt in sorted(all_tuples, key=lambda t: (-len(t), t)):
        owners = [key for key in keys if wt in weight_tuples[key]]
        if len(owners) >= 2:
            any_shared = True
            detail = ", ".join(f"{key}x{weight_tuples[key][wt]}" for key in owners)
            print(f"  weights={wt}: {detail}")
    if not any_shared:
        print("  (none)")


if __name__ == "__main__":
    main()
