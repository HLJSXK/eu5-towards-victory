# B06 - Widow's Deposit

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Widow's Deposit
- description: A widow comes before the Academy with a receipt, a lost dowry, and a voice too steady to dismiss. What had sounded like an argument over banking rules now has a face in the hall.
- option_a: Regulate deposits.
- option_b: Treat it as private misfortune.

## Chinese Text
- title: 寡妇的存款
- description: 一名寡妇带着收据、失去的嫁资和不容轻慢的平静声音来到学院。原本抽象的银行规则之争，忽然在大厅里有了人的面孔。
- option_a: 监管存款。
- option_b: 视为私人不幸。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Regulating deposits turns the banking debate toward public trust and ordinary depositors, making reform easier to defend even while commercial bankers accept closer oversight.
- rationale_zh: 监管存款会把银行制度之争转向公共信任和普通存户，使改革更容易被辩护，即使商业银行家必须接受更严密的监督。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.02
```

### Option B
- progress_delta: -5
- rationale_en: Calling the loss a private misfortune shields bankers from new limits, but it tells undecided listeners that the proposed system protects institutions before people.
- rationale_zh: 将损失称为私人不幸，可以让银行家免于新的限制，但也会让摇摆的旁听者觉得，新制度先保护机构，而不是保护人。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike B04 Public Bank Proposal, B06 is not about founding a Crown-backed institution; it is about whether private depositors deserve enforceable protection.
- Unlike B05 Debased Coin Panic, which treats monetary trust as a market-wide fear, B06 makes trust personal through one visible victim of private banking failure.
- Unlike B14 Merchant Widow Fund, B06 concerns deposit regulation after a loss, not a burgher-led insurance pool for shared commercial risk.
