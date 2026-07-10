# Unique Wonder Ritual Harness

Use this Harness when authoring bespoke rituals for `data/unique_wonders.yaml`.
The goal is to push AI authors toward high-innovation, wonder-specific ritual design,
not to compress every design into a few fixed mechanism shapes. Design fidelity comes
before implementation convenience.

## History: the retired source-compiler ceremony

An earlier version of this Harness spent 40+ commits building a "no-write" source-compiler
pipeline (`node_graph` DSL -> capability/archetype contracts -> a chain of evidence/preview/
readiness-ledger/bundle-gate layers) that was meant to eventually generate loadable EU5
source automatically. It never did: after all that scaffolding, 0/123 specs ever reached
real source through it, and its one real attempt to write source (an Alhambra vertical
slice) produced an unrelated generic 8-event skeleton with `always = yes` triggers — not
usable content. Roughly 22,700 lines of that ceremony (everything downstream of spec/
node_graph schema validation) have been deleted, along with the codegen script and test
suite built around it. **The design corpus was not deleted** — every spec's `design_ir`,
`mechanic_signature`, `cadence_signature`, and `compiler_gap_ledger` in
`data/unique_wonder_ritual_specs.yaml` remains intact and is still the design source of
truth. What changed is how a spec becomes real source: by hand-writing it, not by waiting
for a generator that was never finished.

## How specs become real source

1. Read the wonder's `design_ir`, `mechanic_signature`, and `cadence_signature` in
   `data/unique_wonder_ritual_specs.yaml` (see Spec Contract below for the schema).
2. Hand-write a bespoke content module under `scripts/unique_wonder_ritual_content/<key>.py`
   that implements that specific mechanic, following the pattern in
   `scripts/gen_unique_wonder_rituals.py` (the single generation pipeline for implemented
   wonders). `scripts/unique_wonder_ritual_content/_entity_ritual.py` is a legitimate shared
   helper for wonders whose `design_ir.tracked_entity_sets` genuinely fits a repeated-entity-
   row shape (per-entity status, checklist/incident-log UI) — reuse it when a wonder's design
   actually calls for that shape, but it must not become the default shape for every wonder
   regardless of design. Perform the 3-Step Resolution Rule for any EU5 syntax not already
   proven elsewhere in the mod before writing.
