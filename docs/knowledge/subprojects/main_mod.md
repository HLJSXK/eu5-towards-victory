# Main Mod Subproject

## Scope

`src/` is the main Towards Victory mod. It contains the six victory paths,
shared research and Academy systems, international organizations, events,
on-actions, localization, and shared GUI/script infrastructure. `scripts/` and
`data/` are the main generators and canonical data sources; generated outputs
are registered in `data/generated_files.yaml`.

## Boundaries

- Edit canonical YAML/data or the owning generator when an output is generated.
- Treat `src_engineering_department/`, `src_court_positions/`, and `src_eureka/`
  as separate deployable roots even when they interact with the main mod.
- Shared singleton/full-copy files can exist in every root; verify ownership in
  the generated registry before editing.

## Key Areas

- `data/victory_paths.yaml` and `scripts/gen_victory.py`: victory-path source and outputs.
- `src/in_game/events/`: research, Academy, IO, and victory events.
- `src/in_game/common/international_organizations/`: TV IO definitions.
- `src/in_game/gui/` and `src/main_menu/`: shared UI and localization.

## Validation

Run `scripts/test_ai_context.py`, then `scripts/validate.py --changed --fix --ai-report`
for code changes. Regenerate `docs/knowledge/BRIEF.md` after knowledge changes.
