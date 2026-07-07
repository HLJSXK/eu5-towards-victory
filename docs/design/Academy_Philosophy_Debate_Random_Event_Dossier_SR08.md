# SR08 - Laboratory Accident

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Laboratory Accident
- description: A demonstration explodes with enough force to settle the question of whether experiment has energy. Smoke drifts through the hall while both sides claim the wreckage as evidence.
- option_a: Improve safety and continue.
- option_b: Suspend experiments.

## Chinese Text
- title: 实验室事故
- description: 一场演示轰然炸裂，至少证明了实验确实充满力量。烟雾飘过大厅时，双方都把残骸说成对自己有利的证据。
- option_a: 改进安全并继续。
- option_b: 暂停实验。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Improving safety treats the accident as a procedural failure rather than a failure of experimentation itself, preserving momentum at a practical cost.
- rationale_zh: 改进安全把事故解释为程序上的失败，而不是实验本身的失败，因此能以实际成本保住推进势头。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: temporary_country_modifier
  key: tv_academy_debate_laboratory_safety_rules
  months: 24
  effects:
    safer experimental demonstrations: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Suspending experiments restores public order and prevents further embarrassment, but it hands opponents a simple story: dangerous methods should not guide the realm.
- rationale_zh: 暂停实验能恢复公共秩序并避免更多难堪，但这也给了反对者一个简单说法：危险的方法不该指导国家。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike SR04, which asks whether to fund better instruments before they are trusted, SR08 deals with damage after experimental apparatus has visibly failed.
- Unlike SR13, where the danger is reputational exposure during a planned public demonstration, SR08 turns a physical mishap into a debate over method.
- Unlike SR15, which studies error as data, SR08 is about whether an accident can be regulated without halting experimental practice altogether.
