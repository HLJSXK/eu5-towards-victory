# R10 - Women's Learning Salon

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Women's Learning Salon
- description: A salon of learned women circulates essays that make the Academy look smaller than it claims. Their arguments arrive polished, unattributed to any chair, and inconveniently difficult to dismiss.
- option_a: Welcome the essays.
- option_b: Dismiss the salon.

## Chinese Text
- title: 女性学识沙龙
- description: 一场由博学女性主持的沙龙开始传阅文章，使学会显得没有自己宣称的那样广大。她们的论证优雅、并不依附任何讲席，而且麻烦地难以驳倒。
- option_a: 欢迎这些文章。
- option_b: 轻视这场沙龙。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Welcoming the essays strongly advances acceptance because the Academy admits Renaissance learning can flourish beyond its familiar male and official channels, even as conservative estates object.
- rationale_zh: 欢迎这些文章会显著推动接受，因为学会承认文艺复兴式学问能够在熟悉的男性与官方渠道之外生长，尽管保守阶层会提出反对。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Dismissing the salon restores courtly and conservative comfort, but it teaches the room that accepted learning must remain socially narrow and officially credentialed.
- rationale_zh: 轻视沙龙可以恢复宫廷与保守派的舒适感，却也等于告诉辩论厅：被承认的学问必须继续保持狭窄的社会边界和官方资格。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike R05 The Humanist Tutor, R10 centers learned women writing from a salon outside formal court instruction rather than a tutor advising rulers through history.
- Unlike R14 Poets at the Debate, the challenge is not catchy public verse but polished essays that expose the Academy's social limits.
- Unlike R20 Satire of the Old Masters, the salon's force is serious scholarly inclusion rather than mockery of old authorities.
