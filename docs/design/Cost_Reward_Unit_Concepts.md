# Cost/Reward & Modifier Unit Concepts

## Purpose

This is a reusable design vocabulary for AI-assisted design work across Towards Victory. It
packages six basic concepts, grouped into three families with different levels of independence
from any one mechanic:

- **One-shot units** (sections 1-3): a **country-level unit**, a **local-level unit**, and a
  **character-level unit**. These live in a standalone, foundational data catalog,
  `data/cost_reward_units.yaml` — **base-layer data, not owned by or read by any single
  mechanic**. The catalog's starting magnitudes were extracted from across the mod (originally
  the Engineering Department's Wonder Construction random-event system, later broadened to other
  recurring one-shot effects used across Academy debate, Arts Exhibition, Research, Governor's
  House, and wonder rituals), but it is maintained **independently**: it is not scoped to only
  what any one system uses. **As of 2026-07 this catalog has its first real consumer**: the
  Unique Wonder Ceremony framework's per-stage `cost` (`data/unique_wonders.yaml`
  `ceremony.stages[i].cost`, see `docs/knowledge/risk_cards/wonders.md` rule 20) reads
  `country_reward`/`local_reward`/`character_reward`/`country_modifier`/`local_modifier`
  directly, negating each entry's value (per the convention below) and, for the two modifier
  categories, applying it as a 5-year temporary modifier rather than a persistent per-level
  one. Future mechanics are still free to look up a "1 unit" magnitude here directly, with no
  dependency on the wonder ceremony or any other existing system. **There is no separate cost
  category**: only
  `country_reward`/`local_reward`/`character_reward` are stored, and a cost is simply the
  negative of the matching reward value, applied by whichever system consumes it.
- **Persistent modifier units** (sections 4-5): a **country-level modifier/unlock unit** and a
  **local-level modifier unit** — real EU5 modifier keys (`clergy_estate_max_tax`, `trade_range`,
  `local_merchant_power`, etc.), *not* one-shot effects, and *not* the same stat vocabulary as
  sections 1-3 (a modifier key like `clergy_estate_max_tax` has no equivalent as a one-shot
  effect, and conversely `government_power` is a one-shot effect target, not a valid
  static-modifier key). Numeric entries are per-level increments; `country_modifier` also holds
  two non-scaling boolean unlocks as YAML `value: true`/`value: false`. These live in the same
  base-layer catalog, `data/cost_reward_units.yaml`: country numeric entries combine the original
  wonder-derived set with current vanilla-supported `Country` keys from reference mod `3599735023`'s
  country blocks, while local numeric entries remain extracted from
  `data/wonder_final_buildings.yaml`'s `final_local`. The catalog is independent of those sources
  (it neither reads them nor is read by them). Sections 4 and 5
  document the generic catalog entries first, then the wonder system's own live implementation as
  a worked example of the same underlying keys.
- **Task pool** (section 6): a catalog of assignable "task" definitions — things a future
  mechanic can assign to the player that resolve to a clear complete/incomplete state — split
  into an **on_action-driven family** (completion detected by hooking a real EU5 on_action
  callback) and a **trigger-driven family** (completion detected by polling a real EU5 trigger
  from the shared monthly dispatcher). These live in a sibling standalone catalog,
  `data/task_pool.yaml` — same independence convention as sections 1-5: nothing in the mod reads
  from it yet, and no reward is stored alongside a task (pairing a task with a reward, e.g. from
  this doc's sections 1-5, is left to whichever future mechanic consumes it).

When designing a new random event or persistent mechanic elsewhere in the mod, reuse these unit
tables instead of inventing new magnitudes from scratch.

Section 1-3 numbers, and the `country_modifier`/`local_modifier` generic entries in sections 4-5,
all live in `data/cost_reward_units.yaml` and can be tuned independently of any one system
through the standalone `cost_reward_editor_web/` tool (`scripts/cost_reward_editor.py`, five
tabs), without touching any other file or triggering any regeneration. The wonder-specific
modifier tables in sections 4-5 are still the wonder system's own live data; retuning them
retunes the wonder system directly. If a future mechanic genuinely needs different magnitudes
than the shared catalog provides, add a new sibling table with a stated divergence rationale (see
"Usage guidance" below) rather than silently drifting these values.

Source systems: `data/cost_reward_units.yaml` (sections 1-3 and the generic entries in sections
4-5, standalone catalog, edited via `cost_reward_editor_web/`); `data/wonder_base_modifiers.yaml`
+ `data/wonder_final_buildings.yaml` + `scripts/wonder_mechanics/_core.py` (the wonder-specific
worked examples in sections 4-5, the generated
`src/in_game/common/auto_modifiers/tv_engineering_department_wonder_mechanics_auto_modifiers.txt`
and `src/in_game/common/building_types/tv_engineering_department_wonder_mechanics_buildings.txt`).
The wonder system's own cost/reward event numbers (`data/wonder_construction_events.yaml`,
`scripts/wonder_construction_event_lib.py`,
`scripts/in_game/events/gen_tv_wonder_construction_events.py`) are a separate, independent copy —
see the note at the end of section 2.

## Core idea: the "1 unit" magnitude (one-shot units)

`data/cost_reward_units.yaml` has three one-shot categories: `country_reward`, `local_reward`,
`character_reward`. Each entry has an `id`, a `value` (the "1 unit" magnitude, always a positive
number), and a `loc` block for display.

**There is no separate cost category.** A cost is simply the negative of the matching reward
value — `government_power` is stored once as `5`; a mechanic that wants a cost applies `-5`
itself. The catalog does not store cost and reward as separate rows, and does not require the
two directions' magnitudes to differ (they can't, since there is only one row). The one exception
is `country_reward.inflation`, whose polarity is inverted — see section 1.

- **Country-level unit** — a standardized 1-unit magnitude for effects applied at country scope
  (the `country_reward` list; negate for a cost).
