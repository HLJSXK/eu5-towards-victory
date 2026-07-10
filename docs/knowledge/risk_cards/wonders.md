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

12. Do not let a wonder ritual's implementation reuse another wonder's mechanic template.
    The Unique Wonder Ritual Harness's old "no-write source compiler" ceremony
    (`scripts/wonder_unique_ritual_harness.py`'s repeated-entity-row/Alhambra evidence-chain
    layers, ~22,700 lines) was retired after 40+ commits never produced loadable source and
    its one real generation attempt produced broken output. Read
    `docs/guides/Unique_Wonder_Ritual_Harness.md` before authoring a new unique-ritual
    implementation: `data/unique_wonder_ritual_specs.yaml`'s `design_ir`/`mechanic_signature`
    remains the design source of truth, implementation is hand-written per wonder under
    `scripts/unique_wonder_ritual_content/<key>.py`, and
    `scripts/audit_unique_wonder_ritual_mechanic_similarity.py` is a **mandatory** post-batch
    gate — run it and confirm no new wonder pair crosses `combined_ratio >= 0.15` or shares
    `random_list` weight tuples with another wonder. Do not flatten a spec's high-fidelity
    `design_ir` / `tracked_entity_sets` into a shared generic engine merely to ship faster.

13. Beware "choice → deterministic branch → costed-fix-vs-free-accept → reward" as a new
    template trap.
    Even after removing `random_list` dice, giving three different wonders the same shape —
    an opening choice event that deterministically marks a fixed subset of tracked entities
    "at risk", followed by one retry event offering "pay a cost to fully resolve" vs. "accept
    for free at a lesser tier" — still reads as homogenized to
    `audit_unique_wonder_ritual_mechanic_similarity.py` (SequenceMatcher `combined_ratio`
    0.48–0.71 between Dome of the Rock / Bank of Saint George / St. Peter's Basilica after
    their 2026-07 rewrite, even though block-shape Jaccard stayed low, i.e. no verbatim
    duplicate blocks). The high-level narrative shape, not just literal effect bodies, is part
    of what "mechanically distinct" means for this project.
    Resolved 2026-07 (second rewrite, all four unique wonders using this shared engine):
    Alhambra/Dome of the Rock/Bank of Saint George/St. Peter's Basilica were each reassigned to
    a fully independent subagent with no visibility into the other three's implementation or
    into `_entity_ritual.py`, briefed only on their own wonder's history/theme and the trap to
    avoid. Result: effects-file `combined_ratio` among Dome/Bank/St Peter's dropped from
    0.48–0.71 to 0.18–0.32 (Alhambra vs. any of the three stayed under 0.15 throughout). The
    residual `combined_ratio` (0.21–0.30, still nominally over the 0.15 gate) that remains
    between those three pairs is no longer driven by the effects/mechanic bodies — it is driven
    almost entirely by the short, mandatory `site_control_trigger`/`active_trigger` lifecycle
    gate every ritual in the mod must define near-identically (`owns = location:X`;
    `has_variable = tv_wonder_locked` + `var:tv_wonder_locked ?= <id>` +
    `has_variable = tv_wonder_ritual_in_progress`). On a short triggers file (2-3 blocks total),
    that unavoidable boilerplate is a large fraction of the file, so `SequenceMatcher` still
    flags the pair even when the actual mechanic is unrelated. Adding a genuine, wonder-specific,
    differently-shaped extra trigger per wonder (a simple comparison for one wonder, an
    `OR`-of-`AND` compound check for another) and wiring it into a real `triggered_desc` reduces
    but does not fully eliminate this artifact — treat 0.15 as a soft gate on *short* triggers
    files going forward, and judge homogenization primarily from the effects-file ratio and a
    direct read of the mechanic, not the raw combined score alone, when the triggers file is
    this small for every wonder being compared.

