# G05 - Private Lecture at Dusk

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Private Lecture at Dusk
- description: As the chamber empties, the Chief Scientist offers to gather a few decisive listeners before the candles burn low. Confusion can still be turned into conviction, if someone pays the evening's cost.
- option_a: Authorize the lecture.
- option_b: Save their strength.

## Chinese Text
- title: 黄昏的私人讲课
- description: 议厅渐渐散去时，首席科学家提议在烛火燃尽前召集几位关键听众。只要有人承担这个夜晚的代价，困惑仍可被转化为信念。
- option_a: 准许讲课。
- option_b: 保留他们的精力。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: A focused lecture lets the Chief Scientist convert a small number of pivotal listeners quickly, but the extra labor strains the Academy's most important advocate.
- rationale_zh: 集中的私人讲课能让首席科学家迅速说服少数关键听众，但额外投入会使学院最重要的倡导者承压。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_private_lecture_strain
  months: 12
  effects:
    Chief Scientist workload pressure: -0.05
```

### Option B
- progress_delta: -5
- rationale_en: Refusing the lecture preserves the Chief Scientist's strength and avoids a personal overcommitment, but the undecided listeners drift back toward caution.
- rationale_zh: 拒绝讲课能保存首席科学家的精力，避免个人过度投入，但未决的听众会重新滑向谨慎。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: great_scientist
  cooldown_months: 6
```

## Difference From Same Issue Events
- Unlike G01, which persuades through a public written summary, G05 relies on direct elite instruction by the Chief Scientist.
- Unlike G16, which forces the whole debate toward a decision through procedural pressure, G05 accelerates acceptance by concentrating effort on a few decisive listeners.
- Unlike G20, which keeps exhausted opponents in session after midnight, G05 is a voluntary intervention by a named scientific authority and carries a workload strain rather than general fatigue.
