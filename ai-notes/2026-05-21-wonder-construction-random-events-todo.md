# Wonder Construction Random Events TODO

Source request date: 2026-05-21.

## Goal

Add monthly random events for the Engineering Department wonder construction stage.

## Requirements

- Random events start once a wonder construction site is selected (`tv_wonder_stage = 3` with `tv_wonder_site`) and stop once construction is declared complete, the wonder is finalized, or the project is abandoned.
- Event occurrence ignores current construction speed and active labor/material throughput.
- All events are selected through one monthly random-list roll with a 10% total monthly event chance.
- All titles use the standard `奇观建设：xxx` / `Wonder Construction: xxx` format.
- Event option tooltips must be rendered by actual effects. IO variable changes must use scripted effects with `custom_description` and `effect_localization`.
- Generate the 244 event bodies and localization by script.

## Token Rules

Engineering token values:

- 10 Domestic Support, weight 1.
- 5 Scale Competence, weight 1.
- 5 Organization Competence, weight 1.
- 5 Logistics Competence, weight 1.
- 5000 Materials Stockpile, weight 3.
- 5000 Construction Progress, weight 3.

Non-engineering token values:

- Gold, scale 1, weight 2.
- 5 Legitimacy, weight 1.
- 7 Stability, weight 1.
- 10 Prestige, weight 1.
- 10% Nobles satisfaction, weight 1.
- 10% Clergy satisfaction, weight 1.
- 10% Burghers satisfaction, weight 1.
- 20% Peasants satisfaction, weight 1.
- Construction site 0.25 development, weight 1.
- Construction site 20% prosperity, weight 1.
- Capital 0.25 development, weight 1.
- Capital 20% prosperity, weight 1.
- Construction site 10% laborer population death, weight 1.

Event categories:

- Random token exchange events: 200 events.
- Great Engineer tier events: 44 events, gated by effective MIL thresholds 20 / 50 / 80.

## Implementation Checklist

- [x] Read `CLAUDE.md`, `docs/knowledge/BRIEF.md`, Events risk card, and On Action risk card.
- [x] Add data and generators for events, random-list roll effect, and localization.
- [x] Add reusable scripted effects for construction progress / stockpile / labor casualty tooltips.
- [x] Add triggers for active construction event stage and Great Engineer effective MIL tiers.
- [x] Register the monthly pulse via `data/pulse_registry.yaml` and regenerate on_action files.
- [x] Register generated files in `data/generated_files.yaml`.
- [x] Generate event and localization outputs.
- [x] Run validation with `conda run --no-capture-output -n eu5 python scripts/validate.py --changed --fix --ai-report`.
- [x] Update `PROJECT_OVERVIEW.md` and regenerate `BRIEF.md` if the feature is complete.
