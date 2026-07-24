# MF19 - Merchant Capital Pool

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Merchant Capital Pool
- description: Merchants propose pooling capital large enough to build a manufactory no single family could command. The money arrives not as a purse, but as a committee with ledgers and patience.
- option_a: Legalize the pool.
- option_b: Forbid such concentration.

## Chinese Text
- title: 商人资本池
- description: 商人提议合资筹集一笔足以兴建制造工场的资本，规模大到任何单一家族都难以独自掌握。这笔钱来的时候不像一个钱袋，更像一群带着账本和耐心的委员。
- option_a: 使资本池合法化。
- option_b: 禁止这种集中。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Legalizing pooled capital gives manufactories a financial body large enough to match their physical ambition. Acceptance advances sharply because scale becomes investable, and banking-minded burghers see a path from ledger to workshop.
- rationale_zh: 使资本池合法化，为制造工场提供了足以匹配其物质野心的金融躯体。接受度会大幅推进，因为规模化从此可以被投资，而具有银行思维的市民阶层也看见了从账本通向工场的道路。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: temporary_country_modifier
  key: tv_academy_debate_merchant_capital_pool
  months: 24
  effects:
    large manufactory finance: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Forbidding pooled capital protects noble landlords and guild masters from a new kind of collective commercial power. The debate moves strongly toward rejection because large manufactories remain trapped below the scale their advocates promised.
- rationale_zh: 禁止资本池保护了贵族地主和行会师傅，使他们免受新型集体商业力量的冲击。辩论会强烈转向拒绝，因为大型制造工场仍被困在倡导者所承诺的规模之下。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike MF05 Raw Material Bottleneck, MF19 is about financing the building of scale rather than contracting for the inputs that feed it.
- Unlike MF12 Factory Accounts, this event concerns who may assemble capital before production begins, not how waste appears once production is underway.
- Unlike MF17 Workshop School, MF19 empowers manufactories through ownership and investment instead of through worker training.
