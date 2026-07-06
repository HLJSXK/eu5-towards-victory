# G18 - Allegory on Canvas

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Allegory on Canvas
- description: An artist paints the issue as a scene so flattering to novelty that even its opponents stop to inspect the colors. The argument has learned to wear light.
- option_a: Exhibit the work
- option_b: Keep art out of doctrine

## Chinese Text
- title: 画布上的寓言
- description: 一位艺术家把议题画成一幅格外偏爱新意的场景，连反对者也停下来端详色彩。争论仿佛学会了披上光线。
- option_a: 展出这幅作品
- option_b: 让艺术远离教义

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Exhibition turns abstract reasoning into a shared image, nudging undecided viewers toward acceptance while rewarding the artists who made novelty attractive.
- rationale_zh: 展出作品会把抽象推理变成可以共同观看的图像，推动犹疑者走向接受，同时奖励那些让新意变得动人的艺术家。
- effect_blocks:
```yaml
- type: artist_skill
  amount: 0.05
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Excluding art keeps the debate in safer doctrinal language and reassures religious conservatives, but it wastes a persuasive bridge to the wider court.
- rationale_zh: 排除艺术可以让辩论停留在更安全的教义语言中，并安抚宗教保守派，但也浪费了通向更广泛宫廷听众的说服桥梁。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: artists
  stance: neutral
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike G14 Street Song, this event uses elite visual allegory rather than popular music spreading through the streets.
- Unlike G09 Salon Ridicule, the artistic intervention dignifies novelty instead of turning the debate into aristocratic mockery.
- Unlike G13 Instrument in the Hall, the persuasion comes from representation and patronage, not from a material demonstration.