- **Local-level unit** — a standardized 1-unit magnitude for effects applied at a location scope
  (the `local_reward` list; negate for a cost). *Which* location (a selected/target site, the
  capital, or another designated location) is a choice made by whichever system consumes the
  unit, not something the catalog encodes.
- **Character-level unit** — a standardized 1-unit magnitude for effects applied to a specific
  character (a ruler, a Great Engineer, an artist, etc.), not a country or a location (the
  `character_reward` list; negate for a cost). Added because `add_adm`/`add_dip`/`add_mil` and
  `add_artist_skill` turned out to be the single most recurring one-shot effect pattern across
  the mod — more so than any individual country-scope stat — spanning Academy Philosophy Debate,
  Arts Exhibition, Research Mechanism, Engineering Department, and Governor's House.

The wonder construction event system (this catalog's original inspiration) additionally uses a
"2 unit" crisis/windfall tier for a handful of its own rare event kinds. That tiering is a
wonder-specific event-design choice, not part of this catalog: a future system is free to reuse
the same 1x/2x convention or invent its own multiplier scheme on top of the "1 unit" baseline
stored here.

The remaining two lists, `country_modifier` and `local_modifier`, cover the persistent modifier
units described in sections 4-5 below. Their numeric `value` fields are per-level increments;
`country_modifier` additionally has two non-scaling YAML `value: true`/`value: false` unlock
switches. See "Core idea: the 'per level' unit" further down for how numeric modifier values differ
from the three one-shot reward lists above.

## 1. Country-level unit

`data/cost_reward_units.yaml`'s `country_reward` list:

| id | value | Notes |
|---|---|---|
| `gold` | 1 | Treasury funds. |
| `government_power` | 5 | Auto-resolves to whichever of legitimacy/republican_tradition/devotion/horde_unity/tribal_cohesion applies to the country's government type (the real EU5 effect is `add_government_power`, not `add_legitimacy` — using the latter would only work for monarchies). Value unchanged from the wonder system's original `legitimacy` extraction. |
| `stability` | 7 | |
| `prestige` | 10 | |
| `nobles_satisfaction` | 0.10 | |
| `clergy_satisfaction` | 0.10 | |
| `burghers_satisfaction` | 0.10 | |
| `peasants_satisfaction` | 0.20 | **2x the other three estates** — an intentional asymmetry inherited from the wonder system's original numbers; preserve it if reusing this row. |
| `research_progress` | 5 | Recurs across 5+ files (Arts Exhibition, Governor's House, Research Mechanism, wonder rituals); matches EU5's own `research_progress_mild_bonus` named scale. |
| `army_tradition` | 2.5 | Matches EU5's own `army_tradition_weak_bonus` named scale. |
| `navy_tradition` | 2.5 | Paired with `army_tradition`; kept at the same magnitude for symmetry. |
| `manpower` | 50 | One-shot pool top-up, distinct from the `local_manpower` per-level modifier in section 4. |
| `sailors` | 50 | Paired with `manpower`. |
| `inflation` | 0.05 | **Inverted polarity** — unlike every other row, a *reward* here means REDUCING inflation (apply the real effect with `-value`), and a *cost* means INCREASING it (apply `+value`). Consumers must special-case this row rather than applying the usual "reward = +value, cost = -value" convention. |

A cost is the negative of the value shown (e.g. a `government_power` cost is `-5`), except
`inflation` (see above). The estate-satisfaction and original core-stat magnitudes were extracted
from the wonder construction event system's `non_engineering_tokens` (cost-direction only, at the
time); `research_progress`/`army_tradition`/`navy_tradition`/`manpower`/`sailors`/`inflation` were
added from a broader scan of recurring one-shot effects used across the rest of the mod (Academy
debate, Arts Exhibition, Research Mechanism, Governor's House, wonder rituals). This list is *not*
the wonder system's own `domestic_support`/competence-stat/`construction_progress`
Engineering-Department-IO variables — those remain wonder-specific and are intentionally excluded
from this general-purpose catalog (see the relationship note at the end of section 2).

## 2. Local-level unit

`data/cost_reward_units.yaml`'s `local_reward` list:

| id | value | Notes |
|---|---|---|
| `development` | 0.25 | Development at whichever location the consuming system targets. |
| `prosperity` | 0.2 | Prosperity at whichever location the consuming system targets. |
| `laborers` | 10 | Population-percentage magnitude. |

A cost is the negative of the value shown (e.g. a development cost is `-0.25`). A broader mod-wide
scan (beyond the wonder system) found no other recurring one-shot local-scope effects — only
`change_development`/`change_prosperity` repeat across multiple systems (also used in Arts
Exhibition and Governor's House); everything else location-related in the mod (autonomy, unrest,
migration attraction, literacy caps, etc.) exists only as a *persistent* modifier, already covered
by section 5's `local_modifier` list.

**Scope convention:** "local-level" means the effect targets a location; *which* location is
decided by whichever system consumes this unit, not by the catalog itself.

**Relationship to the wonder system's own numbers:** the Engineering Department Wonder
Construction random-event system (`data/wonder_construction_events.yaml`) keeps a separate,
**independent** set of magnitudes that happens to overlap with, but is neither identical to nor
derived from, this catalog:

- Its `non_engineering_tokens` split `development`/`prosperity` into site-specific and
  capital-specific variants (`site_development`/`capital_development`,
  `site_prosperity`/`capital_prosperity`) rather than one generic entry per stat, and are
  cost-only (the wonder system has no local reward-direction equivalent).
- Its `engineering_tokens` (`domestic_support`, the three competence stats,
  `construction_progress`) are Engineering-Department-IO-specific reward stats with no equivalent
  in this catalog.
- Its magnitudes are consumed through concrete EU5 effect syntax (`ENG_EFFECTS`/`NONENG_EFFECTS`
  in `scripts/in_game/events/gen_tv_wonder_construction_events.py`, with custom stats wrapped in
  `custom_description` + `effect_localization` — see
  `src/in_game/common/scripted_effects/tv_engineering_department_effects.txt` for a worked
  example of that wrapping convention). This catalog has no such generator wiring; it is plain
  data waiting for a future consumer.

Editing `data/cost_reward_units.yaml` does **not** change any wonder event's actual magnitude,
and editing `data/wonder_construction_events.yaml` does not change this catalog. If a design
change should logically apply to both, update them separately and deliberately — there is no
automatic sync.

## 3. Character-level unit

`data/cost_reward_units.yaml`'s `character_reward` list:

| id | value | Notes |
|---|---|---|
| `adm` | 3 | Administrative skill points on a specific character (e.g. `ruler ?= { add_adm = 3 }` or `var:tv_academy_leader_char ?= { add_adm = 3 }`). |
| `dip` | 3 | Diplomatic skill points, same pattern. |
| `mil` | 3 | Military skill points, same pattern. |
| `artist_skill` | 0.05 | `add_artist_skill` on a touring/local artist character. |

A cost is the negative of the value shown (e.g. an ADM cost is `-3`). This is the **most
recurring** one-shot effect family in the entire mod: `add_adm`/`add_dip`/`add_mil` appear across
Academy Philosophy Debate, Arts Exhibition, Research Mechanism, Engineering Department, and
Governor's House event/effect files, with real values ranging roughly ±1 to ±20 depending on
context; `3` was chosen as a representative mid-range "1 unit." `add_artist_skill` appears across
Academy Philosophy Debate and Arts Exhibition at real values around 0.05 (occasionally
±0.03/-0.04).

**Scope convention:** "character-level" means the effect targets a specific character scope (a
ruler, an appointed IO leader, an artist, etc.), not the country or a location. *Which* character
is decided by whichever system consumes this unit — the catalog does not encode a target.

## Core idea: the "per level" unit (persistent modifiers)

Distinct from the one-shot units above, a **persistent modifier unit** describes a bonus that
accrues *per completed level* of whatever multi-level mechanic grants it (a wonder, a building
chain, or any future leveled mechanic), rather than firing once. Here "1 unit" means: the value
stored *is* the per-level increment — some scaling mechanism (an explicit `scales_with` block, or
the engine's native per-building-level application) multiplies it by the current level at
runtime, so it is never pre-multiplied in the source data.

The generic catalog and its source data have distinct roles:

- **The generic catalog** — `data/cost_reward_units.yaml`'s `country_modifier`/`local_modifier`
  lists. Unlike sections 1-3, these are **not** the generic gold/government_power/stability/
  prestige stat vocabulary — a real EU5 static modifier key like `clergy_estate_max_tax` or
  `trade_range` has no equivalent as a one-shot effect, and conversely `government_power` is a
  one-shot effect target with no meaning as a static-modifier key. Numeric entries are real
  per-level increments and can be negative when the real modifier is beneficial as a negative
  number (e.g. a cost-reduction modifier). The country list combines 40 original wonder-derived
  numeric entries with 353 numeric entries from current vanilla-supported `Country` keys in
  reference mod `3599735023` country blocks; after resolving vanilla script values, the latter use
  the smallest nonzero absolute value for each key. It also contains two literal YAML
  `value: true`/`value: false` unlock switches, which never scale by level. These entries are
  plain data with no generator wiring of their own.
- **The wonder system's own live data** — `data/wonder_base_modifiers.yaml` and
  `data/wonder_final_buildings.yaml`, which carry the wonder system's actual, much more
  heterogeneous set of per-level modifier keys (percentages, flat ranges, tax rates — there is no
  single universal "1 unit = X" constant across all of them). This is real, live wonder data —
  retuning it retunes the wonder system directly — and remains the source for the original country
  subset and the local catalog entries.

Sections 4-5 below present the generic catalog entries first, then the wonder system's own live
magnitudes as a worked implementation; the reference-mod source for the expanded country catalog
is documented in section 4 and the source references.

This per-level convention is **size-independent** in the wonder system: a small, medium, or large
wonder uses the same per-level magnitude for a given modifier key, and every wonder shares the
same 0-6 level cap. Size only changes construction cost/time and — for small wonders specifically
— restricts which modifier keys may be used at all (see section 4). Unique wonders apply
`base_effect_multiplier = 2`, which doubles the per-level unit inherited from their generic
prototype (so a unique wonder's "1 unit" is 2 generic units) — the same doubling convention as
the wonder event system's own 2-unit tier, applied here to a per-level rate instead of a one-shot
value.

## 4. Country-level modifier unit

**Generic catalog** — `data/cost_reward_units.yaml`'s `country_modifier` list has 395 entries:
393 numeric per-level modifier keys and two boolean unlock keys. It retains the original 40 numeric
keys exhaustively extracted from the wonder system's ~51 generic mechanics, then adds 353 numeric
keys retrieved from current vanilla-supported `Country` keys in reference mod `3599735023`'s
country blocks. For each reference numeric key, the catalog first resolves the vanilla script value,
then uses the smallest nonzero absolute value across its source occurrences. Reference-mod-specific
custom modifier types, including its administrative-innovation-point types, are intentionally excluded.
The 34 distinct `monthly_towards_*` value-movement axes remain generalized into one
`monthly_towards_axis` entry rather than 34 near-duplicate rows. The catalog also includes
`imperial_authority_modifier`. The two boolean entries (`allow_open_sea_exploration`,
`gender_equality`) use literal YAML `value: true` as non-scaling unlock switches, not numeric
per-level magnitudes — despite the general `value: true`/`value: false` convention described
throughout this doc, both currently-defined boolean entries happen to be `true`; there is no
`value: false` example in the catalog today. The Unique Wonder Ceremony's cost consumer (see
`docs/knowledge/risk_cards/wonders.md` rule 26) excludes both from its usable pool for this
reason, along with the `monthly_towards_axis` placeholder. A representative numeric sample:

| id | `country_modifier` numeric value (per level) |
|---|---|
| `clergy_estate_max_tax` | 0.1 |
| `clergy_estate_target_satisfaction` | 0.05 |
| `monthly_towards_axis` (generalizes any `monthly_towards_*` value-movement modifier; 34 axes used) | 0.05 |
| `monthly_legitimacy` | 0.05 |
| `trade_range` / `naval_range` / `colonial_range` | 200 |
| `hire_privateer_cost_modifier` | -0.05 |
| `privateer_maintenance_cost_modifier` | -0.03 |
| `privateer_durability` | 0.05 |
| `imperial_authority_modifier` | 0.05 |
| `global_pop_conversion_speed` | 0.002 |
| `tolerance_heretic` / `tolerance_heathen` / `tolerance_own` | 0.5 |

See `data/cost_reward_units.yaml` for the complete 395-entry list (also retaining the original
`global_merchant_power`, `country_cabinet_efficiency`, `exploration_mission_speed`,
`pop_join_rebel_threshold`/`pop_leave_rebels_threshold`, `research_speed`, `ship_build_speed`,
`tax_income_efficiency`, `merchant_maintenance_efficiency`, `global_pop_promotion_speed`,
`global_monthly_prosperity`, `global_food_capacity_modifier`, `monthly_army_tradition`,
`num_possible_artists`, `artist_salary_modifier`, `cultural_influence_modifier`,
`skill_of_new_artists`, `diplomatic_reputation`, `monthly_rebel_growth`,
`global_trade_center_power`, `minting_income_factor`, `cultures_capacity`,
`monthly_navy_tradition`, and more).

Some entries are negative because a lower value is the beneficial direction (e.g. the two
privateer-cost modifiers) — `value` is a real signed modifier amount here, not a magnitude with
direction implied by the list (unlike sections 1-3). The Unique Wonder Ceremony's cost consumer
(see `docs/knowledge/risk_cards/wonders.md` rule 26) is this list's first real reader, applying
each usable entry as a 5-year temporary country modifier rather than a persistent per-level one
— it is otherwise still plain data for a future leveled mechanic to consume directly, independent
of the wonder system below. The two boolean unlocks are excluded from the ceremony's usable pool
(see the note in section 4 above); more generally, their YAML `value: true`/`value: false` is a
flat switch and must never be multiplied by the mechanic's level.

**Wonder system's own live data** — authored in `data/wonder_base_modifiers.yaml` as
`base_modifiers.<mechanic_key>.<modifier_key>: <value>`.
The generator (`scripts/wonder_mechanics/_core.py`, `wonder_base_country_modifiers`) writes that
value, multiplied only by `base_effect_multiplier` (1 generic / 2 unique — **never** by size), into
a generated Country Auto modifier gated by a `scales_with = { value = "variable_map(tv_wonder_auto_level_by_wonder_id|<id>)" }`
block, so the effective in-game bonus is `unit value × current wonder level`.

Representative 1-unit (generic, level-1-equivalent) magnitudes actually in use:

| Modifier key | 1-unit (generic) value | Unique (2x) value | Notes |
|---|---|---|---|
| `clergy_estate_max_tax` | `0.1` | `0.2` | `sacred_mountain`, per level. |
| `clergy_estate_target_satisfaction` | `0.05` | `0.1` | `sacred_mountain`, per level. |
| `monthly_towards_spiritualist` / `monthly_towards_centralization` / `monthly_towards_naval` / etc. (any `monthly_towards_*` value-movement modifier) | `0.05` | `0.1` | The **only** modifier family small wonders may use (see restriction below); also used by medium/large wonders. |
| `monthly_legitimacy` | `0.05` | `0.1` | `triumphal_axis`, per level. |
| `trade_range` / `naval_range` / `colonial_range` | `200` | `400` | `great_lighthouse`; doubled value confirmed on `unique_pharos_lighthouse` (`base_effect_multiplier = 2`). |
| `hire_privateer_cost_modifier` | `-0.05` | n/a | `pirate_port`, per level. |
| `privateer_maintenance_cost_modifier` | `-0.03` | n/a | `pirate_port`, per level. |
| `privateer_durability` | `0.05` | n/a | `pirate_port`, per level. |

**Non-numeric (unlock-type) modifiers are a separate, unscaled unit.** A boolean/flag value (e.g.
`can_hire_privateers: true`) is split by the generator into a second, hidden Country Auto
modifier (`..._unscaled`, `hide_effects = yes`) that unlocks flat the moment any level exists — it
does not multiply by level. The generic catalog's two country unlock rows use the same semantics:
they store only YAML `value: true`/`value: false`, with no extra kind field and no level scaling.
Treat this as "1 unlock unit," distinct from "1 per-level numeric unit," when designing a new
country-level modifier.

**Small-wonder restriction:** small wonders may only use `monthly_towards_*` value-movement
modifiers as their country-level modifier unit (enforced by `validate_wonder_size_base_country_modifier_rules`
in `scripts/wonder_mechanics/_core.py`) — any other modifier key on a small wonder is a build-time
error, not a style choice. Medium/large wonders have no such key restriction.

**Engine-fixed-scale ceiling:** for the small set of modifiers EU5 multiplies by 1000 internally
(`local_manpower`, `global_pop_conversion_speed`, `local_pop_conversion_speed`,
`global_pop_assimilation_speed`, `local_pop_assimilation_speed`, `local_sailors`), keep the chosen
per-level unit value low enough that `value × base_effect_multiplier × 6` (worst case: unique
wonder at max level) never exceeds `0.5` — this is an existing hard validator, not a suggestion
(see `docs/knowledge/risk_cards/wonders.md` rule 2).

## 5. Local-level modifier unit

**Generic catalog** — `data/cost_reward_units.yaml`'s `local_modifier` list, **exhaustively**
extracted from the wonder system's own per-level local modifier magnitudes: every distinct
numeric key across all ~51 generic wonder mechanics' `final_local` blocks in
`data/wonder_final_buildings.yaml` (41 entries), plus the `local_cultural_tradition`/
`local_cultural_influence` baseline every final wonder building carries regardless of type — 43
entries total. A representative sample:

| id | `local_modifier` value (per level) |
|---|---|
| `local_cultural_tradition` | 0.5 |
| `local_cultural_influence` | 0.5 |
| `local_merchant_power` | 5 |
| `local_merchant_capacity` | 2.5 |
| `local_crown_estate_power` | 0.5 |
| `local_defensive` | 0.2 |
| `local_unrest` | -0.1 |
| `local_food_capacity_modifier` | 5000 |
| `free_building_levels` | 25 |

See `data/cost_reward_units.yaml` for the complete list of 43 entries (also covering
`local_manpower`, `movement_cost`, `local_build_buildings_efficiency`, `harbor_suitability`,
`local_trade_center_power`, `local_production_efficiency`, `local_max_rgo_size_modifier`,
`local_pop_promotion_speed`/`local_pop_promotion_speed_modifier`,
`local_distance_from_capital_speed_propagation`, `local_max_literacy`,
`local_pop_conversion_speed`/`local_pop_conversion_speed_modifier`,
`local_monthly_development_modifier`, `local_ship_build_speed`, `max_ships_built_at_same_time`,
`local_garrison_size`, `local_frontage_allowed`, `local_manpower_modifier`,
`local_monthly_food_modifier`, `local_population_growth`, `local_monthly_prosperity`,
`local_migration_attraction`, `local_rgo_build_time`, `local_raw_material_output`,
`local_port_cost_distance_impact`, `local_fort_maintenance_efficiency`,
`local_hostile_attrition`, `local_market_access`, `local_merchant_capacity_modifier`,
`local_clergy_max_literacy`, `local_maritime_presence`, and `local_navy_attrition`).

`fort_level` is deliberately excluded: it is a flat, non-per-level `raw_modifier` in the wonder
system (see below), so it does not fit this per-level catalog's definition. The Unique Wonder
Ceremony's cost consumer (see `docs/knowledge/risk_cards/wonders.md` rule 26) is this list's
first real reader, applying each entry as a 5-year temporary location modifier at the wonder's
own site rather than a persistent per-level one — it is otherwise still plain data for a future
leveled mechanic to consume directly, independent of the wonder system below.

**Wonder system's own live data** — authored in `data/wonder_final_buildings.yaml` as
`buildings.<mechanic_key>.final_local.<modifier_key>: <value>`.
Unlike the country-level unit, there is no explicit `scales_with` block — the value is written
directly into the final building's `modifier` block, and EU5's native per-building-level scaling
(the building itself has `max_levels = 6`) multiplies it by the building's own completed level.
`base_effect_multiplier` (1 generic / 2 unique) still applies before that native scaling.

Representative 1-unit (generic, per-level) magnitudes actually in use:

| Modifier key | 1-unit value | Block | Notes |
|---|---|---|---|
| `local_cultural_tradition` | `0.5` | `modifier` | Fixed baseline present on **every** final wonder building regardless of type — not authored per-wonder in `final_local`. |
| `local_cultural_influence` | `0.5` | `modifier` | Same fixed baseline, always paired with `local_cultural_tradition`. |
| `local_merchant_power` | `5` | `modifier` | `colonial_trade_company`'s final building (`tv_wonder_chartered_company_exchange`), per level. |
| `local_merchant_capacity` | `2.5` | `modifier` | Same building, per level. |
| `local_crown_estate_power` | `0.5` | `modifier` | `star_fortress_city` ritual annex building, per level. |
| `fort_level` | `2` | `raw_modifier` | Same annex building — **flat**, not per-level: `raw_modifier` values apply once regardless of the building's own level, unlike everything in `modifier`. |

**`modifier` vs `raw_modifier` is the defining split for this unit**, matching the CLAUDE.md
"Wonder/building effect split" rule: put a per-level local-level modifier unit in `modifier`; put
a flat, level-independent local ceremony-style effect (the only confirmed key today is
`fort_level`) in `raw_modifier`.

**Display-only mirroring:** a final building's generated `modifier` block also mirrors in that
wonder's country-level `base_modifiers` values (e.g. `global_merchant_power`,
`monthly_towards_free_trade`) purely so the location window's `ShowModifierEffect` tooltip can
display them. That mirrored copy is display-only — the actual national/global effect is applied
by the country-level modifier unit (section 4) through the Country Auto modifier, not by the
building. Do not read the mirrored values as a second, independent local-level effect.

## 6. Task pool

`data/task_pool.yaml` — a standalone catalog of assignable task definitions, independent of
sections 1-5 and of any mechanic that might consume it. A "task" is something assignable to the
player that resolves to a clear complete/incomplete state. Unlike sections 1-5, no reward value
is stored: this catalog only records *what must happen* or *what must be reached*, and *how the
engine detects it*. Pairing a task with a reward (e.g. an entry from sections 1-5 above) is a
decision for whichever future mechanic consumes the task.

Two families, split by how completion is detected — the same two detection mechanisms already
used throughout the rest of the mod (on_action callbacks and the shared monthly poll
dispatcher), not a new detection mechanism invented for this catalog.

### 6.1 On_action-driven tasks

`data/task_pool.yaml`'s `on_action_task` list, 48 entries (24 from the initial pass, 24 from a
bolder second wave — see 6.3). Completion is detected by hooking a real EU5 on_action — an engine
callback that fires the moment a qualifying action happens in-game — rather than by polling game
state. Every entry names a real vanilla on_action, verified against
`reference_game_files/game/in_game/common/on_action/_hardcoded.txt` (plus a few from
`exploration_mission_monthly.txt` and `parliament_monthly_pulse.txt`) and cross-checked against
`reference_official_defines/`, together with the exact `root`/`scope:x` variables that on_action
provides (copied from the vanilla source comment, not paraphrased) and a `completion_note`
recording any extra condition needed to turn "the on_action fired at all" into "this specific
task is complete" (e.g. only root's own action counts, not the counterparty's).

**The `wired` flag is the key implementation-cost signal**, following the existing pulse-registry
mechanism documented in `data/pulse_registry.yaml` and generated into
`src/in_game/common/on_action/tv_pulse_bridges.txt` by
`scripts/in_game/common/on_action/gen_tv_pulse_registry.py`:

- `wired: true` — this on_action already has a Towards Victory bridge entry. A consuming
  mechanic adds its own TV-named on_action under the existing bridge block without touching
  `data/pulse_registry.yaml` itself. 19 of the 48 entries are already wired: the 13 from the first
  wave (`on_winning_war`, `on_siege_won`, `on_took_location_in_peace_treaty`, `on_royal_marriage`,
  `on_subject_created`, `on_becoming_free`, `on_reform_change`, `on_capital_moved`,
  `on_work_of_art_created`, `on_institution_embraced`, `on_colonial_charter_finished`,
  `on_exploration_success`, `on_parliament_passed`) plus 6 more from the second wave
  (`on_bureaucracy_added`, `on_policy_changed`, `on_cabinet_assigned`,
  `on_character_moved_country`, `on_transfer_subject`, `on_dependency_gained` — all already
  bridged for other TV systems' own on_action needs).
- `wired: false` — a real, verified vanilla hook, but nothing in the mod currently bridges it. A
  consuming mechanic must add a new entry to `data/pulse_registry.yaml`'s `bridges` map and
  re-run the generator before it can fire. 29 of the 48 entries: the 11 from the first wave
  (`on_great_battle_won`, `on_annexed`, `on_union_formation`, `on_enforce_peace_accepted`,
  `on_gift_sent`, `on_government_type_change`, `on_international_organization_creation`,
  `on_international_organization_changed_leader`, `on_gain_great_power_status`, `on_made_saint`,
  `on_new_country_formed`) plus 18 more from the second wave (`on_command_gained`, `on_election`,
  `on_character_estate_change`, `on_parliament_established`, `on_io_parliament_passed`,
  `on_international_organization_disbanding`, `on_marriage_union_formation`,
  `on_released_country`, `on_regency_end`, `on_heir_selection_changed`,
  `on_subject_type_changed`, `on_country_rank_change`, `on_gain_hegemon_status`,
  `on_mission_completion`, `on_embrace_revolution`, `on_culture_changed`,
  `on_international_organization_policy_changed`, `on_insult`).

Categorized as `political` (21: government/policy/reform/parliament/heir-law changes, IO
founding/leadership/disbanding/policy votes, rank, hegemon status, revolution, missions),
`diplomatic` (12: royal/other marriages, unions, subjects and independence, mediation, gifts,
insults), `military` (6: win a war/siege/great battle, annex a country, take a location in peace,
take command of an army), `economic_colonial` (5: colonial charter, exploration mission, found a
new country, pass a parliament vote, complete a country mission), and `religious_cultural` (4:
canonize a saint, create a work of art, embrace an institution, change primary culture).

**Reuse note:** `create_masterpiece` (`on_work_of_art_created`) is already consumed by the live
Cultural Victory CIP source (`tv_on_work_of_art_created_callback` in the `on_work_of_art_created`
bridge block — see `Towards_Victory_Design.md` section 3.5). A new task built on the same hook
adds its own TV-named on_action under that existing bridge block rather than a second bridge
entry for the same vanilla key — the risk card rule against duplicate direct bridges to one
vanilla on_action key applies here (see `docs/knowledge/risk_cards/on_action.md`).

### 6.2 Trigger-driven tasks

`data/task_pool.yaml`'s `trigger_task` list, 48 entries (24 from the initial pass, 24 from the
second wave). Completion is detected by polling a real EU5 trigger — verified against
`reference_official_defines/docs/triggers.log` — from a monthly check, reusing the same
`monthly_country_pulse` dispatcher every other TV system's monthly logic already goes through
(see `data/pulse_registry.yaml`'s `pulses.monthly_country_pulse` list), not a separate polling
mechanism invented for this catalog.

Each entry has a `scope` (`country`: 38, `character`: 7, `international_organization`: 2, `unit`:
1 — the last two are second-wave additions, see 6.3), a `comparison` direction, and a
`representative_threshold`:

- `comparison: gte` (41 entries) — the ordinary case, e.g. `reach_owned_locations`
  (`num_locations >= 50`).
- `comparison: lte` (1 entry) — inverted polarity, paralleling `country_reward.inflation` in
  section 1: completion means the value stays AT OR BELOW the threshold. The one entry using
  this today is `keep_war_exhaustion_low` (`war_exhaustion <= 5`).
- `comparison: boolean` (6 entries) — the trigger is itself a yes/no fact with no numeric
  threshold (e.g. `become_recognized_great_power` on the `is_great_power` trigger);
  `representative_threshold` is `null` for these entries.

**The threshold is illustrative only** — exactly like the "1 unit" convention in sections 1-5: a
single plausible instance of "reach this," not a tuned milestone tier. A future mechanic scales
it up or down, or substitutes its own multi-tier ladder entirely (the same way
`victory_paths.yaml`'s milestones use their own 5-tier thresholds per path rather than one flat
number) — playtesting decides the final number, not this catalog.

Three entries deliberately mirror an existing victory path's own core metric, so a future
mechanic can sanity-check a task threshold against a live, already-balanced number:
`sustain_monthly_trade_income` (`monthly_trade_income`, mirrors Trade Victory, section 3.3 of
`Towards_Victory_Design.md`), `reach_owned_locations` (`num_locations`, mirrors Conquest Victory,
section 3.1), and `reach_advances_researched` (`num_of_advances_researched`, mirrors Scientific
Victory, section 3.6).

Categorized as `military` (13: army/regular/expected/potential army and navy sizes,
manpower/sailors pools, war exhaustion, army/navy tradition, at-war-with-a-rival, unit morale),
`diplomatic` (10: prestige, stability, government power/legitimacy percentage, diplomats,
average estate satisfaction, Great Power score/status, recognized-as-subject), `economic` (7:
treasury and treasury percentage, monthly income, monthly trade income, markets with merchants,
colonial charters, owned ports), `character` (7, second-wave only: ADM/DIP/MIL thresholds, trait
count, child count, longevity, having an heir), `territorial` (3: owned locations, owned
provinces, total development), `religious_cultural` (3: dominant state religion, a specific
culture's or religion's population share), `international_organization` (2: IO electors, IO
combined Great Power score), `economic_colonial` (1: colonial overlord status), `science` (1:
advances researched), and `political` (1: hold a specific government reform).

**Milestone tooltip reuse:** if a future mechanic surfaces a trigger-driven task's progress in
the UI, the CLAUDE.md **Milestone Trigger Tooltip Pattern** (one `custom_tooltip` block per
condition group, not `custom_description`) is the proven pattern to copy — it is exactly how
`data/victory_paths.yaml`'s own milestone triggers already display a "reach X" condition with an
independent pass/fail indicator per line.

### 6.3 Second wave: wider and bolder

The second wave deliberately reaches into scopes and on_action hooks the first wave left
untouched, at the cost of some entries being less certain to map cleanly onto a "task" the moment
they're implemented. Two optional fields mark that explicitly rather than silently:

- **`requires_target`** (`trigger_task` only, 4 entries: `dominant_culture_share`,
  `dominant_religion_in_realm`, `hold_specific_reform`, `at_war_with_rival`) — the trigger itself
  needs an extra parameter (a specific culture/religion/reform/country id) beyond scope and
  threshold that this catalog cannot pin down generically; the field records what kind of target
  is needed, and the consuming mechanic supplies the actual id.
- **`verify_in_game: true`** (10 `on_action_task` entries, 5 `trigger_task` entries) — the
  on_action/trigger *name* is still verified against source the same as every other entry, but
  the task design built on top of it — its scope resolution, its "is this really a reachable,
  positive task" framing, or an ambiguous direction (e.g. `on_country_rank_change` fires on a
  rank *change*, not specifically a rise) — has not been confirmed by loading the game. Each such
  entry's `completion_note`/`loc` spells out exactly what is uncertain. Treat these as
  design-complete but implementation-unverified: spot-check the specific hook/trigger behavior
  in-game before building a real mechanic on one.

The second wave's new scopes: **character-scope** on_actions (`take_command_of_army` on
`on_command_gained`) and triggers (`adm`/`dip`/`mil`/`num_of_traits`/`num_of_children`/
`age_in_years`/`is_heir` — a person, not the country, is what must change or reach a value);
**International Organization-scope** on_actions (`pass_io_parliament_vote`,
`disband_international_organization`, `adopt_io_policy`) beyond the first wave's country-scope
entries; **unit-scope** (`unit_morale_threshold` on `morale_percentage` — a specific army/navy
unit, not the country); and **percentage-of-maximum** triggers
(`gold_percentage`/`prestige_percentage`/`legitimacy_percentage`), a different flavor of "reach X"
from the first wave's flat magnitudes.

