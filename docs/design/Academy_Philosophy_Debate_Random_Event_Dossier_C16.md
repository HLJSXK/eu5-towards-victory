# C16 - Confession Tax

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Confession Tax
- description: Officials propose a dedicated levy for confessional schools, arguing that doctrine taught cheaply will be doctrine forgotten quickly. The villages hear the word "school" and count the word "tax."
- option_a: Levy the tax.
- option_b: Refuse the tax.

## Chinese Text
- title: 信纲税
- description: 官员提议为宗派学校征收一项专门税，声称教义若教得太廉价，就会被遗忘得太迅速。乡村听见的是“学校”，盘算的却是“税”。
- option_a: 征收这项税。
- option_b: 拒绝这项税。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Funding schools gives the confessional program a practical classroom base, so acceptance advances, but the levy makes ordinary households feel that doctrine is being collected from their purses.
- rationale_zh: 为学校筹资会给宗派纲领提供实际的课堂基础，因此推动接纳；但这项征税也会让普通人家觉得，教义正从他们的钱袋里被征收出来。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: estate_satisfaction
  estate: peasants_estate
  value: -0.04
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Refusing the tax protects rural patience and keeps confessional education from becoming a fiscal grievance, but it also leaves the new doctrine without the funding needed to reach parish children.
- rationale_zh: 拒绝征税可以保全乡村的耐心，避免宗派教育变成财政怨言；但新教义也因此缺少进入堂区儿童生活所需的经费。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.04
- type: seat_cooldown
  group: religious_reformers
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike C10 Feast Day Reform, C16 argues over money and school funding rather than the sacred calendar of local custom.
- Unlike C11 Confessional Schoolbooks, C16 concerns how confessional education is paid for, not what doctrine the books teach.
- Unlike C19 Confessional Census, C16 extracts resources from the population, while C19 classifies communities for administrative knowledge.
