# Wonder Buildings Risk Card

Load this card for Engineering Department building types, construction hooks,
prices, modifier types, auto modifiers, and wonder-building generators.

## Required Checks

1. Use `on_construction_ended` for completion that includes upgrades.
   `on_built` is not a reliable signal when a mechanic can upgrade or reuse an
   existing building. Do not assume `location_building_level` has updated inside
   the callback.

2. Treat `instant = yes` construction as asynchronous.
   `construct_building instant = yes` and `change_building_level_in_location`
   queue a zero-day task; they do not synchronously update the level in the same
   effect. Use bounded branches or scheduled completion, never a waiting loop.

3. Read actual employment, not nominal capacity.
   `location_building_level` reports completed levels. Labor-sensitive logic
   should enter the building object and read `building_employed_amount`, or use
   the established generated worksite cache.

4. Keep fixed-value pop/manpower/sailor modifiers at or below `0.5`.
   EU5 multiplies fixed values such as `global_pop_conversion_speed`,
   `local_pop_assimilation_speed`, `local_manpower`, and `local_sailors` by
   1000 in game. Use the matching `*_modifier` percent variant for percentages.

5. Use current v1.3 `_efficiency` modifier names.
   Do not reintroduce old v1.2 `_cost` names where the engine now expects
   `_efficiency` names with flipped polarity.

6. `common/prices/` amount fields must stay static.
   Do not put dynamic/conditional script values in `gold =` or sibling price
   fields. Runtime price changes belong in modifiers/auto modifiers through an
   explicitly registered `<price>_cost_modifier` modifier type.

7. New modifier/price/auto-modifier entries need companions.
   Add EN/ZH localization for modifier type names/descriptions, auto-modifier
   names, and bare price names. Modifier types also need `modifier_icons`.

8. Read `building_efficiency` numerically with quoted function-call syntax.
   Use `value = "location.building_efficiency(scope:X)"` or a verified scoped
   equivalent. Do not use colon chains such as `building_efficiency:<id>`.
   Remember this value is labor/staffing satisfaction, not the green input-goods bar.

9. Clean marked local scratch variables.
   For high-risk effects using `# @validate_local_variable_cleanup`, every
   top-level `set_local_variable` must have a later top-level
   `remove_local_variable`.

## Validation

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts_engineering_department\test_wonder_mechanics_rules.py
```
