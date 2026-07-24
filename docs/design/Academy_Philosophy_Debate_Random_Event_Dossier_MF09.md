# MF09 - Noble Estate Workshop

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Noble Estate Workshop
- description: A noble estate opens a large workshop with admirable confidence, then objects when burghers ask for the same freedom. The Academy is invited to discover whether scale is modern only when it wears a crest.
- option_a: Apply rules equally.
- option_b: Exempt noble workshops.

## Chinese Text
- title: 贵族庄园作坊
- description: 一处贵族庄园满怀自信地开办了大型作坊，却在市民也要求同样自由时表示反对。学院被迫判断：难道只有带着纹章的规模化才算体面？
- option_a: 平等适用规则。
- option_b: 豁免贵族作坊。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Applying rules equally turns manufactories into a general economic principle rather than a privilege of rank. Noble satisfaction falls because landed status no longer decides who may benefit from concentrated production.
- rationale_zh: 平等适用规则会把手工业工场变成普遍经济原则，而不是等级特权。贵族满意度下降，因为土地身份不再决定谁能从集中生产中获益。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Exempting noble workshops preserves rank privilege while hollowing out the reform. If scale is allowed only for estates, manufactories become another noble exception rather than a new productive order.
- rationale_zh: 豁免贵族作坊会保全等级特权，同时掏空改革本身。如果规模化只准庄园享用，手工业工场就会变成又一项贵族例外，而不是新的生产秩序。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 24
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.05
```

## Difference From Same Issue Events
- Unlike MF01 Workshop Under One Roof, MF09 is not asking whether concentration works, but whether the law applies to noble and burgher concentration alike.
- Unlike MF19 Merchant Capital Pool, MF09 centers noble privilege over workshop rights rather than merchant finance pooling capital.
- Unlike MF02 Guild Master's Complaint, MF09's opposition comes from rank exemption, not guild quality control.
