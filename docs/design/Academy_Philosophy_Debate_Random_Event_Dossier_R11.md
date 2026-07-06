# R11 - Translation of a Greek Text

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Translation of a Greek Text
- description: A Greek text arrives with enough ambiguity to start three arguments and one school.
- option_a: Sponsor translation
- option_b: Delay for review

## Chinese Text
- title: 希腊文本的翻译
- description: 一部希腊文本送抵学院，其中的含混之处足以引发三场争论，并催生一个学派。
- option_a: 资助翻译
- option_b: 延后审阅

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding a careful translation turns ambiguity into humanist momentum. The debate advances because scholars gain usable language for the new Renaissance claim, while the treasury pays for copyists, philologists, and comparison manuscripts.
- rationale_zh: 资助严谨翻译会把含混之处转化为人文主义的推动力。学者获得可用于阐明文艺复兴主张的术语，因此辩论向接受方向推进，但国库需要承担抄写员、语文学者和校勘底本的费用。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Review delays let institutional caution define the text before reformers can use it. Clergy and bureaucrats are reassured because difficult passages remain contained and administratively supervised.
- rationale_zh: 延后审阅让制度性的谨慎先于改革者解释文本。疑难段落仍被控制在审查和行政程序中，因此神职人员与官僚更感安心。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
- type: seat_cooldown
  group: court_bureaucrats
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R06, Classics in the Market, this event is about expert translation and scholarly authority rather than cheap public circulation.
- Unlike R18, Library Reordered, this event changes the meaning of a contested text, not the Academy's cataloging habits.
- Unlike R17, Imported Master, the foreign influence arrives as an ancient manuscript and translation problem rather than as a living artist with local rivals.
