# P02 - Printer's Guild Petition

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Printer's Guild Petition
- description: Printers ask for legal recognition before more presses appear in basements and borrowed kitchens.
- option_a: Recognize the guild.
- option_b: Keep presses licensed case by case.

## Chinese Text
- title: 印刷匠行会请愿
- description: 印刷匠要求获得法律承认，以免更多印刷机出现在地下室和借来的厨房里。
- option_a: 承认行会。
- option_b: 逐案许可印刷机。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Legal recognition makes printing a regulated civic trade rather than a tolerated irregular craft, giving urban producers a stake in acceptance.
- rationale_zh: 法律承认把印刷变成受规制的城市行业，而不是被默许的零散手艺，使城市生产者在接受印刷术中获得利益。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
```

### Option B
- progress_delta: -5
- rationale_en: Case-by-case licensing preserves administrative discretion and slows the formation of a confident printing interest.
- rationale_zh: 逐案许可保留行政裁量，也延缓印刷业形成自信而稳定的利益群体。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike P01, this event concerns the legal status of printers rather than the circulation of a first pamphlet run.
- Unlike P07, the bottleneck is institutional recognition, not paper supply or treasury subsidy.
- Unlike P19, printers are acting collectively as a trade, not through one printer's personal celebrity.
