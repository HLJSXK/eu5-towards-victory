# R09 - A Ruin Measured

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Ruin Measured
- description: Surveyors measure ancient ruins and discover proportions that embarrass current builders. The stones say nothing, which makes their arithmetic harder to interrupt.
- option_a: Publish the measures.
- option_b: Treat them as antiquarian trivia.

## Chinese Text
- title: 丈量古代遗迹
- description: 测绘者丈量古代遗迹，发现其中比例足以让当代建造者脸红。石头一言不发，正因如此，它们的算术更难被打断。
- option_a: 公布丈量结果。
- option_b: 当作古董趣闻处理。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Publishing the measurements lets material evidence from antiquity discipline current practice, strengthening acceptance through craft, proportion, and artist-scholar cooperation.
- rationale_zh: 公布丈量结果会让来自古代的物证反过来规范当下技艺，借工艺、比例以及艺术家与学者的合作来推动接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_measured_ruins
  months: 18
  effects:
    architectural study momentum: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Treating the measures as trivia preserves the ruins as harmless curiosities instead of evidence for reform, muting artists who would turn old stone into a current standard.
- rationale_zh: 把丈量结果当作趣闻，会让遗迹停留在无害收藏物的位置，而不是成为改革证据，也会压低艺术家借古代石材制定当代标准的声量。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: artists
  cooldown_months: 12
- type: seat_stance
  group: scholarly_community
  stance: neutral
  cooldown_months: 6
```

## Difference From Same Issue Events
- Unlike R01 A Newly Found Torso, R09 is about measured proportions and practical standards rather than the emotional force of an unearthed sculpture.
- Unlike R03 Perspective in the Chapel, the evidence comes from surveying ancient ruins, not from a living painter's mathematical method inside sacred architecture.
- Unlike R19 The City as Classroom, this event stops at publishing measurements; it does not commit the state to an expensive urban design program.
