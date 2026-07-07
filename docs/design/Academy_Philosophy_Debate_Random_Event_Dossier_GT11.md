# GT11 - Caravan and Convoy

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Caravan and Convoy
- description: Inland caravan masters and sea captains argue over which route deserves state support. In the Academy chamber, road dust and salt spray are both presented as proof that the realm must learn to treat distance as one connected system.
- option_a: Link caravan to convoy.
- option_b: Keep route privileges separate.

## Chinese Text
- title: 商队与护航船队
- description: 内陆商队首领与海上船长争论哪条路线更值得国家扶持。在学院辩论厅里，路上的尘土和海上的盐雾都被说成证据，证明王国必须学会把遥远距离视为同一套相连的体系。
- option_a: 将商队与船队衔接起来。
- option_b: 保持路线特权分立。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Linking caravans to convoys treats global trade as an integrated system rather than a rivalry between routes. Acceptance rises sharply, but the treasury must pay for coordination and maritime merchants gain a reason to back the debate.
- rationale_zh: 将商队与船队衔接起来，等于把全球贸易视为一套整合体系，而不是几条路线之间的争宠。接受度会明显上升，但国库必须支付协调成本，海贸商人也会因此更有理由支持辩论。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping route privileges separate reassures established carriers and local brokers that their old lanes will not be folded into a larger plan. The debate loses momentum because global trade looks like optional coordination rather than a new order.
- rationale_zh: 保持路线特权分立，会安抚既有承运人和地方掮客，让他们相信旧有通道不会被纳入更大的规划。辩论因此失去动力，因为全球贸易看起来只是可有可无的协调，而不是一种新秩序。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT10 Standard Weights, which standardizes market measurement, GT11 asks whether physically separate trade routes should be connected by policy.
- Unlike GT15 Naval Escort Debate, this event is about coordinating inland and maritime logistics rather than paying for military protection at sea.
- Unlike GT20 Map of Trade Winds, GT11 deals with institutional route support, not navigational knowledge.
