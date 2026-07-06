# GT18 - Distant Price Shock

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Distant Price Shock
- description: News arrives that a price changed abroad, and local plans collapse before the officials can finish insisting that foreign markets are far away. The Academy hears the distance between ports shrink into a number.
- option_a: Accept global exposure.
- option_b: Blame speculators.

## Chinese Text
- title: 远方价格震荡
- description: 海外价格变动的消息传来，本地安排在官员尚未说完“外国市场很遥远”之前就已经塌陷。学院听见港口之间的距离缩成了一个数字。
- option_a: 接受全球性风险。
- option_b: 指责投机者。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Accepting global exposure admits the central premise of Global Trade: distant prices now shape local policy. The debate moves forward because denial is replaced by adaptation, even if the adjustment hurts.
- rationale_zh: 接受全球性风险等于承认全球贸易的核心前提：远方价格已经能塑造本地政策。辩论因以适应取代否认而推进，即使调整会带来痛感。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: -1
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Blaming speculators gives anger a convenient target and makes the shock feel like misconduct rather than interdependence. That protects the old argument by refusing to learn from the price signal.
- rationale_zh: 指责投机者为怒气提供了方便的靶子，把震荡说成恶行而不是相互依赖。它拒绝从价格信号中学习，因此保护了旧论点。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT04 Spice Cargo, GT18 is not about the persuasive spectacle of an exotic good; it is about invisible price movement forcing policy change.
- Unlike GT13 Export Panic, GT18 begins with external market volatility rather than domestic hunger turning exports into a moral crisis.
- Unlike GT07 Smuggler's Map, GT18 reveals legal interdependence through prices, not illegal efficiency through contraband routes.
