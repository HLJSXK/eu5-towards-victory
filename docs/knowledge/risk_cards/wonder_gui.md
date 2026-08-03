# Wonder GUI Risk Card

Load this card for Engineering Department GUI panels, `location_window.gui`,
Europedia wonder cards, generated GUI fragments, and wonder localization used by
GUI widgets.

## Required Checks

1. Remember that `.gui` files are full-file overrides.
   EU5 does not merge GUI files by widget. Any mod that also ships
   `in_game/gui/location_window.gui` can conflict with the wonder overlay. Known
   compat submods splice the overlay into third-party files; do not hand-copy
   partial GUI fragments into the main override.

2. Use tooltip scopes exactly as passed.
   If `ShowScriptedEffectForScope` passes `LocationView.GetLocation.MakeScope.Self`,
   the scripted effect root is already the location. Use `owner ?= { ... }` to
   enter the country. Reserve `location.owner` for callbacks that expose a
   separate `location` event target.

3. Bound paragraph text and its containers.
   A fixed-width `text_multi` with `max_width` and `autoresize` is not enough if
   its parent `hbox`/`vbox` collapses to content. Give explicit-width containers
   the needed layout policy too.

4. Keep dynamic routing numeric and generated.
   Do not use `GetFlagName` as a raw script key for loc, texture, modifier, or
   effect-name concatenation. Store numeric ids and generate branches or use a
   typed datamodel object with a real key accessor.

5. Ceremony card icons use normalized aliases.
   Use generated/verified texticon aliases, not raw nearby vanilla icon names.

6. Prefer GUI display variables refreshed from lifecycle points.
   Do not call expensive rebuilds from hover, tooltip, or render-only paths.

## Validation

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```

For location-window generator changes, run the relevant generator and rely on
`validate.py` freshness checks for generated overrides.
