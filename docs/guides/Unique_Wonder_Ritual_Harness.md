# Unique Wonder Ritual Harness

Use this Harness when authoring bespoke rituals for `data/unique_wonders.yaml`.
The goal is to prevent unique rituals from collapsing into one start popup and one
completion popup. Each batch should produce a playable spec first, then game code.

## Batch Rule

- Work on 1-5 unique wonders per pass.
- Start from `data/unique_wonders.yaml`, `data/unique_wonder_ritual_designs.yaml`,
  `data/unique_wonder_ritual_prompts.yaml`, and `data/wonder_localization.yaml`.
- Update `data/unique_wonder_ritual_specs.yaml` before writing generated EU5 code.
- Run the Harness tests and audit before implementation:
  `conda run --no-capture-output -n eu5 python scripts/test_unique_wonder_ritual_harness.py`
  `conda run --no-capture-output -n eu5 python scripts/audit_unique_wonder_rituals.py`
- Allocate event IDs with:
  `conda run --no-capture-output -n eu5 python scripts/allocate_unique_wonder_ritual_event_ids.py --nodes opening crisis resolution`

## Required AI Output

Every authoring pass must include these sections before implementation:

- `gameplay_loop_summary`: what the player repeatedly checks or decides.
- `node_table`: each node key, event ID, trigger/check, choice, retry/failure route, and historical anchor.
- `state_variable_table`: every runtime variable, owner scope, prefix, meaning, writer, reader, and cleanup point.
- `event_text_inventory`: title, description, options, panel status text, and world-news text.
- `reward_table`: permanent country modifier, local reward building, one-time reward, and any temporary burden or stage reward.
- `risk_verification_checklist`: EU5 interfaces that are verified, and any `needs_verification` items that block code generation.

## Spec Contract

`data/unique_wonder_ritual_specs.yaml` is the executable planning source.
An implementation-ready ritual must include:

- `identity`: id, key, base key, location, runtime prefix, and status.
- `event_ids`: explicit unique numeric IDs, all below `10000`.
- `node_graph`: a custom graph with at least 3 player-visible nodes, at least 3 event IDs,
  at least one failure or retry path, declared listeners, runtime variables, and a historical mechanic.
- `ui_model`: one or more visible UI components from `checklist`, `route_map`, `actor_slots`,
  `material_stockpile`, `incident_log`, or `progress_track`.
- `rewards`: all three mandatory channels: permanent country modifier, local building reward,
  and one-time reward.
- `localization`: event rows, panel text keys, and world-news keys.
- `implementation_notes`: verified EU5 interfaces only; uncertain syntax must remain
  `needs_verification` and blocks `implementation_ready` or `harness_generated`.

## Reject Conditions

Reject the spec if it has only start/completion events, no visible UI state, no failure/retry
route, no historical mechanic, missing reward channels, thin event prose, runtime variables
outside the ritual prefix, undeclared UI variables, unsupported listeners, duplicate or occupied
event IDs, or localization/node rows that reference undeclared events.

Reject implementation if heavy finalization or cleanup is placed in an option tooltip path, or if
tooltips can pre-evaluate variables before they are written. Keep finalization in hidden executor
paths already verified by the project.

## Batch Completion

For each batch, produce:

- audit summary from `scripts/audit_unique_wonder_rituals.py`;
- generated or updated spec entries;
- generated files, if the specs passed and implementation is in scope;
- validation result from `scripts/validate.py --changed --fix --ai-report`;
- a human-readable summary of the gameplay loop, rewards, and remaining verification risks.
