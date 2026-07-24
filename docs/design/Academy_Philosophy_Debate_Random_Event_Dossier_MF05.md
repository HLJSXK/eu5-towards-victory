# MF05 - Raw Material Bottleneck

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Raw Material Bottleneck
- description: Production stalls because wool, timber, dye, or ore still arrives by village habit rather than manufactory appetite. The machines and benches wait while the countryside insists that supply has seasons, neighbors, and old obligations.
- option_a: Organize supply contracts.
- option_b: Limit production to supply custom.

## Chinese Text
- title: 原料瓶颈
- description: 生产停滞了，因为羊毛、木材、染料或矿石仍按村庄习惯抵达，而不是按制造工场的胃口供应。机器与工作台只能等待，乡间则坚持供应自有季节、邻里和旧义务。
- option_a: 组织供应契约。
- option_b: 让产量服从供应旧俗。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Supply contracts make manufactories practical by connecting rural inputs to predictable urban production. The gain is moderate because it solves a bottleneck rather than proving the whole system, and merchants welcome the clearer obligations.
- rationale_zh: 供应契约把乡村投入与可预测的城市生产连接起来，使制造工场更具可行性。推进幅度适中，因为它解决的是瓶颈，而非证明整个制度；商人会欢迎更清楚的义务关系。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Limiting production to supply custom keeps rural obligations, seasonal movement, and local bargaining intact. Acceptance falls because manufactories are forced to match the old rhythm instead of reorganizing the material chain around scale.
- rationale_zh: 让产量服从供应旧俗，能保留乡村义务、季节性流动和地方议价。接受度会下降，因为制造工场被迫适应旧节奏，而不是围绕规模重组原料链条。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.03
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike MF03 Waterwheel Proposal, MF05 is about inputs and contracts before production begins, not the power source used during production.
- Unlike MF12 Factory Accounts, MF05 addresses physical supply flow rather than accounting visibility after goods and waste enter the books.
- Unlike MF19 Merchant Capital Pool, this event gives merchants leverage through procurement discipline, not through pooled ownership of a large manufactory.
