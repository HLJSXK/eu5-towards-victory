# B05 - Debased Coin Panic

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Debased Coin Panic
- description: Rumor claims the coin in every purse is thinner than the Crown's promise. Markets begin weighing trust as carefully as silver.
- option_a: Reform the coinage.
- option_b: Blame rumor-mongers.

## Chinese Text
- title: 劣币恐慌
- description: 流言声称每只钱袋里的硬币，都比王室承诺更薄。市场于是开始像称量白银一样，仔细称量信任。
- option_a: 改革铸币。
- option_b: 指责散布流言者。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Reforming the coinage pays a real fiscal cost to prove that monetary trust can be governed, giving the banking argument a visible foundation in reliable money.
- rationale_zh: 改革铸币需要付出真实的财政代价，以证明货币信任可以被治理；这会让银行制度的论证建立在可靠货币这一可见基础上。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Blaming rumor-mongers preserves immediate order and avoids paying for reform, but it treats monetary distrust as disobedience rather than a banking problem to solve.
- rationale_zh: 指责散布流言者能维持眼前秩序，也能避免改革开支；但这把货币不信任视为不服从，而不是需要解决的银行制度问题。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike B16 Mint Officer's Confession, B05 starts with public panic and rumor rather than an insider admitting tolerated confusion.
- Unlike B04 Public Bank Proposal, B05 concerns the metal and credibility beneath exchange instead of a new Crown-backed banking institution.
- Unlike B01 Double-Entry Demonstration, B05 tests monetary trust in everyday markets rather than accounting standards inside ledgers.
