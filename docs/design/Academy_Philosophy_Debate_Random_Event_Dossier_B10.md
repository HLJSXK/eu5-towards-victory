# B10 - Clerical Credit Chest

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clerical Credit Chest
- description: Monasteries and church offices open their records just far enough to reveal a web of loans, pledges, and quiet exemptions. The debate discovers that sacred hands can also count interest.
- option_a: Bring them under law.
- option_b: Exempt religious credit.

## Chinese Text
- title: 教会信贷箱
- description: 修道院和教会机构把记录打开到刚好足以露出贷款、抵押和沉默豁免的网络。辩论由此发现，神圣之手同样会计算利息。
- option_a: 将其纳入法律。
- option_b: 豁免宗教信贷。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Bringing clerical credit under law extends banking reform beyond merchants and royal offices, proving that no lender can claim sanctity as a permanent exemption.
- rationale_zh: 将教会信贷纳入法律，会把银行改革扩展到商人和王室机构之外，证明没有放贷者能永远以神圣名义获得豁免。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.04
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Exempting religious credit keeps clergy satisfied and avoids a doctrinal quarrel, but it leaves a large lending network outside the very standards the debate claims to need.
- rationale_zh: 豁免宗教信贷可以维持神职阶层满意，并避免教义争执；但这也会让一个庞大的借贷网络留在辩论所主张的标准之外。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: religious_reformers
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B03 Sermon on Usury, B10 is not clergy criticizing interest from the pulpit; it reveals clergy as participants in credit markets.
- Unlike B04 Public Bank Proposal, B10 deals with exemptions inside existing religious lending networks rather than chartering a new public institution.
- Unlike B12 Tax Farm Accounts, B10 tests whether sacred corporate privilege can be audited, not whether fiscal contractors can keep profiting from opacity.
