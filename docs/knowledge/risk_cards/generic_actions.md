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

3. Treat visible effects as tooltip-rendered.
   If an action effect initializes variables and then calls a helper that compares those
   variables, either put the state-changing chain in `hidden_effect`, or make the helper use
   `has_variable` / `var:X ?= ...` before direct comparisons.

4. Keep selection target names vanilla-shaped.
   Use `target`, `target_1`, and `target_2`. Custom names such as `selected_artist` have caused
   unset-scope errors in multi-step actions.

5. Register the action outside the action file.
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
