# M05 - Merit on the Battlefield

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Merit on the Battlefield
- description: Officers argue that command earned under fire should count more than old names.
- option_a: Recognize battlefield merit.
- option_b: Preserve noble command privilege.

## Chinese Text
- title: 战场上的功绩
- description: 军官们主张，炮火下赢来的指挥资格应当比古老姓氏更有分量。
- option_a: 承认战场功绩。
- option_b: 维护贵族指挥特权。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Recognizing battlefield merit gives the reform a martial constituency and shows that competence can be proven under pressure, not merely on paper. The professional military gains a reason to back the debate.
- rationale_zh: 承认战场功绩会为改革带来军事支持者，并说明能力不仅能在纸面上证明，也能在压力之下证明。职业军人因此有理由支持这场辩论。
- effect_blocks:
```yaml
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_commission_review
  months: 24
  effects:
    "army reform credibility": 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Preserving noble command privilege keeps military rank tied to birth and honor. The old command families are reassured, while battlefield competence remains secondary to inherited status.
- rationale_zh: 维护贵族指挥特权会让军阶继续依附于出身与荣誉。旧有统帅家族得到安抚，而战场能力仍被置于继承地位之后。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike M16 Veterans' Service Rolls, this event concerns command earned in battle rather than counting long disciplined service toward appointments.
- Unlike M08 Guild Tests, the practical proof comes from military performance, not urban professional testing for accountants, engineers, or clerks.
- Unlike M10 Boycott by Old Families, noble privilege is defended through command hierarchy rather than by threatening the Academy's open rankings.
