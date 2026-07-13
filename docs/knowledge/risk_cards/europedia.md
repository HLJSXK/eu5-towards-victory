# Europedia Risk Card

Load this card before editing `encyclopedia_lateralview.gui`, adding new browsable Europedia
content, or wiring any `game_concept` into a curated (as opposed to search/link-only) display.

## Required Checks

1. There is no native, data-driven way to add an Encyclopedia sidebar page/category.
   `Encyclopedia.AccessPages` / `EncyclopediaPage` is a read-only, engine-populated collection
   (`GetTitle`, `Self`, `AccessSelf` only — no `AddPage`/`RegisterPage`). A `game_concept` block's
   `family` field is a loose thematic tag with no page/category effect in vanilla's own
   `encyclopedia_lateralview.gui`. Do not search for a registry folder or a `page =` field — none
   exists. See anti-pattern `europedia_page_has_no_native_registration`.

2. A dedicated browsable tab requires a full override of `in_game/gui/encyclopedia_lateralview.gui`
   using the `GetVariableSystem`-toggle pattern (the only working precedent found, confirmed
   against released community mod `3613232232`): one button sets a toggle variable
   (`GetVariableSystem.Set('<var>', 'yes')`), vanilla content and the custom content become two
   sibling `vbox`es with mutually exclusive `visible = "[GetVariableSystem.HasValue(...)]"` /
   `"[Not(GetVariableSystem.HasValue(...))]"` guards, and every vanilla sidebar button additionally
   gets `onclick = "[GetVariableSystem.Clear('<var>')]"` so clicking back into a real page exits the
   custom view. `src/in_game/gui/encyclopedia_lateralview.gui` implements this with
   `tv_encyclopedia_active` (tab toggle) and `tv_encyclopedia_filter` (all/mechanics/generic/unique
   category filter buttons within the tab).

3. Preserve vanilla's `default_format = "#yellow_titles"` exactly on card titles.
   The reference mod's own copy of this line dropped the leading `#` (`"yellow_titles"`) — a
   drift, not an intentional variant. Copy the vanilla card template verbatim for this field.

4. Custom cards reference existing localization via literal `text = "game_concept_<id>"` /
   `"game_concept_<id>_desc"` widget fields, not `[id|e]` link syntax.
   This is a plain `text_single`/`text_multi` `text=` lookup (same mechanism vanilla's own card
   template uses via `EncyclopediaEntry.GetTitle`/`GetBody`), distinct from `[id|e]` cross-link
   markup used inside body prose elsewhere. The `id` still needs a real registered `game_concept`
   block for the key to resolve — reusing an already-registered concept's keys (as this mod's tab
   does) needs no new concept registration, only the two loc keys to already exist.

   For the fixed Engineering Department / Great Project mechanic cards specifically (the
   `MECHANICS` list in `gen_tv_encyclopedia_wonders_cards_gui.py`), a concept in that
   generator's `EXPANDED_MECHANICS` set uses an optional third key,
   `game_concept_<id>_europedia_desc`, as its card body instead of `_desc`
   (`body_key_for()` picks the key). This lets Europedia carry a longer, more detailed
   explanation than the concise `_desc` used for in-game tooltips/`[id|e]` cross-links
   elsewhere, without lengthening the tooltip text itself. Only add `_europedia_desc` for
   ids in `EXPANDED_MECHANICS`; concepts outside that set fall back to the normal `_desc` and
   need no extra key. Ground any new `_europedia_desc` prose in confirmed mechanic facts from
   `docs/knowledge/PROJECT_OVERVIEW.md` / `docs/knowledge/risk_cards/wonders.md` — do not
   invent numbers or behavior not already documented there.

5. Bound card text width explicitly (shared with `docs/knowledge/risk_cards/wonders.md` rule 11).
   Use `text_multi` with matching `max_width`/`min_width` (1450, matching vanilla) and
   `autoresize = yes`; an unconstrained elastic `hbox`/`vbox` column can blow out a card's bounded
   width.

6. Do not build per-entry texture paths with a runtime `Concatenate` inside `texture =`.
   Since a custom card list this size (100+ entries) is always machine-generated from data already
   available at generation time, bake each entry's literal DDS path into the generated `.gui` text
   directly (as `gen_tv_encyclopedia_wonders_cards_gui.py` does via `wonder.get("image")`/
   `wonder['key']`) rather than reaching for a dynamic `Concatenate(...)` expression at GUI-eval
   time, which renders blank (see `docs/knowledge/risk_cards/gui.md` rule 19).

7. Preserve the scrollbox sizing contract on custom content. The custom tab's visible root and
   its `scrollbox` must use `layoutpolicy_expanding`; the static card-list root inside
   `scrollbox_content` must also use it and set `set_parent_dimension_to_minimum = height`.
   Each filter `button_regular` needs `layoutpolicy_horizontal = expanding`. Otherwise the
   scrollbox receives no stable content height and the cards/buttons can collapse into the panel's
   upper-left corner. This follows the same expanding-content shape used by vanilla
   `ui_library.gui`.

## Validation

Run `validate.py --changed --fix --ai-report`, then manually open the Europedia panel in-game,
click the custom tab and each filter button, scroll the full card list, and hover a few cards —
text-width and blank-icon failures typically only surface on render/hover, not statically.

## Relevant Anti-Patterns

- `europedia_page_has_no_native_registration` [advisory]: no data-driven Encyclopedia page
  registration point exists; a custom tab requires the full-panel `GetVariableSystem`-toggle
  override described above.
