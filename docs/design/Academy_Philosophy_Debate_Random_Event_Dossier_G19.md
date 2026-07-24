# G19 - Anonymous Denunciation

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Anonymous Denunciation
- description: A sealed accusation claims the debate is a plot, a vanity, or both. The handwriting is conveniently unfamiliar, and the room suddenly studies the door.
- option_a: Investigate calmly
- option_b: Seize the papers

## Chinese Text
- title: 匿名告发
- description: 一封密封的指控声称这场辩论不是阴谋，就是虚荣，或者两者兼有。字迹恰好无人认得，屋里的人忽然都开始留意门口。
- option_a: 冷静调查
- option_b: 扣押文书

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: A calm inquiry refuses to let suspicion govern the Academy, allowing the debate to continue under lawful scrutiny at the cost of royal credibility.
- rationale_zh: 冷静调查拒绝让猜疑支配学院，使辩论能够在合法审查下继续推进，但会消耗王权信誉。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -5
- type: seat_stance
  group: court_bureaucrats
  stance: neutral
  cooldown_months: 9
```

### Option B
- progress_delta: -10
- rationale_en: Seizing the papers restores visible order and rewards officials who prefer control, but the sharp intervention chills scholars and pushes the debate toward rejection.
- rationale_zh: 扣押文书能恢复可见的秩序，并奖赏偏好控制的官员，但这种强硬干预会寒了学者之心，把辩论推向拒斥。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike G02 Crowded Galleries, public disorder is only implied; the main problem is accusation and state reaction.
- Unlike G10 Student Disputation, the Academy is not managing noisy enthusiasm but deciding whether suspicion should interrupt inquiry.
- Unlike G14 Street Song, suppressing the disturbance here targets documents and witnesses, not a popular cultural echo.
