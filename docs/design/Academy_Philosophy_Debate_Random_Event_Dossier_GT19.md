# GT19 - Free Port Proposal

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Free Port Proposal
- description: Reformers sketch a port where the Crown taxes movement instead of strangling it at every gate. Customs men call it reckless; merchants call it the first honest map of how goods already move.
- option_a: Charter the free port.
- option_b: Reject the experiment.

## Chinese Text
- title: 自由港提案
- description: 改革者描绘了一座港口：王室不再在每道关卡勒紧货流，而是向流动本身征税。海关官员称其鲁莽，商人则说这才是货物流动的第一张诚实地图。
- option_a: 特许自由港。
- option_b: 拒绝这场试验。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Chartering a free port makes the state an organizer of global movement rather than a collector of inherited chokepoints. It strongly advances acceptance while angering protectionists who depend on old barriers.
- rationale_zh: 特许自由港会让国家成为全球流动的组织者，而不只是旧瓶颈的收费人。它会强力推动接受，同时激怒依赖旧壁垒的保护主义者。
- effect_blocks:
```yaml
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Rejecting the experiment keeps customs houses predictable and protects officials who know every gate, but it frames Global Trade as a danger to be contained rather than a flow to be governed.
- rationale_zh: 拒绝这场试验能保持海关体系的可预期性，也保护熟悉每道关卡的官员，但它会把全球贸易塑造成需要围堵的危险，而不是需要治理的流动。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_customs_house_routine
  months: 18
  effects:
    customs routine preserved: 0.02
```

## Difference From Same Issue Events
- Unlike GT02 Foreign Merchant Quarter, GT19 changes the operating rules of an entire port rather than granting a protected neighborhood to foreign traders.
- Unlike GT03 Tariff Confusion, GT19 proposes an institutional experiment instead of merely simplifying mistaken tariff schedules.
- Unlike GT14 Port Quarantine, GT19 loosens commercial friction for revenue design, while quarantine debates restrict ships for public safety.
