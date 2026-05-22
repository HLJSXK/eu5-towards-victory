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

6. Match scope to IO law block type.
   In IO policy `allow`, `on_activate`, and `on_deactivate`, the current root is already the IO.
   Do not wrap IO variable or policy checks in `scope:recipient` there. Reserve `scope:recipient`
   for documented country-root AI math blocks such as `wants_this_policy_bias` and
   `wants_propose_policy`.

7. Guard IO law AI math recipient reads.
   `wants_this_policy_bias`, `wants_propose_policy`, `wants_keep_policy`, `reasons_to_join`,
   and `diplomatic_capacity_cost` may be pre-evaluated without a recipient event target.
   Before direct `scope:recipient` reads, add `exists = scope:recipient` in the same limit
   block, or use optional `scope:recipient ?= { ... }` when a trigger-only check is enough.

8. Use the evaluating country in generic action AI-list IO filters.
   `generic_action_ai_lists` potential root is the country. Inside
   `any_international_organizations_member_of`, `this` is the IO, so leader checks should use
   `exists = leader_country` plus `leader_country = root`, not `leader_country = this`.

9. Use `scope:actor` in country interaction potential blocks.
   In `common/country_interactions`, `potential` exposes the acting country as `scope:actor`.
   Wrap IO membership checks in `scope:actor = { ... }`; direct country-scoped IO iterators
   under `potential` can evaluate from an invalid root.

10. Use real goods quantity metrics for IO trade systems.
   For world goods production totals, use `produced_in_world:<good>`. For an IO's member-owned
   goods trade, iterate `every_international_organization_member = { every_trade = { ... } }`,
   filter with `goods = goods:<good>`, and sum `trade_volume`. Do not substitute
   `total_effective_goods_production_buildings(goods:<good>)` or member `every_market_present_in_country`
   plus `traded_in_market:<good>`; those count building levels or full market totals instead of
   member-owned goods quantities.

## Validation

Run `validate.py --changed --fix --ai-report`, then inspect shared IO tooltips in game. Tooltip
rendering is part of the execution surface for IO maintenance and variables.
