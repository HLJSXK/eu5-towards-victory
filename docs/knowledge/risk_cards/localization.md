# Localization Risk Card

Load this card before writing or editing any player-facing localization text under
`src/main_menu/localization/` (both `english/` and `simp_chinese/`), or before adding loc
strings inline while generating events, GUI, effects, or other content that produces new
localization keys.

## Required Checks

1. **Use the canonical six-way text-formatting mapping — do not invent or repurpose tags.**
   TV has a fixed semantic mapping from meaning to EU5's `#tag content#!` color/style tags,
   documented in full in `CLAUDE.md` section "Localization Text Formatting Convention":

   | Semantic need | Tag |
   |---|---|
   | Positive effect (gain/bonus) | `#G` |
   | Negative effect (loss/malus) | `#R` |
   | Neutral highlighted value/keyword (cost, threshold, non-judged number) | `#Y` |
   | Important content (pure emphasis, no valence) | `#high` |
   | Beginner tip / guidance text | `#weak` |
   | Pure flavor text (wonder descriptions, etc.) | `#F` |

   Do not use `#G`/`#R` for neutral numbers (a cost or requirement is not "positive" or
   "negative"). Do not use `#W`, `#X`, `#P`/`#N`, `#L`, or `#V` for any of the six needs above
   — those tags are reserved for their narrower vanilla roles (difficulty labels, danger
   warnings, enabled/disabled labels, secondary de-emphasis, alternate highlight). Trigger/requirement
   text inside `custom_tooltip`/`trigger` blocks must NOT be manually tagged with this table —
   the engine already colors it via `#trigger_pass`/`#trigger_fail`, and manual tags conflict
   with that automatic coloring. If a genuinely new semantic need doesn't fit these six rows
   (e.g. an irreversible-action risk warning distinct from a stat-based negative effect), ask
   before assigning it a tag rather than silently reusing an existing row for a different
   meaning.

2. **Always separate a color/style tag from its content with a space.**
   `#Y Text#!`, `#G {group}#!`, `#R 30#!` are correct; `#YText#!`, `#G{group}#!`, `#R30#!` are
   not — the parser reads the tag name as everything up to the first non-alphanumeric
   character, so adjacent content gets absorbed into the tag name and dropped or mangled. This
   applies equally to hand-written localization and to codegen that substitutes a generated
   name/value into colored text. See `docs/knowledge/anti_patterns.yaml` rules
   `loc_color_tag_adjacent_text` / `loc_color_tag_adjacent_variable`.

3. **File encoding and quoting.** Localization YAML must be UTF-8 **with BOM**, and only
   straight ASCII double-quotes (`"`) are valid — smart/curly quotes silently break parsing.
   Keep each key/value on one physical line; use `\n` inside the quoted string for an
   intentional line break, not a real newline (a real newline makes the next physical line
   parse as a new key).

4. **Full tag catalog reference.** For the complete list of available `#tag` values (including
   ones not part of TV's six-way mapping, like `#T` tooltip headers, `#col`/`#col_t`/`#col_m`
   tabular tags, and `#TOOLTIP:$TAG$...#!` breakdowns), see
   `docs/technical/EU5_Modding_Knowledge_Base.md` section 6.3 "Text Format Tag Catalog" before
   inventing a bespoke display solution.

5. **A YAML loc key alone is not enough for scripted-effect tooltips.** Any
   `custom_description = { text = KEY ... }` inside `common/scripted_effects` needs a matching
   `KEY = { ... }` registration entry under `in_game/common/effect_localization/` — the YAML
   string is only the display text, not the registry entry the engine validates at load.
   Missing the registration produces `No effect loc KEY` /
   `PostValidate of effect 'custom_description' returned false`. Register all four perspectives
   (`none`/`global`/`first`/`third`) as a safe default, and give positive/negative variants of
   the same event/effect **distinct** loc ids (`..._neg`, `..._past_neg`, etc.) — reusing one id
   for both produces `Negative and positive version share loc for effect loc <key>`. For
   third-person perspectives (`third`/`third_past`), keep the string self-contained (no
   `[COUNTRY.GetName]`-style promotes) since generic-action/event hover tooltips can
   pre-evaluate `custom_description` before a real `COUNTRY` promote target exists. See
   `docs/technical/EU5_Modding_Knowledge_Base.md` §6.1 "Scripted Effect `custom_description`
   Localization" and the risk cards for `philosophy_debate`/`wonders`, which hit this
   repeatedly.

6. **Trigger tooltips need a `trigger_localization` entry, not just a YAML key.** A
   `custom_description`/`custom_tooltip` referencing a trigger's loc key needs a matching entry
   in `src/in_game/common/trigger_localization/`; declare all four perspectives
   (`none`/`global`/`first`/`third`) as the safe default even if only `global` is currently used.

7. **`.tt`-suffixed `custom_tooltip` keys are a naming convention only — not auto-wired.** A key
   like `my_event.1.a.tt` must still be referenced explicitly via `custom_tooltip = my_event.1.a.tt`
   inside the option/effect block; the engine does not pick up `.tt`-suffixed keys automatically
   just because they exist in the YAML.

8. **`customizable_localization` files are non-additive database entries, not merge blocks.**
   Each top-level block name (e.g. `character_title_prefix`) in
   `in_game/common/customizable_localization/` is a single database key. Adding a second file
   with the same block name does not merge with the first — the engine logs
   `Duplicated key <block_name> will not be created` and silently drops the duplicate. To extend
   existing customizable localization (e.g. add title text), edit/copy the full original block
   rather than adding a second file.

9. **Every generated modifier/database id needs its matching `_NAME_<id>` (and, for static
   modifiers, `_DESC_<id>`) loc key in every supported language** — this applies to
   `static_modifier` (`STATIC_MODIFIER_NAME_<id>`), `auto_modifiers`
   (`AUTO_MODIFIER_NAME_<id>`), and action price modifier types
   (`MODIFIER_TYPE_NAME_<id>_cost_modifier` / `MODIFIER_TYPE_DESC_<id>_cost_modifier`). Missing
   entries are silent in-game (blank/id-string display) rather than a load error, so a generator
   emitting a new id must emit its loc key in the same change.

10. **Do not chain `MakeScope` after an already-scripted-scope object in event localization.**
    `ROOT.MakeScope.GetVariable(...)` / `THIS.MakeScope.GetVariable(...)` treats an
    already-scoped object as if it were a GUI-layer binding and logs
    `Could not find promote for 'MakeScope'` / `Failed converting statement`. Read
    `ROOT.GetVariable(...)` / `THIS.GetVariable(...)` directly; reserve `.MakeScope` chains
    (`Country.MakeScope.GetVariable(...)`, `Location.MakeScope.GetVariable(...)`,
    `Player.MakeScope.GetVariable(...)`) for GUI-layer bindings that are not already a script
    scope.

## Validation

Run `validate.py --changed --fix --ai-report` after any localization change — it lints the
adjacent-tag rule, BOM encoding, and `effect_localization`/`trigger_localization` coverage for
`custom_description` keys (including the positive/negative distinct-id rule from check 5). There
is no automated lint for tag *semantic* misuse (e.g. using `#G` on a neutral cost value) or for
the `customizable_localization` non-additive-block rule in check 8; apply those by reading intent
and by grepping for an existing block name before adding a new customizable-localization file.
