# GT14 - Port Quarantine

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Port Quarantine
- description: Quarantine officials slow trade and claim survival as their defense. Merchants call every delay a lost season; physicians answer that a busy harbor is still useless if it imports the next funeral.
- option_a: Improve quarantine systems.
- option_b: Restrict foreign ships.

## Chinese Text
- title: 港口检疫
- description: 检疫官员拖慢贸易，并以生存作为自己的辩护。商人说每一次延误都是失去一个季节，医师则回答，若港口带来的下一批货物是葬礼，再繁忙的码头也毫无用处。
- option_a: 改善检疫体系。
- option_b: 限制外国船只。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Improving quarantine systems argues that global trade can be made safer without closing the harbor. Acceptance rises modestly because the reform removes a practical objection, while the treasury pays for inspection capacity.
- rationale_zh: 改善检疫体系，等于主张全球贸易可以在不关闭港口的前提下变得更安全。改革消除了一个实际反对理由，因此接受度小幅上升，但国库必须支付检查能力的成本。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: temporary_country_modifier
  key: tv_academy_debate_quarantine_reform
  months: 18
  effects:
    health inspection capacity: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Restricting foreign ships makes safety visible by narrowing the flow of trade. The debate loses ground because foreign exchange is treated as the problem itself, even if the public sees the port acting decisively.
- rationale_zh: 限制外国船只，会通过缩窄贸易流动来展示安全感。辩论因此后退，因为外国交换被当成问题本身，哪怕民众会看到港口正在果断行动。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_visible_port_closure
  months: 12
  effects:
    visible disease precautions: 0.02
```

## Difference From Same Issue Events
- Unlike GT02 Foreign Merchant Quarter, which concerns legal space for foreign merchants, GT14 concerns health control over ships entering the port.
- Unlike GT13 Export Panic, this event balances disease prevention against trade flow rather than food security against export contracts.
- Unlike GT15 Naval Escort Debate, GT14 frames port security as public health rather than naval protection.
