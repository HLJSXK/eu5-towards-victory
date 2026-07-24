# P19 - Printer Becomes Celebrity

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Printer Becomes Celebrity
- description: A printer becomes famous enough to annoy scholars who wrote the actual words.
- option_a: Use the fame.
- option_b: Recenter scholars.

## Chinese Text
- title: 印刷商成了名人
- description: 一名印刷商出名到足以惹恼真正写下那些文字的学者。
- option_a: 借用这份名声。
- option_b: 重新把学者放回中心。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Using the printer's fame accepts that the medium now has its own public figures, letting urban trades turn attention into support for acceptance.
- rationale_zh: 借用印刷商的名声等于承认这种媒介已经拥有自己的公共人物，让城市行业把关注转化为支持接受印刷术。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
```

### Option B
- progress_delta: -5
- rationale_en: Recentering scholars protects learned authorship from commercial showmanship, but it pushes the debate away from the public power of the press itself.
- rationale_zh: 重新把学者放回中心能保护学术作者免受商业作秀遮蔽，却会让辩论远离印刷术本身的公共力量。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: scholarly_community
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike P02, this is about one printer's fame rather than printers acting collectively through a guild petition.
- Unlike P05, the notoriety is useful publicity rather than scandalous gossip damaging legitimacy.
- Unlike P15, the memorable public object is the printer as a person, not a printed ballad that simplifies the issue.
