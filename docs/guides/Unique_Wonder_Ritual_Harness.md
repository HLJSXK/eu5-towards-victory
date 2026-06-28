# Unique Wonder Ritual Harness

Use this Harness when authoring bespoke rituals for `data/unique_wonders.yaml`.
The goal is to push AI authors toward high-innovation, wonder-specific ritual design,
not to compress every design into a few fixed mechanism shapes. Design fidelity comes
before current codegen convenience. Each batch should preserve the full playable design
first, then map only the verified projection into the current Harness graph or generator.

## Current Phase Freeze

The Harness design-carrying phase is complete: all 123 unique-wonder ritual designs are carried
by the Harness intermediate layer. Current counts are `compiler_mapped=117`,
`source_codegen_ready=4`, `implemented_parity=2`, `stub=0`, `harness_generated=0`, and
registry/codegen `may_write_src=0`.

`compiler_mapped` is not source-ready. It only means the design has a current semantic
`node_graph` projection. The source generation stage has not started, `source_codegen_ready`
remains limited to the four intermediate-fragment pilots, and v1 codegen may only emit
intermediate Markdown fragments under `data/generated_fragments/unique_wonder_rituals/`.
Every template, capability, and archetype contract must keep `may_write_src: false`.

The 17 design-matrix future gaps are the next source compiler / EU5 verification backlog.
Keep them in the matrix and explain them; do not delete or flatten them just to clear the
matrix warning.

## Next Phase Boundary

The next phase is source-compiler planning and EU5 interface verification, not another
full-corpus design or semantic-projection pass. Treat the existing 123 specs as the design
corpus to preserve. Work should start from `compiler_gap_ledger.search_questions`, the
17 matrix future-gap rows, and the four intermediate-fragment pilots, then prove concrete
source interfaces before any readiness promotion.

Do not promote additional specs to `source_codegen_ready`, legacy `implementation_ready`,
or `harness_generated` merely because their `node_graph` validates. Do not set any
template, capability, archetype, or generator path to `may_write_src: true` until a later
source-writer contract has exact EU5 syntax evidence, generator ownership, source-target
boundaries, validation coverage, and rollback-free lifecycle semantics.

For each next-phase audit, report whether the current work preserves the high-fidelity
`design_ir` or has flattened it. Any proposed source compiler primitive must name the
required EU5 files/interfaces, evidence paths, owned generator/data contracts, validation
gate, and the specs it would unlock.

## Source Compiler Vertical Slice: Repeated Entity Rows

The first source-compiler contract slice is the repeated entity row family:
checklist rows, incident-log rows, and closely related material/route/actor row summaries.
It is shared by all four intermediate-fragment pilots:

- `unique_dome_of_the_rock`: sanctuary access group incident rows and custody-duty checklist rows.
- `unique_alhambra`: treaty-clause checklist rows and palace-risk incident rows.
- `unique_st_peters_basilica`: sacred-official actor state plus apostolic service-duty incident rows.
- `unique_bank_of_saint_george`: charter-option checklist rows and public-credit pledge/default-risk incident rows.

For this slice, `design_ir.tracked_entity_sets` is the canonical source for row keys,
state values, per-row variables, selectors, UI bindings, and cleanup expectations. The
current `node_graph` may summarize those rows through aggregate variables, but that
projection is intentionally lossy and must not replace the high-fidelity row design.

Current evidence supports only contract preparation. Pharos proves that bespoke generated
source can write per-entity variables and render repeated GUI rows, and
`repeated_entity_row_checklist_incident_log_backend` proves the Harness can preserve these
semantics as intermediate summaries. Neither one proves that the Harness can write
loadable EU5 GUI, event, effect, trigger, localization, or cleanup source for arbitrary
ritual row sets.

The Harness repeated-row preflight is a source-compiler pre-check, not a source writer.
It inventories `design_ir.tracked_entity_sets`, current lossy `node_graph` projection
variables, UI bindings, and source-writer blockers so the contract is machine-checkable.
It must not write `src/`, set `may_write_src: true`, promote specs, or treat aggregate
`node_graph.variables` as a replacement for per-row design semantics.

