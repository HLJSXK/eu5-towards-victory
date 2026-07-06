# MF02 - Guild Master's Complaint

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Guild Master's Complaint
- description: Guild masters arrive with samples of warped cloth, brittle tools, and finishing so hurried it feels like an accusation. They warn that scale can multiply errors as efficiently as it multiplies goods.
- option_a: Enforce quality standards in manufactories.
- option_b: Preserve guild inspection.

## Chinese Text
- title: 行会师傅的控诉
- description: 行会师傅带来变形的布匹、易碎的器具和仓促到近乎指控的收尾活。他们警告说，规模既能成倍增加货物，也能同样高效地成倍放大错误。
- option_a: 在制造工场执行质量标准。
- option_b: 保留行会检验。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Quality rules answer the strongest guild criticism without abandoning manufactories. The advance is moderate because regulation makes the model more credible, but the Crown must pay for inspectors, measures, and enforcement.
- rationale_zh: 质量规则回应了行会最有力的批评，同时不放弃制造工场。推进幅度适中，因为监管让新模式更可信，但王权必须为检验员、量具和执行成本付账。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Preserving guild inspection grants older masters the authority to judge scale from inside their own standards. That reassures urban craft interests, but it slows acceptance by making manufactories answer to the institutions they threaten.
- rationale_zh: 保留行会检验，就是让旧师傅继续用自己的标准裁断规模生产。这能安抚城市手工业利益，却会让制造工场服从其所威胁的旧制度，从而减缓接受。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike MF01 Workshop Under One Roof, MF02 does not dispute centralized labor itself; it disputes whether scale can be trusted to maintain quality.
- Unlike MF06 Fire in the Yard, MF02 is a routine standards argument rather than a safety crisis after visible damage.
- Unlike MF18 Quality Scandal, this event is preventive and procedural, not a response to a failed batch that has already embarrassed reformers.
