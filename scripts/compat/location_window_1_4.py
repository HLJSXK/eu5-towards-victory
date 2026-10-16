"""Apply reviewed third-party panel changes to the current 1.4 vanilla panel."""
import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VANILLA_FILE = REPO_ROOT / ".eu5-base/reference_game_files/game/in_game/gui/location_window.gui"


def normalized_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def apply_reviewed_patch(source: list[str], patch: str) -> list[str]:
    result: list[str] = []
    cursor = 0
    patch_lines = patch.splitlines()
    index = 2  # unified diff file headers
    while index < len(patch_lines):
        match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*", patch_lines[index])
        if not match:
            raise RuntimeError(f"Invalid location-panel patch hunk: {patch_lines[index]}")
        start = int(match[1]) - (0 if match[2] == "0" else 1)
        if start < cursor:
            raise RuntimeError("Overlapping location-panel patch hunks")
        result.extend(source[cursor:start])
        cursor = start
        consumed = emitted = 0
        index += 1
        while index < len(patch_lines) and not patch_lines[index].startswith("@@"):
            line = patch_lines[index]
            prefix, payload = line[:1], line[1:]
            if prefix in (" ", "-"):
                if cursor >= len(source) or source[cursor] != payload:
                    raise RuntimeError(f"Vanilla location panel changed at line {cursor + 1}; review the 1.4 patch")
                cursor += 1
                consumed += 1
            if prefix in (" ", "+"):
                result.append(payload)
                emitted += 1
            if prefix not in (" ", "-", "+"):
                raise RuntimeError(f"Invalid patch line: {line}")
            index += 1
        if consumed != int(match[2] or 1) or emitted != int(match[4] or 1):
            raise RuntimeError("Location-panel patch hunk length mismatch")
    result.extend(source[cursor:])
    return result


def indent_gui(lines: list[str]) -> str:
    result = []
    depth = 0
    for line in lines:
        # GUI expressions and comments can contain braces; only syntax counts.
        syntax = re.sub(r'"(?:[^"\\]|\\.)*"|#.*', "", line)
        leading_close = len(syntax) - len(syntax.lstrip("}"))
        result.append("\t" * max(0, depth - leading_close) + line if line else "")
        depth += syntax.count("{") - syntax.count("}")
        if depth < 0:
            raise RuntimeError("Unbalanced closing brace in migrated location panel")
    if depth:
        raise RuntimeError("Unbalanced braces in migrated location panel")
    return "\n".join(result) + "\n"


def migrate_panel(patch_name: str, reference_file: Path) -> str:
    source = normalized_lines(VANILLA_FILE.read_text(encoding="utf-8-sig"))
    patch = (REPO_ROOT / "data/compat" / patch_name).read_text(encoding="utf-8")
    # The patch records a reviewed port of this third-party panel, rather than
    # importing its old vanilla structure on every run. Require a new review
    # when the source mod changes; whitespace-only changes do not invalidate it.
    match = re.fullmatch(
        r"\+\+\+ .* \(third-party-sha256: ([0-9a-f]{64})\)", patch.splitlines()[1]
    )
    if not match:
        raise RuntimeError(f"Missing reviewed third-party hash in {patch_name}")
    reference = normalized_lines(reference_file.read_text(encoding="utf-8-sig"))
    actual_hash = hashlib.sha256("\n".join(reference).encode("utf-8")).hexdigest()
    if actual_hash != match[1]:
        raise RuntimeError(f"Third-party location panel changed: {reference_file}; review {patch_name}")
    return indent_gui(apply_reviewed_patch(source, patch))
