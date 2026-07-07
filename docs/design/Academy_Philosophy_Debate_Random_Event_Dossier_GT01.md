# GT01 - Harbor Ledgers

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Harbor Ledgers
- description: Harbor clerks spread ledgers of salt, silk, spice, freight, and insurance across the Academy table. Every column insists that distant prices already shape the realm, even when landed honor pretends not to notice.
- option_a: Read the ledgers aloud.
- option_b: Dismiss merchant arithmetic.

## Chinese Text
- title: 港口账簿
- description: 港口书记员把盐、丝绸、香料、运费和保险的账簿摊在学院桌上。每一列数字都说明，遥远价格早已在塑造本国，哪怕土地上的荣誉装作毫不在意。
- option_a: 当众宣读账簿。
- option_b: 斥之为商人的算术。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Reading the ledgers aloud makes global price dependence official evidence rather than tavern rumor. Burgher and maritime interests can now argue from records, so the debate moves sharply toward accepting global trade.
- rationale_zh: 当众宣读账簿，会把对全球价格的依赖变成正式证据，而不是酒馆传闻。市民与海商由此可以凭记录发言，因此辩论会明显转向接受全球贸易。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Dismissing the figures restores the dignity of land and lineage over counting-house evidence. That comforts nobles, but it teaches the room to reject the very arithmetic that proves global trade is already present.
- rationale_zh: 斥退这些数字，会让土地与门第的体面重新压过账房证据。这能安抚贵族，却也等于教会会场拒绝那些证明全球贸易已经存在的算术。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT02 Foreign Merchant Quarter, GT01 does not decide legal privileges for outsiders; it asks whether domestic leaders will admit what their own harbor records already prove.
- Unlike GT03 Tariff Confusion, GT01 is about recognizing global price dependence before redesigning the customs machinery around it.
- Unlike GT04 Spice Cargo, which persuades through a visible luxury cargo, GT01 persuades through dry numbers and the political authority of official ledgers.
