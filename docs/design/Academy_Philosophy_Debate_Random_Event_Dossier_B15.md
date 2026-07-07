# B15 - Foreign Banker Arrives

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Foreign Banker Arrives
- description: A foreign banking house offers expertise, capital, and a contract whose clauses are too neat to be innocent. Supporters see imported knowledge; opponents see the realm's purse learning a foreign accent.
- option_a: Invite them under regulation.
- option_b: Keep banking domestic.

## Chinese Text
- title: 外国银行家到来
- description: 一家外国银行行号带来专门知识、资本，以及一份条款整齐得不可能天真的契约。支持者看见输入的知识，反对者则看见王国的钱袋开始带上外国口音。
- option_a: 在监管下邀请他们。
- option_b: 保持银行业本土化。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Inviting the foreign bankers under regulation accepts outside expertise while claiming that law can domesticate it. The reform advances, but foreign influence becomes more visible inside the debate.
- rationale_zh: 在监管下邀请外国银行家，等于接受外来专长，同时宣称法律可以驯化它。改革会向前推进，但外国影响也会在辩论中变得更醒目。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: support
  cooldown_months: 18
- type: foreign_prestige
  amount: 5
```

### Option B
- progress_delta: -5
- rationale_en: Keeping banking domestic reassures nobles and protectionists that financial sovereignty remains familiar, but it narrows the debate away from regulated expertise and toward inherited suspicion.
- rationale_zh: 保持银行业本土化会安抚贵族和保护主义者，让他们相信金融主权仍掌握在熟悉之人手中，但这也会让辩论远离受监管的专长，转向继承下来的猜疑。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B07 Royal Loan Refusal, where domestic bankers use emergency leverage against the Crown, B15 centers on foreign expertise and the political cost of inviting it.
- Unlike B12 Tax Farm Accounts, which exposes internal fiscal opacity, B15 asks whether external banking methods can be accepted without surrendering control.
- Unlike B04 Public Bank Proposal, which asks whether the Crown should guarantee a domestic public bank, B15 asks whether private foreign expertise can be admitted without surrendering control.
