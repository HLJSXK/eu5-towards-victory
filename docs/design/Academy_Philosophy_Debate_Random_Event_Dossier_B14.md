# B14 - Merchant Widow Fund

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Merchant Widow Fund
- description: Burghers propose a pooled fund for sailors' families, failed caravans, and the quiet disasters that follow a broken journey home. The proposal makes risk look less like fate and more like something that can be counted together.
- option_a: Recognize pooled risk.
- option_b: Reject novel liability.

## Chinese Text
- title: 商人遗孀基金
- description: 市民提议设立共同基金，照顾水手家属、失败商队，以及归途断裂后接踵而来的沉默灾难。这个提案让风险不再像命运，而更像某种可以共同计算的东西。
- option_a: 承认共同分担风险。
- option_b: 拒绝新式责任。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Recognizing pooled risk makes banking reform socially useful instead of merely profitable. Burghers gain satisfaction because their financial institutions are treated as civic protection rather than clever speculation.
- rationale_zh: 承认共同分担风险，会让银行改革显得具有社会用途，而不只是谋利手段。市民会更满意，因为他们的金融制度被视为公共保护，而不是精巧投机。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: temporary_country_modifier
  key: tv_academy_debate_pooled_risk_fund
  months: 24
  effects:
    merchant family security: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Rejecting novel liability reassures conservative lawyers that responsibility should remain attached to visible persons and old contracts, but it weakens the case for banking as organized trust.
- rationale_zh: 拒绝新式责任会安抚保守法学者，使他们相信责任仍应附着在可见个人和旧契约上，但这会削弱银行作为有组织信任的论证。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_liability_restraint
  months: 12
  effects:
    legal administration burden: -0.02
```

## Difference From Same Issue Events
- Unlike B06 Widow's Deposit, which begins from one private loss and argues for deposit regulation, B14 designs a standing pool to spread many future losses.
- Unlike B08 Bills of Exchange, which shows finance moving wealth across distance, B14 shows finance distributing risk across a community.
- Unlike B19 Bankruptcy Shame, which manages failure after a merchant is already ruined, B14 tries to pool risk before disaster becomes public insolvency.
