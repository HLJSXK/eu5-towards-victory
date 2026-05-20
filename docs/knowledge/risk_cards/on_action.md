# On Action Risk Card

Load this card before editing `common/on_action/` files or adding monthly/yearly/death hooks.

## Required Checks

1. Respect singleton pulse files.
   EU5 on_action keys with direct `effect = { ... }` bodies do not merge safely across files.
   Use the pulse registry generator for shared country/monthly/yearly/death hooks.

2. Preserve vanilla-copy generated files.
   Generated pulse files copy vanilla content and insert TV-owned additions. Do not hand-edit
   copied vanilla sections; update `data/pulse_registry.yaml` and rerun the generator.

3. Verify root/prev assumptions.
   On_action callbacks often run from global, country, character, or situation roots. Capture
   needed values with `save_scope_as` or local variables before entering iterators.

4. Do not assume UI tooltip semantics.
   On_action effects are execution-time, but events they fire can expose option tooltips. If an
   event option reads state written earlier in the same visible chain, use `hidden_effect` or
   optional reads.

5. Keep death cleanup idempotent.
   Character/ruler death hooks can fire after variables or lists were already cleaned up by
   another path. Use optional scope links and list removal helpers that tolerate absent entries.

## Validation

Run the relevant generator when editing registry data, then `validate.py --changed --fix --ai-report`.
For copied vanilla pulse files, `validate.py` checks that non-TV vanilla content remains unchanged.
