# GT03 - Tariff Confusion

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Tariff Confusion
- description: A customs review reveals duties so tangled that profitable cargo is punished by accident while favored goods slip through by habit. The schedule has become a policy argument written in crossed-out numbers.
- option_a: Simplify tariffs.
- option_b: Keep the schedule.

## Chinese Text
- title: 关税混乱
- description: 一场海关审查发现，现行税目纠缠到会误伤有利可图的货物，而受偏爱的商品却凭惯例轻松通行。税表已经变成一场写满划线数字的政策争论。
- option_a: 简化关税。
- option_b: 保留原有税目。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Simplifying tariffs turns global trade from an accidental privilege into a legible system. The reform strengthens acceptance because merchants can plan around clear rules, even as old customs rents are curtailed.
- rationale_zh: 简化关税会让全球贸易不再只是偶然的特权，而成为可以读懂的制度。商人能够围绕清晰规则制定计划，因此改革会加强接受倾向，尽管旧有海关租利会被削弱。
- effect_blocks:
```yaml
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_simplified_tariffs
  months: 24
  effects:
    old customs rents curtailed: -0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping the schedule preserves the habits and quiet rents of conservative officials. It slows acceptance by treating confusion as a tolerable price for control.
- rationale_zh: 保留原有税目，会维护保守官员的惯例和隐性租利。它把混乱视为控制的可接受代价，因此会拖慢对全球贸易的接受。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT01 Harbor Ledgers, GT03 starts after leaders already know trade matters and asks whether the state can make its fiscal tools coherent.
- Unlike GT07 Smuggler's Map, GT03 addresses legal confusion inside the official tariff book rather than illegal routes outside it.
- Unlike GT10 Standard Weights, GT03 standardizes taxes and categories at the customs house rather than physical measures across markets.
