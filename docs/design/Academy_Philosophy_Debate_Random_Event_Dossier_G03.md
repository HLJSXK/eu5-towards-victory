# G03 - A Useful Misquotation

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Useful Misquotation
- description: A copied line from a respected authority appears to favor the new argument. The wording is convenient, the ink is fresh, and several scholars are suddenly very interested in handwriting.
- option_a: Correct it publicly.
- option_b: Let the ambiguity work.

## Chinese Text
- title: 有用的误引
- description: 一句抄自权威著作的话看起来支持新论点。措辞太过方便，墨迹又太新，几位学者忽然对笔迹产生了浓厚兴趣。
- option_a: 公开更正。
- option_b: 任由含混发挥作用。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Public correction shows that the accepting side can win without corrupted evidence, but admitting the mistake costs reputation in the short term.
- rationale_zh: 公开更正表明接受派不必靠伪证取胜，但承认错误会在短期内损耗声望。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
```

### Option B
- progress_delta: +10
- rationale_en: Keeping the ambiguity gives acceptance an immediate rhetorical victory, while the scholarly community learns that convenience may outweigh accuracy in this debate.
- rationale_zh: 保留含混之处能让接受派迅速取得修辞优势，但学术共同体会意识到这场辩论中便利可能压过准确。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike G01, where clarity itself persuades, G03 asks whether a tainted but useful ambiguity should be corrected or exploited.
- Unlike G04, which debates the authority of a genuinely old note, G03 centers on textual integrity and the political temptation of a suspicious source.
- Unlike G15, which tests arguments under a formal challenge, G03 tests whether the Academy will preserve standards when a mistake helps the preferred side.
