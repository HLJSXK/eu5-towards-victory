# P17 - Multilingual Edition

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Multilingual Edition
- description: Printers propose editions in several languages, making the argument harder to contain.
- option_a: Publish them.
- option_b: Keep one official language.

## Chinese Text
- title: 多语种版本
- description: 印刷商提议用数种语言出版同一论点，让这场争论更难被圈住。
- option_a: 出版多语种版本。
- option_b: 只保留一种官方语言。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Multilingual publication lets print carry the issue through communities that official language normally filters out, giving minorities and cities a stake in acceptance.
- rationale_zh: 多语种出版让印刷品把议题带进官方语言通常过滤掉的群体之中，使少数群体和城市都从接受印刷应用中受益。
- effect_blocks:
```yaml
- type: seat_stance
  group: minorities
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: A single official language keeps interpretation centralized and administratively tidy, but it narrows the press back into an instrument of authority.
- rationale_zh: 单一官方语言能让解释权保持集中，也让行政更整齐，却会把印刷术重新压缩成权威机关的工具。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 3
```

## Difference From Same Issue Events
- Unlike P04, the access problem is linguistic and urban-cultural rather than village devotional print.
- Unlike P09, multiple languages are deliberately issued at home, not produced through hostile or careless foreign reprints.
- Unlike P11, this event is about broadening the audience of debate, not standardizing royal proclamations.
