# R18 - Library Reordered

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Library Reordered
- description: Humanists reorder the Academy library by subject instead of inherited shelf tradition, and suddenly old books begin introducing themselves to new neighbors.
- option_a: Accept the new order.
- option_b: Restore the old shelves.

## Chinese Text
- title: 重新整理图书馆
- description: 人文主义者按照学科重新整理学院图书馆，而不是沿用祖传书架传统。旧书于是突然开始与新的邻居彼此相识。
- option_a: 接受新的分类。
- option_b: 恢复旧书架。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: A subject catalogue quietly normalizes Renaissance habits of comparison and classification, giving scholars a modest but stable reason to support the new issue.
- rationale_zh: 按学科编目的做法会悄然使比较与分类的文艺复兴习惯正常化，给学者们一个温和但稳定的支持理由。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_subject_catalogue
  months: 18
  effects:
    "academy reference efficiency": 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Restoring inherited shelves lets conservative scholars treat the old arrangement as a memory palace of authority, slowing the humanist habit of rearranging knowledge.
- rationale_zh: 恢复旧书架会让保守学者把原有排列视为权威的记忆宫殿，从而减缓人文主义重新组织知识的习惯。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
- type: seat_cooldown
  group: court_bureaucrats
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R11 Translation of a Greek Text, this event does not add a new text; it changes how existing texts can be found and compared.
- Unlike R09 A Ruin Measured, the Renaissance method here is classificatory and archival rather than architectural and empirical.
- Unlike R06 Classics in the Market, the audience remains inside the Academy, so the effect is scholarly alignment rather than broad public diffusion.
