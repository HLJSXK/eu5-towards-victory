# G08 - Merchant Subscription

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Merchant Subscription
- description: Burghers offer to fund pamphlets, copied notes, and coffeehouse discussion, provided their names sit close enough to the title.
- option_a: Accept the subscription
- option_b: Reject commercial noise

## Chinese Text
- title: 商人认捐
- description: 市民商人愿意资助小册子、抄写笔记和咖啡馆讨论，条件是他们的名字要离标题足够近。
- option_a: 接受认捐
- option_b: 拒绝商业喧嚣

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Merchant money spreads the new argument beyond the chamber and makes burghers feel invested in the Academy's conclusion.
- rationale_zh: 商人的资金会把新论点传播到会场之外，也让市民商人觉得自己参与了学院结论的形成。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
```

### Option B
- progress_delta: -5
- rationale_en: Rejecting the subscription keeps commercial branding away from doctrine, which pleases nobles who dislike seeing public argument dressed as a market venture.
- rationale_zh: 拒绝认捐能让商业署名远离学理判断，这会取悦那些不愿看到公共争论被包装成市场事业的贵族。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike G02, this is not about physical access to the galleries but about financed circulation through pamphlets and coffeehouses.
- Unlike G12, the choice does not unlock a rare text; it decides whether patronage and publicity are allowed to amplify an argument.
