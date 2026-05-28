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
   helper so it runs only after persistent prerequisite state exists.

4. Keep selection target names vanilla-shaped.
   Use `target`, `target_1`, and `target_2`. Custom names such as `selected_artist` have caused
   unset-scope errors in multi-step actions.

5. Keep later selectors in the same chooser when they read earlier targets.
   Do not put `source = world` on a later `select_trigger` if its `visible`, `enabled`, or
   tooltip logic reads `scope:target` (or another earlier target flag). Use the inherited
   chooser/source or an explicit `interaction_source_list` instead.

6. Wrap selected numeric values in script-value blocks.
   If a selector result or scoped variable is stored or passed to a numeric effect parameter,
   use `value = { value = scope:target_1 }`, `scale = { value = scope:io.var:X }`, or
   `amount = { value = scope:io.var:X }`. Direct dynamic reads in these slots can collapse
   to `1` at runtime.

7. Register the action outside the action file.
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
- `generic_action_hidden_effect_not_hover_boundary` [advisory]: A `hidden_effect` inside a
  generic action can still be evaluated while a select-trigger candidate is merely hovered; make
  helper reads safe with optional variable links or persistent-state guards.