The repeated-row source-plan contract is the next pre-source-writer layer. It converts
preflight blockers into planned event, scripted-effect, scripted-trigger, GUI,
localization, cleanup, and Alhambra-only listener artifacts with owner-generator names,
EU5 interface candidates, source-target boundaries, row-set keys, entity keys, and
aggregate projection variables. These artifacts are planning data only: every artifact
must keep `may_write_src: false`, block the future source writer, and name missing
generator ownership or EU5 evidence instead of claiming generated source readiness.
For the event, scripted-effect, cleanup, scripted-trigger, GUI, and localization artifact
families, structured evidence mappings record EU5 syntax candidates, source paths, and
generator candidates. GUI mappings are interface candidates for repeated checklist,
incident-log, and actor-slot rows only: they prove fixed generated row widgets,
visibility expressions, per-row variable reads, localized text keys, and actor/action
slot patterns, but still require `design_ir.tracked_entity_sets` per-row semantics and
cannot read only aggregate projection variables. Localization mappings are interface
candidates for row labels, status text, incident text, tooltips, and summary text only:
the existing bilingual generators prove English/Simplified Chinese source boundaries,
`loc_line()` quote/newline escaping, and UTF-8 BOM output, but do not assign repeated-row
loc keys or authorize a localization source writer.
Listener mappings are Alhambra-only war listener interface candidates: the existing
`on_pre_winning_war` / `on_ending_war` registry bridge, selected-ritual scripted triggers,
and completion handoff prove a possible listener interface for the Alhambra war-validation
branch, not loadable Alhambra source generation. They still lack source writer ownership,
source-target boundary validation, and an Alhambra row-state write contract, so they must
remain `may_write_src: false` and must not write `src/`.
Event mappings prove only interface candidates for country-event skeletons, event ID
allocation patterns, title/desc/option localization linkage, option-effect handoff, and
hidden-executor/tooltip safety boundaries; those mappings are still source-writer blockers
and do not authorize `src/` writes.
Repeated-row event source-target contracts are the machine-checkable preflight layer for
that boundary. They name the `tv_engineering_department` namespace, spec `event_ids`,
`node_graph.nodes[].event_id`, `tv_engineering_department.<event_id>.t/d/a(/b)`
localization policy, and future event file pattern
`src/in_game/events/tv_wonder_unique_<wonder_key>_ritual_events.txt`, but those are
boundary validations only. The future target path is not a source generator, event options
may only declare future effect handoff, and no event contract may inline row-state writes,
set `may_write_src: true`, unblock `source_writer_allowed`, or write `src/`.
The repeated-row source preview compiler is an additive dry-run layer on top of the
source-plan. It may render structured event skeleton previews, localization key-plan
previews, scripted-effect name/target plans, cleanup scope/coverage plans,
scripted-trigger condition-group plans, GUI row contract previews, and the Alhambra-only
listener hook contract preview for review, using only existing spec event IDs,
`node_graph.nodes[].event_id`, row-set keys, entity keys, aggregate projection refs, and
future target path contracts. It never writes `src/`, never assigns new IDs, never emits
loadable EU5 effect/cleanup/trigger, GUI, or on_action/listener bodies, never authorizes
row-state writes or unsafe tooltip write paths, and never upgrades contracts or specs to
source-ready. The current repeated-row source preview coverage is closed at 177/177:
event=32, localization=40, scripted-effect=40, cleanup=32, scripted-trigger=24, GUI=8,
and listener=1, with no skipped artifact kinds.
The repeated-row source-writer readiness evidence ledger is the next no-write layer after
that closed preview. It matches every source-plan artifact to its source-preview artifact
and records the remaining evidence chain for EU5 syntax, generator ownership,
source-target boundaries, validation coverage, and lifecycle semantics. The ledger is a
machine-checkable blocker report, not a promotion gate: it keeps all 177 artifacts
blocked, keeps `ready_artifact_count=0`, records unresolved writer blockers, and treats
local paths/generator references as `interface_candidate` evidence unless a later task
adds a complete verified source-writer contract. It does not generate `src/`, does not set
`may_write_src: true`, does not enable `source_writer_allowed`, and does not promote
`source_codegen_ready`, `implementation_ready`, `harness_generated`, or any equivalent
source-ready status.
The event and localization vertical slices in that ledger are closure contracts only.
They add machine-checkable event body preview and localization key-contract evidence for
the four repeated-row pilots, but still keep `may_write_src: false`, `writes_src: false`,
`source_writer_allowed: false`, and `readiness_status: blocked`. They do not grant source
generation permission, do not assign new event IDs or localization files, do not write
`src/`, and do not promote any spec or artifact to source-ready.
The scripted-effect, cleanup, and scripted-trigger vertical slices are also closure
contracts in the readiness ledger. They close state and condition semantics for row
initialization, row-state write boundaries, branch writes, aggregate refreshes, cleanup
handoffs, completion/failure/ownership-loss/reset cleanup, eligibility checks,
row-completion checks, and tooltip-safe condition groups. They still only describe
future target paths and forbidden write contexts; they do not enable a source writer, do
not emit scripted effect or scripted trigger bodies, and do not authorize tooltip or
pre-evaluation contexts to call unsafe write paths.
The GUI and listener vertical slices are now closure contracts in the same readiness
ledger, not source-generation permission. GUI closures close only the repeated-row UI
source-writer boundary: fixed row widget plans, per-row variable binding plans,
checklist/incident-log/actor-slot row policies, tooltip localization linkage,
GUI/event/localization key linkage, aggregate projection boundaries, and the future
`src/in_game/gui/panels/organization/tv_wonder_unique_<wonder_key>_ritual.gui` target
path. They explicitly forbid aggregate-only UI, GUI source body emission, GUI source
writes, row-state writes, and any ready/source-ready claim. The Alhambra listener closure
closes only the listener source-writer boundary: the Alhambra-only scope, future
`src/in_game/common/on_action/tv_wonder_unique_<wonder_key>_ritual_on_actions.txt`
target path, `on_pre_winning_war`/`on_ending_war` hook linkage, selected ritual trigger
linkage, war-scope availability/persistence planning, and row-state handoff boundary.
It does not emit listener bodies, authorize listener or war-scope writes, or permit
source generation.
Repeated-row scripted-effect and cleanup source-target contracts are the matching
source-writer preflight layer for `common/scripted_effects`. They name the future
scripted-effect file pattern
`src/in_game/common/scripted_effects/tv_wonder_unique_<wonder_key>_ritual_effects.txt`
and keep separate `effect` and `cleanup` contract families, including distinct cleanup
scopes for completion, failure, ownership loss, and ritual reset. These contracts verify
only future boundaries, row-state writer/reader responsibility, aggregate projection
boundaries, cleanup coverage, and blocker reasons. They are not scripted-effect source
generators, do not emit effect bodies, do not authorize row-state write schemas, and do
not write `src/`.
Repeated-row scripted-trigger source-target contracts are the preflight layer for
`common/scripted_triggers`, not scripted-trigger source generators. They name only the
future trigger file pattern
`src/in_game/common/scripted_triggers/tv_wonder_unique_<wonder_key>_ritual_triggers.txt`
and verify trigger-name uniqueness, row-completion linkage, eligibility input coverage,
tooltip-safe scope boundaries, aggregate projection responsibility, and blocker reasons.
They do not generate trigger bodies, do not allow tooltip-safe groups to call unsafe
effect/write paths, do not replace `design_ir.tracked_entity_sets` row/entity semantics,
and do not write `src/`.
Repeated-row GUI source-target contracts are source-writer prerequisites for
`in_game/gui/panels/organization`, not GUI source generators. They name only the future
GUI file pattern
`src/in_game/gui/panels/organization/tv_wonder_unique_<wonder_key>_ritual.gui` and
validate fixed row widget boundaries, per-row variable bindings, actor/checklist/incident
row policies, tooltip/key linkage, and aggregate projection boundaries. They do not emit
GUI widgets, do not authorize GUI source writes, do not allow row-state writes, cannot
replace `design_ir.tracked_entity_sets`, and cannot flatten repeated rows into
aggregate-only displays.
Repeated-row localization source-target contracts are source-writer prerequisites for
`main_menu/localization`, not localization source generators. They name only the future
localization file pattern
`src/main_menu/localization/<lang>/tv_wonder_unique_<wonder_key>_ritual_l_<lang>.yml`
and validate English plus Simplified Chinese coverage, loc key namespaces,
`loc_line()` quote/newline escaping, UTF-8 BOM output, row/status/incident/tooltip/summary
coverage, and GUI/event key linkage. They do not write localization files, do not
authorize missing bilingual coverage or unsafe quote/newline handling, and do not write
`src/`.
Preview localization entries are likewise contract previews only: they list bilingual row
label, status, incident, tooltip, and summary keys under the repeated-row namespace and
mirror the existing `loc_line()` escaping/BOM policy without claiming file output.
Scripted-effect, cleanup, scripted-trigger, GUI, and listener previews are also
dry-run/no-write review artifacts: they list future target paths, future names or scopes,
row/entity refs, aggregate boundaries, handoff responsibility, lifecycle coverage,
tooltip-safe predicate plans, fixed GUI row widget and per-row binding plans,
tooltip/localization and GUI/event linkages, Alhambra war hook linkage, selected-ritual
trigger linkage, war-scope availability, and blocker reasons. They do not generate source
bodies, do not authorize `src/` writes, do not produce loadable EU5 GUI/on_action source,
and do not raise `source_codegen_ready`, `implementation_ready`, `harness_generated`, or
any other spec readiness.
The Alhambra-only listener source-target contract is the same kind of source-writer
prerequisite for `common/on_action`. It names only the future on_action file pattern
`src/in_game/common/on_action/tv_wonder_unique_<wonder_key>_ritual_on_actions.txt` and
validates the future hook linkage, listener scope availability, selected-ritual trigger
linkage, row-state handoff boundary, war-listener scope responsibility, and blocker
reasons. The on_action bridge remains an interface candidate only; the contract does not
generate listener bodies, does not authorize listener or war scope writes, and does not
write `src/`.

