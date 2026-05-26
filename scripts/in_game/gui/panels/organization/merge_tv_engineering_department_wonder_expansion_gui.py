import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[5]
MAIN_FILE = REPO_ROOT / "src" / "in_game" / "gui" / "panels" / "organization" / "tv_engineering_department.gui"
FRAGMENT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_engineering_department_wonder_expansion.gui"


MARKERS = {
    "TV_WONDER_EXPANSION_PREVIEW_WIDGETS": 'widget = {\n\t\t\t\t\tvisible = "[Or(And(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').IsSet, EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').GetValue, \'(CFixedPoint)18.0\')), And3(Not(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').IsSet), InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_proposal\').IsSet, EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_proposal\').GetValue, \'(CFixedPoint)18.0\')))]"\n\t\t\t\t\tsize = { 100% 100% }\n\t\t\t\t\tbackground = {\n\t\t\t\t\t\ttexture = "gfx/interface/illustrations/towards_victory/wonders/tv_wonder_test.dds"\n\t\t\t\t\t\ttexture_density = 2\n\t\t\t\t\t\tfittype = centercrop\n\t\t\t\t\t}\n\t\t\t\t}',
    "TV_WONDER_EXPANSION_PROPOSAL_TEXTS": 'text_multi = { visible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_proposal\').GetValue, \'(CFixedPoint)18.0\')]" max_width = 352 autoresize = yes text = "TV_ENGINEERING_PROPOSAL_LIBRARY_TEXT" align = nobaseline|left }',
    "TV_WONDER_EXPANSION_PROPOSAL_RESUME_TEXTS": 'text_multi = { visible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_proposal\').GetValue, \'(CFixedPoint)18.0\')]" max_width = 352 autoresize = yes text = "TV_ENGINEERING_PROPOSAL_RESUME_LIBRARY_TEXT" align = nobaseline|left }',
    "TV_WONDER_EXPANSION_PROPOSAL_EXPAND_TEXTS": 'text_multi = { visible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_proposal\').GetValue, \'(CFixedPoint)18.0\')]" max_width = 352 autoresize = yes text = "TV_ENGINEERING_PROPOSAL_EXPAND_LIBRARY_TEXT" align = nobaseline|left }',
    "TV_WONDER_EXPANSION_LOCKED_TEXTS": 'text = "TV_ENGINEERING_LOCKED_LIBRARY_TEXT"\n\t\t\t\t\t\t\t\t\t\t\talign = nobaseline|left\n\t\t\t\t\t\t\t\t\t\t}',
    "TV_WONDER_EXPANSION_PROPOSAL_BUTTONS": 'action_button_diamond = { size = { 152 30 } visible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_proposal_slot_3\').GetValue, \'(CFixedPoint)18.0\')]" text = "TV_ENGINEERING_PROPOSAL_BUTTON_LIBRARY" title = "tv_wonder_select_proposal_slot_3" description = "tv_wonder_select_proposal_slot_3_desc" actor = "[InternationalOrganizationsView.GetPlayer]" left_action = { action_name = "tv_wonder_select_proposal_slot_3" } }',
    "TV_WONDER_EXPANSION_CEREMONY_STYLE_1_BUTTONS": 'action_button_diamond = {\n\t\t\t\t\t\t\t\t\t\t\tvisible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').GetValue, \'(CFixedPoint)18.0\')]"\n\t\t\t\t\t\t\t\t\t\t\tsize = { 150 30 }\n\t\t\t\t\t\t\t\t\t\t\ttext = "TV_ENGINEERING_CEREMONY_NATIONAL_CATALOG_BUTTON"\n\t\t\t\t\t\t\t\t\t\t\tdown = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_ceremony_style\').GetValue, \'(CFixedPoint)1.0\')]"\n\t\t\t\t\t\t\t\t\t\t\ttitle = "tv_wonder_choose_ceremony_style_1"\n\t\t\t\t\t\t\t\t\t\t\tdescription = "tv_wonder_choose_ceremony_style_1_desc"\n\t\t\t\t\t\t\t\t\t\t\tactor = "[InternationalOrganizationsView.GetPlayer]"\n\t\t\t\t\t\t\t\t\t\t\tleft_action = { action_name = "tv_wonder_choose_ceremony_style_1" }\n\t\t\t\t\t\t\t\t\t\t}',
    "TV_WONDER_EXPANSION_CEREMONY_STYLE_2_BUTTONS": 'action_button_diamond = {\n\t\t\t\t\t\t\t\t\t\t\tvisible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').GetValue, \'(CFixedPoint)18.0\')]"\n\t\t\t\t\t\t\t\t\t\t\tsize = { 150 30 }\n\t\t\t\t\t\t\t\t\t\t\ttext = "TV_ENGINEERING_CEREMONY_COPYISTS_ENDOWMENT_BUTTON"\n\t\t\t\t\t\t\t\t\t\t\tdown = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_ceremony_style\').GetValue, \'(CFixedPoint)2.0\')]"\n\t\t\t\t\t\t\t\t\t\t\ttitle = "tv_wonder_choose_ceremony_style_2"\n\t\t\t\t\t\t\t\t\t\t\tdescription = "tv_wonder_choose_ceremony_style_2_desc"\n\t\t\t\t\t\t\t\t\t\t\tactor = "[InternationalOrganizationsView.GetPlayer]"\n\t\t\t\t\t\t\t\t\t\t\tleft_action = { action_name = "tv_wonder_choose_ceremony_style_2" }\n\t\t\t\t\t\t\t\t\t\t}',
    "TV_WONDER_EXPANSION_CEREMONY_STYLE_3_BUTTONS": 'action_button_diamond = {\n\t\t\t\t\t\t\t\t\t\t\tvisible = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').GetValue, \'(CFixedPoint)18.0\')]"\n\t\t\t\t\t\t\t\t\t\t\tsize = { 150 30 }\n\t\t\t\t\t\t\t\t\t\t\ttext = "TV_ENGINEERING_CEREMONY_LEGAL_DEPOSIT_BUTTON"\n\t\t\t\t\t\t\t\t\t\t\tdown = "[EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_ceremony_style\').GetValue, \'(CFixedPoint)3.0\')]"\n\t\t\t\t\t\t\t\t\t\t\ttitle = "tv_wonder_choose_ceremony_style_3"\n\t\t\t\t\t\t\t\t\t\t\tdescription = "tv_wonder_choose_ceremony_style_3_desc"\n\t\t\t\t\t\t\t\t\t\t\tactor = "[InternationalOrganizationsView.GetPlayer]"\n\t\t\t\t\t\t\t\t\t\t\tleft_action = { action_name = "tv_wonder_choose_ceremony_style_3" }\n\t\t\t\t\t\t\t\t\t\t}',
    "TV_WONDER_EXPANSION_ACTIVE_RITUAL_TEXTS": 'text_multi = { visible = "[And(EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').GetValue, \'(CFixedPoint)18.0\'), EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_ceremony_style\').GetValue, \'(CFixedPoint)3.0\'))]" max_width = 446 autoresize = yes text = "TV_ENGINEERING_ACTIVE_RITUAL_LEGAL_DEPOSIT" align = nobaseline|left }',
    "TV_WONDER_EXPANSION_HOLD_BUTTONS": 'action_button_diamond = { visible = "[And(EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_locked\').GetValue, \'(CFixedPoint)18.0\'), EqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable(\'tv_wonder_ceremony_style\').GetValue, \'(CFixedPoint)3.0\'))]" size = { 180 30 } text = "TV_ENGINEERING_HOLD_CEREMONY_BUTTON" title = "tv_wonder_start_legal_deposit" description = "tv_wonder_start_legal_deposit_desc" actor = "[InternationalOrganizationsView.GetPlayer]" left_action = { action_name = "tv_wonder_start_legal_deposit" } }',
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


