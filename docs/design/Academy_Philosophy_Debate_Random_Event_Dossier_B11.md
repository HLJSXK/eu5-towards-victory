# B11 - City Bank Riot

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: City Bank Riot
- description: Debtors and creditors clash outside a city bank, each side waving contracts like injuries and calling the other side robbery with better handwriting. The Academy cannot pretend that banking reform is only an argument among ledgers.
- option_a: Mediate with new rules.
- option_b: Close the bank temporarily.

## Chinese Text
- title: 城市银行骚乱
- description: 债务人与债权人在城市银行门前冲突，双方都把契约挥得像伤口，并指责对方只是字迹更工整的抢劫。学院再也不能假装银行改革只是账簿之间的争论。
- option_a: 以新规则调停。
- option_b: 暂时关闭银行。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Mediation accepts that credit disputes need public rules rather than private force. It costs stability because the Crown must step into a street crisis before those rules have earned trust.
- rationale_zh: 调停意味着承认信贷纠纷需要公共规则，而不是私人暴力。它会消耗稳定，因为王权必须在这些规则取得信任之前介入街头危机。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: -1
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Closing the bank restores visible order, but it teaches the room that banking institutions are too dangerous to reform in public and pushes the debate toward rejection.
- rationale_zh: 关闭银行可以恢复表面秩序，但它也让会场相信银行机构过于危险，不能公开改革，从而把辩论推向否定。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike B05 Debased Coin Panic, which turns on monetary trust in the coinage itself, B11 is about violence around private credit and the state's willingness to arbitrate it.
- Unlike B06 Widow's Deposit, where one victim humanizes deposit regulation, B11 makes the conflict collective, public, and urgent enough to cost stability.
- Unlike B18 Contract in Plain Language, which focuses on readable financial forms, B11 tests whether contracts can be enforced peacefully when both sides already understand their grievance.
