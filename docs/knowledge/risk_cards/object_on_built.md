# on_built Object Risk Card

Load this card when a target file or generator contains `on_built`.

## Required Checks

1. Do not use `on_built` as the only completion signal for a mechanic that can upgrade or reuse an existing building.
   `on_built` is appropriate for fresh construction only. If the same building can go from level N to N+1, use `on_construction_ended` for the completion path.

2. Do not assume `location_building_level` has already updated inside the same construction-ended hook.
   Treat construction completion callbacks as task notifications. If the next step depends on the new level, schedule or branch from known project state instead of polling the just-updated level synchronously.

3. Keep scope assumptions explicit.
   Building hooks may expose a `location` event target in contexts where tooltip effects do not. In GUI tooltip effects rooted at the location itself, enter the owner with `owner ?= { ... }`; reserve `location.owner` for contexts that actually expose a separate `location` target.

4. Prefer one canonical lifecycle path.
   Do not keep parallel `on_built` and pulse/tooltip repair paths as compatibility fallbacks. This project is unreleased; fix the current lifecycle order instead of preserving old internal state.

## Validation

Run:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```

For Engineering Department wonder building generators, also run:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\test_wonder_mechanics_rules.py
```
