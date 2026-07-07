# G02 - Crowded Galleries

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Crowded Galleries
- description: Students, clerks, idle nobles, and citizens with suspiciously excellent hearing pack the galleries. Every strong line now travels farther than the speaker intended.
- option_a: Keep the doors open.
- option_b: Clear the galleries.

## Chinese Text
- title: 拥挤的旁听席
- description: 学生、书记员、闲散贵族，以及一些听力好得可疑的市民挤满旁听席。每一句有力的话都会传得比发言者预想的更远。
- option_a: 继续开放大门。
- option_b: 清空旁听席。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Open galleries turn the issue into a public lesson. Wider attention gives acceptance a social constituency, even if the room becomes harder to control.
- rationale_zh: 开放旁听席会把议题变成一场公开课程。更广泛的关注会给接受派带来社会支撑，即使会场更难控制。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Clearing the galleries lowers the pressure on the Crown and prevents every careless phrase from becoming rumor, but it also moves the debate away from acceptance.
- rationale_zh: 清空旁听席能减轻王权承受的舆论压力，也避免每句失言变成传闻，但同时会让辩论远离接受方向。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike G01, which spreads an edited intellectual summary, G02 spreads the living performance of debate through a physical audience.
- Unlike G10, where students imitate the debate on their own, G02 concerns whether the official Academy session itself remains publicly visible.
- Unlike G14, which follows a song after the issue escapes into the street, G02 is the earlier choice of whether to let that public energy enter the chamber at all.
