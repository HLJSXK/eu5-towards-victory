# Court Positions Subproject

## Scope

`src_court_positions/` is a standalone CMF-backed situation mod for six court
offices: Physician, Tutor, Steward, Architect, Cultural Emissary, and Chronicler.
Office effects scale from normalized character ability values and include direct
character interactions, monthly salaries, initialization hooks, and a situation
GUI. `scripts_court_positions/` owns the generators.

## Data and Ownership

`data/court_positions.yaml` is the canonical source. It generates static
modifiers, scripted effects, generic actions and AI lists, character
interactions, on-actions, situation GUI, and English/Simplified Chinese
localization. Confirm the registry before editing a generated output.

## Boundaries

This root is independently deployable. Keep CMF situation state and office
effects in this subproject; shared main-mod systems should be changed in `src/`
only when the task explicitly crosses that boundary.

## Validation

Run the affected generator, `scripts/test_ai_context.py`, and
`scripts/validate.py --changed --fix --ai-report` after edits.
