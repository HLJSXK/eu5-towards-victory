# P06 - Corrected Textbook

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Corrected Textbook
- description: A printed textbook spreads corrected diagrams through schools in one season.
- option_a: Adopt it.
- option_b: Review it for another season.

## Chinese Text
- title: 校正课本
- description: 一本印刷课本在一个季节内把修正过的图表传遍各地学校。
- option_a: 采用这本课本。
- option_b: 再审查一个季节。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Adopting the textbook lets print prove its strongest scholarly claim: one correction can travel faster, farther, and more consistently than manuscript teaching.
- rationale_zh: 采用这本课本能让印刷术证明其最强的学术价值：一次修正可以比手抄教学传播得更快、更远，也更一致。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -5
- rationale_en: Another season of review reassures cautious teachers and conservative patrons, but it treats print's ability to standardize knowledge as a risk to be delayed.
- rationale_zh: 再审查一个季节能安抚谨慎教师和保守赞助者，却把印刷术统一知识的能力当成需要拖延的风险。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_textbook_review
  months: 12
  effects:
    curricular caution: 0.02
```

## Difference From Same Issue Events
- Unlike P01, this event is about standardized educational content rather than a first public pamphlet circulation.
- Unlike P13, the school system receives a finished printed work instead of asking for institutional control over a university press.
- Unlike P14, the printed material is corrected and useful from the start, not an error that forces damage control.
