# M18 - Clean Ink, Dirty Hands

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clean Ink, Dirty Hands
- description: Investigators find that the cleanest exam papers came from the dirtiest patronage network.
- option_a: Publicly void them.
- option_b: Bury the investigation.

## Chinese Text
- title: 清白墨迹，肮脏之手
- description: 调查者发现，卷面最干净的试卷，竟来自最肮脏的庇护网络。
- option_a: 公开作废这些试卷。
- option_b: 掩埋这场调查。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publicly voiding the papers makes corruption visible and treats clean presentation as worthless without clean process. Prestige is spent because the Academy must admit that its own examination table was compromised.
- rationale_zh: 公开作废这些试卷，会让腐败暴露在众人面前，并声明没有清白流程，卷面整洁毫无价值。学院必须承认自己的考场已被渗透，因此要付出威望代价。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Burying the investigation protects patrons from scandal and lets noble households treat the exam as another channel of influence. The debate retreats because merit is allowed to wear borrowed handwriting.
- rationale_zh: 掩埋调查会保护庇护者免于丑闻，也让贵族家族继续把考试当成影响力渠道。辩论因此倒退，因为所谓才能被允许披上借来的笔迹。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
- type: temporary_country_modifier
  key: tv_academy_debate_patronage_buried
  months: 24
  effects:
    "patronage network confidence": 0.02
```

## Difference From Same Issue Events
- Unlike M11 Examination Fraud, this event focuses on a patronage network behind apparently excellent papers rather than a leaked answer key.
- Unlike M04 Purchased Office, the corruption hides inside examination success instead of openly selling an office to a donor's son.
- Unlike M01 Anonymous Examination, this is a reactive purge after corruption is found, not a preventive rule for blind scoring.
