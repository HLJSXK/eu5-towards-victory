# C10 - Feast Day Reform

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Feast Day Reform
- description: Reformers spread a revised holy calendar across the table and discover that every crossed-out feast has neighbors, guilds, and grandparents attached to it. The state can align sacred time, but not quietly.
- option_a: Reform the calendar.
- option_b: Keep local feasts.

## Chinese Text
- title: 圣日历改革
- description: 改革者把一份修订后的圣日历铺在桌上，随即发现每个被划去的节日背后都有邻里、行会和祖辈记忆。国家可以校准神圣时间，却很难悄无声息地做到。
- option_a: 改革圣日历。
- option_b: 保留地方节日。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Reforming the calendar makes confession visible in the rhythm of ordinary life, which strongly advances acceptance while provoking peasants and clergy attached to local holy days.
- rationale_zh: 改革圣日历会把信纲写进日常生活的节奏，因而大幅推动接受；但依附地方圣日的农民和教士也会被激怒。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: peasants_estate
  value: -0.04
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Keeping local feasts protects familiar parish rhythms and satisfies local communities, but it concedes that confessional order cannot yet command the calendar.
- rationale_zh: 保留地方节日保护了熟悉的堂区节奏，也让地方社群满意；但这等于承认宗派秩序尚不能支配历法。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.04
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike C07 Army Oath, C10 reshapes public sacred time rather than military discipline.
- Unlike C12 Pilgrim Riot, C10 is a planned calendar reform rather than a crisis around one volatile act of devotion.
- Unlike C16 Confession Tax, C10 burdens custom and memory rather than extracting money to fund confessional schools.
