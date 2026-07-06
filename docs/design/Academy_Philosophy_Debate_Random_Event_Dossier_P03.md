# P03 - Clerical Index

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clerical Index
- description: Clergy propose an index of dangerous books, which the students immediately want to read.
- option_a: Reject broad indexing.
- option_b: Approve the index.

## Chinese Text
- title: 教士禁书索引
- description: 教士提出编制危险书籍索引，学生们立刻想把这些书全读一遍。
- option_a: 拒绝宽泛索引。
- option_b: 批准索引。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Refusing a broad index denies clerical authorities the power to define printed inquiry as danger by default.
- rationale_zh: 拒绝宽泛索引，就是不让教会权威把印刷出来的探究默认定义为危险。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
```

### Option B
- progress_delta: -10
- rationale_en: Approving the index places printed argument under religious gatekeeping, sharply strengthening opposition to press-driven debate.
- rationale_zh: 批准索引会把印刷论辩置于宗教把关之下，明显强化对印刷推动辩论的反对。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike P04, this event is about elite censorship of books, not devotional sheets spreading through villages.
- Unlike P12, the controversy precedes a specific banned bestseller; it creates the category of dangerous print.
- Unlike P18, the pressure comes from religious authority rather than military or technical uses of the press.
