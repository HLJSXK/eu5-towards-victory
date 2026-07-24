# SR01 - Table of Observations

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Table of Observations
- description: A patient table of repeated observations is laid before the Academy, each line too ordinary to dazzle and too consistent to ignore. The old authorities remain impressive, but the numbers have begun refusing to bow.
- option_a: Trust repeated observation.
- option_b: Treat it as anomaly.

## Chinese Text
- title: 观测表
- description: 一份耐心整理的重复观测表被摆到学院面前，每一行都平淡得不足以炫目，却又一致得无法忽视。旧权威依然显赫，但这些数字已经开始拒绝低头。
- option_a: 信任重复观测。
- option_b: 将其视为异常。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Trusting the table gives the debate a reproducible foundation: the current issue no longer rests on a single brilliant claim, but on repeated evidence that cautious scholars can inspect together.
- rationale_zh: 信任观测表会让辩论获得可重复的基础：当前议题不再依靠某个耀眼的单次主张，而是依靠谨慎学者可以共同检视的反复证据。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_observation_tables
  months: 24
  effects:
    recorded observation credibility: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Calling the evidence an anomaly preserves the inherited explanation and comforts those who fear that tables will outrank commentaries, but it teaches the room that inconvenient repetition can be dismissed.
- rationale_zh: 将证据称为异常可以保存继承下来的解释，也安抚那些担心表格凌驾于注疏之上的人，但这会让会场相信，只要重复结果不合心意，也可以被抛开。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike SR02 Failed Replication, SR01 is about repeated observations converging against old doctrine rather than a famous result collapsing under a second trial.
- Unlike SR03 Mathematical Proof, this event advances the Scientific Revolution through empirical regularity instead of symbolic demonstration.
- Unlike SR12 Old Master Contradicted, SR01 does not hinge on challenging a named authority in text; its pressure comes from a quiet accumulation of comparable records.
