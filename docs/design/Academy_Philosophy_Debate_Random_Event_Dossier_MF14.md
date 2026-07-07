# MF14 - Imported Machine

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Imported Machine
- description: A foreign machine is carried into the Academy with unfamiliar bolts and very familiar ambition. Its admirers see a design that can be copied; its enemies see another country reaching a metal hand into local workshops.
- option_a: Copy and adapt it.
- option_b: Reject foreign machinery.

## Chinese Text
- title: 舶来机器
- description: 一台外国机器被搬进学院，螺栓陌生，野心却十分熟悉。赞成者看见一套可以仿制的设计，反对者则看见另一个国家把金属之手伸进本地工坊。
- option_a: 仿制并改造它。
- option_b: 拒绝外国机械。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Copying and adapting the machine turns foreign example into domestic manufacturing capacity, giving the acceptance argument a dramatic proof of usefulness. The cost is both practical expense and sharper foreign unease.
- rationale_zh: 仿制并改造机器，会把外国范例转化为本国制造能力，为接受派提供极有力的实用证明。代价则是实际支出，以及更明显的对外紧张。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: foreign_power
  stance: oppose
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Rejecting the machine protects guild pride and casts foreign methods as contamination rather than opportunity. Rejection gains strong momentum because suspicion of imported technique becomes a defense of local order.
- rationale_zh: 拒绝这台机器会维护行会自尊，并把外国方法说成污染而不是机会。由于对舶来技术的怀疑被包装成维护本地秩序，拒绝方向会强烈推进。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike MF03 Waterwheel Proposal, which debates domestic mechanized pressure, MF14 centers on foreign technology and the political tension of copying it.
- Unlike MF11 Standard Parts, which concerns interchangeable design principles, MF14 concerns the transfer and adaptation of an entire machine from abroad.
- Unlike MF19 Merchant Capital Pool, which asks whether domestic capital may concentrate, MF14 asks whether external technical knowledge should be absorbed despite suspicion.
