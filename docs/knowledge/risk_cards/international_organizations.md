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
   created IOs can have null leader countries during evaluation. IO law browsing can also
   walk `on_activate` / `on_deactivate` effect chains, so mirrored leader-country writes there
   must use `leader_country ?= { ... }`.

4. Do not use IO `monthly_effect`.
   TV international_organization types must not define `monthly_effect` blocks. They have
   severe performance costs even when hidden. Use IO variable `monthly_change` only for
   visible breakdowns meant to appear in tooltips. When a visible IO typed variable's progress
   UI or monthly tooltip depends on automatic monthly gain, keep the real contribution in that
   variable's `monthly_change`. Move maintenance/completion side effects to registered country
   monthly pulses or explicit lifecycle hooks; repair `monthly_change` scope/conditions or
   cached country inputs rather than moving visible variable arithmetic elsewhere.

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
   When the design needs all goods from a route, use the route scope's
   `traded_goods = { save_scope_as = ... }` and put the goods scope into a map/list instead
   of generating one route iterator per good. Keep static per-good branches only where a
   target effect requires a static database id, such as `add_temporary_demand type = demand:*`.

12. Keep Trade League bulk monopoly state off IO variables.
   The generated per-good monopoly/action state is intentionally stored on `leader_country`,
   while the IO is saved as a named scope only for membership checks. Do not reintroduce a
   giant `variables = {}` block on `tv_trade_league`; initializing those IO variables caused
   severe runtime stutter. GUI reads should go through
   `GetInternationalOrganization.GetLeaderCountry.MakeScope.GetVariable(...)`.

13. Keep heavy generated maintenance behind cheap country-pulse gates.
    Register a named country monthly pulse through `data/pulse_registry.yaml`, save the country
    scope, iterate that country's `every_international_organizations_member_of` filtered to the
    relevant TV IO plus `leader_country ?= <saved country>`, and only then call the IO-scoped
    refresh effect.

14. Seed IO laws only when the design requires a baseline state.
    Trade League, Arts Exhibition, Academy of Sciences, and Governor's House start without
    initial policies unless a later design explicitly changes them. Diplomatic Alliance is the
    current exception: its IO definition must seed all five law groups to their baseline
    no-effect policies so creation starts at the baseline tier-0 state rather than no law.

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

18. Sync custom parliament special statuses from stable lifecycle points.
    For custom IO statuses that drive parliament voting or visible special-status power, do
    not rely only on `auto_bestowal_trigger` or same-tick `on_joined` state. Follow the HRE
    free-city pattern: the action or lifecycle effect that creates, invites, promotes, demotes,
    or removes a country should directly call `international_organization_add_special_status`
    or `international_organization_remove_special_status` from the IO scope. Do not add
    recurring monthly refreshes for special-status repair, and do not add extra parliament-seat
    or full-member repair unless a separate law-vote/location bug proves it is needed.

19. Keep IO-scoped helpers out of unstable creation-block roots.
    A `create_international_organization = { ... }` body can be walked during generic-action
    pre-evaluation before the new IO is a stable root. Do not call helpers there if they start
    with IO-only triggers such as `international_organization_type`. Prefer the IO type's
    `on_creation` / `on_joined` hooks, or switch to a verified saved IO scope after creation.

20. Define member opinion biases for every TV IO type.
    Each IO type should have a matching `io_opinion_<io_type>` entry under
    `in_game/common/biases/` and the same key localized in both supported languages.
    Missing the bias logs a startup warning that the organization needs an opinion of
    other members.

21. Filter IO policy member modifiers to their intended recipients.
    Vanilla `policy_vote` adds `scope:vote.modifier_utility(scope:actor)` to each
    voting country's AI support as `POLICY_MODIFIER_UTILITY`. If a visible IO law
    policy effect is meant for the leader country only and must stack with other
    law modifiers, keep it as `country_modifier` but make the display filter
    recipient-safe:
    `potential_trigger = { OR = { NOT = { exists = scope:recipient } is_leader_of_international_organization = scope:recipient } }`.
    The no-recipient branch is for ordinary law browsing; the leader check still
    applies when a vote/application recipient exists. Use `leader_modifier` only
    when replacing previous leader modifiers is intended. Otherwise subject or
    non-target members can strongly favor a policy because they evaluate the
    unfiltered modifier package as their own direct benefit.

22. Keep idle parliament issues positively desirable.
    When a custom IO uses vanilla `call_organization_parliament` for normal, non-law
    sessions, make sure at least one issue for the participating special status has
    valid `potential` / `allow` / `selectable_for` and positive
    `wants_this_parliament_issue_bias` in ordinary founding or neutral-member states.
    Otherwise the issue picker can show that no special status has issues to bring.

23. Do not re-read a variable_map as the confirmation gate for a long-open event.
    A `trigger_event_non_silently` confirmation event can stay open for arbitrary game
    time before the player answers. Validate the scope captured at queue time/`immediate`
    directly (e.g. ownership) instead of re-reading a `variable_map`/`global_variable_map`
    entry for the event's key and identity-matching it against that captured scope;
    ownership-change or lifecycle handling can legitimately reselect the map's candidate
    while the popup is open. Also make any trailing unconditional cleanup effect
    conditional on the confirmation having actually committed, so a failed confirm does
    not silently discard the pending request. If the same option also ran an `instant`
    construction in its visible effect just before this confirm runs, do NOT re-check
    `has_building_with_at_least_one_level` here either -- instant construction does not
    reliably update that read within the same effect chain (see the Critical EU5 Gotchas
    in the repo-root CLAUDE.md); trust that the visible construct_building already ran and
    only re-validate ownership/other non-building state.
    See `tv_govhouse_confirm_local_administration_event_scope_effect` in
    `common/scripted_effects/tv_govhouse_effects.txt` and
    `docs/knowledge/anti_patterns.yaml` rule `variable_map_reread_as_confirmation_gate`.

## Validation

Run `validate.py --changed --fix --ai-report`; it fails any TV IO `monthly_effect` block. Then
inspect shared IO tooltips in game. Tooltip rendering is part of the execution surface for IO
variables. For any visible IO typed variable changed during a task, verify that the monthly
breakdown still appears in the IO variable tooltip.
