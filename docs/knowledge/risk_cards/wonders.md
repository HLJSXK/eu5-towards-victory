# Wonders / Engineering Department Risk Card

Load this card before editing any file with `wonder` or `engineering_department` in its
filename: generated `scripted_effects`, `scripted_triggers`, `static_modifiers`,
`auto_modifiers`, `building_types`, `generic_actions`, `game_concepts`, and `gui` files under
`common/`, their localization, `src/in_game/gui/location_window.gui`, and the
`data/wonder*.yaml` / `data/unique_wonder*.yaml` sources plus their `scripts/*wonder*.py`
generators.

## Required Checks

1. Split local effects from national effects at the building level.
   `capital_country_modifier` only applies its country-wide effects when the building is
   actually built in the capital. Engineering Department wonders can be sited outside the
   capital, so a final/helper building's `modifier` and `raw_modifier` may only carry local,
   per-level or flat ceremony effects. Never put a global/national wonder effect directly on
   a wonder building. Apply all national/global wonder effects through permanent country
   modifiers, driven by building-gated Country Auto modifiers and applied during
   finalization.

2. Keep fixed-value wonder modifiers at or below 0.5.
   EU5 multiplies `global_pop_assimilation_speed`, `global_pop_conversion_speed`,
   `local_pop_assimilation_speed`, `local_pop_conversion_speed`, `local_manpower`, and
   `local_sailors` by 1000 in game when used as fixed values. Keep these at or below `0.5`;
   use the matching `*_modifier` percent variant when a percentage was intended.
   `validate.py` lints this (`wonder_fixed_modifier_thousand_scaled_value`) for direct
   assignments in wonder-path `src/`/`data/` files.

3. Read actual employment, not nominal level capacity.
   `location_building_level` reports completed levels/capacity, not current staffing. For
   labor-sensitive Engineering Department mechanics, scope into the building object with
   `ordered_buildings_in_location` / `random_buildings_in_location` and read
   `building_employed_amount` (multiply by 1000 if the target variable is stored in people
   rather than pop-size units).

4. Treat `instant = yes` construction as asynchronous.
   `construct_building instant = yes` and `change_building_level_in_location` queue a 0-day
   task; they do not update `location_building_level` synchronously inside the same effect. Do
   not write a `while` loop that waits for the level to catch up — it can deadlock or spin
   forever. Use fixed `if`/`else_if` branches or a bounded script-value delta so the effect
   runs once.

5. Use `on_construction_ended` for ritual/annex completion that also covers upgrades.
   `on_built` alone is not a reliable completion signal when the same mechanic also upgrades
   an existing building to a higher level (the annex building is reused, not rebuilt). Use
   `on_construction_ended` to mark the active ritual/annex finished directly, and do not
   assume `location_building_level` has updated inside that hook either.

6. Enter the owner explicitly from a location-rooted tooltip effect.
   When GUI passes the location itself as the scripted-effect scope (for example
   `ShowScriptedEffectForScope` with `LocationView.GetLocation.MakeScope.Self`), a dotted
   `location.owner` chain is parsed as an event-target link named `location`, which is invalid
   from a location root. Use `owner ?= { ... }` to enter the owning country instead. Reserve
   `location.owner` for contexts that expose a separate location event target, such as
   building `on_built`.

7. Keep third-person effect localization self-contained.
   Generic action hover pre-evaluation can select the `third`/`third_past` effect-localization
   perspective for a wonder `custom_description` (e.g. ceremony demand acceptance tooltips)
   before any `COUNTRY` promote target exists. Do not use `[COUNTRY.GetName]` in those
   perspective strings; keep them self-contained (`Gains $VALUE|+$ #Y $var$#!`).

8. Register every `custom_description` effect text key in `effect_localization`.
   Any wonder/Engineering Department `custom_description` used inside a `scripted_effect` —
   including plain narration text with no `value =`, not only IO-style variable-change
   tooltips — needs its `text` key registered under
   `src/in_game/common/effect_localization/` with at least a `global` perspective, or the
   engine logs `No effect loc <key>` and the tooltip renders empty. `validate.py` does not yet
   check this for effect files (only `check_trigger_loc_coverage()` for
   `scripted_triggers/` exists); verify manually until that checker is added — see
   `docs/knowledge/risk_cards/philosophy_debate.md` rule 1 for the confirmed live instance of
   this gap.

9. Keep event-option `hidden_effect` cheap; it is not a performance boundary.
   Option hover rendering still evaluates blocks inside `hidden_effect`. Do not put the
   expensive per-wonder/per-style finalization chain (construction, cleanup, broadcast,
   cache, project-clear) directly in an option's `hidden_effect`. Have the option call a light
   hidden scheduler that triggers a `hidden = yes` event, and put the heavy chain in that
   event's `immediate` block instead.

10. Prefer literal per-level branches over scratch merge/rebuild variables.
    For bounded wonder-module merges, rebuilds, or partially-built reinitialization, avoid
    computing a derived value into a temporary variable (`*_combinable_levels`,
    `*_helper_extra_levels`, `*_helper_current_level`, `*_target_module_level`) and reading it
    back later in the same visible chain — action/option tooltip pre-evaluation can log
    invalid-left-side or unset-variable errors before the write commits. Emit one literal
    `if`/`else_if` branch per level with fixed building deltas from persistent state instead.

11. Bound Engineering Department card text width explicitly.
    Do not put paragraph-style localized text in an unconstrained `hbox` elastic column (a
    `layoutpolicy_horizontal = expanding` child can pull its natural text width back into the
    row and blow out a bounded parent card). Use a fixed-width `text_multi` container with
    `max_width` and `autoresize`.

12. Respect the Unique Wonder Ritual Harness phase freeze.
    Before touching `data/unique_wonder_ritual_*.yaml` or `scripts/gen_unique_wonder_ritual_*.py`,
    read `docs/guides/Unique_Wonder_Ritual_Harness.md`. Do not promote a spec's readiness tier
    (`compiler_mapped` → `source_codegen_ready` → `implemented_parity`) or set any template,
    capability, archetype, or generator's `may_write_src` to `true` without an explicit
    source-writer contract naming the EU5 interfaces, generator ownership, and validation
    gate. Do not flatten a spec's high-fidelity `design_ir` / `tracked_entity_sets` projection
    into simpler aggregate variables merely to make codegen easier.

## Validation

Run `validate.py --changed --fix --ai-report`: it lints rule 2 automatically and, when a
`data/unique_wonder_ritual_*.yaml` or harness script changes, runs
`wonder_unique_ritual_harness.validate_unique_ritual_specs_for_repo()`. Also run
`scripts/test_wonder_mechanics_rules.py` after changing scale-based wonder trigger/effect
generators. Rules 6–11 have no automated check; inspect the affected tooltip, hover state, or
GUI layout in game after any change in those areas.
