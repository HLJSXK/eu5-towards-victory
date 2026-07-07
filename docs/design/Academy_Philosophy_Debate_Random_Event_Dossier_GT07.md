# GT07 - Smuggler's Map

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Smuggler's Map
- description: A seized map marks coves, warehouses, quiet roads, and trusted signals with more care than any customs register. The illegal network is embarrassing because it works.
- option_a: Reform legal routes.
- option_b: Burn the map.

## Chinese Text
- title: 走私者的地图
- description: 一张被缴获的地图细致标出海湾、仓库、隐秘道路和可信暗号，比任何海关簿册都更周密。这个非法网络令人难堪，因为它确实有效。
- option_a: 改革合法商路。
- option_b: 烧掉地图。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Reforming legal routes admits that trade will find efficient channels with or without permission. The debate shifts toward acceptance because the state chooses to learn from the network instead of pretending it does not exist.
- rationale_zh: 改革合法商路，等于承认贸易无论是否获准都会寻找高效通道。国家选择向这个网络学习，而不是假装它不存在，因此辩论会明显转向接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Burning the map preserves the old customs order and denies smugglers any intellectual victory. It also destroys evidence that legal trade routes have become less rational than illegal ones.
- rationale_zh: 烧掉地图可以维护旧海关秩序，不让走私者在论证上占到便宜；但这也毁掉了合法商路已经不如非法商路合理的证据。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: maritime_merchants
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_old_customs_controls
  months: 18
  effects:
    customs gatekeeping preserved: 0.02
```

## Difference From Same Issue Events
- Unlike GT03 Tariff Confusion, GT07 exposes an entire informal route network rather than a mistaken written tariff schedule.
- Unlike GT19 Free Port Proposal, GT07 proposes repairing existing legal routes instead of creating a special experimental port.
- Unlike GT20 Map of Trade Winds, GT07 draws its authority from illicit practice and enforcement failure, not from navigational science.
