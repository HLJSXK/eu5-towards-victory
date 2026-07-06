# M14 - Hereditary Office in Crisis

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Hereditary Office in Crisis
- description: A hereditary official fails publicly at the exact task the debate claims should be tested.
- option_a: Use the failure as proof.
- option_b: Shield the office.

## Chinese Text
- title: 世袭官职危机
- description: 一名世袭官员在众目睽睽之下，正好把辩论声称必须考核的那项职责办砸了。
- option_a: 以这次失败作为证据。
- option_b: 保护该官职。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Using the failure as proof gives the meritocratic side a vivid case that inherited office can endanger public work. The argument advances sharply, while noble satisfaction falls because an old privilege has become evidence against itself.
- rationale_zh: 把这次失败当作证据，为任人唯才一方提供了鲜明案例：世袭官职会危及公共事务。论点因此大幅推进，而贵族满意度下降，因为旧特权成了反证自身的材料。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Shielding the office prevents an immediate legitimacy crisis and protects the dignity of inherited administration. It also tells the debate that birth may survive even the public failure of competence.
- rationale_zh: 保护该官职可以避免眼前的正统性危机，并维护世袭行政的体面。但这也等于告诉辩论，即便能力公开失败，出身仍可幸存。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike M02 Genealogies on the Table, this is not an abstract defense of inherited service; a hereditary official has visibly failed at a concrete task.
- Unlike M17 The Crown's Favorite Fails, the failed candidate represents hereditary office rather than personal favoritism from the Crown.
- Unlike M10 Boycott by Old Families, noble privilege is challenged by public incompetence instead of by a threat to withdraw from Academy rankings.
