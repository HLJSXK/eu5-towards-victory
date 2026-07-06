# M16 - Veterans' Service Rolls

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Veterans' Service Rolls
- description: Veterans ask whether years of disciplined service count as merit or merely scars.
- option_a: Count service in appointments.
- option_b: Keep civil posts separate.

## Chinese Text
- title: 老兵服役名册
- description: 老兵们问，多年严整服役究竟算不算才干，还是只算一身旧伤。
- option_a: 将服役年限计入任官考量。
- option_b: 保持文职任命独立。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Counting disciplined service broadens merit beyond classroom examinations without abandoning evidence. The professional military approves because long service becomes a legible qualification rather than a sentimental appeal.
- rationale_zh: 将严整服役计入考量，会把才能的范围从课堂考试扩展到可验证的军旅履历，而不是单纯诉诸同情。职业军人会支持此举，因为长期服役终于成为可读的资格，而不只是旧日功劳。
- effect_blocks:
```yaml
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_service_rolls
  months: 18
  effects:
    "veteran appointment review": 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping civil posts separate preserves the bureaucratic claim that offices should be filled through paperwork, schooling, and court procedure. It slows the meritocratic case by declaring one proven form of service irrelevant.
- rationale_zh: 保持文职任命独立，会维护官僚体系的主张：职位应由文书、学业和宫廷程序决定。它通过宣布一种已被证明的服务经验无关紧要，削弱任人唯才的推进。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_civil_posts_separate
  months: 18
  effects:
    "civil appointment regularity": 0.02
```

## Difference From Same Issue Events
- Unlike M05 Merit on the Battlefield, this event values long disciplined service records rather than dramatic command earned under fire.
- Unlike M08 Guild Tests, the practical proof comes from state service and military rolls, not urban guild examinations for technical professions.
- Unlike M17 The Crown's Favorite Fails, this is about adding a recognized qualification path before appointments, not judging a single favored candidate after a failed trial.
