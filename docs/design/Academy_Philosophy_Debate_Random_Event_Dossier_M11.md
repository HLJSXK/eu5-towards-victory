# M11 - Examination Fraud

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Examination Fraud
- description: A leaked answer key reveals that merit can be imitated by money with excellent penmanship.
- option_a: Purge the examiners.
- option_b: Quietly invalidate only the worst papers.

## Chinese Text
- title: 考试舞弊
- description: 一份泄露的答案钥匙表明，只要钱袋足够体面，所谓才干也可以被漂亮笔迹仿造出来。
- option_a: 清洗考官队伍。
- option_b: 只悄悄作废最严重的试卷。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Purging the examiners treats fraud as an institutional threat to measured ability, not merely as a few spoiled papers. The reform gains credibility, but the public disruption costs stability.
- rationale_zh: 清洗考官队伍把舞弊视为对能力考核制度的威胁，而不是几份试卷的小瑕疵。改革因此获得可信度，但公开整肃会消耗社会稳定。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: -1
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Invalidating only the worst papers contains the scandal while preserving the existing examining circle. That protects administrative calm, but it implies that fraud is tolerable when hidden well enough.
- rationale_zh: 只作废最严重的试卷可以把丑闻压在可控范围内，同时保住原有考官圈子。行政秩序得以维持，但这也暗示只要藏得足够好，舞弊仍可被容忍。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_limited_exam_scandal
  months: 12
  effects:
    "contained examination scandal": 0.02
```

## Difference From Same Issue Events
- Unlike M01 Anonymous Examination, this event happens after a corrupt examination has already failed rather than before names are hidden to prevent bias.
- Unlike M04 Purchased Office, the abuse is inside the testing apparatus, not a direct sale of office outside it.
- Unlike M18 Clean Ink, Dirty Hands, the scandal is a leaked answer key and compromised examiners rather than a wider patronage network discovered behind polished papers.
