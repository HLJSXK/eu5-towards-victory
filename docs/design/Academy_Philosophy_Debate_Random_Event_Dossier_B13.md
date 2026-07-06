# B13 - Scholar of Interest

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Scholar of Interest
- description: A mathematician demonstrates compound interest on a clean slate, and several listeners look as if the chalk has named them personally. What had seemed like merchant habit becomes a law of numbers.
- option_a: Teach the method.
- option_b: Keep the calculation obscure.

## Chinese Text
- title: 利息学者
- description: 一位数学家在干净的石板上演示复利，几名听众的神情仿佛粉笔点名点到了自己。原本像商人习惯的东西，忽然变成了数字的法则。
- option_a: 讲授这种方法。
- option_b: 让计算继续晦涩。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Teaching compound interest makes credit legible as knowledge rather than mystery, so scholars can defend regulated finance with clearer tools. The gain is modest because clarity also alarms debtors.
- rationale_zh: 讲授复利把信贷从神秘技艺变成可理解的知识，使学者能用更清楚的工具为受监管的金融辩护。推进幅度有限，因为这种清晰同样会让债务人不安。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
- type: scientist_attribute
  adm: 1
  dip: 0
```

### Option B
- progress_delta: -5
- rationale_en: Keeping the calculation obscure spares debtors the humiliation of seeing their burden grow by formula, but it also leaves banking reform dependent on private expertise rather than shared rules.
- rationale_zh: 让计算继续晦涩，可以让债务人免于看见自己的负担被公式放大的羞辱，但这也使银行改革继续依赖私人专家，而不是共同规则。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.02
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike B03 Sermon on Usury, which frames interest as a moral danger, B13 frames it as a mathematical concept that can be taught or deliberately hidden.
- Unlike B08 Bills of Exchange, where paper instruments prove practical speed, B13 is about theoretical literacy and whether people understand the arithmetic beneath credit.
- Unlike B18 Contract in Plain Language, which simplifies legal wording for ordinary readers, B13 exposes the numerical machinery that makes a readable contract still dangerous.
