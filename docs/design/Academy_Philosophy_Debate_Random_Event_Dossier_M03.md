# M03 - The Provincial Prodigy

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Provincial Prodigy
- description: A candidate from a distant province solves a problem that court favorites have avoided for weeks.
- option_a: Invite them to court.
- option_b: Praise them from afar.

## Chinese Text
- title: 外省神童
- description: 一名远方省份来的候选人解决了宫廷宠臣们拖延数周的问题。
- option_a: 邀其入朝。
- option_b: 遥致嘉奖。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Bringing the provincial candidate to court turns meritocracy from a theory into a visible promotion path. Local elites resent the disruption because talent can now bypass their patronage channels.
- rationale_zh: 把这名外省候选人带入宫廷，使任才不再只是理论，而成为一条可见的晋升路径。地方精英会反感这种扰动，因为人才可能绕过他们的庇护渠道。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_provincial_disruption
  months: 24
  effects:
    "provincial elite resentment": -0.02
```

### Option B
- progress_delta: -5
- rationale_en: Praising the prodigy from a distance lets the court applaud ability without letting it disturb appointments. Order is preserved, but the debate learns that talent may still be kept politely outside the door.
- rationale_zh: 遥致嘉奖让宫廷可以赞美才能，却不必让才能扰动任命秩序。秩序得以维持，但辩论也看见人才仍可能被礼貌地挡在门外。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_court_order_preserved
  months: 18
  effects:
    "court routine confidence": 0.02
```

## Difference From Same Issue Events
- Unlike M09 A Peasant's Petition, this candidate has already solved a concrete problem; the event is about whether proven ability can cross the provincial-center divide.
- Unlike M19 A School Outside the Capital, the challenge comes from one exceptional person rather than from recognizing a provincial institution.
- Unlike M17 The Crown's Favorite Fails, the drama is an outsider's success, not a court favorite's public humiliation.
