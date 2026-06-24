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
   `monthly_change` only for visible breakdowns meant to appear in tooltips. When a visible
   IO typed variable's progress UI or monthly tooltip depends on automatic monthly gain,
   keep the real contribution in that variable's `monthly_change`. Do not move it to
   `monthly_country_pulse`, country scripted effects, or IO `monthly_effect` to fix a
   runtime bug; repair the `monthly_change` scope/conditions or cached country inputs instead.

5. Match scope to monthly_change.
   IO variable `monthly_change` evaluates from IO/variable context. Do not call country-scoped
   scripted triggers that depend on `root`, `prev`, or caller-specific saved scopes unless the
   full scope chain is verified in the IO variable context. Prefer writing the condition directly
   under `leader_country ?= { ... }`, or create an IO-scoped helper trigger.

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

10. Guard country interaction pre-selection reads.
   Country interaction `accept` scoring and sometimes `effect` preview paths can be evaluated
   from panel buttons before a `select_trigger` has populated `scope:recipient`. Put direct
   `scope:recipient` reads behind `exists = scope:recipient`, and initialize actor-owned
   variables at the lifecycle point that creates the IO before reading them in `accept`.

11. Use route `trade_volume` for Trade League market control.
   For the Trade League monopoly system, annual global refresh may rank origin markets by
   `produced_in_market:<good>` and consumer markets by `goods_demand_in_market(goods:<good>)`,
   but route control itself must come from market export/import iterators. Sum market
   `every_export` entries filtered by `goods = goods:<good>` for origin/node export control,
   and market `every_import` entries for consumer import control, reading `trade_volume`.
   Do not substitute `traded_in_market:<good>`, `goods_supply_in_market`, or member-present
   market totals; those are market availability/proxy values, not member-owned route volume.

12. Keep Trade League bulk monopoly state off IO variables.
   The generated per-good monopoly/action state is intentionally stored on `leader_country`,
   while the IO is saved as a named scope only for membership checks. Do not reintroduce a
   giant `variables = {}` block on `tv_trade_league`; initializing those IO variables caused
   severe runtime stutter. GUI reads should go through
   `GetInternationalOrganization.GetLeaderCountry.MakeScope.GetVariable(...)`.

13. Keep Trade League generated monopoly maintenance off the IO monthly_effect.
    Even hidden IO monthly maintenance for the per-good Trade League monopoly refresh caused
    severe runtime stutter. Register a named country monthly pulse through `data/pulse_registry.yaml`,
    save the country scope, iterate that country's `every_international_organizations_member_of`
    filtered to `tv_trade_league` plus `leader_country ?= <saved country>`, and only then call the
    IO-scoped refresh effect.

14. Do not seed TV IOs with enacted laws at creation.
    All TV IOs start lawless unless a design document explicitly says otherwise. For Trade League,
    leave the IO definition without a `laws = { ... }` block that maps laws to default policies;
    law groups are enacted later through policy votes.

15. Match IO membership iterators to trigger/effect context.
    `any_international_organizations_member_of` is trigger syntax. In effect bodies,
    use `every_international_organizations_member_of = { limit = { ... } ... }`
    when you need to enter matching IO scopes and run effects.

16. Define custom special-status parliament modifier type pairs.
    Every custom IO special status key that can be implemented by an IO needs
    `<status>_can_participate_in_parliament` and `<status>_agenda_impact` in
    `main_menu/common/modifier_type_definitions`, both with
    `game_data = { category = internationalorganization }`. Missing definitions can
    trigger startup DB assertions even when the status is not explicitly using parliament.

17. Give parliament law votes a real meeting location.
    `call_parliament_for_law_change` ends by calling `set_parliament_location` on a saved
    `parliament_location`. For non-HRE IOs it can use `parliament_seat`, a proposer-owned
    IO-owned location, or a random IO-owned location. If a TV IO has no IO-owned locations,
    set its `parliament_seat` variable to a valid location such as the leader capital before
    policy votes can be proposed.

18. Keep IO-scoped helpers out of unstable creation-block roots.
    A `create_international_organization = { ... }` body can be walked during generic-action
    pre-evaluation before the new IO is a stable root. Do not call helpers there if they start
    with IO-only triggers such as `international_organization_type`. Prefer the IO type's
    `on_creation` / `on_joined` hooks, or switch to a verified saved IO scope after creation.

19. Define member opinion biases for every TV IO type.
    Each IO type should have a matching `io_opinion_<io_type>` entry under
    `in_game/common/biases/` and the same key localized in both supported languages.
    Missing the bias logs a startup warning that the organization needs an opinion of
    other members.

20. Keep idle parliament issues positively desirable.
    When a custom IO uses vanilla `call_organization_parliament` for normal, non-law
    sessions, make sure at least one issue for the participating special status has
    valid `potential` / `allow` / `selectable_for` and positive
    `wants_this_parliament_issue_bias` in ordinary founding or neutral-member states.
    Otherwise the issue picker can show that no special status has issues to bring.

## Validation

Run `validate.py --changed --fix --ai-report`, then inspect shared IO tooltips in game. Tooltip
rendering is part of the execution surface for IO maintenance and variables. For any visible IO
typed variable changed during a task, verify that the monthly breakdown still appears in the
IO variable tooltip.
