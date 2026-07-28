# Generic Actions Risk Card

Load this card before creating or editing files under `src/in_game/common/generic_actions/`
or GUI widgets that call `action_button_diamond` with a generic action.

## Why This Area Is High Risk

Generic actions are evaluated before the player actually clicks the final button. EU5 can
render action cards, selectors, disabled-state tooltips, and effect tooltips by partially
evaluating `allow`, `select_trigger`, and `effect`. That means script that is harmless at
execution time can still spam runtime errors while the mouse is merely hovering a button.

## Required Checks

1. Keep nullable variable reads optional in player-facing trigger paths.
   Use `var:X ?= ...` inside `allow`, `visible`, `enabled`, `custom_tooltip`, and selector
   filters whenever `X` may be absent. Do not rely on a sibling `has_variable = X` line to
   protect a later direct `var:X = { ... }` read or `var:X < N` comparison. If no optional
   threshold operator has been verified, express bounded numeric checks as literal optional
   branches such as `var:X ?= 0` through `var:X ?= 19`, plus an explicit unset branch when
   unset should pass.

2. Guard every multi-step selection effect.
   If an action uses `select_trigger` with `target_flag = target`, `target_1`, or `target_2`,
   wrap the effect body in an `if = { limit = { exists = scope:target ... } ... }` guard for
   every scope the effect reads.

3. Treat action effects as hover-evaluated, even inside `hidden_effect`.
   `hidden_effect` hides output but is not a select-trigger pre-evaluation barrier. If an
   action effect initializes variables and then calls a helper that compares those variables,
   make the helper use `has_variable` / `var:X ?= ...` before direct comparisons, or guard the
   helper so it runs only after persistent prerequisite state exists. This applies even when the
   helper itself sets the display variable to 0 before comparing it; the pre-evaluator may not
   commit that write before reading the later `var:X` line. For derived display refreshes,
   calculate and compare with `set_local_variable` / `change_local_variable` and `local_var:X`
   first, then mirror the final values into persistent variables for GUI display.

4. Hide cleanup-only helper calls.
   If a generic action effect only clears variables, removes list entries, strips stale modifiers,
   or rebuilds display state, call that helper from `hidden_effect = { ... }`. Registered
   cleanup helpers such as `tv_governor_remove_effect` are enforced by `scripts/validate.py`.

5. Keep selection target names vanilla-shaped.
   Use `target`, `target_1`, and `target_2`. Custom names such as `selected_artist` have caused
   unset-scope errors in multi-step actions.

6. Keep later selectors in the same chooser when they read earlier targets.
   Do not put `source = world` on a later `select_trigger` if its `visible`, `enabled`, or
   tooltip logic reads `scope:target` (or another earlier target flag). Use the inherited
   chooser/source or an explicit `interaction_source_list` instead.

7. Use the player-visible source list for player-facing selectors.
   If the player and AI should see the same custom candidate list, use
   `interaction_source_list`. `ai_interaction_source_list` is only applied to AI countries,
   so relying on it alone can make the player selector show `none_available_msg_key` even
   when a valid target exists.

8. Do not pre-scan selector target availability in `allow`.
   Do not add an `allow` trigger whose only purpose is "there is at least one selectable
   target" for a later `select_trigger`. That duplicates the selector's candidate pass on
   action rendering, tooltip evaluation, and AI/list evaluation. Keep actor/state/resource
   prerequisites in `allow`, put target eligibility in `select_trigger` `visible`/`enabled`,
   provide `none_available_msg_key`, and keep the final effect guarded with
   `exists = scope:target`.

9. Wrap selected numeric values in script-value blocks.
   If a selector result or scoped variable is stored or passed to a numeric effect parameter,
   use `value = { value = scope:target_1 }`, `scale = { value = scope:io.var:X }`, or
   `amount = { value = scope:io.var:X }`. Direct dynamic reads in these slots can collapse
   to `1` at runtime.

10. Pass bare ids to helper scripted-trigger parameters that add type prefixes.
   In build-location selector triggers, call `location_and_owner_can_build` with
   `building_type = <id>`, not `building_type = building_type:<id>`. The vanilla helper
   expands the parameter as `building_type:$building_type$`; a typed argument becomes
   `building_type:building_type:<id>` during hover/pre-evaluation.

11. Preserve requested map/id-flow refactors.
   If a generic-action pre-evaluation bug appears inside a `variable_map` helper, do not replace
   map key iteration or `random_key_in_variable_map` with generated per-id branches. Save the
   current owner scope before the map callback and write back through that named scope.

12. Run sibling map reads from the saved owner scope inside iterators.
   In `every_key_in_variable_map` / `ordered_key_in_variable_map`, the callback scope may be
   the numeric key itself. In `every_in_list` / `random_in_list` / `any_in_list`, the current
   scope is the list item, such as a region, location, or character. Copy the key into a
   `local_var`, then run `is_key_in_variable_map` and the quoted `variable_map(...)` scope link
   inside `scope:<saved_owner>` with `target = local_var:<key>`.

