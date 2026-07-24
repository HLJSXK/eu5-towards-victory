# GT05 - Port Nobles Object

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Port Nobles Object
- description: Inland nobles warn that ocean trade teaches the realm to honor warehouses more than fields. Their speeches arrive polished, offended, and entirely certain that wealth should still smell like earth.
- option_a: Challenge their claim.
- option_b: Reassure landed privilege.

## Chinese Text
- title: 港口遭贵族反对
- description: 内陆贵族警告说，海洋贸易会教本国更尊重仓库而不是田地。他们的演说修饰得体、满怀不悦，并且坚信财富仍然应该带着泥土气味。
- option_a: 反驳他们的主张。
- option_b: 安抚土地特权。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Challenging the nobles openly breaks the assumption that land-based wealth is the only honorable foundation of policy. Global trade gains force because maritime profit is defended as legitimate national strength.
- rationale_zh: 公开反驳贵族，会打破以土地财富作为唯一体面政策根基的假设。由于海上利润被辩护为正当的国家力量，全球贸易的接受度会大幅上升。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Reassuring landed privilege protects noble status by framing port wealth as secondary and dependent. The debate turns sharply away from acceptance because the old hierarchy is allowed to define the new economy.
- rationale_zh: 安抚土地特权，会把港口财富描述为次要且依附于土地，从而保护贵族地位。旧等级得以界定新经济，因此辩论会明显转向拒绝接受。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.05
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike GT01 Harbor Ledgers, GT05 centers on ideological resistance from inland nobles rather than evidence that trade already shapes prices.
- Unlike GT11 Caravan and Convoy, GT05 is not a budget fight between inland and sea routes; it is a status fight over which kind of wealth deserves honor.
- Unlike GT16 Guild Monopoly Challenge, GT05 opposes maritime trade from landed privilege, not from urban guild control of production and market access.
