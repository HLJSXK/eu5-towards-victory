# Unique Wonder Ritual Harness

Use this Harness when authoring bespoke rituals for `data/unique_wonders.yaml`.
The goal is to push AI authors toward high-innovation, wonder-specific ritual design,
not to compress every design into a few fixed mechanism shapes. Each batch should
produce a playable spec first, then game code.

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
  Template support comes from `data/unique_wonder_ritual_codegen_templates.yaml`;
  specs may not invent template keys outside that registry.
  Mechanism capability support comes from `data/unique_wonder_ritual_capabilities.yaml`;
  specs may not invent capability keys outside that registry.
  Mechanic archetype support comes from `data/unique_wonder_ritual_archetypes.yaml`;
  registry archetypes are optional, non-exclusive reference tags. Strong DSL specs may
  also use `custom_*` archetype labels when `node_graph.mechanic_signature` explains
  the new shape.

## Required AI Output

Every authoring pass must include these sections before implementation:

- `mechanic_signature`: what makes this ritual mechanically specific to this wonder,
  how the loop differs from stock event chains, and why any `custom_*` archetype exists.
- `cadence_signature`: the ritual's pacing/trigger model, why that cadence fits the
  wonder, how the player can affect it, what non-monthly triggers or decisions exist,
  and how the pacing can fail.
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
  at least one failure or retry path, declared listeners, runtime variables, an `entry_node`,
  `terminal_nodes`, a `mechanic_signature`, a `cadence_signature`, optional graph-level
  `archetypes`, per-node capabilities, optional scope/listener contracts, and a historical
  mechanic.
- `ui_model`: one or more visible UI components from `checklist`, `route_map`, `actor_slots`,
  `material_stockpile`, `incident_log`, or `progress_track`.
- `rewards`: all three mandatory channels: permanent country modifier, local building reward,
  and one-time reward.
- `localization`: event rows, panel text keys, and world-news keys.
- `implementation_notes`: verified EU5 interfaces only; uncertain syntax must remain
  `needs_verification` and blocks `implementation_ready` or `harness_generated`.

## Template Registry

`data/unique_wonder_ritual_codegen_templates.yaml` is the only source of truth for Harness
codegen template contracts. Each template declares supported node/action/check kinds, required
input fields, output kinds, a verified interface, `may_write_src: false`, and notes. The v1
registry is intermediate-only: valid output kinds are `markdown_fragment`, `event_skeleton`,
`effect_stub`, `trigger_stub`, `gui_summary`, and `loc_draft`.

The validator and codegen both reject unknown templates, templates marked as allowed to write
`src/`, blocked templates, action/check kinds not supported by the selected template, and node
kinds not covered by `generation.verified_templates`.

## Capability Registry

`data/unique_wonder_ritual_capabilities.yaml` is the only source of truth for Harness
mechanism semantics. Each capability declares supported node kinds, required node fields,
required variable roles, supported listeners/UI components/output kinds, a verified interface,
`may_write_src: false`, and notes. The v1 capabilities are `event_chain`, `retry_branch`,
`monthly_progress`, `actor_assignment`, `resource_gate`, `route_gate`, `listener_gate`, and
`final_reward_handoff`.

Codegen-eligible nodes must declare `capabilities`. The validator rejects unknown
capabilities, capabilities that do not support the node kind, missing capability-required
fields, missing required variable roles, unsupported listener contracts, and any capability
marked as allowed to write `src/`.

## Archetype Registry

`data/unique_wonder_ritual_archetypes.yaml` is the source of truth for registry-backed
reference archetypes. These are not exclusive mechanism molds; they are reusable contract
tags that add positive requirements when a design wants that support. Each archetype
declares required capabilities, compatible node-kind examples, required variable roles,
required UI components, required listeners, min/max node counts, retry and hidden-executor
requirements, terminal-node capability requirements, a verification tier, `may_write_src: false`,
and notes. The v1 registry archetypes are `expedition_route_chain`,
`patronage_actor_assignment`, `resource_accumulation_ritual`, `monthly_pressure_countdown`,
`incident_retry_gauntlet`, `listener_resolution_ritual`, and `hidden_executor_finalization`.

`implementation_ready` and `harness_generated` specs may declare `node_graph.archetypes`.
Known registry archetypes add their required capability/variable-role/UI/listener/node-count
checks. Unknown ordinary archetype names are rejected as likely typos. `custom_*` archetype
labels are allowed only when `mechanic_signature.custom_archetype_statement` explains the
bespoke shape. The validator rejects archetypes marked as allowed to write `src/`, missing
registry-archetype-required capabilities/variable roles/UI/listeners, node counts outside
registry bounds, missing retry paths, missing hidden-executor handoffs, and terminal nodes
that lack the registry-archetype-required capability. It no longer rejects extra node kinds
solely because they are outside the union of declared archetype examples.

## State Machine DSL

`implementation_ready` and `harness_generated` specs must use the strong node-graph DSL.
`implemented_parity` and `stub` entries may keep the older lightweight shape.

- `node_graph.mechanic_signature`: required for `implementation_ready` and
  `harness_generated`; declares the wonder-specific hook, core interaction loop, player
  decision pattern, state feedback, failure/tension model, reward expression, and reuse-risk
  mitigation. If `node_graph.archetypes` contains a `custom_*` key, it must also include
  `custom_archetype_statement`.
