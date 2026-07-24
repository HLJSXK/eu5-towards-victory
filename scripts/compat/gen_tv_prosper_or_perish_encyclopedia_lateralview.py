import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_mechanics.render import render_header

TV_FILE = REPO_ROOT / "src_engineering_department" / "in_game" / "gui" / "encyclopedia_lateralview.gui"
PP_FILE = REPO_ROOT / "reference_mods" / "3613232232" / "in_game" / "gui" / "encyclopedia_lateralview.gui"
OUT_FILE = REPO_ROOT / "submods" / "tv_prosper_or_perish_compat" / "in_game" / "gui" / "encyclopedia_lateralview.gui"
SCRIPT_REL = "scripts/compat/gen_tv_prosper_or_perish_encyclopedia_lateralview.py"
DATA_REL = (
    "src_engineering_department/in_game/gui/encyclopedia_lateralview.gui + "
    "reference_mods/3613232232/in_game/gui/encyclopedia_lateralview.gui"
)

# Both TV and Prosper or Perish (PP) fully override in_game/gui/encyclopedia_lateralview.gui
# to add their own Europedia tab, each toggled by its own single-mod GetVariableSystem
# variable (tv_encyclopedia_active / pp_encyclopedia_active). EU5's GUI loader replaces this
# file wholesale per relative path -- whichever mod loads last silently drops the other's
# tab entirely. This generator merges both tabs onto one shared toggle variable
# (SHARED_VAR) with distinct string values ('tv' / 'pp') instead of two independent
# booleans, so the vanilla nav buttons only ever need ONE Clear()/Exists() call each --
# no unverified multi-effect onclick chaining is required (see docs/knowledge/risk_cards/
# europedia.md).
SHARED_VAR = "tveu_compat_encyclopedia_active"

# TV's own tab-toggle patterns (all keyed on the single-mod variable + 'yes' sentinel).
TV_CLEAR = "GetVariableSystem.Clear('tv_encyclopedia_active')"
TV_NOT_HASVALUE = "Not(GetVariableSystem.HasValue('tv_encyclopedia_active', 'yes'))"
TV_HASVALUE = "GetVariableSystem.HasValue('tv_encyclopedia_active', 'yes')"
TV_SET = "GetVariableSystem.Set('tv_encyclopedia_active', 'yes')"

SHARED_CLEAR = f"GetVariableSystem.Clear('{SHARED_VAR}')"
SHARED_NOT_EXISTS = f"Not(GetVariableSystem.Exists('{SHARED_VAR}'))"
SHARED_HASVALUE_TV = f"GetVariableSystem.HasValue('{SHARED_VAR}', 'tv')"
SHARED_SET_TV = f"GetVariableSystem.Set('{SHARED_VAR}', 'tv')"

# PP's own tab-toggle patterns.
PP_HASVALUE = "GetVariableSystem.HasValue('pp_encyclopedia_active', 'yes')"
PP_SET = "GetVariableSystem.Set('pp_encyclopedia_active', 'yes')"

SHARED_HASVALUE_PP = f"GetVariableSystem.HasValue('{SHARED_VAR}', 'pp')"
SHARED_SET_PP = f"GetVariableSystem.Set('{SHARED_VAR}', 'pp')"

# Unique anchor: the nav-list scrollbox immediately following TV's own tab button hbox.
# There is a second, differently-indented "scrollbox = {" deeper in the file (TV's own
# Mod Content tab), so this exact line (used with list.index(), which returns the first
# match) always resolves to the nav-list one.
NAV_SCROLLBOX_ANCHOR = "                        scrollbox = {"

# PP's own tab button hbox ("# Prosper or Perish -- sibling of scrollbox") -- 1-indexed
# lines 62-87 of the PP source file.
PP_TAB_BUTTON_RANGE = (61, 87)
# PP's own Mod Content vbox ("# Mod Content -- filter buttons and cards...") -- 1-indexed
# lines 350-1469 of the PP source file.
PP_MOD_CONTENT_RANGE = (349, 1469)


def replace_exact(text: str, old: str, new: str, expected_count: int) -> str:
    actual = text.count(old)
    if actual != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} occurrence(s) of {old!r} in TV/PP source, found {actual}. "
            "The upstream file layout changed -- re-derive the merge anchors before regenerating."
        )
    return text.replace(old, new)


def merged_tv_lines() -> list[str]:
    text = TV_FILE.read_text(encoding="utf-8-sig")
    # Order matters: consume the Not(...)-wrapped occurrences before the bare ones, since
    # the bare pattern is a substring of the wrapped one.
    text = replace_exact(text, TV_NOT_HASVALUE, SHARED_NOT_EXISTS, 3)
    text = replace_exact(text, TV_CLEAR, SHARED_CLEAR, 2)
    text = replace_exact(text, TV_HASVALUE, SHARED_HASVALUE_TV, 2)
    text = replace_exact(text, TV_SET, SHARED_SET_TV, 1)
    return text.splitlines()


def pp_lines() -> list[str]:
    return PP_FILE.read_text(encoding="utf-8-sig").splitlines()


def pp_tab_button_block(lines: list[str]) -> list[str]:
    start, end = PP_TAB_BUTTON_RANGE
    block = "\n".join(lines[start:end])
    block = replace_exact(block, PP_SET, SHARED_SET_PP, 1)
    block = replace_exact(block, PP_HASVALUE, SHARED_HASVALUE_PP, 1)
    return block.splitlines()


def pp_mod_content_block(lines: list[str]) -> list[str]:
    start, end = PP_MOD_CONTENT_RANGE
    block = "\n".join(lines[start:end])
    block = replace_exact(block, PP_HASVALUE, SHARED_HASVALUE_PP, 1)
    return block.splitlines()


def insert_pp_tab_button(tv_lines: list[str], pp_button_lines: list[str]) -> list[str]:
    anchor_idx = tv_lines.index(NAV_SCROLLBOX_ANCHOR)
    return tv_lines[:anchor_idx] + pp_button_lines + [""] + tv_lines[anchor_idx:]


def insert_pp_mod_content(tv_lines: list[str], pp_content_lines: list[str]) -> list[str]:
    # The last 7 lines of TV's file close, in order: the TV Mod Content vbox, the
    # "current" vbox, the "main" hbox, the wrapping vbox, blockoverride "panel_content",
    # and lateralview_full. Splice PP's Mod Content vbox in right after the TV Mod
    # Content vbox closes (i.e. between the first and second of those 7 lines).
    tail = tv_lines[-6:]
    body = tv_lines[:-6]
    expected_tail = [
        "                    }",
        "                }",
        "            }",
        "\t\t}",
        "\t}",
        "}",
    ]
    if tail != expected_tail:
        raise RuntimeError(
            "TV encyclopedia_lateralview.gui tail structure changed -- re-derive the "
            "Mod Content insertion point before regenerating."
        )
    return body + [""] + pp_content_lines + tail


def generate() -> str:
    tv_lines = merged_tv_lines()
    source_pp_lines = pp_lines()
    tv_lines = insert_pp_tab_button(tv_lines, pp_tab_button_block(source_pp_lines))
    tv_lines = insert_pp_mod_content(tv_lines, pp_mod_content_block(source_pp_lines))

    lines = render_header(SCRIPT_REL, DATA_REL)
    lines.append("\n".join(tv_lines))
    return "\n".join(line.rstrip() for line in "\n".join(lines).splitlines()).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