## Usage guidance for future design work

- When designing a new random event or one-off effect elsewhere in the mod, pick an entry from
  `data/cost_reward_units.yaml`'s `country_reward`/`local_reward`/`character_reward` lists
  (sections 1-3) instead of choosing a new arbitrary magnitude — negate the value for a cost
  (except `country_reward.inflation`, which is inverted — see section 1). This catalog has no
  dependency on the wonder system and is meant to be read directly by any future mechanic.
- When designing a new persistent, level-scaling country or local modifier elsewhere in the mod,
  first check `data/cost_reward_units.yaml`'s `country_modifier`/`local_modifier` lists (the
  generic catalog part of sections 4-5) for a matching modifier key before inventing a new
  per-level rate — these are independent of the wonder system, same as sections 1-3, and already
  cover several real modifier keys (e.g. `trade_range`, `imperial_authority_modifier`,
  `local_merchant_power`). For a country-level boolean unlock, use a literal YAML
  `value: true`/`value: false` as a non-scaling switch, never as a per-level value. Only reach
  for the wonder-specific tables (the rest of sections 4-5, still the wonder system's own live
  data) as a worked-syntax reference, or when the new mechanic genuinely needs a modifier key that
  has no equivalent in the generic catalog yet — in which case, consider adding it to the generic
  catalog too if it's reusable beyond that one mechanic. Keep the country/local,
  `modifier`/`raw_modifier`, and scaled/unscaled distinctions intact when following the
  wonder-specific tables — they are structural, not stylistic.
