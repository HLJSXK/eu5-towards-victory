# R02 - Anatomy Before the Court

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Anatomy Before the Court
- description: Physicians ask to conduct a sanctioned anatomical lesson before courtiers and scholars. The old diagrams remain polite on the table, but the physicians warn that politeness has never made a body true.
- option_a: Permit the lesson.
- option_b: Forbid the spectacle.

## Chinese Text
- title: 宫廷前的解剖
- description: 医师请求在廷臣与学者面前举行一场获准的解剖课。旧图谱依旧端正地铺在桌上，但医师提醒众人，端正从来不能让身体变得真实。
- option_a: 准许这堂课。
- option_b: 禁止这场展示。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Permitting the lesson gives direct observation priority over inherited diagrams, sharply advancing Renaissance empiricism while offending clergy who see the display as a breach of sacred restraint.
- rationale_zh: 准许解剖课等于让直接观察压过沿袭下来的图谱，强力推动文艺复兴式经验探究，同时冒犯那些认为公开展示身体越过神圣克制界限的神职人员。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
```

### Option B
- progress_delta: -10
- rationale_en: Forbidding the lesson hands opponents a decisive victory: the court chooses reverence and order over demonstration, making old diagrams safe again.
- rationale_zh: 禁止这堂课会给反对者一场明确胜利：宫廷选择敬畏与秩序，而不是演示与观察，于是旧图谱重新变得安全。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.05
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike R01's ancient sculpture, R02 uses a living intellectual risk: anatomical observation challenges authority in front of the court.
- Unlike R07, where an artist and theologian dispute beauty, R02 makes the conflict practical and bodily rather than aesthetic.
- Unlike R17's imported master, R02 depends on domestic sanction and court permission rather than foreign technique.
