# MF17 - Workshop School

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Workshop School
- description: Reformers propose teaching workers inside manufactories, where the lesson begins at the bench and ends in a counted batch. Guild masters notice that apprenticeship is being asked to share its own vocabulary.
- option_a: Fund workshop schools.
- option_b: Keep guild apprenticeship.

## Chinese Text
- title: 工场学校
- description: 改革者提议在制造工场内部训练工人，让课程从工作台开始，以一批可计数的成品结束。行会师傅立刻意识到，学徒制正在被迫分享自己的语言。
- option_a: 资助工场学校。
- option_b: 保留行会学徒制。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding workshop schools lets manufactories reproduce their own skilled labor instead of borrowing legitimacy from guild apprenticeship. That powerfully advances acceptance, but it costs money and tells guilds that their gatekeeping role is no longer secure.
- rationale_zh: 资助工场学校使制造工场能够自行培养熟练劳动力，而不必再向行会学徒制借取合法性。这会强力推动接受制造工场，但也要花钱，并且等于告诉行会：它们的把关地位不再稳固。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Keeping guild apprenticeship preserves the old ladder of skill, patronage, and urban status. The debate turns decisively against manufactories because training remains tied to the institutions most threatened by factory discipline.
- rationale_zh: 保留行会学徒制，就是保留技能、庇护关系和城市身份的旧阶梯。辩论会明确转向反对制造工场，因为训练仍被系在最受工场纪律威胁的旧制度上。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: temporary_country_modifier
  key: tv_academy_debate_guild_apprenticeship_preserved
  months: 18
  effects:
    continuity of urban craft training: 0.03
```

## Difference From Same Issue Events
- Unlike MF01 Workshop Under One Roof, MF17 concerns how manufactories create trained workers, not whether labor should be gathered in one place.
- Unlike MF11 Standard Parts, this event is about teaching people rather than standardizing the objects they produce.
- Unlike MF16 Piecework Pay, MF17 contests the path into skilled labor instead of the wage formula after work begins.
