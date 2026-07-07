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
   If a visible helper switches into a location/province block (`capital = {}`, `var:site ?= {}`,
   `every_location_in_province = {}`, etc.), plain `var:X` now reads that nested scope's variable
   store. Use `root.var:X` for country-owned numeric inputs, or capture the value before the scope
   switch with `set_local_variable` / `local_var:X`.
   If a visible helper or event-called effect enters a variable-map key iterator, also capture
   any outer-scope numeric `var:X` before the iterator. Do not compare a map-captured local
   directly against `var:X` as a dynamic RHS; compare local to local, using `NOT <` and `NOT >`
   when equality is needed.
   Wonder module/helper rebuilds are a common trap here: for 1..6 level collapse or merge
   logic, prefer one literal branch per level over scratch variables like `*_combinable_levels`,
   `*_current_module_level`, or `*_target_module_level`. For rounded division displays such as
   remaining-month counters, prefer verified script-value operators like `ceiling = yes` over
   writing a temporary check variable and comparing it later in the same hover-rendered chain.
   Dynamic building effects are not inherently unrenderable in event option tooltips:
   `building_type = local_var:X` / `building = local_var:X` can render when `X` is captured
   from a variable map keyed by persistent state before switching to the location scope. The
   unsafe pattern is computing a temporary composite map key earlier in the same visible chain
   and then immediately using that key for `global_variable_map(...)`. For tooltip-visible
   module/final-building effects, branch over bounded dimensions such as part/style and map
   directly from persistent project ids.

3. Preserve existing branch structure.
   Do not collapse per-target `triggered_desc` branches, target-specific options, per-id effect
   dispatch, or localized branch text into generic fallback behavior just because a data list
   changed. If keeping the structure is repetitive, extend the generator/data source first or
   stop and ask before changing the player-facing event shape.

4. Guard stale event confirmations.
   Final confirmation events can sit open while project state changes through another path.
   Re-check all required state in the option effect before applying rewards, building
   effects, or cleanup.

5. Do not wrap visible option effects in `effect = { ... }`.
   Event options are already effect lists. Put effect calls directly under
   `option = { ... }`, next to `name` and optional `trigger`. EU5 parses an
   `effect = { ... }` child as a command named `effect` and logs
   `Unknown effect effect`.

6. Hide application chains when nested tooltips are not needed.
   If an event option must initialize temporary state and then call helpers that compare or
   reuse that state, wrap the sequence in `hidden_effect = { ... }`. This hides nested tooltip
   text, but it is not a commit boundary: helpers inside still must read persistent state or use
   literal bounded branches instead of same-chain scratch variables.

7. Do not treat option `hidden_effect` as a performance boundary.
   Event option hover can still evaluate hidden effect contents while rendering tooltips. Keep
   option hidden blocks light: guards, simple state checks, or a scheduler/trigger only. Move
   global scans, high-cardinality dispatch, completion broadcasts, map rebuilds, construction
   cleanup, and other heavy work to a `hidden = yes` event's `immediate` block or another
   non-tooltip execution path.

8. Keep generated trigger helpers in `common/scripted_triggers`.
   `common/scripted_effects` treats every top-level block as a scripted effect. Do not emit
   `_trigger = { ... }` definitions there; trigger clauses inside such a block are parsed as
   effects and produce `Unknown effect ...` load errors.

9. Use guarded delayed silent loops for daily hidden work.
   For daily background logic, seed exactly one delayed loop from a lifecycle point:
   `trigger_event_silently = { id = tv_namespace.900 days = 1 }`. The target should be a
   `hidden = yes` country event whose `immediate` checks the feature prerequisite and a
   persistent loop sentinel before doing work and rescheduling itself. Clear that sentinel
   during teardown so already queued events stop naturally instead of scheduling the next day.

10. Keep numeric event IDs below 10000.
   EU5 accepts event IDs as `<namespace>.<integer>`, but the integer must be `< 10000`.
   For generated high-cardinality systems, do not encode multiple dimensions into the numeric
   event ID if that crosses the limit. Move large wonder/type dispatch before the event fires;
   small event-local branches are acceptable only for dimensions that are already within a
   single typed event, such as ceremony style inside one wonder's finalization event.

## Validation

Run:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```
