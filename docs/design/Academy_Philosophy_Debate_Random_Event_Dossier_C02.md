# C02 - Parish Registers

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Parish Registers
- description: Reformers place parish registers before the Academy and argue that belief, marriage, and birth cannot guide policy until the state can read them in a steady hand.
- option_a: Require registers.
- option_b: Leave records local.

## Chinese Text
- title: 堂区登记簿
- description: 改革者把堂区登记簿推到学院面前，声称信仰、婚姻与出生若不能被国家稳定读懂，就无法真正成为政策的依据。
- option_a: 强制使用堂区登记簿。
- option_b: 让记录留在地方。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Required registers turn confession into legible administration, so bureaucrats can treat doctrine as a governing system even as local clergy resent being measured by state forms.
- rationale_zh: 强制登记会把信仰告白转化为可读的行政资料，使官僚能够把教义视作治理体系来执行，即便地方教士会反感自己被国家表格衡量。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
```

### Option B
- progress_delta: -5
- rationale_en: Leaving records local preserves parish discretion and avoids a fight over oversight, but it also keeps confession from becoming a realm-wide administrative standard.
- rationale_zh: 让记录留在地方可以保留堂区自主权，避免围绕监督权爆发冲突，但也会阻止信仰告白成为全国通行的行政标准。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike C01 Confession of the Court, C02 moves below the palace and asks whether ordinary parish life becomes readable to the state.
- Unlike C03 Sermon Licensing, C02 regulates written life-cycle records rather than the spoken authority of preachers.
- Unlike C19 Confessional Census, C02 builds continuous parish-level recordkeeping, while C19 is a broader count of communities by confession.
