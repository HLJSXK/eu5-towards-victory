# P04 - Cheap Prayer Sheets

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Cheap Prayer Sheets
- description: Cheap printed prayer sheets reach villages faster than official sermons.
- option_a: Use print for reform.
- option_b: Restrict village printing.

## Chinese Text
- title: 廉价祈祷单
- description: 廉价印刷祈祷单比正式布道更快传到乡村。
- option_a: 用印刷推动改革。
- option_b: 限制乡村印刷。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Using print for reform accepts that cheap religious text can bypass old channels and build practical support for the new medium.
- rationale_zh: 用印刷推动改革，就是承认廉价宗教文本可以绕过旧渠道，并为新媒介建立实际支持。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Restricting village printing reassures clergy that parish authority still controls common religious instruction.
- rationale_zh: 限制乡村印刷让教士相信，堂区权威仍掌握普通人的宗教教导。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike P03, this event focuses on low-cost devotional material and village reach rather than formal indexes of dangerous books.
- Unlike P17, the accessibility problem is rural and devotional, not multilingual publication across cultural communities.
- Unlike P11, the printed text is religious instruction, not standardized royal law.
