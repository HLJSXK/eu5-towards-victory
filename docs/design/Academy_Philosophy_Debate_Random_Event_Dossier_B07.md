# B07 - Royal Loan Refusal

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Royal Loan Refusal
- description: An emergency loan is requested in the Crown's name, and the bankers answer with silence, then conditions. The hall learns that unclear banking law can make even royal need wait at the counter.
- option_a: Clarify the law.
- option_b: Threaten the bankers.

## Chinese Text
- title: 王室贷款遭拒
- description: 王冠以紧急之名请求贷款，银行家先以沉默回应，随后才提出条件。大厅由此明白，含混的银行法甚至能让王室的急需在柜台前等待。
- option_a: 澄清法律。
- option_b: 威胁银行家。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Clarifying the law concedes that credit needs predictable rules rather than pure royal command, strongly advancing banking reform while costing the Crown some aura of unquestioned authority.
- rationale_zh: 澄清法律等于承认信用需要可预期的规则，而不能只靠王命推动；这会大幅推进银行改革，同时削弱王权不容置疑的光环。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -5
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Threatening the bankers preserves the image that royal authority cannot be bargained with, but it turns the debate away from durable credit law and toward coercion.
- rationale_zh: 威胁银行家可以维护王权不可讨价还价的形象，却会把辩论从持久的信用法律转向强制手段。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.04
```

## Difference From Same Issue Events
- Unlike B04 Public Bank Proposal, B07 starts from a credit crisis imposed on the Crown rather than from a planned charter offered by burghers.
- Unlike B12 Tax Farm Accounts, B07 is about legal clarity for lending power, not auditing revenue contractors who profit from opaque collection.
- Unlike B17 Army Pay Delay, the pressure comes before soldiers are unpaid; the immediate question is whether bankers can force legal reform by refusing the Crown.
