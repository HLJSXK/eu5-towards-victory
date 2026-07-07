# C06 - Minority Petition

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Minority Petition
- description: A minority community sends elders to the Academy with a petition folded beneath careful seals. They do not deny the realm's confession; they ask whether obedience will mean protection or only quieter exclusion.
- option_a: Define legal protection under confession.
- option_b: Avoid guarantees.

## Chinese Text
- title: 少数社群请愿
- description: 一个少数信仰社群派出长老来到学院，呈上一份封印谨慎的请愿书。他们并不否认王国的信纲，只想知道服从之后得到的是保护，还是更安静的排斥。
- option_a: 在信纲之下规定法律保护。
- option_b: 避免作出保障。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Legal protection makes confessional order look governable rather than purely exclusionary, so cautious minorities can accept the settlement as a rule they may live under.
- rationale_zh: 法律保护会让宗派秩序显得可以治理，而不只是排斥异己；谨慎的少数社群因此能把新秩序视为可以生活其中的规则。
- effect_blocks:
```yaml
- type: seat_stance
  group: minorities
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: dhimmi_estate
  value: 0.04
```

### Option B
- progress_delta: -5
- rationale_en: Refusing guarantees pleases conservative clergy who fear loopholes, but it leaves the proposed confession looking too brittle to hold a mixed realm together.
- rationale_zh: 拒绝保障会取悦担心留下漏洞的保守教士，却也让拟议中的信纲显得过于脆弱，难以维系一个多元王国。
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

## Difference From Same Issue Events
- Unlike C02 Parish Registers, C06 is not about making communities legible to the state; it is about whether a named minority receives explicit protection inside the confessional order.
- Unlike C04 Noble Chapel Dispute, C06 concerns vulnerable communal status rather than noble privilege and private elite worship.
- Unlike C19 Confessional Census, C06 does not count minorities as administrative categories; it decides whether loyalty can carry legal safeguards.
