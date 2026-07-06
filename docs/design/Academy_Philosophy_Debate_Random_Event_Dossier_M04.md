# M04 - Purchased Office

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Purchased Office
- description: A lucrative office is quietly offered to a donor's son during the debate.
- option_a: Expose the sale.
- option_b: Accept the arrangement.

## Chinese Text
- title: 买来的官职
- description: 辩论进行时，一项肥缺被悄悄许给某位捐献者的儿子。
- option_a: 揭露这笔交易。
- option_b: 接受这项安排。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Exposing the sale proves that purchased office is not a harmless custom but a direct rival to tested competence. The reform gains force, but the Crown loses money and noble patrons lose satisfaction.
- rationale_zh: 揭露这笔交易能证明买官不是无伤大雅的惯例，而是对考核能力的直接竞争。改革因此更有力，但王室失去收入，贵族庇护者也会不满。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Accepting the arrangement turns the debate's enemy into policy: money and connection purchase what merit was supposed to earn. The treasury relaxes, but the argument for open assessment is badly damaged.
- rationale_zh: 接受安排等于把辩论的敌人变成政策：金钱和关系买下了本该由才能赢得的职位。国库得到缓解，但公开考核的主张受到重创。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike M11 Examination Fraud, the corruption here is office purchase through patronage, not cheating inside the examination apparatus.
- Unlike M18 Clean Ink, Dirty Hands, the state catches an active appointment bargain rather than investigating a hidden patronage network behind clean papers.
- Unlike M02 Genealogies on the Table, this event uses immediate money and office access instead of inherited service as the anti-meritocratic claim.
