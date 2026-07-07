# SR20 - The New Method Named

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The New Method Named
- description: Someone gives the method a name, and suddenly a cluster of habits becomes a movement. Friends repeat it with relief, opponents with alarm, and undecided listeners with the dangerous feeling that history may need a label.
- option_a: Embrace the name.
- option_b: Avoid naming it.

## Chinese Text
- title: 新方法得名
- description: 有人为这套方法取了名字，于是一簇习惯忽然变成了一场运动。支持者如释重负地重复它，反对者警惕地重复它，犹豫者则危险地感觉到，历史也许正需要一个标签。
- option_a: 接受这个名称。
- option_b: 避免为它命名。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Embracing the name turns scattered practices into a recognizable program, making acceptance easier to organize and defend. The same clarity also helps opponents consolidate against it.
- rationale_zh: 接受这个名称，会把分散的做法变成一个可识别的纲领，使接受者更容易组织和辩护。同样的清晰度也会帮助反对者凝聚起来。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_named_method
  months: 24
  effects:
    organized scientific faction: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Avoiding the name keeps the debate less threatening and denies opponents a banner to attack. It also weakens momentum because supporters cannot easily rally around unnamed habits.
- rationale_zh: 避免命名可以让辩论显得不那么咄咄逼人，也不给反对者一个可攻击的旗号。但它同样会削弱势头，因为支持者很难围绕没有名字的习惯集合起来。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: public_opinion
  cooldown_months: 12
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike SR01 Table of Observations, SR20 does not introduce new evidence; it changes how existing practices are named, recognized, and organized.
- Unlike SR18 Dangerous Publication, SR20 creates a movement label rather than deciding whether a specific dangerous text should be printed.
- Unlike SR19 Experimental Oath, SR20 protects no witness directly; its pressure comes from identity formation and the consolidation of both supporters and opponents.
