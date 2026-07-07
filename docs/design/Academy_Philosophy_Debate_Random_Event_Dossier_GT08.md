# GT08 - Dock Labor Strike

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Dock Labor Strike
- description: Dockworkers stop the cranes, ropes, carts, and shouting that make trade look effortless from a council chamber. They ask why expanding commerce should make every wage feel smaller.
- option_a: Negotiate protections.
- option_b: Break the strike.

## Chinese Text
- title: 码头劳工罢工
- description: 码头工人停下吊机、绳索、货车和叫喊声，让议事厅里看似轻松的贸易突然露出本来面目。他们追问，为何贸易扩张反而让每一份工钱都显得更少。
- option_a: 谈判劳工保护。
- option_b: 镇压罢工。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Negotiating protections shows that global trade can be accepted without pretending its labor costs are invisible. The progress gain is moderate because compromise steadies support but slows merchant enthusiasm.
- rationale_zh: 谈判劳工保护表明，接受全球贸易并不意味着假装劳工成本不存在。进度提升较小，因为妥协能稳住支持，却也会削弱商人的热情。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.04
- type: seat_stance
  group: peasants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Breaking the strike restores movement on the docks and pleases merchants, but it lets opponents describe global trade as a system that grows by silencing the workers who carry it.
- rationale_zh: 镇压罢工会让码头恢复运转，也会取悦商人；但反对者会借此把全球贸易描绘成一个靠压制搬运者来扩张的制度。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: seat_stance
  group: peasants
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT13 Export Panic, GT08 is a labor dispute over wages and protection at the port, not a food-security crisis caused by exports.
- Unlike GT16 Guild Monopoly Challenge, GT08 centers workers who move cargo rather than guild masters defending corporate privilege.
- Unlike GT04 Spice Cargo, GT08 removes the glamour from imported goods and asks who bears the physical burden of trade.
