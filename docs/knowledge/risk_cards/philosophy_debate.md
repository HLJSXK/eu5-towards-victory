# Philosophy Debate / Academy World Debate Risk Card

Load this card before editing any file with `philosophy_debate`, `world_debate`, or
`academy_debate` in its filename: `data/philosophy_debates.yaml`,
`data/philosophy_debate_random_events/*.yaml`, `scripts/philosophy_debate_codegen.py`, the
`gen_tv_academy_philosophy_debate_*.py` generators, and their generated `scripted_effects`,
`scripted_triggers`, `static_modifiers`, events, GUI, and localization outputs.

## Required Checks

1. Register every generated `custom_description` text key in `effect_localization`.
   `philosophy_debate_codegen.py` generates seat-state narration through
   `custom_description = { text = <key> }` inside `scripted_effects` (for example
   `tv_academy_debate_group_<key>_seated_text` / `_left_text` from `_seated_text_key()` /
   `_left_text_key()`). Every emitted key needs a matching registration block under
   `src/in_game/common/effect_localization/` with at least a `global` perspective. The
   validator's `check_effect_loc_coverage()` catches missing registrations for scripted-effect
   `custom_description` keys. Before adding a new debate group or seat-state text, add its
   `effect_localization` block in the same generator change, not just the localization file
   entries. Also keep negative perspectives mapped to distinct loc ids: `global_neg`,
   `first_neg`, `third_neg`, `global_past_neg`, `first_past_neg`, and `third_past_neg` must
   not reuse the same loc key as their positive counterparts. The validator's
   `check_effect_loc_negative_perspectives()` catches the startup warning
   `Negative and positive version share loc for effect loc <key>`.

2. Never let generated text sit directly against a color tag.
   `#Y<generated_text>#!` with no separator can have the generated/localized content
   swallowed by or mangled with the color-tag parser. Always insert a literal space after the
   tag (`#Y Text#!`) both in hand-written localization and in `philosophy_debate_codegen.py`
   wherever it substitutes a generated name or stance label into colored text.

3. Keep the local roundtable and world debate on separate scopes.
   The six-seat local roundtable's crown/seat state and progress live on the Academy IO
   (e.g. `tv_academy_philosophy_debate_position`). The fifty-seat world debate mirrors each
   country's stance, strength, and progress onto world Situation variables instead. Do not
   read or write one model's variables when implementing the other's UI or scoring — the
   Academy overview GUI and the world debate Situation panel are generated from
   `data/philosophy_debates.yaml` against these two distinct data shapes.

4. Keep new debate content inside the three fixed timeline stages.
   The Academy overview's five-node timeline is generated as exactly three stage kinds —
   History, Local, World — with the roundtable/grid UI, situation panel, and codegen all
   assuming that fixed three-stage shape. Slot new debate issues or content into one of these
   three stages rather than introducing a fourth stage kind.

5. Variant availability must be mutually exclusive by construction, never by random pick.
   `tv_academy_debate_pick_unseated_*_group_effect` puts every group whose
   `_available_trigger` is true into one equal-weight `random_list`
   (`philosophy_debate_codegen.py` `gen_selection_effects`). A base estate's
   `_available_trigger` therefore must `NOT` every variant sharing its `estate`/`base_estate`
   (see `variants_excluding_estate()`), and each variant must `NOT` every lower-id sibling
   variant sharing its `base_group` (see `variant_condition_lines()` /
   `emit_variant_exclusion()`), so that at most one of {base estate, its variants} is ever
   available for a given country state. Group `id` order (ascending, per `groups(data)`
   sorting by `id`) is the tie-break when two variants' raw conditions can both be true —
   lower id wins. Adding a new variant means adding it to this ordering, not just giving it
   its own condition. Societal-value-driven variants (the `societal_value: {axis, pole}`
   field) use `> 50` / `< -50` on `societal_value:<axis>`; an axis that is age/DLC/culture
   gated in vanilla needs no extra gating here, since `societal_value:<axis>` reads 0
   (neutral, never crosses ±50) for any country where the axis is inactive.

6. Seat-narration tooltips must branch on a variable already persistent before the event opens.
   `gen_group_change_tooltip` (`philosophy_debate_codegen.py`) branches on an id variable to pick
   which group's `_seated_text`/`_left_text` to show. Per the Events risk card rule 1/2, a
   `set_variable` written earlier in the same visible option chain may not be committed yet when
   a later helper in that chain reads it for the tooltip preview — the actual gameplay effect
   still applies correctly, only the preview silently fails to render. When a seat-narration call
   needs to describe a group whose id isn't `tv_academy_debate_event_group` itself (e.g. a second
   simultaneous entrant, or one of several pre-rolled candidates), pass `gen_group_change_tooltip`
   the already-persistent source variable via its `id_var` param (see
   `tv_academy_debate_group2_seated_tooltip_effect` reading `tv_academy_debate_event_group_2`, and
   `tv_academy_debate_royal_option_{slot}_seated_tooltip_effect` reading
   `tv_academy_debate_royal_option_{slot}_group`) instead of overwriting `tv_academy_debate_event_group`
   mid-option and re-reading it with the generic tooltip effect.

7. Quote function-call-style event target links used as script values.
   `emit_crown_contribution_add` and `emit_group_static_formula` (`philosophy_debate_codegen.py`)
   emit `leader_country.estate_power(estate_type:<id>)` as the source of the Crown/Nobility/etc.
   contribution to `tv_academy_philosophy_debate_position.monthly_change`. `estate_power(...)` is
   a parenthesized-argument event target link, not a colon-suffixed one, so the entire
   scope+call expression must be wrapped in double quotes on the RHS of `value =`
   (`value = "leader_country.estate_power(estate_type:crown_estate)"`). Leaving it unquoted
   parses as three separate malformed tokens (`(`, `)`, `=`) and the estate contribution silently
   never applies. See `docs/technical/EU5_Modding_Knowledge_Base.md` section 5.3
   "Function-Call-Style Event Target Links Must Be Quoted".

## Validation

Run `validate.py --changed --fix --ai-report` after any codegen or data change. It lints
rule 2 (`loc_color_tag_adjacent_text`), scripted-effect `custom_description` coverage, and
positive/negative effect-localization loc-id reuse. For new generated seat-state narration,
also inspect the generated `src/in_game/common/effect_localization/*.txt` diff so the
positive and negative perspective mappings remain readable. For a new variant, also grep the
generated `tv_academy_philosophy_debate_triggers.txt` for its `_available_trigger` and its
base estate's `_available_trigger` to confirm the `NOT` exclusion chain from rule 5 above is
present.
