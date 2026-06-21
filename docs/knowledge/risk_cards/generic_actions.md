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
   protect a later direct `var:X = { ... }` read.

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
   commit that write before reading the later `var:X` line.

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

10. Preserve requested map/id-flow refactors.
   If a generic-action pre-evaluation bug appears inside a `variable_map` helper, do not replace
   map key iteration or `random_key_in_variable_map` with generated per-id branches. Save the
   current owner scope before the map callback and write back through that named scope.

11. Run sibling map reads from the saved owner scope inside key iterators.
   In `every_key_in_variable_map` / `ordered_key_in_variable_map`, the callback scope may be
   the numeric key itself. Copy `this` into a `local_var`, then run `is_key_in_variable_map`
   and country-variable reads inside `scope:<saved_owner>` with `target = local_var:<key>`.

12. Do not use inflated `ordered_key_in_variable_map` max values.
   The engine logs an error when `max` is larger than the current key list. Use
   `every_key_in_variable_map` with a found flag when the live key count is not known.

13. Keep action title/description localization safe under contextless prefetch.
   Generic action title/description localization can be fetched without a GUI datacontext and
   without a script-scope container, even when the real hover later renders correctly. Do not put
   datacontext-dependent `Country.MakeScope` or container-dependent `SCOPE.sCountry('actor')`
   reads in those keys. If the feature requires dynamic text tied to the player country, use a
   context-independent global GUI binding such as `Player.MakeScope`, or move the dynamic line into
   a GUI widget/tooltip with an explicit datacontext when it needs non-player scopes.
   Do not "fix" this class by deleting the dynamic tooltip.

14. Register the action outside the action file.
   Every new generic action also needs a `common/generic_action_ai_lists` entry and a
   `PERFORM_<action_id>_ACTION` message type.

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
conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix --ai-report
```

Warnings tagged `generic_action_pre_eval` are not always hard failures, but new warnings fail
validation unless they are fixed or explicitly added to `data/validation_baseline.yaml` with a
rationale.

## Relevant Anti-Patterns
- `dynamic_scope_value_must_use_script_value_block` [advisory]: Dynamic selector values and
  scoped variables used in numeric effect parameters should be wrapped in explicit script-value
  blocks so the runtime preserves the selected number instead of treating the read as truthy.
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
- `variable_map_key_iterator_scope_used_for_map_read` [needs_parser]: A key-iterator callback
  should not run `is_key_in_variable_map` on the current numeric key scope; save the map owner,
  copy `this` into a local variable, and check sibling maps from the owner scope.
- `generic_action_loc_uses_gui_country_binding` [advisory]: Action title/description localization
  can be fetched without any data container; avoid `Country`/`SCOPE` reads and preserve dynamic
  player-country features through `Player.MakeScope`, or use an explicitly scoped GUI route for
  non-player scopes.
