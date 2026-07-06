# M20 - Oath of the Examiners

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Oath of the Examiners
- description: Examiners ask the Crown to protect them from noble retaliation before they publish results.
- option_a: Swear protection.
- option_b: Refuse to provoke great houses.

## Chinese Text
- title: 考官之誓
- description: 考官们请求王冠在公布结果之前保护他们，免受贵族报复。
- option_a: 宣誓保护考官。
- option_b: 拒绝激怒大族。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Swearing protection makes the examination process answer upward to law and the Crown rather than sideways to noble retaliation. Meritocracy advances because examiners can publish unwelcome results without first calculating family revenge.
- rationale_zh: 宣誓保护考官，会让考试流程向法律和王冠负责，而不是向贵族报复低头。任人唯才因此大幅推进，因为考官可以公布不受欢迎的结果，不必先计算家族复仇。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Refusing protection keeps the great houses calm by leaving intimidation unchallenged. Noble approval rises, but every examiner learns that a correct result may still be too dangerous to print.
- rationale_zh: 拒绝保护会让大族保持平静，因为恐吓没有受到挑战。贵族赞许随之上升，但每位考官都会明白，即使结果正确，也可能危险到不能刊布。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.05
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 36
```

## Difference From Same Issue Events
- Unlike M12 Public Ranking List, this event occurs before publication and asks whether officials can survive releasing the list at all.
- Unlike M10 Boycott by Old Families, noble pressure appears as threatened retaliation against examiners rather than withdrawal from the Academy.
- Unlike M17 The Crown's Favorite Fails, the Crown is not judging one embarrassing candidate but deciding whether the whole examination apparatus can resist noble intimidation.
