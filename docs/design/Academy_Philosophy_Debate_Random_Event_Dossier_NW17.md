# NW17 - Treaty of Unknown Shores

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Treaty of Unknown Shores
- description: Diplomats ask whether shores still half-imagined by mapmakers can already be divided by ink. The Academy's argument is suddenly not only about what exists, but about who may claim the right to arrive there first.
- option_a: Assert navigational rights.
- option_b: Refuse distant entanglement.

## Chinese Text
- title: 未知海岸条约
- description: 外交官询问，那些制图师还只能半凭想象描绘的海岸，是否已经可以用墨水分割。学院的争论忽然不只关乎那里是否存在，也关乎谁有权声称自己可以率先抵达。
- option_a: 宣示航行权利。
- option_b: 拒绝远方纠葛。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Asserting navigational rights makes the New World claim a matter of state doctrine before every detail is known. It drives acceptance sharply forward, while foreign powers harden against the realm's confidence.
- rationale_zh: 宣示航行权利，会在细节尚未完全明朗前把新世界主张提升为国家原则。这会强力推动接受方向，但也会让外国势力因本国的自信而转为警惕。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: oppose
  cooldown_months: 24
- type: foreign_prestige
  amount: -5
```

### Option B
- progress_delta: -10
- rationale_en: Refusing entanglement lets caution define policy and avoids converting uncertain maps into diplomatic obligations. The debate retreats strongly because the court chooses safety over the legal imagination of discovery.
- rationale_zh: 拒绝远方纠葛，会让谨慎成为政策原则，并避免把不确定的地图变成外交义务。由于宫廷选择安全而不是发现所需要的法律想象，辩论会明显转向拒绝。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike NW12 Foreign Claim, NW17 is not a reaction to a rival's specific assertion but a proactive debate over whether unknown shores can be bound by treaty at all.
- Unlike NW10 Naval Officers Demand Funds, this event tests legal and diplomatic will rather than shipbuilding capacity or treasury support.
- Unlike NW01 The Sailor's Chart, NW17 moves beyond evidence of coastlines into the question of sovereign rights over places still imperfectly known.
