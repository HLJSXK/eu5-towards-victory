# SR16 - Royal Observatory

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Royal Observatory
- description: Astronomers ask for a permanent observatory because the sky refuses to attend meetings indoors. A tower, instruments, and salaried watchers would turn scattered nights of argument into a standing discipline.
- option_a: Build or fund it.
- option_b: Use temporary observations.

## Chinese Text
- title: 皇家天文台
- description: 天文学家请求建立一座常设天文台，因为天空并不会按时走进室内参加会议。一座高塔、一批仪器和受薪守夜人，能把零散夜晚里的争论变成一门稳定的学问。
- option_a: 建造或资助天文台。
- option_b: 继续采用临时观测。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding a permanent observatory gives the new method an institution that can watch, compare, and return to the same question night after night. The cost is heavy, but durable observation strongly favors acceptance.
- rationale_zh: 资助常设天文台，会让新方法获得一个能够长期观察、比较并反复回到同一问题的制度场所。花费不小，但持久观测会有力推动接受当前议题。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: great_scientist
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_royal_observatory
  months: 36
  effects:
    astronomical observation infrastructure: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Relying on temporary observations keeps the treasury calm and leaves astronomers improvising with borrowed roofs and fair weather. The debate moves backward because the realm refuses to make observation a permanent public duty.
- rationale_zh: 依靠临时观测可以安抚国库，却让天文学家继续借屋顶、等晴夜、临时凑合。辩论会后退，因为国家拒绝把观测变成持久的公共职责。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike SR04 Instrument Maker's Claim, SR16 is not about whether better tools can create better evidence; it is about whether the realm will fund a permanent observational institution.
- Unlike SR10 Natural History Cabinet, SR16 looks upward through recurring astronomical measurements rather than arranging earthly specimens by observed likeness.
- Unlike SR14 Measurement Standard, SR16 does not standardize every province's measures; it concentrates royal support in one durable site of sky-watching.
