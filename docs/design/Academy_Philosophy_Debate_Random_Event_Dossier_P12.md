# P12 - Forbidden Book Success

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Forbidden Book Success
- description: A banned book becomes popular because it is banned, as books sometimes do out of spite.
- option_a: Legalize and annotate it.
- option_b: Expand confiscations.

## Chinese Text
- title: 禁书畅销
- description: 一本被禁的书因为遭禁而流行起来，书籍有时就是这样带着几分倔强。
- option_a: 将其合法化并加注解。
- option_b: 扩大查禁。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Legalizing the book and surrounding it with official annotation turns forbidden curiosity into supervised public argument, advancing acceptance while angering clerical guardians.
- rationale_zh: 将禁书合法化并配上官方注解，会把被禁止激起的好奇转化为受监督的公共论辩，在推进接纳的同时激怒宗教守门人。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
```

### Option B
- progress_delta: -10
- rationale_en: Wider confiscations restore visible order, but they also concede that printed text is dangerous enough to be fought by force.
- rationale_zh: 扩大查禁能恢复可见秩序，却也等于承认印刷文本危险到必须用强制手段对付。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
```

## Difference From Same Issue Events
- Unlike P03, this event starts from one specific banned book whose prohibition has already made it famous, not from a proposed general index.
- Unlike P05, the scandal is intellectual and censorial rather than court gossip mixed with serious argument.
- Unlike P08, the printed material has a named forbidden object rather than anonymous broadsides with unclear authorship.
