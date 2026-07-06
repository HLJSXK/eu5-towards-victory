# MF12 - Factory Accounts

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Factory Accounts
- description: Accountants lay out waste, delay, spoilage, and idle time in columns so tidy they feel accusatory. What once hid inside dust and habit now becomes a public question of management, discipline, and responsibility.
- option_a: Use the accounts.
- option_b: Avoid intrusive accounting.

## Chinese Text
- title: 工厂账册
- description: 会计们把废料、迟误、损耗和闲置时间列成整齐得近乎控诉的栏目。曾经藏在尘土和习惯里的东西，如今变成了关于管理、纪律与责任的公共问题。
- option_a: 使用这些账册。
- option_b: 避免侵入式核算。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Using the accounts makes large-scale production governable and gives bureaucrats a practical reason to support manufactories. The gain is modest because visibility creates friction as well as reform.
- rationale_zh: 使用账册会让大规模生产变得可治理，也给官僚一个支持工场的实际理由。进展幅度较小，因为透明度带来改革的同时也会制造摩擦。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Avoiding intrusive accounting protects workshop owners from official scrutiny and keeps production knowledge private. The debate loses ground because manufactories look less like a disciplined institution and more like enlarged private interest.
- rationale_zh: 避免侵入式核算能保护工场主免受官府审视，也让生产知识继续留在私人手中。辩论因此退步，因为工场看起来不再像有纪律的制度，而像被放大的私人利益。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike MF05 Raw Material Bottleneck, which concerns supply contracts outside the workshop, MF12 examines the internal records that make waste and delay visible.
- Unlike MF02 Guild Master's Complaint, which answers quality concerns with standards, MF12 answers production concerns with accounting oversight.
- Unlike MF18 Quality Scandal, which reacts to a failed batch, MF12 creates routine visibility before failure turns into public scandal.