13. Do not use inflated `ordered_key_in_variable_map` max values.
   The engine logs an error when `max` is larger than the current key list. Use
   `every_key_in_variable_map` with a found flag when the live key count is not known.

14. Keep action title/description localization safe under contextless prefetch.
   Generic action title/description localization can be fetched without a GUI datacontext and
   without a script-scope container, even when the real hover later renders correctly. Do not put
   datacontext-dependent `Country.MakeScope` or container-dependent `SCOPE.sCountry('actor')`
   reads in those keys. If the feature requires dynamic text tied to the player country, use a
   context-independent global GUI binding such as `Player.MakeScope`, or move the dynamic line into
   a GUI widget/tooltip with an explicit datacontext when it needs non-player scopes.
   Do not "fix" this class by deleting the dynamic tooltip.

15. Register the action outside the action file.
   Every new generic action also needs a `common/generic_action_ai_lists` entry, a
   `PERFORM_<action_id>_ACTION` message type, and the matching
   `PERFORM_<action_id>_ACTION_SETUP` / `_LOG` / `_MAP` localization keys in every
   supported language.

16. Use action-native AI for simple situation actions.
   When AI should use a player-facing generic action, define its `ai_tick`,
   `ai_tick_frequency`, and `ai_will_do` on the action and register it in an AI list. Do not
   duplicate the action/select/building flow in monthly or yearly effects to make AI "auto"
   progress; those bypasses can evaluate action or building checks without the literal
   `scope:actor` event target.

17. Use `save_temporary_scope_as` inside trigger contexts, never `save_scope_as`.
   `save_scope_as` is effect-only. Any scope save inside a `select_trigger` `visible`/`enabled`
   block, an `allow`/`potential` block, or an `if = { limit = { ... } }` trigger body must use
   `save_temporary_scope_as`. The engine's trigger parser does not recognize `save_scope_as` as a
   trigger type at all and logs "Unknown trigger type: save_scope_as" for every occurrence,
   which can spam hundreds of load errors from one generator helper reused across many action
   variants. Reserve `save_scope_as` for saves written directly inside an effect body (a sibling
   of `limit`, not inside it).

18. Save the owner before reusable helpers compare against IO state.
   A helper reached from a generic action effect should not assume `root` is still the action
   actor/current country. Save the current country or actor with `save_scope_as` at effect entry,
   before entering IO/member iterators, and compare nested state to `scope:<saved_owner>`.

19. Use `force_click_and_confirm_or_hold = yes` for "confirm before commit" — do NOT build a
   custom pending-variable + overlay GUI for it.
   Set `force_click_and_confirm_or_hold = yes` directly on the `generic_action` (see
   `reference_game_files/game/in_game/common/generic_actions/readme.txt:76`, and
   `tatar_yoke.txt`/`italian_wars.txt` for vanilla usage). The engine shows its own native
   confirmation dialog before running `effect`, reusing the SAME `title`/`description` loc
   keys the action's `action_button` already sets for its tooltip — no pending variable, no
   shared overlay widget, no `if`/`else_if` dispatch chain needed. `main_menu/gui/
   confirm_window.gui`'s `ConfirmWindow` is a separate, unrelated hardcoded C++ singleton for
   engine prompts (multiplayer/load/save) that a mod genuinely cannot parametrize — do not
   confuse the two. See `generic_action_confirmation_needs_pending_variable_overlay_not_engine_
   window` in `anti_patterns.yaml` (RETRACTED and corrected 2026-07-13: an earlier version of
   this rule wrongly concluded no native mechanism existed and prescribed the workaround this
   point now warns against) and `scripts/victory_tree_node_codegen.py` `generate_actions` for
   the corrected implementation.

20. Save the owner inside generic-action-reachable scripted triggers.
   A scripted trigger can be reached from an action effect-tooltip pre-evaluation without a
   valid `root`, even when its usual country-pulse caller has one. At a country-scoped trigger
   entry, use `save_temporary_scope_as = <owner_scope>` and compare nested locations/countries
   against `scope:<owner_scope>` (or `scope:<owner_scope>.culture`), never `root`. This is
   distinct from scripted effects, which use `save_scope_as`.

21. Make broad location iterators safe before reading nullable links.
   `any_location_in_the_world` and geography iterators can visit non-ownable, water, and
   ownerless locations. Filter with `is_ownable = yes`; read culture with
   `dominant_culture ?= <culture>` and ownership with `owner ?= <country>`. For an
   "all locations controlled" check, put `NOT = { owner ?= <country> }` inside the filtered
   iterator so an ownable ownerless location correctly remains unconquered without logging.

22. Bind an ordinary right-click action with `right_action`.
   In an `action_button`, use `right_action = { action_name = <id> }` when a single right
   click should execute a separate generic action. `right_click_and_hold_action` is a distinct
   hold-to-confirm interaction and must not replace an ordinary right click. The right-click
   action still needs its own `potential`, `allow`, guarded `effect`, AI-list registration,
   message type, and localization.

## Safe Skeleton

