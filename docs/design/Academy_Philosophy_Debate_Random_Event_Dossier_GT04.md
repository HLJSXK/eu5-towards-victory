# GT04 - Spice Cargo

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Spice Cargo
- description: A spice cargo is opened before the Academy, and the room fills with a scent no inland tax register has ever captured. Suddenly distant islands feel less like rumor and more like an argument with cinnamon on its sleeves.
- option_a: Display the cargo.
- option_b: Tax it quietly.

## Chinese Text
- title: 香料货物
- description: 一批香料货物在学院面前开箱，室内立刻弥漫起内陆税册从未记录过的气味。遥远岛屿忽然不再像传闻，而像一场袖口沾着肉桂的论证。
- option_a: 展示这批货物。
- option_b: 悄悄征税。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Displaying the cargo lets ordinary observers feel the material appeal of distant exchange. The event gives only moderate progress because spectacle stirs curiosity more than it settles policy.
- rationale_zh: 展示货物会让普通旁听者亲身感到远方交换的物质吸引力。它只提供中等推进，因为奇观更能激起好奇，而不是直接解决政策争论。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Quiet taxation turns the cargo into revenue before it becomes public evidence for global trade. The treasury benefits, but the debate loses a vivid chance to make the world economy feel real.
- rationale_zh: 悄悄征税会在货物成为全球贸易的公共证据之前，先把它变成财政收入。国库有所收益，但辩论失去了一次让世界经济变得可感可触的机会。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_cooldown
  group: public_opinion
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike GT01 Harbor Ledgers, GT04 persuades through sensory display rather than written accounts and price columns.
- Unlike GT13 Export Panic, GT04 concerns a luxury import that excites curiosity, not food exports that threaten hungry towns.
- Unlike GT20 Map of Trade Winds, GT04 is about public appetite for trade goods rather than technical navigation knowledge.
