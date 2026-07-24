# G07 - A Moral Preface

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Moral Preface
- description: Religious figures ask that the disputed proposition be wrapped in moral caution before anyone dares to call it wisdom.
- option_a: Add the preface
- option_b: Refuse the preface

## Chinese Text
- title: 道德序言
- description: 宗教人士要求在任何人敢称这项争议主张为智慧之前，先为它包上一层道德上的谨慎说明。
- option_a: 加上序言
- option_b: 拒绝序言

## Mechanics
### Option A
- progress_delta: -5
- rationale_en: A moral preface reassures the clergy and frames the issue as something dangerous enough to require restraint, nudging the debate away from acceptance.
- rationale_zh: 道德序言能安抚教士，并把该议题描绘成必须加以约束的危险之物，从而使辩论偏离接受方向。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
```

### Option B
- progress_delta: +5
- rationale_en: Refusing the preface lets the Academy treat the proposition on its own intellectual merits, but clergy satisfaction falls as caution is set aside.
- rationale_zh: 拒绝序言使学院能按主张本身的学理价值来讨论它，但这种搁置谨慎的做法会降低教士满意度。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.04
```

## Difference From Same Issue Events
- Unlike G04, which uses an old commentary as evidence, this event concerns moral framing before the argument is heard.
- Unlike G17 and G18, the clergy reaction is not tied to translation or art; it is a direct dispute over whether caution should govern the debate's opening language.