A future row-set compiler interface must assign ownership before any source-writing claim:

- data ownership: `design_ir.tracked_entity_sets` owns row keys, labels, states, variable
  patterns, UI binding, and cleanup point;
- events generator: owns row-state initialization/update event skeletons only after event
  IDs are allocated;
- scripted effects generator: owns row variable writes, aggregate refreshes, branch-state
  writes, and cleanup effects;
- scripted triggers generator: owns row completion/eligibility checks and tooltip-safe
  condition groups;
- GUI fragment generator: owns fixed repeated checklist/incident rows, starting from the
  verified Pharos-style expansion pattern;
- localization generator: owns row labels, status text, incident text, tooltips, and
  summary text;
- on_action/listener registry integration: participates only for listener-backed row sets,
  such as Alhambra's war listener contract;
- validation: rejects missing row variables, missing writers/readers, missing GUI rows,
  missing localization, unsafe tooltip paths, missing cleanup, and row/UI mismatches.

Until that interface exists and is verified against exact EU5 syntax, the Harness may only
emit intermediate row-set summaries, trigger/effect stubs, GUI summaries, and tooltip notes.
Do not set `may_write_src: true` for this slice, do not write `src/`, and do not treat
`backend_ready` repeated-row gaps as loadable-source readiness.

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
  existing Harness audit and codegen checks.
