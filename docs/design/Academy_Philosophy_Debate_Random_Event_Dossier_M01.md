# M01 - Anonymous Examination

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Anonymous Examination
- description: The examiners propose removing names from the papers before judgement. Birth complains that ink has become blind.
- option_a: Adopt anonymous scoring.
- option_b: Keep names visible.

## Chinese Text
- title: 匿名考试
- description: 考官提议在评判之前抹去试卷上的姓名。门第抱怨说，墨水竟然也学会了装瞎。
- option_a: 采用匿名评分。
- option_b: 保留姓名可见。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Anonymous scoring makes the debate's central claim practical: offices can be judged by demonstrated ability rather than family recognition. Nobles lose comfort because their names no longer do quiet work in the margins.
- rationale_zh: 匿名评分把这场辩论的核心主张变成了具体制度：官职可以按表现而不是按家名来评判。贵族之所以不满，是因为他们的姓氏不能再在页边悄悄发挥作用。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.04
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping names visible preserves the old social signals inside the examination process, slowing the meritocratic argument while reassuring noble families that rank still has an authorized voice.
- rationale_zh: 保留姓名让旧有的社会信号继续留在考试流程里，削弱任才主张的推进，同时安抚贵族家族，让他们相信等级仍有被认可的发言权。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike M11 Examination Fraud, this is a preventive rule about blind judgement rather than a scandal cleanup after corruption is exposed.
- Unlike M12 Public Ranking List, this concerns what examiners see during scoring, not whether families and factions see the final rankings.
- Unlike M20 Oath of the Examiners, pressure falls on noble privilege itself rather than on protecting officials from retaliation after results are published.