def replace_existing_segment(text: str, marker: str, block: str) -> tuple[str, bool]:
    begin = f"# BEGIN GENERATED {marker}"
    end = f"# END GENERATED {marker}"
    pattern = re.compile(rf"\n(?P<indent>[ \t]*){re.escape(begin)}\n.*?\n(?P=indent){re.escape(end)}", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return text, False
    indent = match.group("indent")
    replacement = f"\n{indent}{begin}\n{indent_block(block, indent)}\n{indent}{end}"
    return text[: match.start()] + replacement + text[match.end():], True


def insert_after_anchor(text: str, marker: str, anchor: str, block: str) -> str:
    if anchor not in text:
        raise ValueError(f"Anchor for {marker} not found")
    index = text.index(anchor) + len(anchor)
    line_start = text.rfind("\n", 0, text.index(anchor)) + 1
    indent = text[line_start:text.index(anchor)]
    segment = f"\n{indent}# BEGIN GENERATED {marker}\n{indent_block(block, indent)}\n{indent}# END GENERATED {marker}"
    return text[:index] + segment + text[index:]


def main() -> None:
    text = MAIN_FILE.read_text(encoding="utf-8")
    fragment = FRAGMENT_FILE.read_text(encoding="utf-8")
    for marker, anchor in MARKERS.items():
        block = extract_fragment(marker, fragment)
        text, replaced = replace_existing_segment(text, marker, block)
        if not replaced:
            text = insert_after_anchor(text, marker, anchor, block)
    MAIN_FILE.write_text(text, encoding="utf-8")
    print(f"Merged {FRAGMENT_FILE.relative_to(REPO_ROOT)} into {MAIN_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
