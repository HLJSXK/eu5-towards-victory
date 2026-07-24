# GT02 - Foreign Merchant Quarter

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Foreign Merchant Quarter
- description: Foreign merchants ask for warehouses, lodging, and their own watchmen near the harbor. The request sounds practical until everyone realizes it would give distant markets a permanent address inside the realm.
- option_a: Grant the quarter.
- option_b: Refuse special rights.

## Chinese Text
- title: 外商商馆区
- description: 外国商人请求在港口附近拥有仓库、住所和自己的守卫。这个要求听起来务实，直到众人意识到，它会让遥远市场在本国境内拥有一个固定地址。
- option_a: 准许设立商馆区。
- option_b: 拒绝特殊权利。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Granting the quarter accepts that global trade needs durable institutions, protected contracts, and trusted foreign intermediaries. It advances the issue strongly, while giving foreign powers a visible channel into the debate.
- rationale_zh: 准许商馆区，等于承认全球贸易需要稳定机构、受保护的契约和可信的外国中介。这会大幅推动议题，但也让外国势力在辩论中拥有显眼入口。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: support
  cooldown_months: 24
- type: foreign_prestige
  amount: 5
```

### Option B
- progress_delta: -5
- rationale_en: Refusing special rights protects local guild custom and limits foreign influence, but it also signals that international merchants may trade only as guests, not as partners in a new order.
- rationale_zh: 拒绝特殊权利可以保护本地行会惯例并限制外国影响，却也表明国际商人只能作为客人经商，而不能成为新秩序的伙伴。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike GT01 Harbor Ledgers, GT02 is about granting a legal and physical foothold to foreign merchants, not interpreting domestic evidence of global prices.
- Unlike GT09 Rival Trade Embassy, GT02 concerns resident commercial privileges near the port rather than a diplomatic visit from a rival court.
- Unlike GT19 Free Port Proposal, GT02 is narrower than a full free-port experiment because it protects a merchant quarter without rewriting the whole customs regime.