- Do not bypass the matrix to bulk-write all unique wonder specs directly.

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
- `design_ir`: the high-fidelity mechanism layer that records phases, tracked entity sets, selectors, risk branches, player proofs, map/scope evidence, UI feedback, uniqueness constraints, and projection notes.
- `compiler_gap_ledger`: one row per high-complexity primitive, including the primitive semantics, required game interfaces, current evidence, verification status, search questions, blockers, and fallback.

`needs_codebase_search` and `semantic_only` are normal design states. They mean the design
is worth preserving and should drive later codebase exploration; they do not mean the design
should be flattened to the current template registry.

## Evidence Mapping Stage

Run an evidence mapping pass after `design_complete` and before any source compiler or
source-codegen readiness claim. Use `compiler_gap_ledger.search_questions` as the entry point
for codebase exploration, then update each row with concrete evidence such as paths, helper
functions, event IDs, variable names, UI patterns, scopes, capabilities, or templates.

- `verified_existing` means codebase evidence exists, often through a manual implementation
  or bespoke generator. It does not mean the Harness source generator can emit that primitive.
- `interface_candidate` means a likely interface or pattern exists, but the mapping is not
  proven enough for backend generation.
- `backend_ready` means the primitive is backed by current Harness capability/template
  evidence. Use explicit `capability:<key>` or `template:<key>` evidence. A
  backend-ready capability may still be an intermediate backend contract only; it does not
  imply loadable EU5 source generation unless a later source generator is separately verified.
