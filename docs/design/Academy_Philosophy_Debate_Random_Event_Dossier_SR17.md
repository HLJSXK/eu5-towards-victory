# SR17 - Mechanic's Model

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Mechanic's Model
- description: A mechanic sets a model on the table and turns the crank. Gears translate an invisible process into motion, and the room leans forward before anyone remembers to look dignified.
- option_a: Treat models as evidence.
- option_b: Treat models as illustrations only.

## Chinese Text
- title: 机械匠的模型
- description: 一名机械匠把模型摆上桌面，转动曲柄。齿轮把看不见的自然过程翻译成运动，满屋人还没来得及端起架子，身体已经向前倾去。
- option_a: 将模型视为证据。
- option_b: 只把模型当作图解。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Treating the model as evidence modestly advances the debate by admitting that mechanical analogy can clarify natural process. It favors artisans without replacing observation, proof, or replication as stronger sources of acceptance.
- rationale_zh: 将模型视为证据，会承认机械类比能够澄清自然过程，从而温和推动辩论。它抬高工匠地位，但并不取代观测、证明或复验这些更强的接受依据。
- effect_blocks:
```yaml
- type: scientist_attribute
  adm: 0
  dip: 1
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Demoting the model to a mere illustration reassures scholars who fear workshop devices will outrank learned argument. The issue slips backward because a useful bridge between craft and theory is deliberately narrowed.
- rationale_zh: 把模型降格为单纯图解，会安抚那些担心作坊器具凌驾于学术论证之上的学者。议题因此后退，因为工艺与理论之间一座有用的桥被刻意收窄。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
- type: seat_cooldown
  group: burghers
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike SR09 Artisan Knowledge, SR17 does not let an artisan solve the disputed problem directly; it asks whether a model can make an unseen process credible.
- Unlike SR03 Mathematical Proof, SR17 persuades through mechanical resemblance and demonstration rather than abstract symbols.
- Unlike SR04 Instrument Maker's Claim, SR17 uses a specific explanatory model instead of debating investment in a wider instrument-making program.
