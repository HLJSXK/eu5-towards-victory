# GT06 - Insurance for Ships

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Insurance for Ships
- description: Merchants place storm accounts, wreck inventories, and survivor statements before the Academy. Their argument is blunt: a realm that shares distant profit must also learn to share distant loss.
- option_a: Recognize maritime insurance.
- option_b: Treat loss as private risk.

## Chinese Text
- title: 船舶保险
- description: 商人把风暴记录、沉船清单和幸存者证词摆到学院面前。他们的论点很直接：既然国家要分享远洋利润，就必须学会分担远洋损失。
- option_a: 承认海运保险。
- option_b: 将损失视为私人风险。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Recognizing maritime insurance turns global trade from a gamble for reckless merchants into a disciplined system of shared risk, making acceptance easier for listeners who fear sudden ruin.
- rationale_zh: 承认海运保险，会把全球贸易从鲁莽商人的赌博变成有制度约束的共同分险机制，使害怕突发破产的听众更容易接受这一议题。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_maritime_insurance_pool
  months: 24
  effects:
    shared voyage-loss risk: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Treating shipwreck as private misfortune reassures moralists who distrust speculative contracts, but it leaves overseas commerce looking fragile and personally ruinous.
- rationale_zh: 将海难视为私人不幸，可以安抚不信任投机契约的道德保守派，但也会让远洋贸易显得脆弱且足以毁掉个人家产。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.02
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike GT15 Naval Escort Debate, GT06 asks whether merchants may pool commercial risk rather than whether the state should spend money protecting ships.
- Unlike GT11 Caravan and Convoy, GT06 is about financial treatment of loss, not about tying inland and maritime route privileges together.
- Unlike GT04 Spice Cargo, GT06 does not persuade through exotic goods or spectacle; it persuades through contracts, actuarial trust, and fear of ruin.
