# B04 - Public Bank Proposal

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Public Bank Proposal
- description: City burghers draft a public bank backed by Crown promise. The plan offers stability on paper and then invites everyone to ask what the promise itself is worth.
- option_a: Charter the bank.
- option_b: Delay the charter.

## Chinese Text
- title: 公共银行提案
- description: 城市市民起草了一份由王室承诺担保的公共银行方案。纸面上它能带来稳定，却也立刻让所有人追问：这个承诺本身究竟值多少。
- option_a: 特许成立银行。
- option_b: 推迟特许状。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Chartering the bank turns the debate from theory into public credit, giving reformers a flagship institution while putting the Crown's credibility visibly at stake.
- rationale_zh: 特许成立银行会把辩论从理论推向公共信用，为改革者提供一个标志性制度，同时也把王室信誉明明白白地押上台面。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -5
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Delay reassures conservative officials that the Crown will not guarantee a fragile experiment too quickly, but hesitation makes banking reform look premature.
- rationale_zh: 推迟会让保守官员放心，认为王室不会过快担保一项脆弱的试验；但这种犹豫也会让银行改革显得尚未成熟。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike B07 Royal Loan Refusal, B04 is not triggered by bankers forcing legal clarity during an emergency; it is a proactive institutional charter.
- Unlike B14 Merchant Widow Fund, B04 creates a Crown-backed public bank rather than recognizing private pooled insurance for commercial families.
- Unlike B20 Crown Account Published, B04 risks legitimacy through a new guarantee instead of through transparent publication of royal accounts.
