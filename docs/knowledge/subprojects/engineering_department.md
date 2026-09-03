# Engineering Department Subproject

## Scope

`src_engineering_department/` is the standalone Engineering Department mod. It
owns Wonder Construction, generic and unique wonder definitions, construction
and ceremony lifecycle hooks, Wonder Control settings, wonder GUI, Europedia
content, and wonder-specific localization. `scripts_engineering_department/`
contains generators, audits, image tooling, and ritual design helpers.

## Data and Ownership

Canonical wonder data lives in `data/wonders.yaml`, `wonder_final_buildings.yaml`,
`wonder_generic_rituals.yaml`, `wonder_base_modifiers.yaml`, `wonder_site_rules.yaml`,
and `unique_wonders.yaml`. Generated outputs are listed in
`data/generated_files.yaml`; do not hand-edit those outputs.

## Boundaries

Wonder GUI often overrides full vanilla files and may have compatibility outputs
under `submods/`. Preserve generator ownership and check the routed wonder cards
before changing building lifecycle, ceremony, modifier, or GUI code.

## Validation

Run the relevant Engineering Department generator tests and
`scripts/validate.py --changed --fix --ai-report` after edits.
