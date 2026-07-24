# B09 - Fraudulent Ledger

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Fraudulent Ledger
- description: The ledger is elegant, balanced, and false. Its columns possess the calm beauty of order, which makes the theft behind them feel like an insult to arithmetic itself.
- option_a: Use it to demand standards.
- option_b: Punish only the clerk.

## Chinese Text
- title: 欺诈账簿
- description: 这本账簿优雅、平衡，并且虚假。它的栏目有着秩序的冷静美感，也因此让藏在其中的盗窃显得像是对算术本身的侮辱。
- option_a: 借此要求标准。
- option_b: 只惩罚书记员。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Using the fraudulent ledger as evidence turns scandal into a demand for enforceable standards, but exposing a beautiful crime costs prestige because the Academy admits how easily order can be forged.
- rationale_zh: 将欺诈账簿作为证据，会把丑闻转化为对可执行标准的要求；但揭开这场漂亮的犯罪也会损耗声望，因为学院承认秩序原来如此容易被伪造。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Punishing only the clerk contains the scandal and protects elite patrons from scrutiny, but it teaches the debate that banking rules will be enforced only where power is weakest.
- rationale_zh: 只惩罚书记员可以压住丑闻，并保护上层赞助人免受追查；但这会让辩论意识到，银行规则只会在权力最弱处得到执行。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike B01 Double-Entry Demonstration, B09 shows a ledger failing through deliberate fraud rather than succeeding as a clean instructional proof.
- Unlike B02 Noble Debt Roll, B09 is not about revealing elite indebtedness; it is about whether one exposed accounting crime justifies system-wide standards.
- Unlike B16 Mint Officer's Confession, B09 centers on documentary manipulation in private accounts rather than an official admission that the monetary system tolerates confusion.
