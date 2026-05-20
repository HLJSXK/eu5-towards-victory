# International Organizations Risk Card

Load this card before editing files under `common/international_organizations/` or effects
that create, find, or mutate TV IOs.

## Required Checks

1. Preserve TV IO leader invariants.
   Do not call `international_organization_chooses_new_leader` for TV IOs. Keep
   `leader_change_trigger_type = none`, and read appointed characters through
   `leader_country.var:tv_xxx_leader_char.attribute`.

2. Treat TV IOs as non-unique unless explicitly documented otherwise.
   Do not use `international_organization:type_key` links for non-unique TV IOs. Iterate
   memberships and filter by `international_organization_type = international_organization_type:<id>`.

3. Make nullable leader_country access optional.
   Use `leader_country ?= ...` in filters or tooltip-visible contexts. Vanilla IOs and newly
   created IOs can have null leader countries during evaluation.

4. Keep maintenance hidden.
   Non-player-facing `monthly_effect` logic should be inside `hidden_effect`. Use IO variable
   `monthly_change` only for visible breakdowns meant to appear in tooltips.

5. Match scope to monthly_change.
   IO variable `monthly_change` evaluates from IO/variable context. Do not call country-scoped
   scripted triggers that depend on `root.var` unless root is verified.

## Validation

Run `validate.py --changed --fix --ai-report`, then inspect shared IO tooltips in game. Tooltip
rendering is part of the execution surface for IO maintenance and variables.
