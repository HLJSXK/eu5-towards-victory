# NW14 - Sailors' Superstitions

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Sailors' Superstitions
- description: Sailors refuse another voyage until omens are answered, and every official explanation seems to make the signs more stubborn. The Academy must decide whether fear at sea is a problem of pay, persuasion, or providence.
- option_a: Pay and persuade them.
- option_b: Accept their fear as wisdom.

## Chinese Text
- title: 水手的迷信
- description: 水手们拒绝再次出航，除非那些征兆得到回应，而每一种官方解释似乎都让征兆变得更加顽固。学院必须判断，海上的恐惧究竟是薪酬、劝说，还是天意的问题。
- option_a: 付钱并劝服他们。
- option_b: 将他们的恐惧视为智慧。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Paying and persuading the sailors treats superstition as an obstacle to manage rather than a verdict against discovery. Acceptance rises modestly because the voyage program survives, but the Crown must spend to restore confidence.
- rationale_zh: 付钱并劝服水手，是把迷信当作需要管理的障碍，而不是反对发现的判决。由于远航计划得以继续，接受度会小幅上升；但王权必须花费资金来恢复信心。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Accepting the sailors' fear gives religious and cautious voices a language that sounds respectful rather than timid. The debate slows because omens become acceptable evidence against further discovery.
- rationale_zh: 接受水手的恐惧，会给宗教人士和谨慎派一种听起来像尊重而不是胆怯的说法。辩论会放缓，因为征兆被承认为反对继续发现的有效证据。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW06 Disease Report, NW14 answers fear through morale, omens, and religious interpretation rather than physicians and quarantine precautions.
- Unlike NW07 Missing Expedition, resistance here comes before departure from sailors who can still be persuaded, not after a lost expedition turns absence into evidence.
- Unlike NW10 Naval Officers Demand Funds, this event spends money on crew confidence rather than ship capacity or naval preparation.
