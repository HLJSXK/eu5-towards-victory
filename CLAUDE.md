# Towards Victory - Claude Instructions

## Shared EU5 Base (required)

Read `.eu5-base/CLAUDE.md` and `.eu5-base/docs/knowledge/BRIEF.md` together with this project's instructions and `docs/knowledge/BRIEF.md`. Run `python scripts/bootstrap_base.py` after cloning if `.eu5-base/` is absent. Use `scripts/ai_context.py --changed` or `--files ...` before non-trivial edits; its knowledge loader combines shared and workspace-specific rules.


## Session Start

For any non-trivial task, read `docs/knowledge/BRIEF.md` first.

For gameplay design, balance, victory tasks, wonder rewards, trade, diplomacy,
or research mechanics, read `docs/knowledge/EU5_Gameplay_Reference.md` and the
relevant linked system/case notes before proposing changes. Distinguish local
vanilla evidence, older player experience, and 1.4 previews; do not infer gameplay
from EU4 or from unviewed video metadata.

For tool-integration or `towards_victory_editor_web` refactor work, read in this
order: `docs/knowledge/BRIEF.md` → the status snapshot
`docs/technical/Editor_Web_Refactor_Status.md` → the work plan
`docs/technical/Editor_Web_Work_Plan.md` → `towards_victory_editor_web/README.md`.
The work plan is the only source for picking work packages (WP), their
dependencies, shared-file merge order, interface contracts, and acceptance
criteria; the status snapshot records completed slices and validation. Use
`docs/technical/Towards_Victory_Editor_Web_Assessment.md` for the detailed
architecture baseline and rationale.

Before editing files, build a task-scoped AI context:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --changed
```

or, when target files are known:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --files <path> [<path> ...]
```

In Codex, Claude subagents, or other managed sandboxes, do not use `conda run -n eu5`.
Use the direct interpreter or the `activate.bat` form shown above.

## Project Identity

- Mod name: Towards Victory
- Mod ID: `eu5mp.towards_victory`
- Version: build date (`YYMMDD`)
- Status: In Development
- Language: English + Simplified Chinese
- Deployable roots:
  - `src/` main mod
  - `src_engineering_department/` standalone Engineering Department mod
  - `src_court_positions/` standalone Court Positions mod
  - `src_eureka/` standalone Eureka mod

## Core Rules

- This project is unreleased. Do not preserve old internal schemas, old-state repair paths,
  compatibility wrappers, or defensive fallback branches unless the user explicitly asks.
- EU5 uses Jomini. Do not assume EU4 syntax works.
- Read official defines or source before writing anything in the mandatory reference categories:
  `blockoverride`, `custom_tooltip`, `situation_card_common`, `location_rank:*`,
  any modifier name, any undeclared scripted trigger/effect, YAML localization encoding,
  GUI expressions, and any `variable_map`/`global_variable_map`/`local_variable_map` use.

## Critical Gotchas

- `location_rank` values: `rural_settlement`, `town`, `city`, `megalopolis`
- Localization YAML must use UTF-8 BOM and straight ASCII double quotes
- `custom_tooltip` dotted suffixes are valid; do not remove the tooltip to silence behavior
- `variable_map` RHS values are unsafe without a saved scope or local variable
- `select_trigger` is pre-evaluated; guard multi-step effects with `exists = scope:target...`
- `on_built` is not a reliable completion signal for upgradeable building mechanics
- Wonder buildings keep local effects in building modifiers and national effects in country effects
- TV IOs are non-unique, use `leader_change_trigger_type = none`, and keep monthly visible gains in `monthly_change`

## Script System

- Generated files are owned by their data files and generators. Check `data/generated_files.yaml` before editing any `src/` output.
- Use `scripts/validate.py --changed --fix --ai-report` before launching the game in managed sandboxes.
- If a knowledge/workflow file changes, regenerate `docs/knowledge/BRIEF.md` with:

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\gen_brief.py
```

## AI Workflow Maintenance

- Keep `docs/knowledge/context_routes.yaml` as the route source for `scripts/ai_context.py`.
- If `scripts/ai_context.py` routing changes, update this file, `docs/guides/AI_Tool_Workflow_Prompt.md`, and `docs/knowledge/PROJECT_OVERVIEW.md`.
- If a new risk card is added, register it in `context_routes.yaml`.
- If `anti_patterns.yaml`, `valid_enums.yaml`, or `PROJECT_OVERVIEW.md` changes, regenerate `BRIEF.md`.

## Resume / Handoff

- Trust handoff summaries unless local evidence contradicts them.
- After a handoff, start with the exact next validation or the named target file.
- Do not rerun broad bootstrap commands unless the handoff is inconsistent or stale.

When a tool-integration slice changes its completion state, update
`docs/technical/Editor_Web_Refactor_Status.md` in the same change and record
the validation environment. Keep the status snapshot current instead of adding
another chronological progress log to `BRIEF.md`.

## Current Routing

- `generic_actions` -> `docs/knowledge/risk_cards/generic_actions.md`
- `events` -> `docs/knowledge/risk_cards/events.md`
- `international_organizations` -> `docs/knowledge/risk_cards/international_organizations.md`
- `on_action` -> `docs/knowledge/risk_cards/on_action.md`
- `localization` -> `docs/knowledge/risk_cards/localization.md`
- Wonder service files (`towards_victory_editor_web/services/wonder/` or the CLI-relative `services/wonder/`) -> `docs/knowledge/risk_cards/wonders.md`
- wonder / engineering_department files -> routed wonder cards in `docs/knowledge/risk_cards/`
