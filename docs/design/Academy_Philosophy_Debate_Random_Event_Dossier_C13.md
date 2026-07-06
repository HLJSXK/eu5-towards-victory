# C13 - Marriage Court

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Marriage Court
- description: Jurists propose marriage courts recognized by the state and ruled by confessional law. What families once carried to familiar clergy may soon arrive with seals, clerks, and precedent.
- option_a: Establish the courts.
- option_b: Leave marriage to existing clergy courts.

## Chinese Text
- title: 婚姻法庭
- description: 法学家提议设立由国家承认、依宗派法律裁决的婚姻法庭。过去家庭交给熟悉教士处理的事情，或许很快就要带着印章、书记员和判例而来。
- option_a: 设立这些法庭。
- option_b: 仍由现有教会法庭处理婚姻。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Establishing marriage courts gives confession a daily legal jurisdiction over households, strongly advancing acceptance while empowering bureaucratic interpreters of doctrine.
- rationale_zh: 设立婚姻法庭会让宗派教义获得支配日常家庭关系的法律管辖权，强力推动接纳，同时也增强官僚对教义的解释权。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.04
```

### Option B
- progress_delta: -10
- rationale_en: Keeping marriage in existing clergy courts protects old jurisdiction and wins clerical approval, but it denies the confessional state a powerful household-level institution.
- rationale_zh: 继续由现有教会法庭处理婚姻能保护旧有管辖权并赢得教士支持，但也会让宗派国家失去一个深入家庭层面的有力制度。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.06
- type: temporary_country_modifier
  key: tv_academy_debate_clergy_marriage_jurisdiction
  months: 18
  effects:
    clerical marriage court authority: 0.03
```

## Difference From Same Issue Events
- Unlike C02, which makes family facts legible through parish registers, C13 decides who judges marriage disputes under confessional law.
- Unlike C17, which is about clergy privilege versus discipline as a corporate struggle, C13 moves a specific legal jurisdiction between clerical courts and state-backed courts.
- Unlike C06, which asks whether minorities receive protection, C13 concerns household status and marriage authority inside the dominant confessional framework.