14. Verify war outcome with `scope:winner`/`scope:loser`, not just "a war ended."
    `on_pre_winning_war` and `on_ending_war` both expose `root` (fires for both participants),
    `scope:winner`, `scope:loser`, and `scope:war`
    (reference_game_files/game/in_game/common/on_action/_hardcoded.txt:1518-1576). Checking
    only `has_variable = tv_wonder_locked` + site ownership in one of these on_actions lets a
    *lost* war validate a win-gated ritual step. Add `scope:winner = { this = root }` (the
    verified scope-equality idiom — same reference file line 3292
    `leader_country ?= { this = root }`; also used in
    `src/in_game/common/generic_actions/tv_arts_exhibition_actions.txt`) to require root to
    actually be the war's winner. Historical instance: Alhambra's war-validation gate
    (formerly `scripts/unique_wonder_ritual_content/alhambra.py:build_on_action_body`, since
    removed along with the rest of Alhambra's bespoke ritual) validated on any war ending while
    owning Granada, win or lose, until fixed 2026-07.

15. Re-run `gen_tv_wonder_ritual_effects.py` after renaming any bespoke ritual variable.
    `tv_wonder_ritual_effects.txt`'s `tv_wonder_mechanics_clear_selected_ritual_runtime_effect`
    is generated straight from each unique wonder's live `ritual.runtime_variables` list in
    `data/unique_wonders.yaml`. When a content module under `scripts/unique_wonder_ritual_content/`
    changes its row-set/variable-naming helpers (as Dome of the Rock, Bank of Saint George, and
    St. Peter's Basilica did in their 2026-07 bespoke rewrite), the data list gets updated but a
    stale, unregenerated `tv_wonder_ritual_effects.txt` keeps `remove_variable`-ing the *old*
    names — producing `used but never set` warnings for names nothing sets, while never actually
    cleaning up the real current-name status/favorable_count/narrowed/started/completed/
    ritual_stage variables on ritual reset (real state leak across restarts, not just a lint
    warning). See `docs/knowledge/anti_patterns.yaml` rule
    `wonder_ritual_cleanup_stale_after_entity_ritual_rename`.

16. Use v1.3 `_efficiency` modifier names, not the old v1.2 `_cost` names.
    EU5 v1.3 renamed ~29 `_cost`-suffixed static modifiers to `_efficiency` (e.g.
    `global_build_buildings_cost` -> `global_build_buildings_efficiency`,
    `local_fort_maintenance_cost` -> `local_fort_maintenance_efficiency`,
    `stability_cost` -> `stability_cost_efficiency`,
    `court_spending_cost_modifier` -> `court_spending_efficiency`), flipping
    `color=bad` to `color=good` at the same nominal-value polarity, so the value must be
    negated. Wonder data (`data/wonder_final_buildings.yaml`, `data/wonder_generic_rituals.yaml`,
    `data/unique_wonders.yaml`) is the single largest concentration of these fields in the mod.
    See `docs/knowledge/anti_patterns.yaml` rule `v1_3_cost_modifier_renamed_to_efficiency`.

17. Never let a per-event localization dict's option-letter loop read the same dict as `\"t\"`/`\"d\"`.
    A content module's `_EVENTS_TEXT[language][event_id]` dict must nest option text under its
    own `"options"` sub-dict. If option text lives directly on that dict (`{"t":..., "d":...,
    "a":..., "d": "Install the Alms Prefect."}`), any event reaching option letter `"d"` silently
    overwrites the dict's own description (`"d"` key collision — Python keeps only the last
    literal), and `build_localization`'s `for letter in ("a",...,"e"): if letter in text` loop
    re-emits the description a second time as a spurious `.d` option on every *other* event too,
    producing the engine's `Duplicate localization key ... defined in both X and X` warning. See
    `docs/knowledge/anti_patterns.yaml` rule
    `ritual_content_event_text_dict_letter_key_collides_with_desc` (historical instance: former
    `st_peters_basilica.py`'s 1678/1679/1680/1681 events, 2026-07; that content module has since
    been removed along with the rest of St. Peter's Basilica's bespoke ritual).

18. Reuse the location-scoped base site rule trigger for construction-condition GUI displays,
    and alias it by numeric id, not `any_owned_location`.
    `tv_wonder_location_meets_<key>_base_site_rules_trigger` is already the unwrapped,
    location-scoped form of the same site rule conditions the Engineering Department's
    `any_owned_location`-wrapped `tv_wonder_player_visible_site_rules_<key>_trigger` checks. A
    GUI block already rooted at `LocationView.GetLocation.MakeScope.Self` (like the
    location-window wonder tooltip) should call the base trigger directly, not re-wrap it in
    `any_owned_location`. Because it is addressed dynamically from a numeric display id (not
    the wonder's string key), generate a thin per-id alias —
    `tv_wonder_display_<id>_base_site_rules_trigger = { tv_wonder_location_meets_<key>_base_site_rules_trigger = yes }`
    — and call it via
    `ShowTriggerConditionsForScope(Concatenate('tv_wonder_display_', Concatenate(idString,
    '_base_site_rules_trigger')), LOCATION_SCOPE)`. Unlike `ShowModifierEffect`'s static
    modifier ids, scripted_trigger/scripted_effect names are not a separate database lookup, so
    the alias needs no `always = no` unreachable-reference block — see
    `docs/knowledge/anti_patterns.yaml` rule
    `gui_show_trigger_conditions_dynamic_key_needs_numeric_id_alias`.

## Validation

Run `validate.py --changed --fix --ai-report`: it lints rule 2 and rule 16 automatically, and when a
`data/unique_wonder_ritual_*.yaml` or harness script changes, runs
`wonder_unique_ritual_harness.validate_unique_ritual_specs_for_repo()`. Also run
`scripts/test_wonder_mechanics_rules.py` after changing scale-based wonder trigger/effect
generators, and `scripts/audit_unique_wonder_ritual_mechanic_similarity.py` after implementing
or reworking any unique-wonder ritual. Rules 6–11 have no automated check; inspect the
affected tooltip, hover state, or GUI layout in game after any change in those areas. Rule 15
has no automated staleness check either — after editing a content module's naming helpers,
always re-run `gen_tv_wonder_ritual_effects.py` even if no runtime error has been observed yet.
