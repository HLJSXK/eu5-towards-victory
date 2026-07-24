# GT09 - Rival Trade Embassy

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Rival Trade Embassy
- description: A rival court sends merchants with gifts, draft contracts, and compliments polished until they almost pass for friendship. Every offer smells faintly of opportunity and leverage.
- option_a: Receive them openly.
- option_b: Restrict their access.

## Chinese Text
- title: 敌手的贸易使团
- description: 一个敌对宫廷派来商人，带着礼物、契约草案和打磨得几乎像友谊的恭维话。每一项提议都同时带着机会和牵制的气味。
- option_a: 公开接待他们。
- option_b: 限制他们的接触。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Receiving the embassy openly treats global trade as diplomacy conducted through contracts as well as envoys. The gain is modest because deeper contact creates opportunity while admitting rival influence into the debate.
- rationale_zh: 公开接待使团，是把全球贸易视为一种通过契约和使节共同进行的外交。进度提升有限，因为更深接触既带来机会，也会把敌手影响引入辩论。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_trade_embassy_reception
  months: 18
  effects:
    rival contract channels opened: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Restricting access reassures protectionists that foreign merchants will not write policy by smiling at it. It also makes the Academy's trade argument narrower and more suspicious of exchange.
- rationale_zh: 限制接触能让保护主义者放心，外国商人不会靠微笑来书写政策；但这也会使学院的贸易论证变得更狭窄、更怀疑交流。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: seat_stance
  group: foreign_power
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike GT02 Foreign Merchant Quarter, GT09 concerns diplomatic access and contract negotiation, not protected residence rights near a port.
- Unlike GT18 Distant Price Shock, GT09 brings external pressure through identifiable envoys rather than an impersonal market movement abroad.
- Unlike GT15 Naval Escort Debate, GT09 deepens trade through diplomatic reception rather than military spending or convoy protection.
