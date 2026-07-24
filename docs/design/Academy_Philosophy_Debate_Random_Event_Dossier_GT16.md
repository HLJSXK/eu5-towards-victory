# GT16 - Guild Monopoly Challenge

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Guild Monopoly Challenge
- description: Overseas traders lay their contracts beside the city guild charters and call the old monopolies beautiful chains. The masters bristle, but the younger merchants can already hear distant markets rattling the locks.
- option_a: Break the monopoly.
- option_b: Preserve guild privilege.

## Chinese Text
- title: 行会垄断挑战
- description: 海外贸易商把契约摆在城市行会特许状旁边，称那些旧垄断不过是精美的锁链。行会大师们怒气上涌，但年轻商人已经听见远方市场在撼动锁扣。
- option_a: 打破垄断。
- option_b: 维护行会特权。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Breaking guild monopoly makes Global Trade feel like a real restructuring of market power, not just more ships at the harbor. It advances acceptance by siding with overseas exchange against inherited urban privilege.
- rationale_zh: 打破行会垄断会让全球贸易显得是真正重组市场权力，而不只是港口多了几艘船。它通过支持海外交换、反对旧有城市特权来推动接受。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.04
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Preserving guild privilege reassures old masters that commerce will remain disciplined by local custom, but it teaches the debate that global exchange must bow before corporate rights.
- rationale_zh: 维护行会特权会安抚旧日大师，让他们相信商业仍会受本地惯例约束，但这也等于告诉辩论：全球交换必须向团体特权低头。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: seat_stance
  group: maritime_merchants
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT02 Foreign Merchant Quarter, GT16 is not about granting protected space to outsiders; it attacks domestic guild control over who may trade at all.
- Unlike GT03 Tariff Confusion, GT16 targets corporate monopoly rather than accidental fiscal complexity or official rent-seeking.
- Unlike GT10 Standard Weights, GT16 changes market access and privilege, not the neutral rules used to measure goods once trade is allowed.