3. Regenerate via `scripts/gen_unique_wonder_rituals.py --write`.
4. Add English + Simplified Chinese localization for any new event/option text.
5. Run `scripts/validate.py --changed --fix` (0 errors/warnings expected).
6. **Run `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`** — this is the
   mandatory post-batch gate that replaces the old ceremony. It statically compares the
   generated `scripted_effects`/`scripted_triggers` source across every implemented wonder
   after normalizing away wonder-specific naming, so that two rituals built from the same
   underlying mechanic template (just with different entity names swapped in) show up as
   highly similar. Flag and address any pair scoring `combined_ratio >= 0.15` against
   another implemented wonder, or sharing an identical `random_list` weight tuple 3+ times —
   both thresholds are empirically justified against the known case (Alhambra / Dome of the
   Rock / Bank of Saint George / St. Peter's Basilica all reusing `_entity_ritual.py`) and
   documented in the script's own `--help`. Do not raise the threshold without re-checking
   the gap on current data.

## Full-Corpus Authoring Workflow

For any full-corpus pass across all unique wonders, start with
`data/unique_wonder_ritual_design_matrix.yaml` and the dedicated
[Global Authoring Workflow](Unique_Wonder_Ritual_Global_Authoring_Workflow.md).

- Maintain the design matrix before writing formal ritual specs.
- Run the global matrix audit:
  `conda run --no-capture-output -n eu5 python scripts/audit_unique_wonder_ritual_design_matrix.py`
- Resolve overused cadence types, repeated prompt atom/UI combinations, missing
  non-monthly validation points, missing uniqueness notes, and feasibility gaps.
- Freeze or review the mechanism allocation in the matrix before spec conversion.
- Only after matrix review should an authoring pass create formal entries in
  `data/unique_wonder_ritual_specs.yaml`, and those specs must still pass the
  existing Harness audit and spec-quality checks.
- Do not bypass the matrix to bulk-write all unique wonder specs directly.

## Batch Rule

- Work on 1-5 unique wonders per pass.
- Start from `data/unique_wonders.yaml`, `data/unique_wonder_ritual_designs.yaml`,
  `data/unique_wonder_ritual_prompts.yaml`, and `data/wonder_localization.yaml`.
- Update `data/unique_wonder_ritual_specs.yaml` before writing generated EU5 code:
  `conda run --no-capture-output -n eu5 python scripts/gen_unique_wonder_ritual_specs.py`
- Run the audit before implementation:
  `conda run --no-capture-output -n eu5 python scripts/audit_unique_wonder_rituals.py`
- Allocate event IDs with:
  `conda run --no-capture-output -n eu5 python scripts/allocate_unique_wonder_ritual_event_ids.py --nodes opening crisis resolution`
- Implement per "How specs become real source" above, then close the batch with
  `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`.
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
- `design_ir`: the high-fidelity mechanism layer that records phases, tracked entity sets, selectors, risk branches, player proofs, map/scope evidence, UI feedback, uniqueness constraints, and projection notes.
- `compiler_gap_ledger`: one row per high-complexity primitive, including the primitive semantics, required game interfaces, current evidence, verification status, search questions, blockers, and fallback.

`needs_codebase_search` and `semantic_only` are normal design states. They mean the design
is worth preserving and should drive later codebase exploration; they do not mean the design
should be flattened to the current template registry.

## Evidence Mapping Stage

Run an evidence mapping pass after `design_complete` and before implementation.
Use `compiler_gap_ledger.search_questions` as the entry point for codebase exploration,
then update each row with concrete evidence such as paths, helper functions, event IDs,
variable names, UI patterns, scopes, capabilities, or templates.

- `verified_existing` means codebase evidence exists, often through a manual implementation
  or bespoke generator.
- `interface_candidate` means a likely interface or pattern exists, but the mapping is not
  proven enough yet.
- `backend_ready` means the primitive is backed by current capability/template evidence
  (`capability:<key>` or `template:<key>`).
- Implementation should not begin while compiler gap rows remain `semantic_only` or
  `needs_codebase_search` — resolve them to at least `interface_candidate` first.

## Status Model

Use statuses to describe which layer is complete:

- `design_complete`: the high-fidelity `design_ir` is complete. `compiler_gap_ledger`
  may contain `semantic_only`, `needs_codebase_search`, or `interface_candidate` rows.
- `compiler_mapped`: the design also has a `node_graph` projection that passes semantic
  graph validation. This does not mean implementation has started.
- `evidence_verified`: the important design primitives have codebase evidence, but
  implementation may still be missing.
- `source_codegen_ready` / legacy `implementation_ready`: the spec has no unresolved
  compiler gaps and is ready for hand-written implementation per "How specs become real
  source" above.
- `implemented_parity`: a manual implementation exists that mirrors the spec. It may carry
  `design_ir` and `compiler_gap_ledger` to document the full manual design.

`harness_generated` is retired — no path in this project auto-generates loadable source
from a spec; every implemented wonder is hand-written.

## Spec Contract

`data/unique_wonder_ritual_specs.yaml` is the executable planning source, validated by
`scripts/gen_unique_wonder_ritual_specs.py` / `scripts/wonder_unique_ritual_harness.py`.
A high-fidelity formal ritual spec must include:

- `identity`: id, key, base key, location, runtime prefix, and status.
- `event_ids`: explicit unique numeric IDs, all below `10000`. Declared event ids are
  unique across the spec file, and `node.event_id` values are unique within the same spec.
- `design_ir`: phases/gameplay stages, player proofs, tracked entity sets, per-entity
  state, selectors, risk branches, player actions/decisions, map or scope evidence, UI
  feedback model, uniqueness constraints, and projection notes.
- `compiler_gap_ledger`: one row per complex primitive with `primitive`,
  `design_semantics`, `required_game_interfaces`, `codebase_evidence`,
  `verification_status`, `search_questions`, `blocked_by`, and
  `fallback_if_unavailable`.
- `node_graph`: for `compiler_mapped` and above, a custom graph with at least 3
  player-visible nodes, at least 3 event IDs, at least one failure or retry path, declared
  listeners, runtime variables, an `entry_node`, `terminal_nodes`, a `mechanic_signature`,
  a `cadence_signature`, optional graph-level `archetypes`, per-node capabilities, optional
  scope/listener contracts, and a historical mechanic.
- `ui_model`: one or more visible UI components from `checklist`, `route_map`, `actor_slots`,
  `material_stockpile`, `incident_log`, or `progress_track`.
- `rewards`: all three mandatory channels: permanent country modifier, local building reward,
  and one-time reward.
- `localization`: event rows, panel text keys, and world-news keys.
- `implementation_notes`: verified EU5 interfaces only; uncertain syntax must remain
  `needs_verification` and blocks `source_codegen_ready` / `implementation_ready`.

Allowed `compiler_gap_ledger.verification_status` values are:

- `semantic_only`
- `needs_codebase_search`
- `interface_candidate`
- `verified_existing`
- `backend_ready`

The first three are unresolved compiler gaps. They do not block `design_complete`; they do
block `source_codegen_ready` / `implementation_ready`. `verified_existing` also blocks those
statuses because it proves existing codebase feasibility, not that the primitive has been
implemented for this wonder. Only `backend_ready` satisfies compiler gap closure.

## Projection Contract

`design_ir` is the high-fidelity design layer. `node_graph` is only the current semantic
projection. When that projection is lossy, `design_ir.projection_notes` must explain what is
preserved, replaced, compressed, summarized, or intentionally omitted.

- Named tracked sets in `design_ir.tracked_entity_sets`, such as route, office, debt,
  manuscript, district, or frontier networks, must not be silently compressed into one
  anonymous counter.
- If `design_ir.ui_feedback_model` declares repeated rows or per-entity status, projection
  notes must say whether the current node graph preserves rows/status, substitutes a summary,
  or compresses them for the current layer.
- `compiler_mapped` may accept a lossy projection when the node graph passes semantic
  validation and the loss is documented.
- `source_codegen_ready` / `implementation_ready` must still hard fail while any compiler
  gap row is not `backend_ready`.

## Template Registry

`data/unique_wonder_ritual_codegen_templates.yaml` is the source of truth for spec-level
template contracts. Each template declares supported node/action/check kinds, required
input fields, output kinds, a verified interface, and notes.

## Capability Registry

`data/unique_wonder_ritual_capabilities.yaml` is the source of truth for mechanism
semantics. Each capability declares supported node kinds, required node fields,
required variable roles, supported listeners/UI components/output kinds, a verified
interface, and notes. Codegen-eligible nodes must declare `capabilities`. The validator
rejects unknown capabilities, capabilities that do not support the node kind, missing
capability-required fields, missing required variable roles, and unsupported listener
contracts.

## Archetype Registry

`data/unique_wonder_ritual_archetypes.yaml` is the source of truth for registry-backed
reference archetypes. These are not exclusive mechanism molds; they are reusable contract
tags that add positive requirements when a design wants that support. Each archetype
declares required capabilities, compatible node-kind examples, required variable roles,
required UI components, required listeners, min/max node counts, retry and hidden-executor
requirements, terminal-node capability requirements, a verification tier, and notes.

`compiler_mapped` and above specs may declare `node_graph.archetypes`. Known registry
archetypes add their required capability/variable-role/UI/listener/node-count checks.
Unknown ordinary archetype names are rejected as likely typos. `custom_*` archetype
labels are allowed only when `mechanic_signature.custom_archetype_statement` explains the
bespoke shape.

## State Machine DSL

`compiler_mapped` and above specs must use the strong node-graph DSL. `implemented_parity`
and `stub` entries may keep the older lightweight shape.

- `node_graph.mechanic_signature`: required for `compiler_mapped` and above; declares the
  wonder-specific hook, core interaction loop, player decision pattern, state feedback,
  failure/tension model, reward expression, and reuse-risk mitigation. If
  `node_graph.archetypes` contains a `custom_*` key, it must also include
  `custom_archetype_statement`.
- `node_graph.cadence_signature`: required for `compiler_mapped` and above; declares
  `cadence_type`, `cadence_rationale`, `player_agency_model`, `non_monthly_triggers_or_reason`,
  and `pacing_failure_mode`. Supported cadence types are `instant_but_branching`,
  `event_driven`, `player_action_sequence`, `construction_or_auxiliary_building`,
  `war_validated`, `succession_validated`, `route_certification`, `actor_assignment`,
  `resource_delivery`, `monthly_institutionalization`, and `hybrid`.
- `node_graph.entry_node` / `terminal_nodes` / `nodes` / `edges` / `actions` / `checks` /
  `variables`: see field requirements in Spec Contract above.
- `ui_model.bindings`: each binding declares component key, variable refs, node refs, and
  localization refs.
- `generation`: declares status, target files, verified templates, and dry-run notes.

The v1 registry: node kinds `event`, `choice_event`, `assignment_gate`, `resource_gate`,
`route_gate`, `listener_gate`, `incident_event`, `hidden_executor_handoff`, `retry_event`,
`monthly_progress_gate`, `final_reward_dispatch`; listener kinds `monthly`, `ruler_death`,
`pre_winning_war`, `ending_war`, `auxiliary_building_completion`; action kinds
`effect_script`, `generator_template`, `reward_dispatch_stub`; check kinds `trigger_script`,
`generator_template`.

Every edge target, retry target, next node, variable read/write, UI binding ref, node event ID,
and localization ref must resolve to a declared object. Every node must be reachable from
`entry_node`. A `monthly_progress_gate` must read and write at least one declared
progress/count variable, and `final_reward_dispatch` nodes must be terminal nodes.
`needs_verification` anywhere in a `source_codegen_ready` / `implementation_ready` spec
blocks validation.

Monthly pacing is allowed only when it is designed, not when it is convenient — see the
cadence rules above; unjustified monthly cadence is a reject condition.

## Reject Conditions

Reject source/codegen readiness if it has only start/completion events, no visible UI state, no distinctive
`mechanic_signature`, no declared `cadence_signature`, unknown cadence type, unjustified monthly
cadence, unknown ordinary archetypes, unexplained `custom_*` archetypes, no failure/retry
route, no historical mechanic, missing reward channels, thin event prose, runtime variables
outside the ritual prefix, undeclared UI variables, unsupported listeners, duplicate or occupied
event IDs, unsupported node/action/check kinds, unknown or unsupported registry templates or
capabilities, missing node capabilities, missing capability/archetype-required fields/roles, invalid
scope/listener contracts, graph references that point to undeclared nodes or variables,
unreachable nodes, terminal lifecycle violations, mismatched variable reader/writer declarations,
or localization/node rows that reference undeclared events.

Reject design completeness only when the high-fidelity design surface is missing or internally
invalid: absent `design_ir`, absent `compiler_gap_ledger`, missing required design fields,
invalid ledger `verification_status`, or `design_ir.compiler_primitives` without matching ledger
rows. Do not reject `design_complete` merely because a primitive is `semantic_only` or
`needs_codebase_search`.

Reject implementation if heavy finalization or cleanup is placed in an option tooltip path, or if
tooltips can pre-evaluate variables before they are written. Keep finalization in hidden executor
paths already verified by the project.

## Batch Completion

For each batch, produce:

- audit summary from `scripts/audit_unique_wonder_rituals.py`;
- generated or updated spec entries;
- hand-written `scripts/unique_wonder_ritual_content/<key>.py` implementation, if the specs
  passed and implementation is in scope, regenerated via `scripts/gen_unique_wonder_rituals.py --write`;
- similarity audit from `scripts/audit_unique_wonder_ritual_mechanic_similarity.py` confirming
  no new homogenization against existing implemented wonders;
- validation result from `scripts/validate.py --changed --fix --ai-report`;
- a human-readable summary of the gameplay loop, rewards, and remaining verification risks.
