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
   `src/in_game/common/effect_localization/` with at least a `global` perspective — the same
   requirement `check_trigger_loc_coverage()` already enforces for `scripted_triggers` against
   `trigger_localization/`, but there is currently no equivalent check for effects. **This is
   a confirmed, currently-live gap**: as of this session's `docs/error_log/error.log`, all 36
   seat/group `_seated_text` / `_left_text` keys are missing their `effect_localization`
   registration and log `No effect loc <key>` at runtime, even though the player-facing
   strings exist correctly in `tv_academy_philosophy_debate_l_english.yml` /
   `_l_simp_chinese.yml`. Before adding a new debate group or seat-state text, add its
   `effect_localization` block in the same generator change, not just the localization file
   entries.

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

Run `validate.py --changed --fix --ai-report` after any codegen or data change — it lints
rule 2 (`loc_color_tag_adjacent_text`) automatically. It does **not** yet check rule 1
(effect-localization coverage for effect files); until a `check_effect_loc_coverage()`
equivalent exists, manually grep new `custom_description` keys emitted by
`philosophy_debate_codegen.py` against `src/in_game/common/effect_localization/*.txt` before
considering the task done, and check `docs/error_log/error.log` after an in-game load for
`No effect loc` lines.