- If implementing a new cost/reward unit as an EU5 scripted effect and it needs a "severity" tier
  beyond the catalog's baseline "1 unit," the wonder event system's own 1x/2x convention (rare
  crisis/windfall at 2x) is a proven pattern to copy, but is not mandatory — invent whatever
  multiplier scheme fits the new mechanic on top of the catalog's stored 1-unit value.
- Any new custom (non-vanilla) stat implemented as an EU5 scripted effect should follow the
  `custom_description` + `effect_localization` wrapping convention demonstrated by the wonder
  system's own effects (`src/in_game/common/scripted_effects/tv_engineering_department_effects.txt`
  + `src/in_game/common/effect_localization/tv_engineering_department_effects.txt`) — never call a
  bare custom effect with no tooltip text.
- If a small-sized wonder-like mechanic is involved, remember the `monthly_towards_*`-only
  restriction on country-level modifier keys (section 4) applies to size, not to level or
  uniqueness.
- When designing a new assignable-task mechanic, pick an entry from `data/task_pool.yaml`'s
  `on_action_task`/`trigger_task` lists (section 6) instead of inventing a new detection hook
  from scratch. For an on_action-driven task, check the entry's `wired` flag first — `wired:
  true` needs only a new TV-named on_action under the existing bridge block, while `wired: false`
  needs a new `data/pulse_registry.yaml` bridge entry plus a regenerator run before the hook can
  fire. For a trigger-driven task, treat `representative_threshold` as a starting point only and
  retune it during playtesting, the same as any milestone threshold elsewhere in the mod. Neither
  family stores a reward — pair the chosen task with an entry from sections 1-5 above (or a
  bespoke reward) as part of designing the consuming mechanic, not by editing this catalog.
- This doc packages existing numbers; it is not a live proxy for either data source. If
  `data/cost_reward_units.yaml` changes (any of its five lists), update the matching section(s)
  above to match; if the wonder system's own modifier magnitudes change, update the wonder-specific
  parts of sections 4-5 to match. If a different mechanic genuinely needs a different magnitude
  for the same stat, add a new sibling table (e.g. a "Cost/Reward & Modifier Unit Concepts —
  <mechanic>" section or doc) with a one-line rationale for the divergence, rather than quietly
  drifting these shared tables.

## Source references

- `data/cost_reward_units.yaml` — the standalone, foundational unit catalog, five top-level
  lists: `country_reward`/`local_reward`/`character_reward` (sections 1-3, one-shot — negate for
  a cost, no separate cost list) and `country_modifier`/`local_modifier` (sections 4-5).
  Numeric modifier entries are per-level; the two country unlock rows are literal YAML
  `value: true`/`value: false` non-scaling switches. Each entry is an `id`/`value`/`loc`.
  Edited through the standalone `cost_reward_editor_web/` tool
  (`scripts/cost_reward_editor.py`, default port 8766, five tabs).
- `data/wonder_construction_events.yaml` — the wonder system's own, independent copy of
  cost/reward token magnitudes (both `engineering_tokens` and `non_engineering_tokens` carry a
  `value` field). Not read by, and does not read from, `cost_reward_units.yaml`.
- `scripts/wonder_construction_event_lib.py` — the wonder system's 12 event kinds and their
  combinatorics, plus `format_noneng_magnitude`/`NONENG_MAGNITUDE_DECIMALS` (shared presentation
  formatting for its own non-engineering magnitudes).
- `scripts/in_game/events/gen_tv_wonder_construction_events.py` — the wonder system's own
  `ENG_EFFECTS`/`NONENG_EFFECTS` dicts mapping each of its tokens to exact EU5 effect syntax.
- `src/in_game/common/scripted_effects/tv_engineering_department_effects.txt` — `custom_description`-wrapped
  reward/cost effects (a worked example of the wrapping convention, wonder-specific).
- `src/in_game/common/effect_localization/tv_engineering_department_effects.txt` — tooltip text
  registrations for the wrapped effects above.
- `data/wonder_base_modifiers.yaml` — per-wonder-mechanic country-level modifier values (section 4).
- `data/wonder_final_buildings.yaml` — per-wonder-mechanic `final_local`/`final_maintenance`/`final_attributes`
  values (section 5).
- `reference_mods/3599735023/` — reference source for the 353 added numeric country modifier keys:
  retain only current vanilla-supported `Country` keys in its country blocks, resolve vanilla script
  values, then use the smallest nonzero absolute value for each key; exclude modifier types added
  by that reference mod itself.
- `scripts/wonder_mechanics/_core.py` — `wonder_base_country_modifiers`, `authored_final_building_local_modifiers`,
  `scale_numeric_modifier_mapping`, `split_scaled_modifiers`, `validate_wonder_size_base_country_modifier_rules`,
  and the engine-fixed-scale ceiling check.
- `src/in_game/common/auto_modifiers/tv_engineering_department_wonder_mechanics_auto_modifiers.txt` —
  generated, level-gated Country Auto modifiers (section 4).
- `src/in_game/common/building_types/tv_engineering_department_wonder_mechanics_buildings.txt` —
  generated final/helper building `modifier`/`raw_modifier` blocks (section 5).
- `data/task_pool.yaml` — the standalone task-pool catalog (section 6), two top-level lists:
  `on_action_task` (48 entries: `id`/`on_action`/`wired`/`scope`/`category`/`completion_note`/`loc`,
  optionally `verify_in_game`) and `trigger_task` (48 entries:
  `id`/`trigger`/`scope`/`comparison`/`representative_threshold`/`category`/`loc`, optionally
  `requires_target`/`verify_in_game`). No reward is stored; no generator exists (plain data, same
  as `cost_reward_units.yaml`). Edited through the same standalone `cost_reward_editor_web/` tool
  (two additional tabs beyond the original five, editing only `wired`/`completion_note` for
  `on_action_task` and `comparison`/`representative_threshold` for `trigger_task` — everything
  else, including the two second-wave-only fields, stays read-only in the editor and is edited
  directly in the YAML).
- `data/pulse_registry.yaml` + `scripts/in_game/common/on_action/gen_tv_pulse_registry.py` —
  the existing on_action bridge registry a `wired: false` task entry (section 6.1) must be added
  to before its on_action can fire; `wired: true` entries already have a bridge block here.
- `reference_game_files/game/in_game/common/on_action/_hardcoded.txt` (plus
  `exploration_mission_monthly.txt`, `parliament_monthly_pulse.txt`) — the vanilla on_action
  definitions section 6.1's entries were verified against, including each hook's `root`/`scope:x`
  comment.
- `reference_official_defines/docs/triggers.log` — the vanilla trigger reference section 6.2's
  entries were verified against (supported scopes, comparison operators).
- `docs/knowledge/risk_cards/on_action.md` — the singleton-bridge-registry rule (never a second
  direct `effect` body on a shared vanilla on_action key) that governs how a `wired: false`
  section 6.1 entry must be implemented.
