# B12 - Tax Farm Accounts

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Tax Farm Accounts
- description: Tax farmers object that transparent finance will make their profession less profitable, which is true and therefore very badly received. Their ledgers arrive tied in ribbon, as if ribbon could make rents look like service.
- option_a: Audit the farms.
- option_b: Preserve tax custom.

## Chinese Text
- title: 包税账目
- description: 包税人抗议说，透明财政会让他们的行当不再那么有利可图；这话是真的，所以格外刺耳。他们把账簿用缎带捆好送来，仿佛缎带能把租利装扮成服务。
- option_a: 审计包税账目。
- option_b: 保留税收惯例。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Auditing tax farms turns banking reform into a direct attack on opaque fiscal privilege. It strongly advances acceptance, but nobles and revenue contractors resent losing the profitable shadows around collection.
- rationale_zh: 审计包税把银行改革变成对不透明财政特权的直接挑战。它会大幅推动接受改革，但贵族和承包税收者会怨恨征收过程中的有利阴影被驱散。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.04
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Preserving custom keeps short-term collections comfortable and avoids a fight with entrenched contractors, but it concedes that finance should remain private knowledge guarded by privileged hands.
- rationale_zh: 保留惯例能让短期税收显得安稳，也能避免同根深蒂固的承包人开战，但这等于承认财政仍应是由特权之手守护的私人知识。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B01 Double-Entry Demonstration, which proves a technique inside merchant bookkeeping, B12 asks whether the state will expose an entire revenue system to that discipline.
- Unlike B09 Fraudulent Ledger, where a single beautiful fraud becomes evidence for standards, B12 targets a legally tolerated structure whose profits depend on limited visibility.
- Unlike B20 Crown Account Published, which risks the Crown's own legitimacy through disclosure, B12 begins with delegated tax collection and the contractors who benefit from opacity.