- `source_codegen_ready`, legacy `implementation_ready`, and `harness_generated` require all
  compiler gap rows to be `backend_ready`; unresolved rows and `verified_existing` rows still
  block those statuses.

## Status Model

Use statuses to describe which layer is complete:

- `design_complete`: the high-fidelity `design_ir` is complete. `compiler_gap_ledger`
  may contain `semantic_only`, `needs_codebase_search`, or `interface_candidate` rows.
- `compiler_mapped`: the design also has a current Harness `node_graph` projection that
  passes semantic graph validation. This still does not mean source codegen is ready.
- `evidence_verified`: the important design primitives have codebase evidence, but source
  generation may still be missing.
- `source_codegen_ready`: the spec has no unresolved compiler gaps and passes source/codegen
  gates.
- `implementation_ready`: legacy alias for `source_codegen_ready`. Do not use it to mean
  "design complete."
- `harness_generated`: generated implementation is owned by the Harness generator.

`implemented_parity` remains for manual implementations mirrored by the spec. It may carry
`design_ir` and `compiler_gap_ledger` to document the full manual design.

## Spec Contract

`data/unique_wonder_ritual_specs.yaml` is the executable planning source.
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
- `node_graph`: for `compiler_mapped`, `source_codegen_ready`, `implementation_ready`,
  and `harness_generated`, a custom graph with at least 3 player-visible nodes, at least 3 event IDs,
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
  `needs_verification` and blocks `source_codegen_ready`, legacy `implementation_ready`,
  or `harness_generated`.

Allowed `compiler_gap_ledger.verification_status` values are:

- `semantic_only`
- `needs_codebase_search`
- `interface_candidate`
- `verified_existing`
- `backend_ready`

The first three are unresolved compiler gaps. They do not block `design_complete`; they do
block `source_codegen_ready`, legacy `implementation_ready`, and `harness_generated`.
`verified_existing` also blocks source-codegen statuses because it proves existing codebase
feasibility, not generator support. Only `backend_ready` satisfies source-codegen gap closure.

## Projection Contract

`design_ir` is the high-fidelity design layer. `node_graph` is only the current Harness
projection. When that projection is lossy, `design_ir.projection_notes` must explain what is
preserved, replaced, compressed, summarized, or intentionally omitted.

- Named tracked sets in `design_ir.tracked_entity_sets`, such as route, office, debt,
  manuscript, district, or frontier networks, must not be silently compressed into one
  anonymous counter.
- If `design_ir.ui_feedback_model` declares repeated rows or per-entity status, projection
  notes must say whether the current node graph preserves rows/status, substitutes a summary,
  or compresses them for the current Harness layer.
- `compiler_mapped` may accept a lossy projection when the node graph passes semantic
  validation and the loss is documented.