```txt
tv_example_action = {
	type = owncountry
	potential = { scope:actor = { has_variable = tv_feature_enabled } }
	allow = {
		scope:actor = {
			var:tv_optional_character ?= { is_alive = yes }
		}
	}
	select_trigger = {
		looking_for_a = character
		source = actor
		target_flag = target
		none_available_msg_key = "tv_example_no_character_available"
		visible = { is_alive = yes }
	}
	effect = {
		if = {
			limit = { exists = scope:target }
			scope:actor = {
				hidden_effect = {
					# initialize or mutate state here if later visible helpers depend on it
				}
				scope:target = { save_scope_as = tv_selected_character }
			}
		}
	}
}
```

## Validation

Run:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```

Warnings tagged `generic_action_pre_eval` are not always hard failures, but new warnings fail
validation unless they are fixed or explicitly added to `data/validation_baseline.yaml` with a
rationale.

- `save_scope_as_used_in_trigger_context` [needs_parser]: `save_scope_as` is not a valid trigger
  type at all; any scope save inside select_trigger `visible`/`enabled`, `allow`/`potential`, or a
  trigger `limit` body must use `save_temporary_scope_as` instead.

## Relevant Anti-Patterns
- `dynamic_scope_value_must_use_script_value_block` [advisory]: Dynamic selector values and
  scoped variables used in numeric effect parameters should be wrapped in explicit script-value
  blocks so the runtime preserves the selected number instead of treating the read as truthy.
- `scripted_trigger_typed_parameter_double_prefix` [lint]: `location_and_owner_can_build`
  receives a typed `building_type:<id>` argument even though the helper already adds the
  `building_type:` prefix internally.
- `select_trigger_world_source_reads_previous_target` [needs_parser]: A later selector with
  `source = world` cannot safely read `scope:target` from an earlier selector; omit `source`,
  use a non-world source, or provide an `interaction_source_list`.
- `generic_action_player_selector_uses_ai_interaction_source_list` [advisory]: A player-facing
  selector that relies only on `ai_interaction_source_list` can show no targets for human
  players; use `interaction_source_list` for shared player/AI candidate lists.
- `generic_action_allow_rechecks_select_target_availability` [advisory]: Do not repeat
  "has at least one selectable target" scans in `allow`; rely on `select_trigger`
  `visible`/`enabled` plus `none_available_msg_key` and final `exists = scope:target` guards.
- `generic_action_hidden_effect_not_hover_boundary` [advisory]: A `hidden_effect` inside a
  generic action can still be evaluated while a select-trigger candidate is merely hovered; make
  helper reads safe with optional variable links or persistent-state guards.
- `generic_action_cleanup_effect_must_be_hidden` [needs_parser]: Cleanup-only helper calls from
  generic action effects should be inside `hidden_effect`; `validate.py` enforces the registered
  high-risk helper list.
- `variable_map_callback_root_in_generic_action` [needs_parser]: A variable-map key callback
  called from a generic-action effect should not rely on `root` to write back to the action actor;
  save the actor/current country as a named scope before the callback.
- `generic_action_helper_assumes_root_owner` [needs_parser]: A reusable helper reached from a
  generic action should not compare nested IO state to `root` unless that root was verified; save
  the current owner as a named scope and compare against `scope:<saved_owner>`.
- `generic_action_scripted_trigger_assumes_root_owner` [advisory]: A scripted trigger reached
  from a generic action uses `root` after entering a nested scope; save the country with
  `save_temporary_scope_as` at trigger entry and use the saved scope in nested comparisons.
- `generic_action_single_right_click_uses_right_action` [advisory]: A normal right-click action
  must use `right_action`; reserve `right_click_and_hold_action` for deliberate hold interactions.
- `variable_map_key_iterator_scope_used_for_map_read` [needs_parser]: A key-iterator callback
  should not run `is_key_in_variable_map` on the current numeric key scope; save the map owner,
  copy `this` into a local variable, and check sibling maps from the owner scope.
- `variable_map_owner_read_from_item_iterator_scope` [needs_parser]: A variable-list item iterator
  should not run country-scoped map reads from the current region/location/character scope; save
  the map owner, copy the key into a local variable, and perform map checks from the owner scope.
- `generic_action_loc_uses_gui_country_binding` [advisory]: Action title/description localization
  can be fetched without any data container; avoid `Country`/`SCOPE` reads and preserve dynamic
  player-country features through `Player.MakeScope`, or use an explicitly scoped GUI route for
  non-player scopes.
- `on_action_simulates_generic_action_actor_context` [advisory]: Do not duplicate generic-action
  AI flows in monthly/yearly pulses when the copied chain can evaluate helpers or building
  `allow` blocks that expect literal `scope:actor`.
- `subjugation_effect_hardcodes_vassal_subject_type` [advisory]: A subjugation effect must not
  unconditionally call `make_subject_of` with `subject_type:vassal`; branch on the overlord's
  `has_advance = samanta_advance` and fall back to `subject_type:samanta`, since vassal is
  uncreatable for any overlord with that advance. See
  `docs/technical/EU5_Modding_Knowledge_Base.md` section 5.11.
