# On Action Risk Card

Load this card before editing `common/on_action/` files or adding monthly/yearly/death hooks.

## Required Checks

1. Respect singleton bridge hooks.
   EU5 on_action keys with direct `effect = { ... }` bodies do not merge safely across files.
   Use the on_action bridge registry generator for shared country/monthly/yearly/death hooks and
   TV extensions of shared hardcoded/general hooks.

2. Preserve generated on_action bridge shape.
   The bridge registry generates one TV-owned file, `tv_pulse_bridges.txt`, containing lightweight
   bridge blocks that declare only the parent hook key plus `on_actions = { tv_* }`; do not use vanilla
   filenames such as `country_monthly.txt`, and do not copy vanilla `events`, `random_events`, or
   `effect` blocks into the bridge. Update `data/pulse_registry.yaml` and rerun the generator. For
   hardcoded hooks such as `on_winning_war`, `on_work_of_art_created`, `on_annex`, `on_war_declared`,
   `on_join_war`, `on_ending_war`, and `on_ruler_death`, add TV logic via
   `on_actions = { tv_*_callback }` delegation in `tv_pulse_bridges.txt` instead of a second direct
   `effect`; feature files should keep only the named TV callback bodies.

3. Delay monthly country pulse events by one day.
   Any event whose conditions are checked from `monthly_country_pulse` must fire one day later.
   Direct calls use `trigger_event_* = { id = <event> days = 1 }`; native `events` and
   `random_events` blocks use `delay = { days = 1 }` before event ids. Keep the delay in
   generator data/templates for generated monthly chains.

4. Verify root/prev assumptions.
   On_action callbacks often run from global, country, character, or situation roots. Capture
   needed values with `save_scope_as` or local variables before entering iterators.

5. Do not simulate generic-action AI in broad pulses.
   If AI should use a player-facing situation/generic action, enable that action with
   `ai_tick`, `ai_will_do`, and a `generic_action_ai_lists` entry. Do not copy its
   select/effect/building-check flow into monthly/yearly on_action code: action and building
   eligibility helpers can evaluate blocks that expect the literal `scope:actor` event target,
   and a custom saved scope name will not satisfy those reads.

6. Guard nullable country links in broad pulses.
   Monthly/yearly country refreshes can touch countries without a valid capital. In trigger
   or `limit` checks, use `capital ?= { ... }`; do not rely on a sibling
   `exists = capital` line to short-circuit a later direct `capital = { ... }`.

7. Do not assume UI tooltip semantics.
   On_action effects are execution-time, but events they fire can expose option tooltips. If an
   event option reads state written earlier in the same visible chain, use `hidden_effect` or
   optional reads.

8. Keep death cleanup idempotent.
   Character/ruler death hooks can fire after variables or lists were already cleaned up by
   another path. Use optional scope links and list removal helpers that tolerate absent entries.

## Validation

Run the relevant generator when editing registry data, then `validate.py --changed --fix --ai-report`.
`validate.py` flags direct top-level `effect` blocks on the hardcoded vanilla hooks above and checks
monthly-country-pulse reachable events for the required one-day delay.

## Relevant Anti-Patterns

- `on_action_simulates_generic_action_actor_context` [advisory]: Broad pulses should not
  manually simulate generic action/building eligibility chains that expect literal
  `scope:actor`; put AI behavior on the generic action itself.
