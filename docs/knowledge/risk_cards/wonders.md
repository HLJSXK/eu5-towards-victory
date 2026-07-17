# Wonders / Engineering Department Risk Card

Since 2026-07, the entire Engineering Department / Wonder Construction subsystem
lives in its own standalone, deployable mod root, `src_engineering_department/`
(mirroring `src/`'s `in_game/`/`main_menu/` layout), with its own generator tree
`scripts_engineering_department/` (mirroring `scripts/`). This mod works fully
without the main "Towards Victory" mod, but requires Community Mod Framework
(CMF) 2.x because CMF supplies the custom `on_game_load` callback; the main mod
declares a hard dependency on the Engineering Department mod instead, since Prosperity Victory's
establishment effect calls `tv_engineering_department_create_effect`, which now
lives only there. Load this card before editing any file with `wonder` or
`engineering_department` in its filename, under **either** mod root: generated
`scripted_effects`, `scripted_triggers`, `static_modifiers`, `auto_modifiers`,
`building_types`, `generic_actions`, `game_concepts`, and `gui` files under
`common/`, their localization, `src_engineering_department/in_game/gui/location_window.gui`
and `encyclopedia_lateralview.gui`, and the `data/wonder*.yaml` /
`data/unique_wonder*.yaml` sources (data stays in the repo-root `data/` for both
mods) plus their `scripts_engineering_department/*wonder*.py` generators.

A handful of small shared files serving all 6 Towards Victory IOs generically
were split so the standalone mod is self-contained: `tv_io_leader_actions.txt`
and `tv_pulse_bridges.txt` are now multi-output generators (like `gen_victory.py`)
emitting a second file into the new mod root, filtered by the same
`wonder`/`engineering_department` substring convention applied to IO type names
and on_action ids; `tv_io_role_modifiers.txt`, `tv_game_concepts.txt` (+ loc),
and `tv_io_chief_alert_triggers.txt` had their Engineering-Department-specific
entries hand-moved out. `character_title.txt` and `messagetypes.txt` are
winner-takes-all singleton databases, so each mod root receives a **full
vanilla copy**, not an additive fragment. The Engineering Department copies
contain its own subset; the main-mod copies are strict supersets. The declared
main-mod -> Engineering Department dependency makes the main copy load later
and win when both are enabled. Never reverse that subset relation or remove the
dependency/load-order guarantee; `scripts/validate.py` checks vanilla-copy
integrity, the exact Great Engineer title subset, every root's generic-action
message types, and both superset relations.

The missing-Great-Engineer CMF alert is fully owned by the standalone mod:
`tv_engineering_department_chief_alert_on_action.txt` provides the monthly sync
and `cmf_on_callback` handler, the dedicated trigger/effects maintain the CMF
alert and click request, a scripted GUI plus hidden GUI bridge opens the
Engineering Department panel and clears the request, and the existing EN/ZH
Engineering Department localization owns the alert labels. Do not move any
part of this chain back into the main mod or describe a standalone cosmetic
gap.

The standalone bootstrap is registered on `on_game_start` and CMF's custom
`on_game_load`. It schedules the visible intro country event for every country
with `days = 1`; it does not wait for `monthly_country_pulse`. On load, the
intro is scheduled only when the save-wide initialization marker is absent,
while the idempotent Engineering Department creation effect silently runs for
every country regardless so missing or damaged IOs are repaired.

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
    `max_width` and `autoresize`. This is only half the contract: the surrounding `hbox`/`vbox`
    itself must also declare `layoutpolicy_horizontal = expanding` whenever it sets an explicit
    `size` alongside expanding children (fixed icon column + expanding text, etc.) — a container
    with `size` but no `layoutpolicy_horizontal` of its own falls back to sizing off children's
    intrinsic minimums instead of the declared size, silently collapsing the whole row toward the
    fixed column's width and leaving the expanding text column at ~0 width. See rule 22's fifth
    follow-up and `docs/knowledge/anti_patterns.yaml` rule
    `hbox_explicit_size_without_layoutpolicy_horizontal_collapses_to_content_width` for the
    verified instance and precedent citations. `max_width`/`autoresize` on the `text_multi` alone
    does not substitute for this container-level property.

12. Do not let a wonder ritual's implementation reuse another wonder's mechanic template.
    The Unique Wonder Ritual Harness's old "no-write source compiler" ceremony
    (`scripts_engineering_department/wonder_unique_ritual_harness.py`'s repeated-entity-row/Alhambra evidence-chain
    layers, ~22,700 lines) was retired after 40+ commits never produced loadable source and
    its one real generation attempt produced broken output. Read
    `docs/guides/Unique_Wonder_Ritual_Harness.md` before authoring a new unique-ritual
    implementation: `data/unique_wonder_ritual_specs.yaml`'s `design_ir`/`mechanic_signature`
    remains the design source of truth, implementation is hand-written per wonder under
    `scripts_engineering_department/unique_wonder_ritual_content/<key>.py`, and
    `scripts_engineering_department/audit_unique_wonder_ritual_mechanic_similarity.py` is a **mandatory** post-batch
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
    `data/unique_wonders.yaml`. When a content module under `scripts_engineering_department/unique_wonder_ritual_content/`
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
    `scripts_engineering_department/wonder_mechanics/_core.py`'s `load_unique_wonders()` hard-requires
    `mechanic_key == base_key` for every entry in `data/unique_wonders.yaml` and raises before
    any generator runs otherwise. Before changing `base_key` (e.g. to fix a site-rule mismatch
    found by `scripts_engineering_department/audit_unique_wonder_site_requirements.py`), diff the old and new
    `base_key`'s entries in `data/wonders.yaml` for compatible `size`/`category`/`pop_type`/
    `final_buildings` level count, then update both `base_key` and `mechanic_key` together. See
    `docs/knowledge/anti_patterns.yaml` rule
    `unique_wonder_base_key_reassignment_requires_mechanic_key_match`.

20. The Unique Wonder Ceremony framework (`ceremony` block in
    `data/unique_wonders.yaml`, built by `scripts_engineering_department/wonder_ceremony_lib.py` and
    its per-file generators) is a deliberately uniform mechanic for the 121
    unique wonders *without* a bespoke ritual, and is explicitly out of scope
    for `audit_unique_wonder_ritual_mechanic_similarity.py` (confirmed by the
    user, 2026-07) — do not treat its shared 8-stage shape as a rule 12/13
    violation, and do not "fix" it by bespoke-ifying each wonder's ceremony.
    Since 2026-07, each stage carries its own authored `cost` (a list of
    **exactly 1** `{type, value}` entry, validated by `_validate_ceremony_stage_cost` /
    `SUPPORTED_CEREMONY_STAGE_COST_TYPES` in `scripts_engineering_department/wonder_mechanics/_core.py`,
    which hard-rejects 0, 2, or more entries)
    instead of the wonder's single `ritual.cost_type` being repeated
    identically at every stage. (Prior to 2026-07-15, the schema mistakenly
    allowed 1-2 entries, which let 120/121 wonders drift to 2 costs per stage
    during authoring — see `anti_patterns.yaml` rule
    `unique_wonder_ceremony_stage_cost_must_have_exactly_one_entry`.) A
    `country_reward` gold cost renders as `change_gold_effect = { scale = <N> }`
    (catalog id `scaled_gold` in `data/cost_reward_units.yaml`), never bare
    `add_gold = <N>` — the cost is meant to scale with the country's economy
    like every other gold cost in the Wonder Ritual system, not be a flat
    literal; see `anti_patterns.yaml` rule
    `ceremony_cost_gold_must_use_scaled_gold_not_flat_add_gold`. The framework has no manual confirmation
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
    generic mechanic: stage 2 applies
    `generic_rituals[mechanic_key].style_3.reward` (including a
    `location_scalar` reward inside `var:tv_wonder_site`), stage 4 constructs
    `tv_wonder_{mechanic_key}_ritual_annex` from the prototype's style 2 local
    modifier, and stage 8 applies the prototype's
    `generic_rituals[mechanic_key].style_1.country_modifier` through the
    canonical completion chain while retaining a unique modifier identity per
    wonder. Do not restore a hand-authored `ceremony.stage_2_reward` field or
    construct the unique final building at stage 4: both duplicate or replace
    the wrong reward channel. Since 2026-07-16, the shared stage-8 effect calls
    `tv_wonder_complete_active_ritual_effect` **inline**, in the same
    `tv_wonder_ceremony_advance_to_stage_8_effect` body the option's own
    `effect =` invokes — matching stages 2/4, which already call their reward
    dispatch effects inline. This was previously deferred one day later through
    a dedicated hidden event (`tv_engineering_department.9308`,
    `trigger_event_silently`), which made the completion reward execute
    correctly but never render in the stage-8 option's tooltip preview (the
    preview only walks the option's own effect body, never follows
    `trigger_event_silently` into another event's `immediate` block) — steps
    2/4 showed both cost and reward, step 8 showed only cost. Investigation
    confirmed the completion chain
    (`tv_wonder_mechanics_apply_selected_ritual_completion_effect` +
    `_apply_selected_ritual_static_modifier_effect` + `tv_wonder_finalize_effect`)
    is `add_country_modifier` plus variable bookkeeping and one
    `every_international_organizations_member_of` read-only loop for all 121
    generic-ceremony wonder ids — no `construct_building`,
    location/building iteration, or world-news calls — and is demonstrably
    lighter than stage 4's own inline 66-branch `construct_building` switch, and
    the identical chain (`tv_wonder_complete_active_ritual_effect`) already runs
    inline from several `on_action` hidden_effects (monthly ritual pulse, ruler
    death) for every ritual in progress. So unlike rule 9/31's `destroy_building`/
    character-promotion cases, there was no measured tooltip-preview error or
    performance cost specific to this chain — the deferral had been "match the
    async pattern used for stage-4 construction's finalization and for
    Pharos/Hagia" rather than a proven necessity, and removing it fixed the
    tooltip gap with no new pre-evaluation errors observed. The now-unused
    `tv_engineering_department.9308` event and `COMPLETION_EVENT_ID` constant
    were deleted rather than kept dormant. Pharos Lighthouse and Hagia Sophia
    are excluded (`ceremony: null`) and keep their existing bespoke
    `auxiliary_building`-mode rituals untouched, including their own use of
    `trigger_event_silently`/non-silently-scheduled completion paths, which are
    unaffected by this change. EU5 event numeric IDs must be `< 10000` (already
    enforced by `validate.py`'s `event_id` rule) — the ceremony's 8 shared
    events use ids 9300-9307, not the more readable 10000-10007 originally
    chosen.
    The GUI card fragment (`data/generated_fragments/tv_wonder_ceremony_cards.gui`,
    from `scripts_engineering_department/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py`)
    is merged into `src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui`'s
    Construction-and-ceremony tab by a **dedicated** merge script,
    `scripts_engineering_department/in_game/gui/panels/organization/merge_tv_wonder_ceremony_cards_gui.py`
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
    `pieslice` entries. Its central `text_single` must dynamically localize
    `TV_WONDER_CEREMONY_CARD_ICON_S<n>_<wonder_id>`, whose `@icon!` value comes
    from that exact `ceremony.stages[i].icon` field. Every stage must also carry
    a non-empty `icon_rationale` that explains its title/description connection;
    validate icon names against `font_icons.gui`. Do not restore a global
    stage-number icon table or route ceremony-card icons through
    `GetConceptTexture`: the badge represents this wonder's current ritual act,
    not a reused wonder illustration or a generic step counter.
    The outer Ceremony card is 500px wide, but its content column is 462px;
    every nested stage card must therefore use a fixed 462px width, not 500px,
    or the card margins expand the tab to roughly 538px at runtime.
    `gen_tv_wonder_ceremony_cards_gui.py`'s per-stage `visible` line used
    `And(a, b, c)` (3 operands) — GUI `And`/`Or` are binary-only; use `And3(...)`
    for exactly three operands (see the GUI risk card / `gui_boolean_helper_arity`).
    Separately, the generic style-3 reward vocabulary
    (`STYLE_3_REWARD_EFFECTS` in `scripts_engineering_department/wonder_mechanics/_core.py`) must only
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
    A fourth follow-up: `gen_tv_wonder_ceremony_cards_gui.py`'s `append_card()` emitted the
    closing brace for the `hbox` and for `blockoverride "common_bottom_content"` but never
    emitted the final closing brace for the `tv_engineering_department_card_common = { ... }`
    instantiation itself. Since a `.gui` block's scope is determined purely by brace balance
    (not by generator function boundaries), each of the 8 stage cards silently nested inside
    the previous one instead of closing as a sibling in the `TV_WONDER_CEREMONY_CARDS` vbox —
    stage 1 opened at depth 1, stage 2 opened at depth 2 (one level *inside* stage 1's own
    `common_bottom_content` blockoverride), stage 3 at depth 3, and so on, cascading all 8
    cards' content into the base type's single header `hbox` (`tv_engineering_department.gui:59`)
    instead of stacking as 8 independent cards. This rendered as all 8 cards' icon+text content
    packed side by side in one row and pushed to an extreme height, i.e. exactly inverted from
    the intended wide/short vertically-stacked cards — a brace-balance bug, not a
    layoutpolicy/size bug like the three follow-ups above. Detected by counting `{`/`}` per card
    span and confirming each `tv_engineering_department_card_common = {` opened at a
    strictly-increasing depth instead of a constant one; fixed 2026-07-12 by adding the missing
    `lines.append(f"{T}}}")` at the end of `append_card()`. When a generator emits a nested
    brace structure across many `lines.append` calls, verify total `{`/`}` counts for one
    generated unit balance to zero (or, for a list of repeated siblings, that every repeated
    unit opens at the same nesting depth) — do not assume a function "looks complete" just
    because its last few lines contain closing braces. See `docs/knowledge/anti_patterns.yaml`
    rule `gui_generator_function_missing_final_closing_brace_cascades_nesting`.
    A fifth follow-up, found right after the brace fix above: the per-card `common_bottom_content`
    `hbox` (`gen_tv_wonder_ceremony_cards_gui.py`, icon column + flavor `text_multi`) declared an
    explicit `size = { 432 104 }` but no `layoutpolicy_horizontal` of its own. In-game inspection
    showed the hbox actually rendering at only ~80px wide (roughly the fixed 64px icon column plus
    spacing) with its `text_multi` collapsed to an unselectable, effectively 0-width column --
    i.e. the declared `size` was not being honored at all. Every other stacked-content hbox in
    this file that combines an explicit `size` with expanding children sets
    `layoutpolicy_horizontal = expanding` on the hbox itself (the Pharos stage rows,
    `tv_engineering_department.gui:8401-8402`; the Hagia active-ritual row,
    `:9372-9375`) -- without it, the container's own width falls back to summing children's
    intrinsic minimums (a fixed 64px icon plus a `text_multi` with no `minimumsize`, whose
    intrinsic width is 0 until layout stretch is applied) instead of honoring the literal `size`
    hint. Fixed 2026-07-12 by adding `layoutpolicy_horizontal = expanding` as the first property
    of that hbox. See `docs/knowledge/anti_patterns.yaml` rule
    `hbox_explicit_size_without_layoutpolicy_horizontal_collapses_to_content_width`.
    A sixth follow-up, found when the user reported the ceremony-finalized text ("the wonder
    has already completed its inauguration") also rendering narrow and tall: this one is a
    DIFFERENT mechanism from the fifth follow-up above, not the same fix applied one level up.
    `TV_ENGINEERING_CEREMONY_ACTION_ONGOING`/`_FINALIZED_TEXT` (`:10520-10536`) are bare
    `text_multi` leaves (only `max_width`/`autoresize`/`layoutpolicy_horizontal = expanding`, no
    `minimumsize`) inside a `vbox` that uses `set_parent_size_to_minimum = yes` (`:8132`/`:8224`,
    the standard auto-height chain from the third follow-up above). `set_parent_size_to_minimum`
    computes the vbox's OWN size from the minimum size each child reports, not from any
    `layoutpolicy_horizontal`/`size` on the vbox or its parent widget -- two live-tested guesses
    confirmed this: adding `ignoreinvisible = yes` to a sibling hbox did nothing (wrong
    container), and adding/removing `layoutpolicy_horizontal`/`layoutpolicy_vertical`/explicit
    `size` on the ancestor `widget = { size = { 470 -1 } ... }` (`:8128`) and its `vbox` (`:8132`)
    also did nothing -- the user's own measurements showed the vbox stuck at exactly its own
    doubled horizontal margin (8 = 4+4) regardless, and removing the widget's own
    `layoutpolicy_vertical = shrinking` broke the widget's OWN width too (470 -> 8). The real fix:
    give the bare `text_multi` itself `minimumsize = { 462 -1 }` matching its `max_width`, so it
    reports a real width instead of 0 into the `set_parent_size_to_minimum` computation. Fixed
    2026-07-12. Rule 14 in `docs/knowledge/risk_cards/gui.md` and the tooltip-row paragraph in
    `docs/technical/EU5_Modding_Knowledge_Base.md` already said to give the ROW a `minimumsize`
    under `set_parent_size_to_minimum` -- neither said the LEAF content widget also needs one,
    which is why this took three attempts instead of one doc lookup; both docs are now corrected.
    See `docs/knowledge/anti_patterns.yaml` rule
    `set_parent_size_to_minimum_vbox_needs_leaf_minimumsize_for_width`.
    Two more bare leaves were found sharing the exact same vbox (`:8132`) and fixed the same
    way: `TV_ENGINEERING_CEREMONY_HELP_TEXT` (`:8140`) and `TV_ENGINEERING_CEREMONY_LOCKED_
    BY_EXPANSION_TEXT` (`:8211`). A quick project-wide regex/brace scan for other bare
    `text_multi` leaves under a `set_parent_size_to_minimum` ancestor produced far more false
    positives than real hits -- it cannot tell that an intervening fully-literal-sized `widget`
    (explicit numeric width AND height, e.g. the `size = { 462 136 }` boxes at `:8263`/
    `:8298`-style ritual-requirement rows) breaks the dependency chain and makes everything
    inside it safe regardless of ancestors further up. Do not trust a naive scan for this
    pattern; a real fix needs a `needs_parser` `validate.py` check that tracks whether such a
    literal-size wrapper intervenes before treating a `set_parent_size_to_minimum` ancestor as
    live.

22. `tv_wonder_surveyed` is a shared gate for three different consumers — seed it atomically
    with priority-candidate registration, never separately.
    `tv_wonder_initialize_existing_unique_wonders_effect`
    (`append_existing_unique_wonders_initialization_effect` in
    `gen_tv_engineering_department_wonder_mechanics_effects.py`, feeding
    `generate_location_display_effects()` -> `tv_wonder_location_display_effects.txt`, not the
    file's own `OUT_FILE`/`generate()`) fires on both `on_game_start` and `on_game_load`. The
    `NOT is_key_in_variable_map(tv_wonder_surveyed, wonder_id)` guard around
    `append_register_existing_unique_priority_candidate` exists so that reloading a save does not
    re-register the priority candidate every time. The same `tv_wonder_surveyed` map is also
    read by `tv_wonder_mechanics_copy_completed_survey_from_location_effect` (restores saved
    competence into the country's active project) and by
    `tv_wonder_selected_survey_already_cached_trigger` (checked from
    `tv_wonder_mechanics_start_survey_effect` to decide whether reassigning the survey site to a
    location restores cached competence or starts a fresh survey from 0). Because the
    existing-wonder priority-resume path (`tv_wonder_prepare_priority_project_effect`) never
    runs a real survey, `tv_wonder_surveyed` was never being set for these wonders at all, so
    reassigning the survey site to that location always took the from-0 branch. Fix: seed
    `tv_wonder_surveyed=1` plus `tv_wonder_survey_scale_competence` / `..._logistics_competence`
    / `..._organization_competence` / `..._scale_tier` for that wonder id inside the SAME
    not-yet-surveyed guarded block that calls `append_register_existing_unique_priority_candidate`
    — this satisfies all three consumers at once instead of requiring a second map or a
    conflicting gate. See `docs/knowledge/anti_patterns.yaml` rule
    `wonder_existing_wonder_location_never_seeded_as_surveyed`.

23. `TooltipRequirementsList` needs an explicit `tooltip_minimumsize` override whenever
    `maximumsize` is narrower than the template default, or the wider default minimumsize wins.
    `TooltipRequirementsList`'s base type (`main_menu_cooltip_types.gui:337`) declares
    `block "tooltip_minimumsize" { minimumsize = { @tooltip_inner_wide -1 } }`, where
    `@tooltip_inner_wide` resolves to `420 - 10*2 = 400`. Setting only `maximumsize = { N -1 }`
    with `N < 400` and no `blockoverride "tooltip_minimumsize"` leaves the inherited 400px
    minimumsize in place, which conflicts with and overrides the narrower maximumsize — the
    widget renders at its ~400px minimum regardless. Inside a `layoutpolicy_horizontal = fixed`
    wrapper that does not clip children, that extra width bubbles up through every ancestor
    `expanding` container and stretches an outer fixed-`maximumsize` card wider than declared.
    Historical instance: the Engineering Department's three wonder-debate demand rows
    (nobles/burghers/clergy, `tv_engineering_department.gui`, debate-stage-only content nested
    under `tv_engineering_department_card_common`'s `maximumsize = { 500 -1 }`) each declared
    `maximumsize = { 230 -1 }` on their `TooltipRequirementsList` with no matching
    `tooltip_minimumsize` override, stretching the 500px-wide card wider only while the debate
    stage (`tv_wonder_stage == 1`) was active and its demand rows visible — reverting to 500px
    once the debate ended and that content collapsed. Fixed 2026-07-13 by adding
    `blockoverride "tooltip_minimumsize" { minimumsize = { 230 -1 } }` to each of the three
    instances, matching the working precedent already used by every "suitability location
    conditions" `TooltipRequirementsList` elsewhere in the same file (e.g. `:1728-1736`, which
    pairs `maximumsize = { 218 -1 }` with `blockoverride "tooltip_minimumsize" { minimumsize =
    { 218 -1 } }`). See `docs/knowledge/anti_patterns.yaml` rule
    `tooltip_requirements_list_maximumsize_without_matching_minimumsize_override`.

24. Collapse homogeneous per-entity static GUI branches into one dynamic-routed widget with
    `MakeScopeFlag(Concatenate(...))` + `GetVariableFromGlobalVariableMap(...)`, not N copies.
    When a GUI block would otherwise emit one near-identical static `widget` per data-table row
    (e.g. one per wonder id) purely to show a (label, value) pair, build a composite runtime key
    with `MakeScopeFlag(Concatenate(<id_string>, '_<slot>'))`, read a value baked into a global
    variable map at generation time via `GetVariableFromGlobalVariableMap('<map_name>',
    <composite_key>).GetValue`, and resolve a dynamic loc key from a small numeric enum id with
    `text = "[Localize(Concatenate('PREFIX_', ToString_int32(FixedPointToInt(<id_value>))))]"`.
    Both the composite-key read pattern and the `Localize(Concatenate(...))` loc-key pattern are
    confirmed working in vanilla/community GUI (see
    `docs/knowledge/anti_patterns.yaml` rule `gui_dynamic_composite_key_variable_map_lookup`).
    This only applies when the *display* is homogeneous (same widget shape, different data) — it
    does not license flattening genuinely heterogeneous per-target logic, such as each wonder's
    distinct survey trigger script (rule 1's local/national split and this project's Structural
    Fidelity Rule still require those to stay explicit per-wonder branches. Applied 2026-07-13 to
    the "suitability location conditions" block: 54 static per-wonder widgets (~4000 generated
    lines) collapsed to one shared widget backed by two new global variable maps
    (`tv_wonder_suitability_condition_type`, `tv_wonder_suitability_weight`, keyed
    `flag:tv_wonder_suitability_<mechanic_id>_<slot 1..5>`), dropping
    `tv_engineering_department.gui` from 9041 to 5168 lines. Always prefix a generated composite
    flag key with the owning system's name, not a bare `<id>_<slot>` number pair — otherwise its
    benign "flag is set but never used" startup log line (see
    `docs/knowledge/anti_patterns.yaml` rule `gui_dynamic_composite_key_variable_map_lookup`)
    reads as an unrelated concatenation bug. `validate.py` cannot execute
    `Concatenate`/`MakeScopeFlag`/`GetVariableFromGlobalVariableMap` — verify any change to this
    pattern in-game per wonder/reveal-tier combination. That "flag is set but never used" line is
    benign and does not need fixing by default, but if it must be eliminated, a `has_flag` reference
    only satisfies the engine's flag-usage scanner when it sits inside a scripted trigger/effect that
    is itself reachable from a real on_action/event/decision entry point — a `has_flag` placed in a
    trigger/effect that is never called anywhere still logs the warning (the engine's own message
    says so: "Use in unused scripted triggers and effects also does not count"). The working fix,
    `tv_wonder_suitability_flag_static_reference_trigger`
    (`gen_tv_engineering_department_wonder_mechanics_triggers.py`), ORs `has_flag` across every baked
    `tv_wonder_suitability_<mechanic_id>_<slot>` key and is called once, as a side-effect-free no-op,
    from the already-reachable `tv_wonder_initialize_index_on_game_start`/`_on_game_load` hooks in
    `tv_engineering_department_on_action.txt`.

25. A wrapper `vbox`/`hbox` does not inherit its ancestor's fixed width — give it its own
    `layoutpolicy_horizontal = expanding` whenever it sits between a fixed-width column and an
    `expanding` row (especially one containing `expand = {}`). `suitability_dynamic_row()`
    (`gen_tv_engineering_department_wonder_mechanics_gui.py`) wraps each suitability condition row's
    `hbox` in a new per-row `vbox` (to gate the row + its "hidden" placeholder text behind one shared
    `visible` check) — introduced 2026-07-13 by the same commit that added the dynamic composite-key
    lookup (rule 24). That wrapper vbox has no `layoutpolicy_horizontal` of its own, so — unlike the
    pre-refactor flat hbox/text_single siblings that sat directly under the fixed-218px
    `tv_engineering_suitability_location_conditions_column` vbox — it shrinks to its content's natural
    width instead of inheriting the column's fixed width, starving the inner `expanding` hbox and
    zeroing its `expand = {}` widget. Fixed by adding `layoutpolicy_horizontal = expanding` to the
    wrapper vbox. This GUI section is fragment-generated then merged into the hand-maintained file
    (`gen_..._gui.py` writes `data/generated_fragments/...gui`, then
    `merge_tv_engineering_department_wonder_mechanics_gui.py` splices it into
    `tv_engineering_department.gui` between markers) — regenerating requires running both scripts, not
    just the generator. See `docs/knowledge/anti_patterns.yaml` rule
    `expanding_row_wrapper_vbox_missing_layoutpolicy_horizontal`.

26. Since 2026-07, the Unique Wonder Ceremony's per-stage `cost` is drawn from
    `data/cost_reward_units.yaml`'s standalone catalog, not the old ~39-type
    `STYLE_3_REWARD_EFFECTS`-derived vocabulary — this rework is that catalog's first real
    consumer (see `docs/design/Cost_Reward_Unit_Concepts.md`, previously "nothing in the mod
    reads from this catalog"). Each `cost` item is now `{catalog, type, value}`, where
    `catalog` is one of `country_reward`/`local_reward`/`character_reward`/
    `country_modifier`/`local_modifier` and `type` is an id within that catalog list.
    `value` is **always computed**, never hand-authored: `-1 × base_value × stage_multiplier`
    (stage 1/3/5/7 → ×1, stage 2/4/6/8 → ×2), except `country_reward.inflation` which is
    inverted (`+1 × ...`, since a cost there *increases* inflation). `_validate_ceremony_stage_cost_item`
    (`scripts_engineering_department/wonder_mechanics/_core.py`) cross-checks the authored `value` against this
    formula and rejects any drift. Three `country_modifier` ids and one `local_reward` id are
    excluded from the usable pool and must never be picked: `allow_open_sea_exploration`/
    `gender_equality` (the catalog's only two boolean unlock switches — a flat unlock has no
    "5-year temporary cost" reading), `monthly_towards_axis` (a representative placeholder for
    34 real `monthly_towards_*` keys, not itself a valid static-modifier field name), and
    `laborers` (no one-shot EU5 effect exists for it — confirmed absent from
    `reference_official_defines/docs/effects.log`). The old cost vocabulary
    (`CEREMONY_STAGE_COST_REWARD_SCOPES`/`SUPPORTED_CEREMONY_STAGE_COST_TYPES`, including the
    `"artwork"` special case) was fully removed, not layered alongside the new one — do not
    reintroduce it. `STYLE_3_REWARD_EFFECTS`/`reward_effect_lines()` themselves are unchanged
    and still back the unrelated stage-2/4/8 reward channels; the new cost path uses a
    separate function, `wonder_ceremony_lib.ceremony_cost_effect_lines()`, specifically so
    those reward channels are never touched by a cost-schema change.

    Per-category effect syntax: `country_reward`/`local_reward`/`character_reward` (adm/dip/mil)
    reuse `STYLE_3_REWARD_EFFECTS`'s existing effect names where the id matches 1:1 (verified
    via this mod's own `tv_wonder_construction_events.txt` for the 4 estate-satisfaction ids,
    which use `add_estate_satisfaction = { type = estate_type:<x>_estate value = <v> }`).
    `character_reward.artist_skill` needed a new scope not previously supported by the ceremony
    cost path: `random_artist = { limit = { is_alive = yes } save_scope_as = ... }` then a
    guarded `if = { limit = { exists = scope:... } ... }` (confirmed via this mod's own
    `tv_engineering_department_effects.txt` and vanilla precedent) — **accepted tradeoff**: if
    the paying country has zero living artists, this cost silently no-ops that one time (rare,
    ~2 expected uses across 968 stages; not worth a compensating fallback).
    `country_modifier`/`local_modifier` ids are persistent-modifier keys, not one-shot effects,
    so each usable id gets a static modifier generated by two generators,
    `gen_tv_wonder_ceremony_cost_country_modifiers.py` and `_local_modifiers.py`. **Since
    2026-07 (updated)**, these are scoped one modifier per `(wonder, stage)` — named
    `tv_wonder_ceremony_cost_{country,local}_modifier_<wonder_key>_s<stage_index>` via
    `ceremony_stage_cost_{country,local}_modifier_name()` (`wonder_mechanics/_core.py`) — not
    the original shared-by-`(id, tier)` scheme. The original scheme deduped by `(entry_id,
    tier)` across all 121 wonders (a single modifier could be reused by up to ~48 unrelated
    wonder stages), which made it impossible for the modifier's `STATIC_MODIFIER_NAME_` display
    label to read as that stage's own flavor text — it could only ever show the raw effect
    label from `data/cost_reward_units.yaml` (e.g. "Bank Interest"). The un-shared scheme fixes
    that: each modifier's loc label is now that stage's own `title_en`/`title_zh`, and
    `wonder_ceremony_lib.ceremony_stage_cost_entries(wonders, catalog)` (replacing the old
    `used_ceremony_cost_tiers()`) enumerates every `(wonder, stage_index, entry_id)` triple
    without deduping. Magnitude math is unchanged (`base_value × stage_multiplier`, tier
    computed the same way as before) — only the identifier/label granularity changed. This
    grew the two static-modifier files from ~193 combined blocks to 325 (`country_modifier`) +
    242 (`local_modifier`) = 567 blocks; accepted tradeoff, explicitly requested by the user
    over keeping the shared/generic-name scheme. These are
    applied as **5-year temporary** modifiers (`add_country_modifier`/`add_location_modifier`
    with `years = 5 mode = add_and_extend`), not a permanent Country Auto modifier — confirmed
    via vanilla precedent (`personality_events.txt:409`, `culture_japan.txt:544`,
    `ennoble.txt:70-74`) and this mod's own `tv_academy_philosophy_debate_events.txt:4263-4267`,
    all of which use `years =`/`months =`, never `duration =` in days. New location-scoped
    static modifier names are brand-new `tv_`-prefixed identifiers with no vanilla/mod
    collision, so — despite CLAUDE.md's general "use `TRY_REPLACE`" wording for
    location-scoped statics — no `TRY_REPLACE:` wrapper is needed or used; every existing
    wonder-domain location-modifier generator (e.g.
    `gen_tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.py`) already
    confirms this narrower rule in practice. `TRY_REPLACE` is only for overriding an
    already-existing (vanilla/other-mod) modifier name.

    The two event options at each stage ("Pay the price."/"Not yet." previously, identical
    across all 121 wonders × 8 stages) now read as wonder-specific flavor text coordinating
    with that stage's own `desc`, via EU5's **Customizable Localization** mechanism
    (`in_game/common/customizable_localization/`, documented in
    `docs/technical/EU5_Modding_Knowledge_Base.md` "Customizable Localization Syntax and
    Usage") — not a change to the event's option structure. `option.name` in
    `tv_wonder_ceremony_events.txt` stays a single flat key per stage/option exactly as before
    (matching every vanilla `option.name` precedent, which is always a flat key — there is no
    vanilla or mod precedent anywhere for a per-condition dynamic `option.name` block, so this
    mechanism was deliberately routed around rather than attempted). Only that flat key's
    localization **value** changed, to `[ROOT.GetCountry.Custom('tv_wonder_ceremony_stage_<n>_
    <pay|decline>')]` — the `.GetCountry` link is mandatory (see rule 30 below); a bare
    `[ROOT.Custom(...)]` throws `Could not find data system function 'Custom' in
    'ROOT.Custom(...)'` on every stage. 16 new Customizable Localization blocks (8 stages ×
    pay/decline, generated by the new `gen_tv_wonder_ceremony_options.py` into
    `tv_wonder_ceremony_options.txt`) each carry `type = country` and 121 `text` entries
    dispatched on `var:tv_wonder_locked`, plus a `fallback = yes` entry, following this mod's
    own already-proven pattern (`tv_academy_debate_groups.txt`). Two new required stage fields,
    `option_pay_en/zh` and `option_decline_en/zh`, hold the actual per-wonder-per-stage text.

27. A `cmf_suppress = { v = X }` entry (via `data/cmf_warning_suppressions.yaml` +
    `gen_tv_cmf_suppressions.py`) is never proof by itself that variable `X` is a handled false
    positive — `cmf_suppress`'s own definition
    (`reference_mods/3692202776/in_game/common/scripted_effects/cmf_utility_effects.txt`) is an
    `always = no`-guarded dead branch referencing `$v$` in every set/get form specifically to make
    the engine's static scanner see both a "set" and a "used" occurrence for
    `jomini_effect.cpp`'s "used but never set"/"set but never used" lines — whether that trick
    reliably fires through this project's own extra outer `always = no` wrapper for every
    reference shape is not independently confirmed one way or the other without an in-game
    error.log re-check after redeploying. What is certain regardless: `tv_wonder_{foundation,
    body,function,decoration}_progress` and `tv_wonder_construction_paused` were suppressed since
    this file's first commit while having zero real setters anywhere, dead cleanup left over
    after the design moved to a shared `tv_wonder_construction_progress` + `tv_wonder_active_part`
    model — the suppression entry was masking dead code, not a real false positive. Before
    trusting any suppression entry, grep for a real setter and a real reader (script or GUI)
    first; delete dead `remove_variable` calls and their suppression entries together rather than
    re-suppressing. `tv_wonder_suitability_weight` (read only via GUI
    `GetVariableFromGlobalVariableMap`, which the native script-only scanner cannot see) and
    `tv_wonder_suitability_flag_static_reference_never_set` (an intentional, self-documented
    trade-off on `tv_wonder_suitability_flag_static_reference_trigger` — one accepted variable
    warning instead of dozens of unused-flag warnings) are both cases where the code itself is
    correct; both are now suppressed for consistency with every other GUI-only-read/deliberate-
    workaround entry in that file. `tv_wonder_final_building_type_to_display_id` (formerly
    `gen_tv_wonder_index_effects.py`'s `FINAL_BUILDING_DISPLAY_ID_MAP`) turned out to be a dead
    duplicate of `tv_wonder_final_building_type_to_wonder_id` (same generator loop, same
    `wonder_id` value, zero readers anywhere) rather than a genuine dynamic-reference case like its
    sibling maps `tv_wonder_final_building_type_to_wonder_id`/`_to_ritual_style` (both read in three
    effect files) — deleted from the generator and the suppression list rather than kept. See
    `[[cmf_suppress_status_is_not_proof_a_variable_reference_is_real]]`.

28. Every raw variable comparison inside a `custom_tooltip` must have a `has_variable` guard if
    the compared variable is only conditionally set — per the Milestone Trigger Tooltip Pattern —
    and this matters even more when the same trigger doubles as an effect's own `if.limit` (not
    just a generic_action's `allow`). `tv_wonder_can_finish_construction_trigger`'s "must have
    gained a level" gate compared `var:tv_wonder_level > var:tv_wonder_project_base_level`
    unguarded, even though `tv_wonder_project_base_level` only exists when
    `var:tv_wonder_project_mode ?= 2` at site-selection time; its sibling branch one line below
    already used the safe `var:tv_wonder_level ?= { this >= 1 }` form. Because this trigger also
    gates `tv_wonder_finish_construction_effect`'s body, the bug did not just show a wrong
    checkmark — the button's effect-tooltip preview pass corrupted an unrelated *later* line in
    the same body (`tv_wonder_destroy_labor_camp_effect`'s `destroy_building_forcefully` building
    name came back garbled). When a "why is this unrelated tooltip broken" report traces back to a
    `custom_tooltip` earlier in the same effect body, check that trigger's own comparisons first.
    See `[[custom_tooltip_unguarded_comparison_corrupts_later_effect_tooltip_in_same_pass]]`.

29. `tv_wonder_project_base_level` (the "level when this resume/expansion project started"
    snapshot) is captured in `tv_wonder_select_construction_site_effect` as
    `set_variable = { name = tv_wonder_project_base_level value = var:tv_wonder_level }`, guarded
    only by `var:tv_wonder_project_mode ?= 2`. This silently produced no variable at all for a
    wonder resuming construction on a site with pre-existing progress — e.g. an existing-at-game-
    start unique wonder (`initial_level > 0`, like Jerusalem's Dome of the Rock) — because
    `tv_wonder_initialize_existing_unique_wonders_effect` only seeds the survey/final-building-
    level global maps at game start, not the country's own `tv_wonder_level`/`_units` variables;
    the restore effects called earlier in `tv_wonder_select_construction_site_effect`
    (`tv_wonder_restore_locked_wonder_final_building_state_effect`,
    `tv_wonder_sync_units_from_buildings_effect`) correctly rebuild the `_units` counters from the
    site's actual building levels, but nothing recomputed the *derived* `tv_wonder_level` from
    those counters before the snapshot line ran two calls later, so `tv_wonder_level` was still
    unset at that exact moment. Fixed by inserting `tv_wonder_update_wonder_level_effect = yes`
    between the restore calls and the snapshot — mirroring `tv_wonder_reinitialize_building_state_
    core_effect`'s already-correct restore-then-recompute order, which is the reference for this
    ordering requirement generally: any time a wonder effect restores/backfills `_units` (or any
    other counters a derived cache variable is computed from) from location building state, always
    re-run the matching recompute effect before anything reads the derived variable, even inside
    the same effect body. Also added the equivalent missing-base-level repair to
    `tv_wonder_reinitialize_building_state_core_effect` itself, since a player already mid-
    playthrough with a silently-missing `tv_wonder_project_base_level` has no other way to recover
    it besides the `tv_reinitialize_mod` debug action. See
    `[[derived_cache_variable_not_recomputed_after_restoring_its_source_counters]]`.

30. A Customizable Localization block is never callable as `[ROOT.Custom('block_name')]` in
    event/effect loc text — `Custom` must be chained off a scope link matching the block's own
    `type` (`ROOT.GetCountry.Custom(...)` for `type = country`, matching
    `docs/technical/EU5_Modding_Knowledge_Base.md`'s own worked example), even though the event
    or effect is already root-scoped to that same type. A bare `ROOT.Custom(...)` throws
    `Could not find data system function 'Custom' in 'ROOT.Custom(...)'` on every evaluation.
    The 8-stage Unique Wonder Ceremony's pay/decline option text (rule 26 above) shipped with
    this exact bug in `gen_tv_wonder_ceremony_l_english.py`/`_simp_chinese.py`; the same bug was
    also latent (not yet triggered in any playthrough) in the Academy Philosophy Debate's
    seated/vacated `custom_description` text via `scripts/philosophy_debate_codegen.py`'s
    `tooltip_change_text`. `validate.py` now lints the bare `[ROOT.Custom(` pattern directly. See
    `[[custom_localization_call_needs_typed_scope_link_not_bare_root]]`.

31. `destroy_building`/`destroy_building_forcefully` targeting `building(building_type:X|scope:Y)`
    must resolve `scope:Y` through an implicit link (`owner`, `root`, `prev`, `scope:actor`) —
    never a custom name captured earlier in the same effect via `save_scope_as`. Every vanilla
    usage (e.g. `catholic.txt`'s `destroy_building_forcefully = "building(building_type:
    seat_of_cardinal|owner)"`, called from inside `scope:target_location`) uses only implicit
    links. `tv_wonder_destroy_labor_camp_effect` did `save_scope_as = tv_wonder_labor_camp_owner`
    at country scope, then referenced `scope:tv_wonder_labor_camp_owner` after entering the
    location (`var:tv_wonder_site ?= { ... }`). The runtime executor resolves this fine and
    correctly destroys the Labor Camp on click — but the button's effect-tooltip preview pass
    does not replay `save_scope_as` before resolving the destroy target for display, so it fails
    to promote the engine's internal `TARGET_BUILDING` placeholder
    (`Promote 'TARGET_BUILDING' returned nullptr`) and shows garbled text instead of "Labor Camp
    will be destroyed" even though the click-through behavior is completely correct. Fixed by
    using the location's own `owner` link directly and deleting the now-unnecessary
    `save_scope_as`. The same `save_scope_as`-then-`scope:X_owner` pattern is used ~926 times
    across `tv_wonder_module_effects.txt` (`tv_wonder_module_owner`) for the generic/module
    wonder building-consolidation system, reachable only via `tv_wonder_reinitialize_building_
    state_core_effect` (the `tv_reinitialize_mod` debug action) — not yet confirmed broken there
    (no player-facing construction button walks that chain), left alone rather than blindly
    refactoring 926 call sites without a reported symptom. See
    `[[destroy_building_target_via_custom_saved_scope_breaks_tooltip_preview]]`.
    Follow-up (2026-07-16): the owner-link fix alone did not clear the error — it kept logging
    because `tv_wonder_destroy_labor_camp_effect` was still called directly from
    `tv_wonder_finish_construction_effect`, which is itself the `tv_wonder_finish_construction`
    generic_action's own `effect =` body, i.e. the exact chain the button's hover/tooltip preview
    pre-evaluates. Rule 9's guidance (keep `hidden_effect` light, defer heavy chains to a
    triggered event) generalizes here too: any generic_action's non-hidden `effect =` body is
    also pre-evaluated for the button tooltip, so a `destroy_building`/`destroy_building_forcefully`
    call anywhere in that chain — even with a correct implicit link — must be deferred to a
    separately-triggered event rather than run inline. Fixed by removing
    `tv_wonder_destroy_labor_camp_effect = yes` from `tv_wonder_finish_construction_effect` and
    adding it to event `tv_engineering_department.202`'s `option` effect instead; the event
    already fires asynchronously via the existing `trigger_event_non_silently ... days = 1` call
    made earlier in the same effect, so every completion path (player button, on_action
    auto-completion, direct events.txt call) still schedules the demolition identically. See
    `[[destroy_building_forcefully_in_button_effect_chain_fails_tooltip_preview_even_with_owner_link]]`.
    Second follow-up (2026-07-16): moving the call into the event was still not enough — event
    *options* get the same hover/tooltip pre-evaluation pass as generic_action buttons, so
    `tv_engineering_department.202`'s `option` block calling `tv_wonder_destroy_labor_camp_effect`
    directly (not inside `hidden_effect`) kept erroring identically. There is no scope depth or
    async distance that exempts a visible option's own effect body — only `hidden_effect` is
    skipped by the pre-evaluation walk. Fixed by wrapping the call in `hidden_effect = { ... }`
    and adding a sibling `custom_tooltip = tv_engineering_department.202.a.tt` line (matching
    vanilla's own pattern in `earthquake_events.txt`'s `earthquake_events_minor` options) so the
    option still shows static, correct tooltip text instead of the real effect chain. See
    `[[destroy_building_forcefully_needs_hidden_effect_even_inside_deferred_event_option]]`.

32. `tv_wonder_active_part` being set is not proof that real monthly progress is accumulating.
    `tv_wonder_monthly_construction_effect`'s auto-advance branch assigns
    `tv_wonder_active_part` from `tv_wonder_organization_logistics_unlocked_trigger` (debate/
    lock/site-selected/not-complete) plus "some part still below max" alone — it never checks
    `tv_wonder_has_organized_labor_trigger`
    (`total_effective_building_levels:tv_wonder_labor_camp > 0`), the same check the four manual
    `tv_wonder_begin_foundation/body/function/decoration` actions already require. So a wonder
    with an unstaffed Labor Camp can have `tv_wonder_active_part` set while
    `tv_wonder_monthly_construction_progress` sits at 0 all month. The construction card's "no
    active work site" vs. "remaining time" toggle (added 2026-07-13) was gated purely on
    `tv_wonder_active_part.IsSet`, so it showed a nonsensical remaining-time estimate instead of
    the intended "no available work site" message during a 0-progress stall. Fixed by AND-ing
    `GreaterThan_CFixedPoint(GetVariable('tv_wonder_monthly_construction_progress').GetValue,
    '(CFixedPoint)0.0')` into both visibility conditions — the script-side construction math
    itself needed no change (0 progress simply never crosses a completion threshold). See
    `[[gui_visibility_gate_on_proxy_variable_not_the_real_condition]]`.

33. A `has_variable` guard earlier in the same `AND` block does NOT stop the engine's tooltip/
    effect-preview pre-evaluation pass from independently erroring on a later raw two-variable
    hard comparison (`var:X <= var:Y`). `tv_wonder_has_selected_ceremony_trigger` already had
    `has_variable = tv_wonder_ceremony_style` and `has_variable = tv_wonder_locked_style_count`
    directly above `var:tv_wonder_ceremony_style <= var:tv_wonder_locked_style_count` — matching
    rule 27/28's documented fix pattern — yet the generic action `tv_wonder_confirm_ceremony*`'s
    `allow` block still logged `Event target link 'var' returned an unset scope` / `Invalid left
    side during comparison 'var'` / `Failed to fetch variable ... due to not being set` every time
    the action's tooltip/allow state was pre-evaluated before a ceremony style had been chosen.
    The preview pass evaluates each condition line on its own to render an independent pass/fail
    indicator, so a preceding guard in the same block never actually short-circuits it. Fixed by
    converting the comparison itself to the self-contained safe form:
    `var:tv_wonder_ceremony_style ?= { this <= var:tv_wonder_locked_style_count }`, mirroring the
    sibling line immediately above it and the two-variable-safe precedent already in use at
    `tv_diplomatic_alliance_actions.txt:149` (`var:tv_alliance_cohesion ?= { this >=
    local_var:tv_alliance_subjugation_cost }`). Every raw two-variable comparison must be
    self-contained this way — a preceding `has_variable` line is not sufficient on its own. See
    `[[preceding_has_variable_does_not_guard_a_later_raw_two_variable_comparison]]`.
    Follow-up (2026-07-16): the `?=`-wrap fix above did not actually clear the error — two more
    syntax variants were tried afterward (`var:X ?= { this <= root.var:Y }`, matching the safe
    pattern at `reference_game_files/game/in_game/events/disaster/castilian_civil_war.txt:2446`)
    and both still failed. The real cause was structural per rule 10: `tv_wonder_locked_style_count`
    is a derived cache variable written by `tv_wonder_index_cache_locked_wonder_attributes_effect`
    and read back by this same trigger later in the same pre-evaluated chain
    (`tv_wonder_choose_ceremony_style_effect`'s non-hidden `effect=` -> `tv_wonder_index_refresh_
    country_cache_effect` -> writes the cache -> calls this trigger to read it), so the write
    hadn't committed yet during tooltip/allow preview — no RHS syntax fixes that. But the deeper
    finding was that the comparison never needed to be dynamic at all: this trigger (gated by
    `tv_wonder_can_choose_ceremony_style_trigger`'s `NOT = { tv_wonder_unique_locked_trigger = yes
    }`) is reachable only for generic wonders, which always have exactly 3 fixed ceremony styles;
    unique wonders use an entirely separate ritual system and never reach it. Commit 66b5edf5
    ("implement wonder global variable map", 2026-06-04) had mistakenly swapped the trigger's
    original literal `var:tv_wonder_ceremony_style ?= { this <= 3 }` (from its introducing commit
    d394ac0a, never broken) for the two-variable form while wiring up the *unique*-wonder-only
    dynamic style count. Restored the literal `<= 3` and dropped the now-unneeded `has_variable`
    guards. Lesson: two consecutive failed syntax-only fixes on the same two-variable comparison is
    a signal to check git history / design intent for whether the dynamism belongs on that path at
    all, rather than trying a third RHS variant. See
    `[[preceding_has_variable_does_not_guard_a_later_raw_two_variable_comparison]]`.

34. When a GUI generator rewrite adds a bespoke special-case button path, verify the generic
    case it's carved out of still has its own working path — do not assume the special case's
    deletion leaves the generic case unaffected. Every player-facing generic_action in the
    Engineering Department panel (`tv_wonder_confirm_ceremony`/`_scaled_gold`/`_prestige`
    included) is reachable ONLY through an explicitly hand-authored widget in
    `gen_tv_engineering_department_wonder_mechanics_gui.py` — there is no vanilla-surfaced
    fallback UI. Commit 5a56683e ("add unique ceremony framework and update UI elements",
    2026-07-12) added the two bespoke Pharos/Hagia `hold_button()` calls (wonder id 101/102) and,
    in the same edit, deleted the pre-existing generic-wonder hold-button block (three
    `hold_button()` calls gated to "any locked wonder that is not Pharos/Hagia") without adding a
    replacement. The generic_actions' `allow=` chains and cache-effect pipeline stayed fully
    correct throughout — this was a pure GUI-wiring regression that silently removed every
    generic wonder's manual ceremony-confirm button while Pharos/Hagia (the only wonders the
    accompanying test exercised) kept working, masking it from
    `test_wonder_mechanics_rules.py::validate_generated_ceremony_gui`, which asserted only that
    the bespoke buttons exist and (over-broadly) that the shared button must never appear at all.
    Fixed by restoring the generic hold-button block, reusing `generic_wonder_locked_expr()`
    (added later for the ceremony-style-choice buttons, a cleaner equivalent of the deleted
    `not_special_unique_locked_expr()`) instead of re-adding a redundant helper, and narrowing the
    test assertions to "must appear, gated on `tv_wonder_locked_is_unique`" so generic wonders and
    Pharos/Hagia can't double-render buttons. See
    `[[gui_generator_rewrite_silently_dropped_generic_wonder_confirm_buttons]]`.

35. **ED event title phase-prefix convention.** Every Engineering Department event title must carry
    a phase indicator: a `[concept_key|E]` bracket where a fitting concept already exists, or bare
    text where it does not. Random-pool events use their own phase's concept: debate pool
    (`tv_engineering_department.100`-`.105`) → `[tv_wonder_debate|E]` (辩论); survey pool
    (`.310`-`.322` minus notification `.300`) → `[tv_wonder_survey|E]` (测绘, already correct
    pre-existing). The construction random pool (`tv_wonder_construction_events.txt`/
    `wonder_construction_event_lib.py` TITLE_EN/TITLE_ZH, ids 7000-7211) has no dedicated concept —
    `[tv_wonder_construction|E]` itself renders as the generic "Great Project"/伟大工程, not
    "Construction"/建设 — so those titles use bare `Construction：`/`建设：` text instead, replacing
    (not stacking in front of) the old generic bracket. Ceremony content — the 121 unique wonders'
    8-step ceremony template (`TV_WONDER_CEREMONY_S{n}_TITLE_{id}`) plus the bespoke Hagia
    Sophia/Pharos Lighthouse ritual titles — uses `[tv_wonder_ceremony|E]` even though these are
    fixed/triggered sequences, not random pools (an explicit carve-out). Everything else (milestone
    notifications, finalization/ownership titles, the standalone intro event) defaults to
    `[tv_wonder_construction|E]` (伟大工程/Great Project). Titles that already carry any concept
    bracket are otherwise left untouched — only bare titles get one added.
    **Critical gotcha:** the ceremony stage title (`title_en`/`title_zh` in
    `data/unique_wonders.yaml`) is a single shared field reused by the generator for the actual
    event title AND for `CARD_ACTIVE`/`CARD_COMPLETED` card flavor text and
    `STATIC_MODIFIER_NAME_*` entries. Do NOT edit the data-source title field to add a prefix — that
    prefixes the card/modifier text too, which is not "the event title." Instead patch the
    generator's title-emission line only (`title_key(...)` call in
    `gen_tv_wonder_ceremony_l_english.py`/`_simp_chinese.py`), leaving `card_flavor_text()` and the
    modifier-name lines reading the raw untouched field.

## Validation

Run `validate.py --changed --fix --ai-report`: it lints rule 2 and rule 16 automatically, and when a
`data/unique_wonder_ritual_*.yaml` or harness script changes, runs
`wonder_unique_ritual_harness.validate_unique_ritual_specs_for_repo()`. Also run
`scripts_engineering_department/test_wonder_mechanics_rules.py` after changing scale-based wonder trigger/effect
generators, and `scripts_engineering_department/audit_unique_wonder_ritual_mechanic_similarity.py` after implementing
or reworking any unique-wonder ritual. Rules 6–11 have no automated check; inspect the
affected tooltip, hover state, or GUI layout in game after any change in those areas. Rule 15
has no automated staleness check either — after editing a content module's naming helpers,
always re-run `gen_tv_wonder_ritual_effects.py` even if no runtime error has been observed yet.

Run `scripts_engineering_department/audit_unique_wonder_site_requirements.py` after adding a new unique wonder or
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
