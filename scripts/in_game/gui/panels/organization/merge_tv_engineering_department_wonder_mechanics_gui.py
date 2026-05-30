import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[5]
MAIN_FILE = REPO_ROOT / "src" / "in_game" / "gui" / "panels" / "organization" / "tv_engineering_department.gui"
FRAGMENT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_engineering_department_wonder_mechanics.gui"

MARKERS = [
    "TV_WONDER_MECHANICS_PREVIEW_WIDGETS",
    "TV_WONDER_MECHANICS_CEREMONY_PREVIEW_WIDGETS",
    "TV_WONDER_MECHANICS_CEREMONY_WONDER_TEXTS",
    "TV_WONDER_MECHANICS_CEREMONY_SELECTED_TEXTS",
    "TV_WONDER_MECHANICS_CEREMONY_DOSSIER_TEXTS",
    "TV_WONDER_MECHANICS_PROPOSAL_TEXTS",
    "TV_WONDER_MECHANICS_PROPOSAL_RESUME_TEXTS",
    "TV_WONDER_MECHANICS_PROPOSAL_EXPAND_TEXTS",
    "TV_WONDER_MECHANICS_LOCKED_TEXTS",
    "TV_WONDER_MECHANICS_PROPOSAL_BUTTONS",
    "TV_WONDER_MECHANICS_CEREMONY_STYLE_1_BUTTONS",
    "TV_WONDER_MECHANICS_CEREMONY_STYLE_2_BUTTONS",
    "TV_WONDER_MECHANICS_CEREMONY_STYLE_3_BUTTONS",
    "TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS",
    "TV_WONDER_MECHANICS_HOLD_BUTTONS",
]

LEGACY_START_HINTS = {
    "TV_WONDER_MECHANICS_PREVIEW_WIDGETS": "tv_wonder_sacred_mountain.dds",
    "TV_WONDER_MECHANICS_PROPOSAL_TEXTS": "TV_ENGINEERING_PROPOSAL_SACRED_MOUNTAIN_TEXT",
    "TV_WONDER_MECHANICS_PROPOSAL_RESUME_TEXTS": "TV_ENGINEERING_PROPOSAL_RESUME_SACRED_MOUNTAIN_TEXT",
    "TV_WONDER_MECHANICS_PROPOSAL_EXPAND_TEXTS": "TV_ENGINEERING_PROPOSAL_EXPAND_SACRED_MOUNTAIN_TEXT",
    "TV_WONDER_MECHANICS_LOCKED_TEXTS": "TV_ENGINEERING_LOCKED_SACRED_MOUNTAIN_TEXT",
    "TV_WONDER_MECHANICS_PROPOSAL_BUTTONS": "TV_ENGINEERING_PROPOSAL_BUTTON_SACRED_MOUNTAIN",
    "TV_WONDER_MECHANICS_CEREMONY_STYLE_1_BUTTONS": 'action_name = "tv_wonder_choose_ceremony_style_1"',
    "TV_WONDER_MECHANICS_CEREMONY_STYLE_2_BUTTONS": 'action_name = "tv_wonder_choose_ceremony_style_2"',
    "TV_WONDER_MECHANICS_CEREMONY_STYLE_3_BUTTONS": 'action_name = "tv_wonder_choose_ceremony_style_3"',
    "TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS": "TV_ENGINEERING_ACTIVE_RITUAL_THEOCRATIC_CENTER",
    "TV_WONDER_MECHANICS_HOLD_BUTTONS": "TV_ENGINEERING_HOLD_CEREMONY_BUTTON",
}


def extract_fragment(marker: str, fragment: str) -> str:
    pattern = re.compile(
        rf"### BEGIN {re.escape(marker)}\n(.*?)\n### END {re.escape(marker)}",
        re.DOTALL,
    )
    match = pattern.search(fragment)
    if not match:
        raise ValueError(f"Missing fragment marker {marker}")
    return match.group(1).rstrip()


def indent_block(block: str, indent: str) -> str:
    return "\n".join(f"{indent}{line}" if line else line for line in block.splitlines())


