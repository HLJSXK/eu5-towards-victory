# C17 - Clergy Split

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clergy Split
- description: Clergy who once spoke as a single estate now divide over whether the new confession should discipline them as servants of a doctrine or protect them as guardians of inherited privilege.
- option_a: Back discipline.
- option_b: Back clerical privilege.

## Chinese Text
- title: 教士分裂
- description: 曾经以同一等级发声的教士，如今争论新宗派究竟应把他们约束为教义的仆从，还是继续保护他们作为祖传特权守护者的身份。
- option_a: 支持宗派纪律。
- option_b: 支持教士特权。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Backing discipline makes the confession more than a clerical possession; it becomes a rule that can bind even churchmen, sharply advancing acceptance while angering clergy attached to corporate privilege.
- rationale_zh: 支持宗派纪律会让信纲不再只是教士阶层的财产，而成为连教士也要遵守的规则；这会强力推动接纳，却激怒依恋团体特权的教士。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
- type: temporary_country_modifier
  key: tv_academy_debate_clerical_discipline
  months: 12
  effects:
    parish oversight hardens around the new confession: 0.02
```

### Option B
- progress_delta: -10
- rationale_en: Protecting clerical privilege reassures the clergy estate that confession will not become a royal leash, but it signals that institutional comfort matters more than doctrinal discipline.
- rationale_zh: 保护教士特权会让教士等级相信，宗派信纲不会变成王权的缰绳；但这也表明制度安逸比教义纪律更重要。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 24
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.05
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike C03 Sermon Licensing, C17 is an internal estate struggle over clerical discipline, not a rule for who may preach.
- Unlike C05 Catechism Draft, C17 turns on the status of the clergy themselves rather than the wording of doctrine for lay instruction.
- Unlike C13 Marriage Court, C17 does not create a new confessional jurisdiction; it decides whether clergy privilege survives the new order.