- `source_codegen_ready`, legacy `implementation_ready`, and `harness_generated` must still
  hard fail while any compiler gap row is not `backend_ready`.

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
`may_write_src: false`, and notes. The v1 semantic capabilities are `event_chain`,
`retry_branch`, `monthly_progress`, `actor_assignment`, `resource_gate`, `route_gate`,
`listener_gate`, and `final_reward_handoff`. The v1 intermediate backend contracts are
`actor_assignment_character_selector_backend`,
`repeated_entity_row_checklist_incident_log_backend`,
`branch_specific_reward_scaling`, and
`bounded_opposition_religious_community_pressure`; these contracts provide evidence mapping
for richer `design_ir` primitives while still producing only intermediate fragments, stubs, or
summaries. `pilgrimage_route_certification_backend` is the route-certification counterpart:
it preserves pilgrimage route endpoint, waypoint, offering, recognition-proof, failed-route
fallback, and local-only circuit semantics as markdown fragments, trigger/effect stubs, GUI
summaries, and tooltip notes only. It must not generate route source, GUI rows, event chains,
or other loadable EU5 `src` files. `overland_relay_route_certification_backend` is the
overland relay counterpart: it preserves named road segments, tambos, rope-bridge
checkpoints, runner-carried relay message proof, reroute, and domestic-only fallback
semantics as markdown fragments, trigger/effect stubs, GUI summaries, and tooltip notes
only. It must not generate route source, GUI rows, event chains, or other loadable EU5
`src` files. `maritime_trade_route_certification_backend` is the maritime-commercial
counterpart: it preserves monsoon route endpoints, bonded warehouse certification,
translator and merchant-law compacts, blocked or unaffordable route incidents, reroute, and
lower-prestige domestic certification fallback semantics as markdown fragments,
trigger/effect stubs, GUI summaries, and tooltip notes only. It must not generate trade-route,
market, GUI, event-chain, or other loadable EU5 `src` files.
`auxiliary_building_completion_listener_backend` is the construction/auxiliary
completion counterpart: it preserves completion listener, annex inspection, repair retry, and
reward-handoff semantics as markdown fragments, trigger/effect stubs, GUI summaries, and
tooltip notes only. It must not generate `on_action`, `building_type` hooks, or loadable EU5
source.

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
`public_credit_charter_retry` and `arsenal_ropewalk_launch_inspection` are pilot archetypes
for public-credit branching and auxiliary-completion inspection respectively.
`overland_relay_route_proof` is the pilot archetype for road-segment, tambo, rope-bridge,
runner-message, reroute, and domestic-only relay certification. `maritime_trade_route_covenant`
is the pilot archetype for monsoon route endpoints, warehouse seals, translator and
merchant-law compact proof, route incidents, reroute, and domestic-only port certification.
All four remain
intermediate-only and keep `may_write_src: false`.

`compiler_mapped`, `source_codegen_ready`, legacy `implementation_ready`, and
`harness_generated` specs may declare `node_graph.archetypes`.
Known registry archetypes add their required capability/variable-role/UI/listener/node-count
checks. Unknown ordinary archetype names are rejected as likely typos. `custom_*` archetype
labels are allowed only when `mechanic_signature.custom_archetype_statement` explains the
bespoke shape. The validator rejects archetypes marked as allowed to write `src/`, missing
registry-archetype-required capabilities/variable roles/UI/listeners, node counts outside
registry bounds, missing retry paths, missing hidden-executor handoffs, and terminal nodes
that lack the registry-archetype-required capability. It no longer rejects extra node kinds
solely because they are outside the union of declared archetype examples.

## State Machine DSL

`compiler_mapped`, `source_codegen_ready`, legacy `implementation_ready`, and
`harness_generated` specs must use the strong node-graph DSL.
`implemented_parity` and `stub` entries may keep the older lightweight shape.

- `node_graph.mechanic_signature`: required for `compiler_mapped`, `source_codegen_ready`,
  legacy `implementation_ready`, and `harness_generated`; declares the wonder-specific hook, core interaction loop, player
  decision pattern, state feedback, failure/tension model, reward expression, and reuse-risk
  mitigation. If `node_graph.archetypes` contains a `custom_*` key, it must also include
  `custom_archetype_statement`.
- `node_graph.cadence_signature`: required for `compiler_mapped`, `source_codegen_ready`,
  legacy `implementation_ready`, and `harness_generated`; declares `cadence_type`, `cadence_rationale`,
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
- `node_graph.nodes`: each node declares `key`, `kind`, a spec-unique `event_id`, visibility,
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
- listener kinds: `monthly`, `ruler_death`, `pre_winning_war`, `ending_war`,
  `auxiliary_building_completion`. The auxiliary completion listener is an intermediate
  Harness contract for construction/annex completion inspection only; the observed
  `on_construction_ended` source evidence remains owned by source generators outside v1
  unique-ritual codegen.
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
reason or hidden executor handoff. `needs_verification` anywhere in a `source_codegen_ready`,
legacy `implementation_ready`, or `harness_generated` spec blocks validation.

Monthly pacing is allowed only when it is designed, not when it is convenient. If
`node_graph.listeners` includes `monthly`, a node uses `monthly_progress_gate`, a node declares
`monthly_progress`, a listener contract has monthly cadence, or a generator template uses
`monthly_progress_gate`, the cadence type must be `monthly_institutionalization` or `hybrid`.
The rationale must explicitly explain the monthly role. `monthly_institutionalization` still
needs at least one non-monthly decision, risk, listener, event branch, trigger, or player
action; `hybrid` must explain monthly as a local/supporting part of a larger non-monthly loop.

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
