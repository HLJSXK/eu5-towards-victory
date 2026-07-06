# C12 - Pilgrim Riot

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Pilgrim Riot
- description: A pilgrimage spills from devotion into street violence after rival sermons, old badges, and new slogans meet on the same road. The Academy must decide whether custom can be disciplined without being broken.
- option_a: Regulate the pilgrimage.
- option_b: Let custom rule.

## Chinese Text
- title: 朝圣骚乱
- description: 一场朝圣在相互竞争的布道、旧徽记和新口号相遇后，从虔敬滑向街头冲突。学院必须判断，是否能约束旧俗而不彻底摧毁它。
- option_a: 规范朝圣活动。
- option_b: 让习俗自行维持秩序。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Regulation proves the state confession can contain inherited devotion inside public order, but calming a holy crowd costs real stability.
- rationale_zh: 规范朝圣说明国家化的宗派秩序能够把旧有虔敬纳入公共秩序之中，但安抚神圣人群需要付出真实的稳定代价。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: -1
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Letting custom rule reassures clergy and local guardians of pilgrimage practice, but it concedes that inherited devotion outranks confessional discipline.
- rationale_zh: 让习俗自行维持秩序会安抚教士和地方朝圣守护者，但也等于承认旧有虔敬高于新宗派纪律。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike C10, which reforms the calendar of holy days, C12 deals with a moving crowd and the immediate stability cost of policing devotion.
- Unlike C14, which argues over one church image, C12 tests whether an entire public pilgrimage can fit the new confessional order.
- Unlike C08, where elites summon a synod to settle doctrine, C12 begins with disorder among worshippers before the Academy can make doctrine tidy.
