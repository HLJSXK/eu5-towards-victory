# GT20 - Map of Trade Winds

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Map of Trade Winds
- description: Navigators unroll wind charts across the Academy table, and old routes suddenly look less like tradition than superstition with sails. Even the captains who scoff keep glancing at the lines.
- option_a: Adopt wind routing.
- option_b: Keep established routes.

## Chinese Text
- title: 贸易风向图
- description: 航海者在学院桌上展开风向图，旧航线忽然不再像传统，而像挂着帆的迷信。连出声嘲笑的船长也忍不住反复偷看那些线条。
- option_a: 采用风向航路。
- option_b: 保留既定航线。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Adopting wind routing lets practical navigation become evidence for Global Trade. It modestly advances acceptance by showing that distant exchange can be planned through observation rather than inherited habit.
- rationale_zh: 采用风向航路会让实际航海技术成为全球贸易的证据。它表明远距离交换可以凭观察来规划，而不必依赖旧习，因此温和推动接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
- type: scientist_attribute
  adm: 0
  dip: 1
```

### Option B
- progress_delta: -5
- rationale_en: Keeping established routes honors captains who trust inherited seamanship, but it leaves the debate treating wind knowledge as a curiosity instead of a system for global exchange.
- rationale_zh: 保留既定航线是在尊重信赖旧航海术的船长，却也让辩论把风向知识视为奇谈，而不是全球交换的体系。
- effect_blocks:
```yaml
- type: seat_stance
  group: professional_military
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_established_routes
  months: 12
  effects:
    conservative navigation practice preserved: 0.01
```

## Difference From Same Issue Events
- Unlike GT11 Caravan and Convoy, GT20 is about navigational knowledge changing routes, not state funding between inland and sea interests.
- Unlike GT15 Naval Escort Debate, GT20 does not buy security for merchants; it asks whether route planning should follow observed winds.
- Unlike GT17 Language of Contracts, GT20 concerns maritime practice and charts rather than the legal language that makes trade agreements portable.
