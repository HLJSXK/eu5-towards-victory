# SR03 - Mathematical Proof

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Mathematical Proof
- description: A mathematician turns the disputed natural question into symbols so spare that several officials seem personally accused by the clarity. What had sounded like philosophy now sits on the page as a chain of necessity.
- option_a: Accept mathematical method.
- option_b: Demand plain tradition.

## Chinese Text
- title: 数学证明
- description: 一名数学家把争议中的自然问题化成简洁的符号，清晰得仿佛在当面指控几位官员。原本听起来像哲学的话题，如今在纸面上成了一串不得不承认的必然。
- option_a: 接受数学方法。
- option_b: 要求沿用朴素传统。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Accepting mathematical proof lets the debate move from inherited description to demonstrable relation. It strengthens the Great Scientist's methodological authority and gives scholars a precise language for acceptance.
- rationale_zh: 接受数学证明会让辩论从继承下来的描述转向可展示的关系。它会强化首席科学家的方法权威，也给学者们一种精确的接受语言。
- effect_blocks:
```yaml
- type: scientist_attribute
  adm: 1
  dip: 0
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Demanding plain tradition does not fully defeat the new claim, but it slows acceptance by insisting that inherited language remain the only respectable way to speak about nature.
- rationale_zh: 要求沿用朴素传统并不会完全击败新主张，但它会通过坚持旧语言才是谈论自然的体面方式，放慢接受的速度。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike SR01 Table of Observations, SR03 relies on abstraction and proof rather than accumulated empirical entries.
- Unlike SR04 Instrument Maker's Claim, this event does not ask whether tools create better evidence; it asks whether symbols can govern natural explanation.
- Unlike SR07 A Prediction Comes True, SR03 persuades through internal demonstration before any public predictive success is observed.
