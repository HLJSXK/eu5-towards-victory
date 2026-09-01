# Towards Victory - Project Overview

## Mod Identity

- **Mod Name:** Towards Victory
- **Mod ID:** `eu5mp.towards_victory`
- **Version:** Build date (`YYMMDD`)
- **Target:** EU5 `1.*.*`
- **Status:** In Development
- **Language:** English + Simplified Chinese

## Development Policy

Towards Victory is unreleased. There are no save compatibility, published-version
compatibility, or public API compatibility requirements unless the user explicitly
names an external consumer.

Active code and data should represent one current architecture. When a refactor
improves clarity, performance, generator ownership, or data flow, update all
producers and consumers to the new shape and delete stale branches rather than
keeping migrations, aliases, duplicate paths, wrapper entry points, or defensive
fallbacks for old internal state.

## Deployable Roots

- `src/`: main Towards Victory mod.
- `src_engineering_department/`: standalone Engineering Department / Wonder Construction mod.
- `src_court_positions/`: standalone Court Positions mod.
- `src_eureka/`: standalone Eureka mod scaffold.

All four roots are first-class for validation, source indexing, version stamping,
and deployment. Shared singleton databases such as `character_title.txt` and
`messagetypes.txt` are generated as full vanilla copies per root.

## Core Systems

- **Victory Paths:** six implemented paths: Conquest, Prosperity, Trade, Diplomatic,
  Cultural, and Scientific. Most route data is generated from `data/victory_paths.yaml`
  and related data sources.
- **International Organizations:** TV IOs are non-unique, use appointed character
  variables rather than vanilla elections, and keep visible monthly variable gain in
  `monthly_change`.
- **Engineering Department:** owns Wonder Construction, all generic and unique wonder
  data, CMF lifecycle hooks, Wonder Control settings, wonder GUI, Europedia content,
  and wonder-specific localization.
- **Court Positions:** standalone CMF-backed situation mod with six character offices,
  ability-scaled effects, direct character interactions, and monthly salaries.
- **Eureka:** standalone mod scaffold (framework only; mechanics not yet implemented).
- **Editor/Web Tools:** root-level tools support victory tree editing, wonder localization,
  cost/reward data, generated wonder assets, and static unique-wonder atlas data.
- **Compat Submods:** GUI full-file overrides are handled through generated compat submods
  where needed rather than by relying on GUI merge behavior.

## Directory Map

- `data/`: canonical YAML/JSON data sources and generated-file registry.
- `docs/knowledge/`: AI-maintained compact knowledge, routing, anti-patterns, enums,
  overview, and risk cards.
- `docs/technical/`: broad EU5 technical notes.
- `reference_official_defines/`: official define/type references.
- `reference_game_files/`: mirrored vanilla EU5 source.
- `reference_mods/`: selected community mod references.
- `scripts/`: main infrastructure and main-mod generators.
- `scripts_engineering_department/`: Engineering Department generators and audits.
- `scripts_court_positions/`: Court Positions generators.
- `tests/fixtures/anti_patterns/`: lint fixture cases.

## AI Workflow Knowledge

`CLAUDE.md` is the single startup workflow entry. `docs/knowledge/BRIEF.md` is the
compact generated broad read. `scripts/ai_context.py` builds task-scoped context
from explicit or changed files, generated-file metadata, and
`docs/knowledge/context_routes.yaml`.

Default `ai_context.py` output is concise: files, generated ownership, domains,
immediate risk alerts, required reads, relevant anti-pattern summaries, and validation.
Use `--full` only when full routed card text is needed. Use `--json` for regression
tests or future tool integration.

Current routing sources:

- path routes for `generic_actions`, GUI, events, IOs, on_actions, localization,
  and wonder file types;
- filename routes for interspersed domains such as wonders, philosophy debate,
  trade league, and Europedia;
- content routes for `variable_map` APIs, excluding workflow prose;
- object alerts for high-risk objects such as `on_built`.

When routing behavior changes, update `context_routes.yaml`, `scripts/ai_context.py`,
`CLAUDE.md`, `docs/guides/AI_Tool_Workflow_Prompt.md`, and this overview, then run
`scripts/test_ai_context.py` and regenerate `BRIEF.md`.

## Script Reference

| Script | Purpose |
|---|---|
| `scripts/ai_context.py` | Task-scoped AI context router; supports `--changed`, `--files`, `--full`, and `--json`. |
| `scripts/gen_brief.py` | Regenerates compact `docs/knowledge/BRIEF.md` after AI knowledge changes. |
| `scripts/gen_index.py` | Rebuilds symbol indexes used by validation and generated brief output. |
| `scripts/validate.py` | Main validation/lint entry, including generated-file, localization, IO, on_action, GUI, and knowledge checks. |
| `scripts/test_lint_rules.py` | Fixture regression tests for `detectability: lint` anti-patterns. |
| `scripts/test_ai_context.py` | Regression tests for context routing and immediate-alert behavior. |
| `scripts/gen_victory.py` | Generates core victory-path outputs. |
| `scripts/gen_messagetypes.py` | Generates per-root full-copy message type files. |
| `scripts_engineering_department/gen_unique_wonder_rituals.py` | Generates currently implemented bespoke unique-wonder ritual source. |
| `scripts_engineering_department/test_wonder_mechanics_rules.py` | Engineering Department wonder generator regression checks. |

## Maintenance Rule

This overview describes the current project shape, not a session changelog. If a
future task needs detailed incident history, consult the specific anti-pattern entry or
routed risk card rather than expanding this file back into a chronological log.
