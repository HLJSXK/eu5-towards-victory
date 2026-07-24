# NW13 - Cosmographer's Error

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Cosmographer's Error
- description: The Academy's favored cosmographer admits that a major distance estimate was wrong. The error is small on parchment only because parchment is mercifully flat.
- option_a: Praise correction as science.
- option_b: Hide the error.

## Chinese Text
- title: 宇宙志学者的错误
- description: 学院偏爱的宇宙志学者承认，一项重要的距离估算错了。这个错误只有在羊皮纸上才显得很小，因为羊皮纸毕竟仁慈地保持平整。
- option_a: 将修正誉为科学精神。
- option_b: 掩盖这个错误。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Praising the correction turns embarrassment into the method itself. The debate moves strongly toward acceptance because New World evidence becomes proof that knowledge can improve by admitting error, though scholarly prestige is spent to make that lesson credible.
- rationale_zh: 赞扬修正会把尴尬转化为方法本身。辩论会大幅转向接受，因为新世界的证据变成了知识可以通过承认错误而进步的证明；不过，为了让这个教训可信，学术声望会被消耗。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Hiding the error preserves the old hierarchy of expertise at the cost of honest revision. Acceptance falls sharply because the Academy chooses authority's appearance over the corrected evidence that would have supported discovery.
- rationale_zh: 掩盖错误会维护旧有专家等级的体面，却牺牲诚实修正的机会。接受度会大幅下降，因为学院选择了权威的外观，而不是能够支持发现论点的修正证据。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike NW09 Mapmaker's Correction, NW13 centers on an abstract distance estimate and professional embarrassment rather than a public redrawing of a visible boundary.
- Unlike NW01 The Sailor's Chart, the evidence comes from correcting the Academy's own favored expert, not from deciding whether to trust an external chart.
- Unlike NW20 School Globe, this event is about the discipline of admitting error before knowledge can be taught, not about presenting a finished teaching object to the public.
