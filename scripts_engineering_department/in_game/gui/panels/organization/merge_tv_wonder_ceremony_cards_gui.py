"""Merge the Unique Wonder Ceremony card fragment into tv_engineering_department.gui.

First run inserts a new `# BEGIN/END GENERATED TV_WONDER_CEREMONY_CARDS`
marker pair immediately after the existing
`# END GENERATED TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS` marker (the
Pharos/Hagia hand-coded step display, at the end of the Construction-and-
ceremony tab's ritual-status area). Subsequent runs replace only the content
between the markers, exactly like merge_tv_engineering_department_wonder_mechanics_gui.py
does for its own markers. .gui syntax is brace-delimited, not indentation-
sensitive, so the inserted block does not need to match the surrounding
hand-written indentation depth (confirmed against the existing
TV_WONDER_MECHANICS_* markers, which are themselves left unindented in the
middle of deeply-nested widgets).
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[5]
MAIN_FILE = REPO_ROOT / "src_engineering_department" / "in_game" / "gui" / "panels" / "organization" / "tv_engineering_department.gui"
FRAGMENT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_wonder_ceremony_cards.gui"

MARKER = "TV_WONDER_CEREMONY_CARDS"
ANCHOR_END = "# END GENERATED TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS"


def extract_fragment_block(fragment: str) -> str:
    pattern = re.compile(
        rf"# BEGIN GENERATED {re.escape(MARKER)}\n(.*?)\n# END GENERATED {re.escape(MARKER)}",
        re.DOTALL,
    )
    match = pattern.search(fragment)
    if not match:
        raise ValueError(f"Missing fragment marker {MARKER} in {FRAGMENT_FILE}")
    return match.group(1).rstrip()


def main() -> None:
    text = MAIN_FILE.read_text(encoding="utf-8")
    fragment = FRAGMENT_FILE.read_text(encoding="utf-8-sig")
    block = extract_fragment_block(fragment)
    new_segment = f"# BEGIN GENERATED {MARKER}\n{block}\n# END GENERATED {MARKER}"

    existing_pattern = re.compile(
        rf"# BEGIN GENERATED {re.escape(MARKER)}\n.*?# END GENERATED {re.escape(MARKER)}",
        re.DOTALL,
    )
    if existing_pattern.search(text):
        text = existing_pattern.sub(lambda _m: new_segment, text, count=1)
    else:
        anchor_index = text.find(ANCHOR_END)
        if anchor_index == -1:
            raise ValueError(f"Anchor marker not found in {MAIN_FILE}: {ANCHOR_END}")
        insert_at = anchor_index + len(ANCHOR_END)
        text = text[:insert_at] + "\n" + new_segment + text[insert_at:]

    MAIN_FILE.write_text(text, encoding="utf-8")
    print(f"Merged {FRAGMENT_FILE.relative_to(REPO_ROOT)} into {MAIN_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
