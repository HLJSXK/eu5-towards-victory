# NW15 - Colonial Charter Abuse

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Colonial Charter Abuse
- description: A charter holder abuses distant authority before the principle has even won the argument at home. The scandal hands opponents a sharp question: if discovery begins this badly, what exactly is being accepted?
- option_a: Reform charters.
- option_b: Revoke the experiment.

## Chinese Text
- title: 殖民特许权滥用
- description: 一名特许权持有人在这项原则尚未于国内辩论中获胜之前，就已经滥用了远方权力。这桩丑闻给了反对者一个尖锐的问题：如果发现事业一开始就如此糟糕，我们到底是在接受什么？
- option_a: 改革特许制度。
- option_b: 撤销这场实验。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Reforming charters admits the abuse but argues that discovery can be governed instead of abandoned. Acceptance rises modestly because regulation saves the principle, while burghers lose some freedom over distant ventures.
- rationale_zh: 改革特许制度承认了滥用，却主张发现事业可以被治理，而不是被抛弃。接受度会小幅上升，因为规制挽救了原则；但市民阶层会失去一部分经营远方事业的自由。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.03
- type: temporary_country_modifier
  key: tv_academy_debate_reformed_colonial_charters
  months: 24
  effects:
    regulated charter oversight: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Revoking the experiment lets the scandal condemn the whole premise of distant charters. Conservatives approve because the realm chooses familiar authority over risky overseas delegation, and the debate moves sharply toward rejection.
- rationale_zh: 撤销这场实验会让丑闻定罪整个远方特许的前提。保守派会赞成，因为王国选择了熟悉的权威，而不是危险的海外授权；辩论也会明显转向拒绝。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
- type: seat_stance
  group: maritime_merchants
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike NW04 Merchants Want Charter, NW15 begins after delegated authority has already misbehaved, so the question is oversight or cancellation rather than whether to issue a first charter.
- Unlike NW11 Rumor of Gold, this event is about institutional abuse by a named charter holder, not loose speculation before voyages are organized.
- Unlike NW12 Foreign Claim, the threat comes from domestic governance failure across the sea, not from a rival court pressing an external claim.
