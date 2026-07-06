# NW19 - Port Investors Panic

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Port Investors Panic
- description: A storm breaks ships prepared for the next voyage, and the port's confidence cracks almost as loudly as the masts. Investors who praised discovery yesterday now study the wreckage like accountants of fear.
- option_a: Guarantee the expedition.
- option_b: Let investors retreat.

## Chinese Text
- title: 港口投资者恐慌
- description: 一场风暴摧毁了为下一次航行准备的船只，港口的信心几乎和桅杆一起断裂。昨日还称颂发现事业的投资者，如今像恐惧的账房一样盯着残骸盘算。
- option_a: 为远征提供担保。
- option_b: 允许投资者退场。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Guaranteeing the expedition turns a commercial panic into a public commitment. Acceptance surges because the Crown refuses to let weather decide the debate, but the treasury absorbs the risk that private investors no longer will.
- rationale_zh: 为远征提供担保，会把商业恐慌转化为公开承诺。由于王权拒绝让天气决定辩论走向，接受方向会迅速推进，但国库也必须承担私人投资者不愿再承担的风险。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Letting investors retreat allows the wrecked ships to become a verdict on the whole enterprise. Trade confidence falls, and the debate turns sharply away from acceptance because discovery now looks financially fragile.
- rationale_zh: 允许投资者退场，会让这些破损船只成为对整项事业的判决。贸易信心下降，而发现事业也显得财务基础脆弱，因此辩论会明显转向拒绝。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_port_credit_shock
  months: 18
  effects:
    port investment confidence: -0.03
```

## Difference From Same Issue Events
- Unlike NW07 Missing Expedition, NW19 is about commercial panic after damaged preparations, not the prestige and grief caused by a vanished crew.
- Unlike NW10 Naval Officers Demand Funds, the pressure comes from private investors and port credit rather than naval officers asking for planned state capacity.
- Unlike NW11 Rumor of Gold, NW19 tests whether financial appetite survives a visible loss instead of whether greed can be used to start voyages.
