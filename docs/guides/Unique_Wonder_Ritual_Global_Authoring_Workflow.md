# Unique Wonder Ritual Global Authoring Workflow

This workflow is for full-corpus planning before any bulk Unique Wonder Ritual
Harness spec authoring. It exists to prevent 123 unique wonders from collapsing
into repeated cadence shapes, repeated UI models, or the safest mature template.
It also prevents formal specs from flattening matrix ideas merely because current
capabilities, templates, or codegen cannot express them yet.

The design matrix is not a formal ritual spec and is not loadable EU5 code.
It is the global allocation surface that must be reviewed before any later pass
turns entries into `data/unique_wonder_ritual_specs.yaml` records.

## Current Phase Freeze

The full-corpus Harness design承载阶段 is complete. All 123 unique-wonder ritual designs
are represented in the Harness intermediate layer with `compiler_mapped=117`,
`source_codegen_ready=4`, `implemented_parity=2`, `stub=0`, `harness_generated=0`, and
registry/codegen `may_write_src=0`.

`compiler_mapped` is a design-bearing semantic projection, not a source-ready state. The
source generation stage has not started: v1 codegen remains restricted to intermediate
Markdown fragments, and all template/capability/archetype registry contracts must keep
`may_write_src: false`.

The 17 rows marked as future Harness/EU5 gaps are the next source compiler / EU5
verification backlog. Preserve those rows and their feasibility labels instead of removing
or simplifying them to silence the warning.

## Required Sequence

1. Maintain `data/unique_wonder_ritual_design_matrix.yaml`.
   - Each unique wonder must have one row.
   - Safe fact fields come from local data: wonder id/key/name, base wonder type,
     category, location, and localization-derived historical hook.
   - Culture, religion, and region stay `null` unless a local data source directly
     provides them.
2. Draft global mechanism allocation in the matrix.
   - Choose cadence, prompt atoms, core mechanism, player agency, UI model,
     expected capabilities, expected listeners, non-monthly validation point,
     risk branch, feasibility, uniqueness notes, and similarity group.
   - Use prompt atoms from `docs/guides/Unique_Wonder_Ritual_Design_Prompt_Library.md`.
   - Use only supported Harness listeners: `monthly`, `ruler_death`,
     `pre_winning_war`, and `ending_war`.
3. Run the global matrix audit:
   `conda run --no-capture-output -n eu5 python scripts/audit_unique_wonder_ritual_design_matrix.py`
4. Resolve global risks before freezing entries.
   - Rebalance overused cadence types.
   - Split repeated atom/UI combinations.
   - Add missing non-monthly validation points and uniqueness notes.
   - Mark future gaps clearly with `implementation_feasibility`.
5. Freeze mechanism allocation.
   - Set `authoring_status: reviewed` after the row is ready for spec conversion.
   - Set `authoring_status: frozen` only after the row has survived global audit
     with acceptable repetition and feasibility risk.
6. Only after matrix review, create formal Harness specs.
   - Do not bypass the matrix to bulk-write `data/unique_wonder_ritual_specs.yaml`.
   - Formal specs must preserve the matrix's design complexity in `design_ir` before
     writing any current `node_graph` projection.
   - Unverified mechanisms belong in `compiler_gap_ledger` with `semantic_only`,
     `needs_codebase_search`, or `interface_candidate`; do not delete them to satisfy
     the current registry.
   - Formal spec generation remains a later pass and must still run Harness design,
     semantic graph, and source/codegen checks at the appropriate status layer.
7. Run evidence mapping before source compiler readiness.
   - Use each `compiler_gap_ledger.search_questions` entry to search the codebase for
     existing functions, event IDs, variables, scopes, UI patterns, capabilities, or templates.
   - Promote rows only as far as the evidence supports: `interface_candidate` for plausible
     interfaces, `verified_existing` for manual/codebase evidence, and `backend_ready` only
     for current Harness capability/template support.
   - A `verified_existing` row proves that a primitive exists somewhere in the codebase; it
     does not prove the source compiler can generate it.
   - If a current `node_graph` projection compresses repeated rows, named entity networks,
     per-entity status, selectors, or multi-axis UI feedback, record the loss and reason in
     `design_ir.projection_notes`.

## Matrix Field Semantics

- `primary_cadence_type`: Main pacing model. Must use a Harness-supported cadence
  type when filled.
- `secondary_cadence_type`: Optional supporting cadence. Keep null unless it
  materially changes the loop.
- `cadence_rationale`: Why this cadence fits the wonder. Required in practice for
  any monthly institutionalization design.
- `mechanic_prompt_atoms`: Atom numbers or short keys from the prompt library.
- `proposed_core_mechanic`: One concise description of what the player proves.
- `player_agency_model`: The player's meaningful decision or validation role.
- `expected_ui_model`: Harness UI components expected by the design, such as
  `checklist`, `route_map`, `actor_slots`, `material_stockpile`, `incident_log`,
  or `progress_track`.
- `expected_capabilities`: Harness capabilities expected by the design.
- `expected_listeners`: Only the four currently supported listener names may be used.
- `non_monthly_validation_point`: A concrete non-monthly decision, risk, listener,
  trigger, route/resource proof, actor assignment, war result, succession point,
  construction completion, or event branch.
- `risk_or_failure_branch`: How the ritual can fail, retry, stall, or produce a
  weaker outcome.
- `implementation_feasibility`: One of `current_harness_ready`,
  `needs_trigger_check_only`, `needs_new_capability`, `needs_new_listener`,
  `needs_eu5_verification`, or `blocked`. It may be null only while
  `authoring_status` is `unassigned`.
  Future-gap feasibility should become `compiler_gap_ledger` rows during formal spec
  conversion, not generic simplification.
- `uniqueness_notes`: Why this loop belongs to this wonder rather than its base
  category.
- `similarity_group`: A freeform grouping key used only for global repetition audit.
- `authoring_status`: `unassigned`, `drafted`, `reviewed`, or `frozen`.

## Audit Expectations

`scripts/audit_unique_wonder_ritual_design_matrix.py` checks coverage,
unknown or duplicate wonder ids, supported cadence/listener/UI/capability values,
prompt atom references, feasibility/status enums, and global distributions.

The audit exits nonzero for structural errors. Distribution and authoring risks
remain warnings so an early planning matrix can be inspected before it is complete.

Initial seeded matrices are expected to report warnings for missing
`non_monthly_validation_point` and `uniqueness_notes`. Those warnings become work
items for the full-corpus design pass, not reasons to generate formal specs early.

During spec conversion, treat `design_complete` as the first target status. Promote to
`compiler_mapped` only after a current Harness `node_graph` projection exists, and promote
to `source_codegen_ready` only after every compiler gap row is `backend_ready`. `needs_codebase_search`
is expected in early high-fidelity specs and should drive the next codebase exploration pass.
