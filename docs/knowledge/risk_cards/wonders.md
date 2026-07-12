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

19. Reassigning a unique wonder's `base_key` requires updating `mechanic_key` to match, and
    checking generic-wonder structural compatibility first.
    `scripts/wonder_mechanics/_core.py`'s `load_unique_wonders()` hard-requires
    `mechanic_key == base_key` for every entry in `data/unique_wonders.yaml` and raises before
    any generator runs otherwise. Before changing `base_key` (e.g. to fix a site-rule mismatch
    found by `scripts/audit_unique_wonder_site_requirements.py`), diff the old and new
    `base_key`'s entries in `data/wonders.yaml` for compatible `size`/`category`/`pop_type`/
    `final_buildings` level count, then update both `base_key` and `mechanic_key` together. See
    `docs/knowledge/anti_patterns.yaml` rule
    `unique_wonder_base_key_reassignment_requires_mechanic_key_match`.

20. The Unique Wonder Ceremony framework (`ceremony` block in
    `data/unique_wonders.yaml`, built by `scripts/wonder_ceremony_lib.py` and
    its per-file generators) is a deliberately uniform mechanic for the 121
    unique wonders *without* a bespoke ritual, and is explicitly out of scope
    for `audit_unique_wonder_ritual_mechanic_similarity.py` (confirmed by the
    user, 2026-07) — do not treat its shared 8-stage shape as a rule 12/13
    violation, and do not "fix" it by bespoke-ifying each wonder's ceremony.
    Since 2026-07, each stage carries its own authored `cost` (a list of 1-2
    `{type, value}` entries, validated by `_validate_ceremony_stage_cost` /
    `SUPPORTED_CEREMONY_STAGE_COST_TYPES` in `scripts/wonder_mechanics/_core.py`)
    instead of the wonder's single `ritual.cost_type` being repeated
    identically at every stage. The framework has no manual confirmation
    entry: `tv_wonder_finish_construction_effect` calls
    `tv_wonder_initialize_ceremony_runtime_state_effect`, which selects style
    1, refreshes the selected-ritual cache, and calls
    `tv_wonder_ceremony_begin_effect`. That effect must be limited to
    `tv_wonder_selected_unique_ceremony_framework_trigger` (the 121
    `ceremony != null` unique wonders), clear prior runtime state, set
    `tv_wonder_ritual_in_progress`, `tv_wonder_ceremony_locked`,
    `tv_wonder_ceremony_stage = 0`, and
    `tv_wonder_ceremony_quarter_month = 0`, without calling the completion or
    monthly-tick effect. The first stage event is therefore emitted only after
    three later monthly pulses. Keep the framework exclusion in
    `tv_wonder_ceremony_ready_for_confirmation_trigger`; do not restore a
    ready card or shared Hold Ceremony button. Pharos Lighthouse and Hagia
    Sophia remain outside that trigger and retain their dedicated manual
    buttons. The stage flavor and each stage's `cost` remain authored per
    wonder, while the three reward channels deliberately reuse the matching
    generic mechanic: stage 1 applies
    `generic_rituals[mechanic_key].style_3.reward` (including a
    `location_scalar` reward inside `var:tv_wonder_site`), stage 4 constructs
    `tv_wonder_{mechanic_key}_ritual_annex`, and stage 8 applies the unique
    ritual's permanent country modifier through the canonical completion
    chain. Do not restore a hand-authored `ceremony.stage_1_reward` field or
    construct the unique final building at stage 4: both duplicate or replace
    the wrong reward channel. The shared stage-8 effect schedules the hidden
    `tv_engineering_department.9308` event one day later; its `immediate`
    calls `tv_wonder_complete_active_ritual_effect`, which reaches
    `tv_wonder_finalize_effect` only after the generated custom-completion
    trigger verifies stage 8. This keeps the heavy finalization chain out of
    the visible event option while retaining the normal inauguration/world-news
    path. Pharos Lighthouse and Hagia Sophia are excluded (`ceremony: null`)
    and keep their existing bespoke `auxiliary_building`-mode rituals untouched.
    EU5 event numeric IDs must be `< 10000` (already enforced by
    `validate.py`'s `event_id` rule) — the ceremony's 8 shared events use ids
    9300-9307, not the more readable 10000-10007 originally chosen.
    The GUI card fragment (`data/generated_fragments/tv_wonder_ceremony_cards.gui`,
    from `scripts/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py`)
    is merged into `src/in_game/gui/panels/organization/tv_engineering_department.gui`'s
    Construction-and-ceremony tab by a **dedicated** merge script,
    `scripts/in_game/gui/panels/organization/merge_tv_wonder_ceremony_cards_gui.py`
    — it is intentionally separate from
    `merge_tv_engineering_department_wonder_mechanics_gui.py` (whose marker
    list and legacy-pruning logic all belong to the old per-style ceremony
    proposal/button widgets and is not a generic "splice anywhere" tool). The
    new `# BEGIN/END GENERATED TV_WONDER_CEREMONY_CARDS` marker pair sits
    right after the existing `TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS` marker
    (the Pharos/Hagia hand-coded step display); `.gui` syntax is
    brace-delimited, not indentation-sensitive, so the inserted block does
    not need to match the surrounding hand-written indentation depth (that
    existing marker's own content is unindented mid-file too). Regenerate the
    fragment, then rerun the merge script, to pick up any future changes.
    This panel's scope root is `InternationalOrganizationsView.GetPlayer.MakeScope`,
    not `Country.MakeScope` or any bare `GetVariable`. The status text is plain,
    non-clickable localization and must use the verified dynamic form
    `Localize(Concatenate('TV_WONDER_CEREMONY_CARD_<ACTIVE|COMPLETED>_S<n>_',
    ToString_int32(FixedPointToInt(...))))`, matching the working proposal-text
    precedent at `tv_engineering_department.gui:556`; it does **not** need a
    game-concept route. Generate both active and completed flavor keys from the
    stage title/first description sentence, rather than reverting to `x/8`.
    The left badge must be a real `piechart` using `piechart_angles` and two
    `pieslice` entries, with its central `text_single` using one of the eight
    verified built-in font icons (`government`, `topography`, `laborers`,
    `construction`, `building_levels`, `building`, `art_work`, `building_open`)
    via `@icon!`. Do not route ceremony-card icons through `GetConceptTexture`:
    these are step-state glyphs, not wonder illustrations.
    The outer Ceremony card is 500px wide, but its content column is 462px;
    every nested stage card must therefore use a fixed 462px width, not 500px,
    or the card margins expand the tab to roughly 538px at runtime.
    `gen_tv_wonder_ceremony_cards_gui.py`'s per-stage `visible` line used
    `And(a, b, c)` (3 operands) — GUI `And`/`Or` are binary-only; use `And3(...)`
    for exactly three operands (see the GUI risk card / `gui_boolean_helper_arity`).
    Separately, the generic style-3 reward vocabulary
    (`STYLE_3_REWARD_EFFECTS` in `scripts/wonder_mechanics/_core.py`) must only
    list reward types whose mapped effect is a genuine scalar per
    `reference_official_defines/docs/effects.log`'s "Supported Targets" line —
    `bureaucracy` was removed after `add_bureaucracy = 12` turned out to require
    a `bureaucracy_type` target, not a number, and silently no-op'd
    (`PostValidate of effect 'add_bureaucracy' returned false`) in the historical
    ceremony reward entries that used it. Check effects.log before adding a new
    reward type to this table.

21. Put ceremony-card `modify_texture` blocks inside a rendered `background`.
    `tv_engineering_department_card_common`'s `card_bg` block expands at its `vbox`
    level, so a `modify_texture` placed directly in a `blockoverride "card_bg"` is
    an unsupported property on that layout container. It produces `Property
    'modify_texture' not handled` and then fails the card's property setup. Preserve
    the paper card's background layers and place each conditional yellow/green
    `modify_texture` inside the relevant `background = { ... }` layer, matching
    vanilla's `reference_game_files/game/in_game/gui/attribute_columns/cabinet_action.gui:509-520`.

22. A zero-height `header_size` override does not suppress a card_common header's content;
    override `common_header` too, and give every stacked card an explicit fixed height.
    `tv_engineering_department_card_common`'s header widget (icon + title text) is a separate
    `block "common_header"` nested inside the `header_size`-controlled widget. Forcing
    `blockoverride "header_size" { size = { -1 0 } }` alone does not stop the default
    `common_header_icon`/`common_header_text_full` content from being created and rendered — it
    just overflows the zero-height parent, showing as a leaked duplicate icon+title above the
    card. Always pair it with `blockoverride "common_header" {}`, matching the verified
    untitled-card precedent at `tv_engineering_department.gui:7547-7549`/`:7640-7642`. Separately,
    every stacked `tv_engineering_department_card_common` instance needs `layoutpolicy_vertical =
    fixed` plus an explicit numeric `minimumsize`/`maximumsize` height set directly on the
    instantiation (see `:7467-7472`, `:1646-1650`) — a plain `widget` wrapper with only
    `layoutpolicy_horizontal = expanding` and no vertical size collapses to zero height, so a
    `vbox` of such cards stacks them all at the same position instead of listing them in
    sequence. Historical instance: the Unique Wonder Ceremony card fragment
    (`gen_tv_wonder_ceremony_cards_gui.py`) had neither override, so its 9 cards (1 ready + 8
    stage) all leaked the same default header at the top of the group and rendered piled on top
    of each other, fixed 2026-07-11. See `docs/knowledge/anti_patterns.yaml` rules
    `card_common_untitled_card_missing_common_header_blockoverride` and
    `card_common_list_missing_fixed_vertical_size_overlaps_in_vbox`.
    A related follow-up bug in the same fragment: its stage-card text sat in an extra
    `widget = { layoutpolicy_horizontal = expanding text_multi = { ... max_width = 380 } }`
    wrapper, which pulled the text column's natural width (observed ~375px) into the row and
    made the whole fixed-500-wide card overflow, even though 380 nominally fit the arithmetic
    budget (card width minus margin minus icon column minus spacing gaps). Do not wrap
    `text_multi` in an extra expanding `widget`; place it directly as the hbox child with
    `layoutpolicy_horizontal = expanding`, `max_width`, and `autoresize = yes` set on the
    `text_multi` itself, matching the verified precedent at `:8422-8428` (the Pharos stage-1
    text row), and keep `max_width` well below the arithmetic budget rather than flush against
    it. See `docs/knowledge/anti_patterns.yaml` rule
    `card_common_text_wrapped_in_expanding_widget_blows_out_fixed_card`.
    A third follow-up: the outer Ceremony card (`TV_ENGINEERING_CEREMONY_CARD_TITLE`,
    `tv_engineering_department.gui:8115-8226`) already used the correct auto-height chain at its
    outermost level (`maximumsize = { 500 -1 }` on the card_common instance, `layoutpolicy_vertical
    = shrinking` + `size = { 470 -1 }` + `set_parent_size_to_minimum = yes` on the first nested
    wrapper/vbox) — but a SECOND, deeper wrapper widget around the ritual-status area
    (`:8220-8226`) still hardcoded `size = { 462 330 }` with no shrinking policy, a leftover from
    when this area only ever held the short Pharos/Hagia step text. That single fixed-height link
    in the chain capped the measured content at 330px regardless of how many ceremony stage cards
    actually rendered inside it, so the stage cards overflowed past the outer card instead of
    stretching it taller. The auto-height chain must be applied at every nesting level between the
    outermost flexible card and the actual variable-height content, not just the first level; fixed
    2026-07-11 by changing that wrapper to `layoutpolicy_vertical = shrinking` + `size = { 462 -1 }`
    and adding `set_parent_size_to_minimum = yes` + `layoutpolicy_vertical = shrinking` to its vbox.
    See `docs/knowledge/anti_patterns.yaml` rule
    `card_common_shrinking_height_chain_broken_by_one_fixed_height_wrapper`.

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

Run `scripts/audit_unique_wonder_site_requirements.py` after adding a new unique wonder or
changing its `location`/`base_key` in `data/unique_wonders.yaml`, or after editing a
`trigger_script` in `data/wonder_site_rules.yaml`. It statically evaluates every unique
wonder's fixed `location` against its `base_key`'s site-rule `trigger_script` using real
vanilla map/setup data (`reference_game_files/game/in_game/map_data/location_templates.txt`
for topography/raw_material/port suitability, `main_menu/setup/start/07_cities_and_buildings.txt`
for starting `location_rank`, `main_menu/setup/start/10_countries.txt` for
ownership/capital, `in_game/setup/countries/*.txt` for owner religion, and
`in_game/map_data/definitions.txt` for continent), so a wonder pinned to a location that can
never satisfy its own base site rule (e.g. a `sacred_mountain`-keyed wonder sited on
non-mountain terrain, or a `colonial_trade_company`-keyed wonder sited on the owner's home
continent) shows up as `FAIL` with the exact failing condition. `has_river` and
`is_adjacent_to_lake` have no static source anywhere in `reference_game_files` (rivers/lakes
are baked into the heightmap, not exposed as text data) and always report `UNKNOWN` rather
than a guessed value; `dominant_religion = owner.religion` is approximated from the location's
static seeded religion field, not the true pop-computed dominant religion. Treat `FAIL` as a
confirmed authoring bug and `UNKNOWN` as a manual in-game/map check.

Reviewed FAIL/UNKNOWN results that are historically-accurate 1337-start facts (e.g. a wonder's
owner capital is correctly somewhere other than the wonder's location, or the location is
correctly still rural/non-port at the fixed start date) or are only achievable later in the
game (e.g. a `colonial_trade_company` port not yet colonized) are recorded in
`data/wonder_site_requirement_baseline.yaml` and reported as `INTENDED` instead. The script
checks that each baseline entry's recorded `status` still matches the current computed result
and reports a `BASELINE DRIFT` section (nonzero exit) if a data/rule change has invalidated an
entry — never edit the baseline to make a genuinely new result disappear without a rationale
grounded in real reference data.
