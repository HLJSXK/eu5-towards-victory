# C07 - Army Oath

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Army Oath
- description: Officers warn that soldiers who pray in different parishes still stand in the same line of battle. They want one oath strong enough to bind the camp before local custom pulls it apart.
- option_a: Issue the oath.
- option_b: Keep old oaths.

## Chinese Text
- title: 军中誓词
- description: 军官们警告说，士兵即使在不同堂区祈祷，也终究站在同一条战线上。他们要求一份共同誓词，在地方习俗把军营分开之前先把军队系紧。
- option_a: 颁布共同誓词。
- option_b: 保留旧有誓词。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: A common oath turns confession into a shared military discipline, giving the new settlement practical force beyond pulpits and court language.
- rationale_zh: 共同誓词把信纲转化为共享的军事纪律，使新秩序不再只停留在讲坛和宫廷文辞之中，而具有实际约束力。
- effect_blocks:
```yaml
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_common_army_oath
  months: 18
  effects:
    confessional army cohesion: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping older oaths avoids forcing provincial estates and local commanders into a single formula, but it weakens the claim that confession can organize the realm as one body.
- rationale_zh: 保留旧誓词可以避免把省份等级和地方军官强行纳入同一套公式，却也削弱了信纲能够把王国组织成一个整体的说服力。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike C03 Sermon Licensing, C07 treats confession as a bond of command and service rather than a rule for who may preach.
- Unlike C10 Feast Day Reform, C07 acts inside the army and its oath culture, not through the public calendar of villages and parishes.
- Unlike C15 Border Preachers, C07 is domestic military integration rather than cross-border religious activism with diplomatic risk.
