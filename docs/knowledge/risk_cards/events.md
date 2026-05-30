# Events Risk Card

Load this card before editing `src/in_game/events/` files or scripted effects that are
called directly from event options.

## Required Checks

1. Treat option effects as tooltip-rendered.
   Event option hover can pre-evaluate the option's effect stack. A `set_variable` earlier
   in the option, or in a called visible helper, may not be committed before a later helper
   reads it.

2. Keep nullable reads optional in visible option chains.
   Use `var:X ?= ...` for optional trigger checks. If a later effect value needs `X`, ensure
   `X` is persistent state already set before the event opened, or branch over bounded values
   with literal `value = N` effects instead of `value = prev.var:X`.
   Wonder module/helper rebuilds are a common trap here: for 1..6 level collapse or merge
   logic, prefer one literal branch per level over scratch variables like `*_combinable_levels`,
   `*_current_module_level`, or `*_target_module_level`. For rounded division displays such as
   remaining-month counters, prefer verified script-value operators like `ceiling = yes` over
   writing a temporary check variable and comparing it later in the same hover-rendered chain.

3. Guard stale event confirmations.
   Final confirmation events can sit open while project state changes through another path.
   Re-check all required state in the option effect before applying rewards, building
   effects, or cleanup.

4. Hide application chains when nested tooltips are not needed.
   If an event option must initialize temporary state and then call helpers that compare or
   reuse that state, wrap the sequence in `hidden_effect = { ... }`. This hides nested tooltip
   text, but it is not a commit boundary: helpers inside still must read persistent state or use
   literal bounded branches instead of same-chain scratch variables.

## Validation

Run:

```powershell
conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix --ai-report
```
