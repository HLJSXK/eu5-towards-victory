# P14 - Errors Multiply

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Errors Multiply
- description: One bad printed table spreads the same error through hundreds of copies.
- option_a: Create correction sheets.
- option_b: Use it against print reliability.

## Chinese Text
- title: 错误成倍扩散
- description: 一张错误的印刷表格让同一个错误随着数百份副本传播开来。
- option_a: 印制勘误单。
- option_b: 借此质疑印刷可靠性。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Correction sheets admit the failure while showing that print can repair itself through the same rapid circulation that spread the mistake.
- rationale_zh: 印制勘误单是在承认失误的同时，证明印刷术能用传播错误的同一种速度来修正自身。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
```

### Option B
- progress_delta: -5
- rationale_en: Treating the error as proof against the press lets conservative scholars argue that multiplication magnifies falsehood as easily as truth.
- rationale_zh: 把错误当作反对印刷术的证据，会让保守学者声称，大量复制既能放大真理，也同样能放大谬误。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike P06, this event begins with a printed educational error rather than a corrected textbook improving schools.
- Unlike P07, the cost is for quality control after publication, not for subsidizing scarce paper before publication.
- Unlike P12, the danger is accidental misinformation rather than the political magnetism of forbidden text.
