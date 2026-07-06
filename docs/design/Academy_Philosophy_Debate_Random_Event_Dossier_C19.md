# C19 - Confessional Census

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Confessional Census
- description: Bureaucrats ask to count communities by confession, promising that columns are calmer than rumors. Minority elders notice that a column can become a target as easily as a tool.
- option_a: Count them.
- option_b: Refuse the count.

## Chinese Text
- title: 宗派户籍清查
- description: 官僚请求按宗派统计各地社群，保证表格总比传闻冷静。少数社群的长老却明白，一栏数字既可以是工具，也很容易变成目标。
- option_a: 将他们统计入册。
- option_b: 拒绝这次清查。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Counting communities gives the confessional state the knowledge it needs to govern doctrine locally, strongly advancing acceptance while making minorities fear that visibility will become vulnerability.
- rationale_zh: 统计各社群会让宗派国家获得在地方治理教义所需的知识，强力推动接纳；但少数群体会担心，被看见也意味着更容易受伤害。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: dhimmi_estate
  value: -0.03
- type: seat_stance
  group: minorities
  stance: oppose
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Refusing the count preserves local peace and reassures vulnerable communities, but it keeps the confessional program half-blind outside the Academy chamber.
- rationale_zh: 拒绝清查可以维持地方和平，并安抚脆弱社群；但这也让宗派纲领在学院之外依旧半盲。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: dhimmi_estate
  value: 0.03
- type: resource
  resource: stability
  amount: 1
```

## Difference From Same Issue Events
- Unlike C02 Parish Registers, C19 classifies communities by confession at the group level rather than recording births, marriages, and belief through parish administration.
- Unlike C06 Minority Petition, C19 makes minorities the object of state measurement instead of asking whether they receive legal protection.
- Unlike C16 Confession Tax, C19 spends administrative attention rather than extracting money for schools.
