# NW07 - Missing Expedition

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Missing Expedition
- description: An expedition fails to return, and the empty harbor argues with better timing than any lecturer. Opponents call the silence evidence; supporters answer that the unknown was never going to surrender politely.
- option_a: Continue the program.
- option_b: Suspend voyages.

## Chinese Text
- title: 失踪的远征队
- description: 一支远征队迟迟未归，空荡的港口比任何讲师都更会挑时候发言。反对者把沉默称作证据，支持者则回答说，未知从来不会礼貌地投降。
- option_a: 继续航海计划。
- option_b: 暂停远航。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Continuing despite a missing expedition is a dramatic commitment to the discovery thesis. It pushes acceptance hard, but the Crown spends prestige by appearing willing to risk honor and lives before the proof is complete.
- rationale_zh: 在远征队失踪后仍继续计划，是对发现论点的强烈承诺。它会大幅推动接受，但王权也会消耗声望，因为这显得愿意在证据未全之前冒着荣誉与人命的风险。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Suspending voyages lets the loss define policy. Families, clergy, and cautious observers feel heard, while the debate retreats sharply from accepting oceanic discovery as a governing principle.
- rationale_zh: 暂停远航等于让这次损失来定义政策。家属、神职人员与谨慎的旁观者会觉得自己的担忧被听见，但辩论也会明显远离把远洋发现作为治国原则。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW06 Disease Report, NW07 is not a forecasted danger but a visible absence that turns grief and uncertainty into political pressure.
- Unlike NW19 Port Investors Panic, this event risks prestige and public courage more than commercial confidence or expedition finance.
- Unlike NW14 Sailors' Superstitions, resistance comes from a failed return and anxious families rather than from sailors demanding that omens be answered.
