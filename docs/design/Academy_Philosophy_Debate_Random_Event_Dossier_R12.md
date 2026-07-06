# R12 - Fresco of the New Age

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Fresco of the New Age
- description: A fresco depicts the realm stepping from shadow into measured light. It is not subtle, which is why it works.
- option_a: Place it in the Academy
- option_b: Keep walls neutral

## Chinese Text
- title: 新时代的湿壁画
- description: 一幅湿壁画描绘王国从阴影中走向有度量的光明。它并不含蓄，也正因如此才有效。
- option_a: 将它置于学院
- option_b: 保持墙面中立

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Installing the fresco makes Renaissance renewal part of the Academy's daily visual language. It advances acceptance modestly because the argument becomes atmospheric and memorable rather than strictly doctrinal.
- rationale_zh: 将湿壁画安置在学院中，会让文艺复兴式更新成为学院日常视觉语言的一部分。它不是以教义论证取胜，而是以氛围和记忆推动接受，因此进度小幅上升。
- effect_blocks:
```yaml
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 12
- type: artist_skill
  amount: 0.05
```

### Option B
- progress_delta: -5
- rationale_en: Neutral walls keep the debate from becoming visual propaganda. Conservative seats can frame restraint as dignity, slowing acceptance without requiring a harsher crackdown.
- rationale_zh: 保持墙面中立，可以避免辩论变成视觉宣传。保守席位能够把克制解释为庄重，从而减缓接受进度，同时不必采取更严厉的压制。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike R03, Perspective in the Chapel, this event uses a public Academy artwork rather than a technical method inside sacred architecture.
- Unlike R08, Court Masque of Renewal, this event is permanent visual messaging rather than a temporary court performance.
- Unlike R15, The Prince's Portrait, this event represents the age and the realm, not the ruler's personal iconography.
