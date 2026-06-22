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
- Generate conservative intermediate fragments with:
  `conda run --no-capture-output -n eu5 python scripts/gen_unique_wonder_ritual_code.py`
  Add `--write` only after the spec passes validation. The generator writes Harness-owned
  fragments under `data/generated_fragments/unique_wonder_rituals/`; it does not write `src/`.

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

## State Machine DSL

`implementation_ready` and `harness_generated` specs must use the strong node-graph DSL.
`implemented_parity` and `stub` entries may keep the older lightweight shape.

- `node_graph.nodes`: each node declares `key`, `kind`, `event_id`, visibility,
  historical anchor, enter/completion checks, retry target, next nodes, reads/writes,
  UI state, and localization refs.
- `node_graph.edges`: each edge declares `from`, `to`, `condition`, `effect`, and `label_key`.
- `node_graph.actions`: each action declares `key`, `kind`, `scope`, `verified_interface`,
  and either an `effect_script` or a `generator_template`.
- `node_graph.checks`: each check declares `key`, `kind`, `tooltip_key`, and either a
  `trigger_script` or a `generator_template`.
- `node_graph.variables`: each variable declares name, scope, type, initial value, writer
  nodes, reader nodes, and cleanup.
- `ui_model.bindings`: each binding declares component key, variable refs, node refs, and
  localization refs.
- `generation`: declares status, target files, verified templates, blocked templates, and
  dry-run notes. `harness_generated` entries must have target files and verified templates.

The v1 codegen allowlist is deliberately small:

- node kinds: `event`, `retry_event`, `monthly_progress_gate`, `final_reward_dispatch`
- action kinds: `effect_script`, `generator_template`, `reward_dispatch_stub`
- check kinds: `trigger_script`, `generator_template`
- templates: `sequential_event_chain`, `branch_retry_event`, `monthly_progress_gate`,
  `simple_progress_track_ui_binding`, `final_reward_dispatch_stub`

Every edge target, retry target, next node, variable read/write, UI binding ref, node event ID,
and localization ref must resolve to a declared object. `needs_verification` anywhere in an
`implementation_ready` or `harness_generated` spec blocks validation.

## Reject Conditions

Reject the spec if it has only start/completion events, no visible UI state, no failure/retry
route, no historical mechanic, missing reward channels, thin event prose, runtime variables
outside the ritual prefix, undeclared UI variables, unsupported listeners, duplicate or occupied
event IDs, unsupported node/action/check kinds, unsupported templates, graph references that
point to undeclared nodes or variables, or localization/node rows that reference undeclared events.

Reject implementation if heavy finalization or cleanup is placed in an option tooltip path, or if
tooltips can pre-evaluate variables before they are written. Keep finalization in hidden executor
paths already verified by the project.

Reject code generation if any template is not both supported by the Harness allowlist and listed
in `generation.verified_templates`, or if `generation.blocked_templates` is non-empty. The v1
generator emits Markdown skeletons and draft inventories only; promotion into loadable EU5 script
requires a later verified generator.

## Batch Completion

For each batch, produce:

- audit summary from `scripts/audit_unique_wonder_rituals.py`;
- generated or updated spec entries;
- generated intermediate fragments, if the specs passed and implementation is in scope;
- validation result from `scripts/validate.py --changed --fix --ai-report`;
- a human-readable summary of the gameplay loop, rewards, and remaining verification risks.
