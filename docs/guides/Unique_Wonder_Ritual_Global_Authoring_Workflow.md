# Unique Wonder Ritual Global Authoring Workflow

This workflow is for full-corpus planning before any bulk Unique Wonder Ritual
Harness spec authoring. It exists to prevent 123 unique wonders from collapsing
into repeated cadence shapes, repeated UI models, or the safest mature template.

The design matrix is not a formal ritual spec and is not loadable EU5 code.
It is the global allocation surface that must be reviewed before any later pass
turns entries into `data/unique_wonder_ritual_specs.yaml` records.

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
   - Formal spec generation remains a later pass and must still run the existing
     Harness audit and codegen checks.

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
