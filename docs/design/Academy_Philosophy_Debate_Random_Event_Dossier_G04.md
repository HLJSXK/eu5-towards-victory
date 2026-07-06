# G04 - Margins of the Old Book

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Margins of the Old Book
- description: An old commentary emerges from the Academy library with a note in the margin sharp enough to cut both sides. By noon, everyone claims the dead commentator as an ally.
- option_a: Treat the old note as evidence.
- option_b: Challenge the authority of the note.

## Chinese Text
- title: 旧书页边的批注
- description: 学院图书馆里翻出一部旧注释，页边的批注锋利得足以被双方同时当作武器。到正午时，所有人都声称那位已故注释者站在自己一边。
- option_a: 将旧批注视为证据。
- option_b: 质疑批注的权威。

## Mechanics
### Option A
- progress_delta: -5
- rationale_en: Treating the marginal note as evidence privileges inherited authority and reassures religious conservatives who prefer the debate to remain bound by older readings.
- rationale_zh: 将页边批注视为证据，会抬高继承权威，并安抚希望辩论受旧解释约束的宗教保守派。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

### Option B
- progress_delta: +5
- rationale_en: Challenging the note tells scholars that old annotations may be studied without being obeyed, strengthening confidence in fresh interpretation.
- rationale_zh: 质疑批注等于宣布旧注可以被研究，却不必被服从，从而增强学者对新解释的信心。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike G03, the disputed text in G04 is not useful because it is dubious; it is powerful because it is old and socially authoritative.
- Unlike G07, which asks for moral framing by living religious figures, G04 lets inherited commentary pressure the debate through precedent.
- Unlike G17, which turns on competing translations of a key term, G04 turns on whether an old marginal authority deserves weight at all.
