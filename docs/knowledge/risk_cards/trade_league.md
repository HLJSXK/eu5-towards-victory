# Trade League Risk Card

Load this card before editing any file with `trade_league` or `trade_chain` in its filename:
`data/trade_league_goods.yaml`, `data/trade_chain.yaml`, `data/trade_league_laws.yaml`, the
`gen_tv_trade_league_*.py` / `gen_tv_trade_chain_display_modifiers.py` generators, and their
generated IO type, effects, `goods_demand`, `generic_actions`, GUI, static modifiers, and
localization outputs.

The Trade League is a TV international organization, so
`docs/knowledge/risk_cards/international_organizations.md` rules 11–14 also apply here
(route control via market `trade_volume`, bulk monopoly/action state on `leader_country` not
IO variables, no IO `monthly_effect` for monopoly maintenance, lawless at creation). This card
covers the rules specific to the Trade League's generated goods/monopoly system.

## Required Checks

1. Compute monopoly control from a full market route scan, not proxy totals.
   `produced_in_market:<good>` and `goods_demand_in_market(goods:<good>)` are valid for
   ranking origin/consumer markets and choosing the annual representative market, but they
   are not route-volume proxies. Origin/transit control must sum market `every_export`
   entries filtered by `goods = goods:<good>` and read `trade_volume`; consumer control must
   sum market `every_import` entries the same way. Do not substitute `traded_in_market:<good>`
   or `goods_supply_in_market`. When a mechanic needs all goods on a route, use the route
   scope's `traded_goods = { save_scope_as = ... }` into a map/list instead of generating one
   iterator per good; keep static per-good branches only where a target effect requires a
   static database id (e.g. `add_temporary_demand type = demand:*`).

2. Wrap dynamic numeric reads in an explicit script-value block.
   Passing a generic-action value selector or scoped variable directly as `set_variable`
   `value`, `add_temporary_demand` `scale`, or `add_goods_supply` `amount` can collapse to `1`
   instead of the selected number. Use `value = { value = scope:target_1 }`,
   `scale = { value = scope:io.var:X }`, or `amount = { value = scope:io.var:X }` (inline
   arithmetic such as `divide = 2` belongs inside the same block).

3. Keep merchant-power keyed state synchronized, not additively stacked.
   Commercial-intelligence strength is `leader_country` state, but the merchant power it
   grants is market/country-keyed state. Each monthly refresh must clear only the
   `tv_trade_intelligence_network` key from previously tracked markets before reapplying
   `months = -1` permanent merchant power for current members, and only when the current
   floor strength is at least 1. Also clear that key when the Grand Merchant becomes invalid.
   Do not refresh by repeatedly stacking a temporary `months = 2` modifier.

4. Start the Trade League lawless.
   Do not emit a `laws` block with policy-to-default mappings in `tv_trade_league.txt`, and do
   not mark generated Trade League policies as `default: true` in `trade_league_laws.yaml`.
   Diplomatic Alliance is a separate, explicitly-designed exception that seeds baseline
   no-effect policies; the Trade League is not.

## Validation

Run `validate.py --changed --fix --ai-report`: it lints rule 4
(`tv_io_initial_laws_seeded`) and the shared IO `monthly_effect` ban automatically. Rules 1–3
have no automated check — after changing monopoly/intelligence generators, verify in game
that monopoly control percentages and intelligence network strength match expected market
data, since a wrong-metric regression here does not fail validation.
