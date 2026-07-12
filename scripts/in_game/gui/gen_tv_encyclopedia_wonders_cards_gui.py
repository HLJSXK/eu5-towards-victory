"""Generate the "Towards Victory" Europedia tab card list as a standalone fragment.

Merged into src/in_game/gui/encyclopedia_lateralview.gui (a hand-authored full
override of the vanilla Europedia panel -- EU5 has no native, data-driven way to
register a new Encyclopedia sidebar page/category, see
docs/knowledge/risk_cards/europedia.md) by
scripts/in_game/gui/merge_tv_encyclopedia_wonders_cards_gui.py, which inserts or
replaces a `# BEGIN/END GENERATED TV_ENCYCLOPEDIA_CARDS` marker pair right after
the `# TV_ENCYCLOPEDIA_CARDS_ANCHOR` comment in that shell file.

One card per entry, in three groups: the fixed Engineering Department mechanic
concepts (MECHANICS below, textures mirrored from
src/main_menu/common/game_concepts/tv_game_concepts.txt -- not re-derived), then
every generic wonder archetype, then every unique wonder, both from the shared
wonder_mechanics data package (the same merged list
gen_tv_engineering_department_wonder_mechanics_concepts.py already uses). Every
card reuses an EXISTING game_concept_<id>/_desc localization pair -- no new
prose is authored here. Each card is gated by a `tv_encyclopedia_filter` value
('mechanics' / 'generic' / 'unique') so the shell's filter buttons can show it.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.io import load_all_wonder_mechanics_data  # noqa: E402
from wonder_mechanics.render import render_header  # noqa: E402
from wonder_image_crop_lib import cropped_wonder_image_name  # noqa: E402

OUT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_encyclopedia_wonders_cards.gui"
SCRIPT_REL = "scripts/in_game/gui/gen_tv_encyclopedia_wonders_cards_gui.py"
MARKER = "TV_ENCYCLOPEDIA_CARDS"
T = "\t"

MECHANICS_TEXTURE = "gfx/interface/icons/location_icons/new/prosperity.dds"
MECHANICS = [
    "tv_engineering_department",
    "tv_great_engineer",
    "tv_wonder_concept",
    "tv_wonder_survey",
    "tv_wonder_materials",
    "tv_wonder_ceremony",
    "tv_wonder_construction",
    "tv_wonder_construction_part",
    "tv_wonder_small",
    "tv_wonder_medium",
    "tv_wonder_large",
    "tv_wonder_domestic_support",
    "tv_wonder_scale_competence",
    "tv_wonder_organization_competence",
    "tv_wonder_logistics_competence",
]


def wonder_icon_texture(wonder: dict) -> str:
    image = wonder.get("image", f"tv_wonder_{wonder['key']}")
    return f"gfx/interface/icons/towards_victory/wonders/{cropped_wonder_image_name(image)}.dds"


def append_card(lines: list[str], *, category: str, texture: str, title_key: str, body_key: str) -> None:
    lines.append(f"{T}vbox = {{")
    lines.append(
        f"{T}{T}visible = \"[Or(GetVariableSystem.HasValue('tv_encyclopedia_filter', 'all'), GetVariableSystem.HasValue('tv_encyclopedia_filter', '{category}'))]\""
    )
    lines.append(f"{T}{T}set_parent_size_to_minimum = yes")
    lines.append(f"{T}{T}margin = {{ 0 10 }}")
    lines.append("")
    lines.append(f"{T}{T}vbox = {{")
    lines.append(f"{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}{T}{T}spacing = 10")
    lines.append(f"{T}{T}{T}using = bg_paper_card")
    lines.append("")
    lines.append(f"{T}{T}{T}blockoverride \"card_color\" {{")
    lines.append(f"{T}{T}{T}{T}using = color_intense_bg_blue_texture")
    lines.append(f"{T}{T}{T}{T}blend_mode = multiply")
    lines.append(f"{T}{T}{T}}}")
    lines.append("")
    lines.append(f"{T}{T}{T}max_width = 1450")
    lines.append(f"{T}{T}{T}min_width = 1450")
    lines.append("")
    lines.append(f"{T}{T}{T}icon = {{")
    lines.append(f"{T}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}{T}{T}{T}using = button_main_tab_texture")
    lines.append(f"{T}{T}{T}{T}frame = 4")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}using = color_intense_bg_blue_texture")
    lines.append(f"{T}{T}{T}{T}{T}blend_mode = multiply")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}using = overlay_leather_texture")
    lines.append(f"{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}alpha = 0.2")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}hbox = {{")
    lines.append(f"{T}{T}{T}{T}{T}margin = {{ 40 0 }}")
    lines.append(f"{T}{T}{T}{T}{T}margin_top = 8")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}{T}icon = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}name = \"image\"")
    lines.append(f'{T}{T}{T}{T}{T}{T}texture = "{texture}"')
    lines.append(f"{T}{T}{T}{T}{T}{T}size = {{ 45 45 }}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}{T}text_single = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}name = \"title\"")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = layoutpolicy_expanding")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = Font_Size_Medium")
    lines.append(f"{T}{T}{T}{T}{T}{T}fontsize = 18")
    lines.append(f"{T}{T}{T}{T}{T}{T}autoresize = no")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}{T}{T}default_format = \"#yellow_titles\"")
    lines.append(f'{T}{T}{T}{T}{T}{T}text = "{title_key}"')
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append("")
    lines.append(f"{T}{T}{T}TooltipListScrollArea = {{")
    lines.append(f"{T}{T}{T}{T}blockoverride \"scrollarea_content\" {{")
    lines.append(f"{T}{T}{T}{T}{T}vbox = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}set_parent_dimension_to_minimum = height")
    lines.append(f"{T}{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append("")
    lines.append(f"{T}{T}{T}{T}{T}{T}text_multi = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}name = \"body\"")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}max_width = 1450")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}min_width = 1450")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}autoresize = yes")
    lines.append("")
    lines.append(f'{T}{T}{T}{T}{T}{T}{T}text = "{body_key}"')
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}margin = {{ 40 10 }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}block \"block_scrollarea\" {{")
    lines.append(f"{T}{T}{T}{T}{T}maximumsize = {{ -1 800 }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def generate() -> str:
    wonders, _ = load_all_wonder_mechanics_data()
    lines = render_header(SCRIPT_REL)
    lines.append(f"# BEGIN GENERATED {MARKER}")
    lines.append("vbox = {")
    lines.append(f"{T}using = layoutpolicy_expanding")
    lines.append(f"{T}set_parent_dimension_to_minimum = height")
    lines.append(f"{T}spacing = 4")
    lines.append("")

    for concept in MECHANICS:
        append_card(
            lines,
            category="mechanics",
            texture=MECHANICS_TEXTURE,
            title_key=f"game_concept_{concept}",
            body_key=f"game_concept_{concept}_desc",
        )
        lines.append("")

    for wonder in wonders:
        category = "unique" if wonder["is_unique"] else "generic"
        append_card(
            lines,
            category=category,
            texture=wonder_icon_texture(wonder),
            title_key=f"game_concept_{wonder['concept']}",
            body_key=f"game_concept_{wonder['concept']}_desc",
        )
        lines.append("")

    lines.append("}")
    lines.append(f"# END GENERATED {MARKER}")
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
