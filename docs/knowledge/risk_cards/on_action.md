# On Action Risk Card

Load this card before editing `common/on_action/` files or adding monthly/yearly/death hooks.

## Required Checks

1. Respect singleton pulse files.
   EU5 on_action keys with direct `effect = { ... }` bodies do not merge safely across files.
   Use the pulse registry generator for shared country/monthly/yearly/death hooks.

2. Preserve vanilla-copy generated files and hardcoded hook bridges.
   Generated pulse files copy vanilla content and insert TV-owned additions. Do not hand-edit
   copied vanilla sections; update `data/pulse_registry.yaml` and rerun the generator. For
   vanilla hardcoded hooks such as `on_winning_war`, `on_work_of_art_created`, `on_annex`,
   `on_war_declared`, `on_join_war`, `on_ending_war`, and `on_ruler_death`, add TV logic via
   `on_actions = { tv_*_callback }` delegation instead of a second direct `effect`.

3. Delay monthly country pulse events by one day.
   Any event whose conditions are checked from `monthly_country_pulse` must fire one day later.
   Direct calls use `trigger_event_* = { id = <event> days = 1 }`; native `events` and
   `random_events` blocks use `delay = { days = 1 }` before event ids. Keep the delay in
   generator data/templates for generated monthly chains.

4. Verify root/prev assumptions.
   On_action callbacks often run from global, country, character, or situation roots. Capture
   needed values with `save_scope_as` or local variables before entering iterators.

5. Do not assume UI tooltip semantics.
   On_action effects are execution-time, but events they fire can expose option tooltips. If an
   event option reads state written earlier in the same visible chain, use `hidden_effect` or
   optional reads.

6. Keep death cleanup idempotent.
   Character/ruler death hooks can fire after variables or lists were already cleaned up by
   another path. Use optional scope links and list removal helpers that tolerate absent entries.

## Validation

Run the relevant generator when editing registry data, then `validate.py --changed --fix --ai-report`.
For copied vanilla pulse files, `validate.py` checks that non-TV vanilla content remains unchanged.
It also flags direct top-level `effect` blocks on the hardcoded vanilla hooks above and checks
monthly-country-pulse reachable events for the required one-day delay.
