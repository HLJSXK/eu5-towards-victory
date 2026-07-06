# SR15 - Dissection of Error

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Dissection of Error
- description: Scholars propose studying errors as data, a suggestion that threatens many careers. Suddenly every failed calculation, cracked lens, and spoiled sample looks less like shame than like evidence with inconvenient timing.
- option_a: Record errors openly.
- option_b: Preserve reputations.

## Chinese Text
- title: 解剖错误
- description: 学者提议把错误也当作数据来研究，这个建议威胁到了许多人的仕途。突然之间，每一次失败的计算、裂开的镜片和变质的样本，都不再只是羞耻，而像是来得不合时宜的证据。
- option_a: 公开记录错误。
- option_b: 维护名声。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Recording errors openly strengthens the method by making failure useful instead of shameful. The progress is modest because the lesson is procedural, but it still nudges the debate toward acceptance while costing prestige.
- rationale_zh: 公开记录错误会让失败变得有用，而不只是可耻，从而强化新方法。由于这一教训偏向程序性，进度提升较小；但它仍会推动辩论走向接纳，并付出威望代价。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -5
- type: scientist_attribute
  adm: 1
  dip: 0
```

### Option B
- progress_delta: -5
- rationale_en: Preserving reputations spares established scholars from public embarrassment, but it also teaches the Academy to hide the very mistakes that could improve the method.
- rationale_zh: 维护名声能让资深学者免于公开难堪，但也等于教会学院隐藏那些本可改进方法的错误。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
- type: resource
  resource: prestige
  amount: 5
```

## Difference From Same Issue Events
- Unlike SR02 Failed Replication, SR15 is not about one celebrated result collapsing. It creates a standing habit of treating many errors as useful data.
- Unlike SR13 Public Demonstration, SR15 keeps the focus on internal records and career risk rather than a spectacle before public witnesses.
- Unlike SR05 Academy Experiment Code, SR15 narrows the method question to mistakes, failed trials, and reputations rather than the full protocol for witnessing experiments.
