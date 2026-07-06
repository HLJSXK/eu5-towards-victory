# C01 - Confession of the Court

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Confession of the Court
- description: Courtiers ask whether the Crown's faith should stand in public as a rule for the realm, or remain a private habit spoken through chapel attendance and careful silences.
- option_a: Make confession public policy.
- option_b: Keep court faith private.

## Chinese Text
- title: 宫廷的信仰告白
- description: 朝臣们追问，君主的信仰究竟应当公开成为统治王国的准则，还是只在礼拜出席与谨慎沉默中作为私人习惯存在。
- option_a: 将信仰告白列为公开国策。
- option_b: 让宫廷信仰留在私下。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Declaring confession as public policy makes the Crown an open patron of the confessional settlement, giving reformers a signal strong enough to move the debate toward acceptance while unsettling noble households that prefer ambiguity.
- rationale_zh: 将信仰告白列为公开国策，会让君主成为信仰定制的明确庇护者，给改革派足够强的信号推动辩论走向接受，同时也会搅动那些偏爱模糊空间的贵族家族。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Keeping court faith private prevents the royal household from becoming a confessional banner, calming clerical factions but making acceptance look premature and politically needless.
- rationale_zh: 让宫廷信仰留在私下，可以避免王室自身变成信仰旗帜，并安抚教士派系，但也会让接受该议题显得过早且没有政治必要。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: clergy
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike C02 Parish Registers, C01 is about the visible confession of the royal household rather than the administrative recording of ordinary parish life.
- Unlike C04 Noble Chapel Dispute, C01 begins at the center of court policy and only indirectly pressures noble houses, while C04 confronts a specific noble privilege.
- Unlike C20 The Crown's Formula, C01 asks whether the Crown should confess publicly at all; C20 concerns the wording of an already drafted royal formula.
