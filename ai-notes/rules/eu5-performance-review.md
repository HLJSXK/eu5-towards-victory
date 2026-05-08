# Rule: EU5 Performance Review

Use this rule for all AI development and CR work on this EU5 mod.

EU5 can be CPU-heavy, so scripts that look harmless in isolation can become expensive when evaluated for every country, every province, every pop, every month, or every GUI item. Treat performance as a first-class review dimension alongside syntax and gameplay logic.

## Required Review Questions

Before approving or merging a change, answer these questions:

1. Does this code run on a frequent pulse such as daily, monthly, yearly, AI tick, GUI refresh, or interaction candidate evaluation?
2. Does it contain broad iterators such as `every_country`, `every_location`, `every_pop`, `every_market`, `any_*`, `ordered_*`, or large dynamic GUI lists?
3. Are expensive iterators protected by cheap gates first?
4. Is this work one-time setup, rare event logic, or repeated background logic?
5. Could the same value be cached in a variable and updated incrementally instead of recomputed repeatedly?
6. Does the GUI evaluate complex expressions inside repeated list items?
7. Does AI evaluation use narrowed candidate lists rather than scanning the whole world?

## Pulse And Iterator Rules

- Avoid unconditional broad scans in `daily_*`, `monthly_*`, and AI tick logic.
- Prefer cheap conditions first:
  - existence checks;
  - simple variables/flags;
  - country ownership/leader checks;
  - milestone state checks.
- Only run broad iterators after all cheap gates pass.
- `every_country` is acceptable for rare one-time setup events, but should be avoided in recurring pulse logic.
- If a value changes predictably, update it incrementally rather than recalculating from global state.

## AI Interaction Rules

- Do not use `every_country` as the default AI candidate source.
- Prefer scoped candidate providers such as friendly/high-opinion countries, neighbors, diplomatic range, same IO members, or relation-based lists.
- Keep `ai_tick_frequency` conservative for interactions that evaluate many targets.
- AI acceptance formulas should avoid nested broad checks.

## GUI Rules

- GUI code is not free: expressions can be reevaluated often while a panel is open.
- Avoid deep nested datamodels unless the list is small or already filtered by the engine.
- Avoid expensive per-item expressions inside large lists.
- Prefer displaying cached variables such as `tv_alliance_cohesion`, `tv_alliance_tier`, and support counts.
- If a custom UI requires derived values, prefer maintaining those values in script variables rather than computing them in GUI.

## Safe Patterns

- One-time `every_country` during milestone reward setup.
- Monthly pulse logic gated by:
  - `exists = international_organization:...`
  - `is_leader_of_international_organization = ...`
  - simple variable checks.
- GUI displaying direct variables with `MakeScope.GetVariable(...).GetValue`.
- Interaction AI source lists filtered by relation or diplomatic range.

## Risky Patterns

- `monthly_country_pulse` with unconditional `every_country`.
- `every_country` nested inside another broad iterator.
- GUI lists where each row performs several variable lookups across unrelated scopes.
- AI interactions with broad target searches and low `ai_tick_frequency`.
- Recomputing counts each month when they can be incremented on add/remove events.

## CR Output Requirement

When reviewing a change, include a short performance section:

- `Performance risk: low / medium / high`
- `Repeated execution paths: ...`
- `Broad iterators: ...`
- `Caching/incremental update opportunities: ...`
- `Recommended follow-up, if any: ...`

If no performance issues are found, explicitly say so.
