# R19 - The City as Classroom

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The City as Classroom
- description: Urban reformers argue that streets, squares, and facades can teach citizens better taste, provided the treasury accepts that stone is now a syllabus.
- option_a: Back the urban program.
- option_b: Keep art indoors.

## Chinese Text
- title: 城市即课堂
- description: 城市改革者主张，街道、广场与立面都能教导市民更好的品味，只要国库愿意承认石头如今也是一种课程。
- option_a: 支持城市计划。
- option_b: 让艺术留在室内。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding public urban reform makes Renaissance taste unavoidable in daily life, so acceptance advances strongly, but the program needs real construction money.
- rationale_zh: 资助公共城市改造会让文艺复兴品味进入日常生活、无法回避，因此接受度大幅推进；但这项计划需要真实的建设经费。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 24
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Keeping art indoors avoids expensive civic works and keeps the treasury calm, but it limits Renaissance ideas to controlled interiors rather than shared public space.
- rationale_zh: 让艺术留在室内可以避免昂贵的市政工程，使国库保持平静；但这也把文艺复兴思想限制在受控的室内空间，而非公共场所。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R04 Patronage Ledger, this does not merely expand court patronage; it spends on the visible city as a public lesson.
- Unlike R12 Fresco of the New Age, the art is not contained on an Academy wall but distributed through streets, squares, and facades.
- Unlike R08 Court Masque, the program is durable urban infrastructure rather than a temporary performance.