def replace_generated_segment(text: str, marker: str, block: str) -> str:
    begin = f"# BEGIN GENERATED {marker}"
    end = f"# END GENERATED {marker}"
    pattern = re.compile(
        rf"(?P<prefix>^|\n)(?P<indent>[ \t]*){re.escape(begin)}[ \t]*\n.*?\n[ \t]*{re.escape(end)}(?=\n|$)",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Generated marker {marker} not found in {MAIN_FILE.relative_to(REPO_ROOT)}")
    prefix = match.group("prefix")
    indent = match.group("indent")
    if not indent:
        previous_line_start = text.rfind("\n", 0, match.start())
        previous_line = text[previous_line_start + 1:match.start()] if previous_line_start != -1 else ""
        previous_indent = re.match(r"[ \t]*", previous_line).group(0)
        if previous_line.strip():
            indent = previous_indent
    replacement = f"{prefix}{indent}{begin}\n{indent_block(block, indent)}\n{indent}{end}"
    return text[: match.start()] + replacement + text[match.end():]


def legacy_start_from_hint(text: str, marker: str, marker_index: int) -> int | None:
    hint = LEGACY_START_HINTS[marker]
    hint_index = text.rfind(hint, 0, marker_index)
    if hint_index == -1:
        return None
    if marker in {
        "TV_WONDER_MECHANICS_PREVIEW_WIDGETS",
        "TV_WONDER_MECHANICS_LOCKED_TEXTS",
        "TV_WONDER_MECHANICS_CEREMONY_STYLE_1_BUTTONS",
        "TV_WONDER_MECHANICS_CEREMONY_STYLE_2_BUTTONS",
        "TV_WONDER_MECHANICS_CEREMONY_STYLE_3_BUTTONS",
    }:
        block_index = text.rfind("{", 0, hint_index)
        name_index = text.rfind("=", 0, block_index)
        line_index = text.rfind("\n", 0, name_index)
    else:
        line_index = text.rfind("\n", 0, hint_index)
    return 0 if line_index == -1 else line_index + 1


def remove_legacy_segment(text: str, marker: str) -> str:
    begin = f"# BEGIN GENERATED {marker}"
    marker_index = text.find(begin)
    if marker_index == -1:
        raise ValueError(f"Generated marker {marker} not found while pruning legacy blocks")
    start = legacy_start_from_hint(text, marker, marker_index)
    if start is None:
        return text
    return text[:start] + text[marker_index:]


def strip_legacy_ceremony_widgets(region: str) -> str:
    lines = region.splitlines(keepends=True)
    kept: list[str] = []
    index = 0
    legacy_needles = (
        "TV_ENGINEERING_RITUAL_",
        "TV_ENGINEERING_ACTIVE_RITUAL_",
    )
    block_start = re.compile(r"^\s*(hbox|progressbar)\s*=\s*\{\s*$")
    while index < len(lines):
        line = lines[index]
        if block_start.match(line):
            depth = line.count("{") - line.count("}")
            end = index + 1
            while end < len(lines) and depth > 0:
                depth += lines[end].count("{") - lines[end].count("}")
                end += 1
            block = "".join(lines[index:end])
            if any(needle in block for needle in legacy_needles):
                index = end
                continue
            kept.append(block)
            index = end
            continue
        if not any(needle in line for needle in legacy_needles):
            kept.append(line)
        index += 1
    return "".join(kept)


def remove_legacy_ceremony_widgets(text: str) -> str:
    active_begin = "# BEGIN GENERATED TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS"
    search_start = text.rfind("# END GENERATED TV_WONDER_MECHANICS_CEREMONY_STYLE_3_BUTTONS", 0, text.find(active_begin))
    start = text.find("\n", search_start)
    end = text.find(active_begin, start)
    if start == -1 or end == -1:
        return text
    start += 1
    if start >= end:
        return text
    region = text[start:end]
    return text[:start] + strip_legacy_ceremony_widgets(region) + text[end:]


def normalize_marker_newlines(text: str) -> str:
    text = re.sub(r"(?<!\n)([ \t]*# BEGIN GENERATED)", r"\n\1", text)
    text = re.sub(r"(# END GENERATED [A-Z0-9_]+)(?=[ \t]*# BEGIN GENERATED)", r"\1\n", text)
    return text


def main() -> None:
    text = MAIN_FILE.read_text(encoding="utf-8")
    fragment = FRAGMENT_FILE.read_text(encoding="utf-8")
    text = normalize_marker_newlines(text)
    for marker in MARKERS:
        text = replace_generated_segment(text, marker, extract_fragment(marker, fragment))
    for marker in LEGACY_START_HINTS:
        text = remove_legacy_segment(text, marker)
    text = remove_legacy_ceremony_widgets(text)
    text = normalize_marker_newlines(text)
    MAIN_FILE.write_text(text, encoding="utf-8")
    print(f"Merged {FRAGMENT_FILE.relative_to(REPO_ROOT)} into {MAIN_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
