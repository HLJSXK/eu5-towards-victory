# MF04 - Women at the Looms

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Women at the Looms
- description: A manufactory hires women in numbers too large to be dismissed as household help. What began as wages becomes an argument about custom, discipline, and who may stand visibly inside the new economy.
- option_a: Defend wage work.
- option_b: Restrict hiring custom.

## Chinese Text
- title: 织机旁的女性
- description: 一家制造工场雇用了许多女性，多到无法再被轻描淡写地称作家内帮工。最初只是工资的问题，如今变成了关于习俗、纪律以及谁能公开站进新经济的争论。
- option_a: 捍卫有薪劳动。
- option_b: 限制雇佣惯例。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Defending wage work treats the manufactory as a social transformation, not just a production trick. Acceptance advances sharply because the Academy endorses new labor arrangements, while conservative moral and household authorities object.
- rationale_zh: 捍卫有薪劳动，就是把制造工场视为社会变革，而不仅是生产技巧。学术院认可新的劳动安排，接受度会显著上升；但保守的道德与家户权威会表示反对。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Restricting hiring custom makes manufactories prove that they will not disturb accepted household and moral order. That reassures clergy and guild conservatives, but it turns the debate decisively away from embracing the new model.
- rationale_zh: 限制雇佣惯例，等于要求制造工场证明自己不会扰乱既有家户和道德秩序。这能安抚教士与行会保守派，却会让辩论明确远离接受新模式。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike MF07 Clock Discipline, MF04 focuses on who enters manufactory labor rather than how time is imposed on workers already inside it.
- Unlike MF10 Child Labor Petition, MF04 is about women's wage work and public custom, not child protection in proto-factory conditions.
- Unlike MF16 Piecework Pay, this event turns on social legitimacy and household order rather than the arithmetic of wages and output.
