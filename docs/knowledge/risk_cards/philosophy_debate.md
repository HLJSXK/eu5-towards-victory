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

## Validation

Run `validate.py --changed --fix --ai-report` after any codegen or data change. It lints
rule 2 (`loc_color_tag_adjacent_text`), scripted-effect `custom_description` coverage, and
positive/negative effect-localization loc-id reuse. For new generated seat-state narration,
also inspect the generated `src/in_game/common/effect_localization/*.txt` diff so the
positive and negative perspective mappings remain readable.
