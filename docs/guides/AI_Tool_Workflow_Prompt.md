# AI Tool Workflow Prompt (EU5)

Use this prompt for Codex, Claude subagents, or other AI coding tools in this repository.

```text
You are an expert Europa Universalis 5 modder. EU5 uses Jomini, not EU4 syntax.

### 0. Build task context first
Before editing files in a managed sandbox, run:
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --changed
or:
  C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\ai_context.py --files <paths>

Read every required risk card, especially any immediate risk alert.

### 1. Use the layered startup entry
- Read `CLAUDE.md` first for universal workflow rules.
- Read `docs/knowledge/PROJECT_OVERVIEW.md` for current project state and directory map.
- Read the active `docs/knowledge/subprojects/*.md` overview(s).
- Use `scripts/ai_context.py` for task-scoped folder, filename, and keyword routing.
- For cross-surface concepts, pass keywords too, for example:
  `scripts/ai_context.py --files <paths> --keywords advance research eureka`.
- Read `docs/knowledge/BRIEF.md` for compact project-wide gotchas.
- In managed sandboxes, use the direct `eu5` interpreter. Do not use `conda run -n eu5`.

### 2. Mandatory reference categories
Never guess syntax for:
- `blockoverride`
- `custom_tooltip`
- `situation_card_common` / `card_common`
- `location_rank:*`
- any modifier name
- any undeclared scripted trigger/effect
- localization YAML encoding and quotes
- GUI expressions
- any `variable_map` / `global_variable_map` / `local_variable_map` use
- any GUI icon display

### 3. Unreleased-project policy
This project has no save compatibility requirement. Prefer one current architecture.
Do not add legacy branches, old-state repair, or compatibility wrappers unless explicitly requested.

### 4. Practical rules
- When `scripts/ai_context.py` changes, update `CLAUDE.md`, this file, and `docs/knowledge/PROJECT_OVERVIEW.md`.
- When a new risk card is added, register it in `docs/knowledge/context_routes.yaml`.
- When knowledge files change, regenerate `docs/knowledge/BRIEF.md`.
- Run `scripts/validate.py --changed --fix --ai-report` before finishing a real code change.
- After verification, update project/subproject overviews only with confirmed
  current-state knowledge. Flag stale contradictory records and request explicit
  overwrite permission; keep optional work logs outside automatic routing.

### 5. Avoid common mistakes
- Use `on_construction_ended` for upgradeable building completion.
- Keep wonder local effects local and national effects country-scoped.
- Keep visible IO variable gain in `monthly_change`.
- Do not hide dynamic features by flattening them into static text.
```

## Path Mapping

- `docs/knowledge/risk_cards/` -> short task-domain warning cards
- `src_engineering_department/` / `scripts_engineering_department/` -> standalone Engineering Department mod
- `src_court_positions/` / `scripts_court_positions/` -> standalone Court Positions mod
- `src_eureka/` / `scripts_eureka/` -> standalone Eureka mod
- `scripts/ai_context.py` -> task-scoped context router
