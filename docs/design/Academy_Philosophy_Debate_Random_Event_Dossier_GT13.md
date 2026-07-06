# GT13 - Export Panic

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Export Panic
- description: A poor harvest makes exports look like treason to hungry towns. Merchants insist that contracts keep future grain moving; the crowd outside wants to know why tomorrow's trust should outrank tonight's bread.
- option_a: Regulate but continue trade.
- option_b: Halt exports broadly.

## Chinese Text
- title: 出口恐慌
- description: 一场歉收让饥饿城镇眼中的出口几乎像是叛国。商人坚持契约能保证未来粮食流通，门外的人群却想知道，为什么明日的信用应当高过今晚的面包。
- option_a: 加以监管，但继续贸易。
- option_b: 广泛停止出口。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Regulating but continuing trade makes acceptance conditional on visible restraint. The debate advances only modestly because the policy preserves global exchange, but public order must absorb the anger of hungry towns.
- rationale_zh: 加以监管但继续贸易，意味着接受全球贸易必须附带可见的约束。辩论只会小幅推进，因为政策保住了全球交换，却也必须用公共秩序来承受饥饿城镇的怒气。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: -1
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Halting exports broadly lets immediate scarcity condemn the wider principle of global trade. Public anger cools, but the debate turns sharply toward rejection because markets are treated as a danger when food is short.
- rationale_zh: 广泛停止出口，会让眼前的短缺定罪整个全球贸易原则。民愤会缓和，但辩论会明显转向拒绝，因为粮食不足时，市场被描绘成危险本身。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.04
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT04 Spice Cargo, where imported luxury changes imagination, GT13 tests global trade under scarcity and fear.
- Unlike GT18 Distant Price Shock, which begins with a foreign market movement, GT13 begins with a domestic harvest crisis.
- Unlike GT14 Port Quarantine, the public emergency is food supply rather than disease control.
