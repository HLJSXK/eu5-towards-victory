# R16 - New Calendar of Festivals

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: New Calendar of Festivals
- description: Scholars suggest reshaping civic festivals around learning, arts, and urban pride, until the year's holy and market days begin to look like an argument about what the realm honors.
- option_a: Adopt the new festivals.
- option_b: Keep the old festival order.

## Chinese Text
- title: 新节庆历
- description: 学者建议重塑市民节庆，使其围绕学问、艺术与城市荣誉展开。于是，一年的圣日与集市日也开始像是在争论王国究竟尊崇什么。
- option_a: 采纳新的节庆安排。
- option_b: 保留旧有节庆秩序。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Turning the calendar itself into a civic-humanist teaching tool makes Renaissance acceptance feel public and durable, but organizing new festivals costs money and unsettles inherited ritual rhythms.
- rationale_zh: 把历法本身改造成市民人文主义的教化工具，会让文艺复兴的接受显得公开而持久；但筹办新节庆需要花费，也会扰动既有礼仪节奏。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Preserving the old order lets clergy and local elders frame Renaissance festival reform as needless disruption, hardening resistance rather than merely slowing the debate.
- rationale_zh: 保留旧秩序会让神职人员与地方长老把节庆改革说成无谓扰动，从而强化反对，而不只是拖慢辩论。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike R08 Court Masque, this is not a court performance or prestige pageant; it moves Renaissance values into the recurring civic year.
- Unlike R12 Fresco of the New Age, this is not one symbolic artwork inside the Academy; it asks towns and communities to reorder public time around learning and art.
- Unlike R14 Poets at the Debate, public enthusiasm here is formalized through institutions and festivals rather than loose language escaping into the streets.