- `node_graph.cadence_signature`: required for `implementation_ready` and
  `harness_generated`; declares `cadence_type`, `cadence_rationale`,
  `player_agency_model`, `non_monthly_triggers_or_reason`, and `pacing_failure_mode`.
  Supported cadence types are `instant_but_branching`, `event_driven`,
  `player_action_sequence`, `construction_or_auxiliary_building`, `war_validated`,
  `succession_validated`, `route_certification`, `actor_assignment`, `resource_delivery`,
  `monthly_institutionalization`, and `hybrid`.
- `node_graph.archetypes`: optional registry-backed reference tags or `custom_*` labels.
  Known keys add positive contract checks; unknown non-custom keys are rejected even on
  non-codegen specs that choose to declare this field.
- `node_graph.entry_node`: the first runtime node; it must resolve to a declared node.
- `node_graph.terminal_nodes`: one or more declared terminal nodes.
- `node_graph.graph_shape`: optional authoring label for the graph shape.
- `node_graph.completion_policy`: optional lifecycle policy; terminal outgoing edges are
  rejected unless `allow_terminal_outgoing: true` is explicitly set.
- `node_graph.nodes`: each node declares `key`, `kind`, `event_id`, visibility,
  capabilities, historical anchor, enter/completion checks, retry target, next nodes,
  reads/writes, UI state, and localization refs. Optional `scope_contract` declares
  root/current/target scopes plus tooltip and unsafe pre-evaluation policy; optional
  `listener_contract` declares listener, cadence, reads/writes, completion check, and
  failure route.
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

The v1 registry is deliberately small:

- node kinds: `event`, `choice_event`, `assignment_gate`, `resource_gate`, `route_gate`,
  `listener_gate`, `incident_event`, `hidden_executor_handoff`, `retry_event`,
  `monthly_progress_gate`, `final_reward_dispatch`
- action kinds: `effect_script`, `generator_template`, `reward_dispatch_stub`
- check kinds: `trigger_script`, `generator_template`
- templates: `sequential_event_chain`, `branch_retry_event`, `monthly_progress_gate`,
  `simple_progress_track_ui_binding`, `final_reward_dispatch_stub`,
  `semantic_contract_fragment`

Every edge target, retry target, next node, variable read/write, UI binding ref, node event ID,
and localization ref must resolve to a declared object. Every node must be reachable from
`entry_node`. Non-terminal nodes need a next node or outgoing edge; terminal nodes may not have
ordinary outgoing edges by default. Retry targets may not point to terminal nodes. A
`monthly_progress_gate` must read and write at least one declared progress/count variable, and
`final_reward_dispatch` nodes must be terminal nodes. Variable `writer_nodes` / `reader_nodes`
must exactly match the node `writes` / `reads` declarations. Variable `roles` is the canonical
way to satisfy capability-required roles. `listener_gate` nodes must have `listener_contract`.
Allowed scope contract values are `country`, `location`, `character`,
`international_organization`, `gui_fragment`, and `none`. `tooltip_safe: false` nodes/actions
may not declare `player_facing_tooltip` output, and `unsafe_pre_eval: true` requires a blocked
reason or hidden executor handoff. `needs_verification` anywhere in an `implementation_ready`
or `harness_generated` spec blocks validation.

Monthly pacing is allowed only when it is designed, not when it is convenient. If
`node_graph.listeners` includes `monthly`, a node uses `monthly_progress_gate`, a node declares
`monthly_progress`, a listener contract has monthly cadence, or a generator template uses
`monthly_progress_gate`, the cadence type must be `monthly_institutionalization` or `hybrid`.
The rationale must explicitly explain the monthly role. `monthly_institutionalization` still
needs at least one non-monthly decision, risk, listener, event branch, trigger, or player
action; `hybrid` must explain monthly as a local/supporting part of a larger non-monthly loop.

## Reject Conditions

Reject the spec if it has only start/completion events, no visible UI state, no distinctive
`mechanic_signature`, no declared `cadence_signature`, unknown cadence type, unjustified monthly
cadence, unknown ordinary archetypes, unexplained `custom_*` archetypes, no failure/retry
route, no historical mechanic, missing reward channels, thin event prose, runtime variables
outside the ritual prefix, undeclared UI variables, unsupported listeners, duplicate or occupied
event IDs, unsupported node/action/check kinds, unknown or unsupported registry templates or
capabilities, missing node capabilities, missing capability/archetype-required fields/roles, invalid
scope/listener contracts, graph references that point to undeclared nodes or variables,
unreachable nodes, terminal lifecycle violations, mismatched variable reader/writer declarations,
or localization/node rows that reference undeclared events.

Reject implementation if heavy finalization or cleanup is placed in an option tooltip path, or if
tooltips can pre-evaluate variables before they are written. Keep finalization in hidden executor
paths already verified by the project.

Reject code generation if any used template is not both present in the registry and listed in
`generation.verified_templates`, if the template does not support the current node/action/check
kind, or if `generation.blocked_templates` is non-empty. The v1 generator emits Markdown
skeletons, mechanic/cadence signature summaries, capability summaries, scope/listener contract
summaries, hidden-executor/tooltip safety notes, and draft inventories only; promotion into
loadable EU5 script requires a later verified generator.

## Batch Completion

For each batch, produce:

- audit summary from `scripts/audit_unique_wonder_rituals.py`;
- generated or updated spec entries;
- generated intermediate fragments, if the specs passed and implementation is in scope;
- validation result from `scripts/validate.py --changed --fix --ai-report`;
- a human-readable summary of the gameplay loop, rewards, and remaining verification risks.
