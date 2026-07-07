# G20 - Consensus After Midnight

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Consensus After Midnight
- description: By candlelight, tired opponents accidentally admit which points they can no longer deny. No one calls it agreement yet, but everyone hears the shape of it.
- option_a: Keep them in session
- option_b: Adjourn with dignity

## Chinese Text
- title: 午夜后的共识
- description: 烛光之下，疲惫的反对者无意中承认了哪些论点已经无法否认。还没有人称之为同意，但所有人都听见了它的轮廓。
- option_a: 让他们继续开会
- option_b: 体面休会

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Keeping the session going captures a fragile moment of convergence before pride returns, but it strains the intellectual staff holding the room together.
- rationale_zh: 继续开会可以在自尊回潮之前抓住脆弱的趋同瞬间，但也会消耗维持会场运转的智识骨干。
- effect_blocks:
```yaml
- type: scientist_attribute
  adm: -1
  dip: 0
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 9
```

### Option B
- progress_delta: -5
- rationale_en: Adjournment preserves decorum and lets exhausted opponents leave without humiliation, but it allows the emerging consensus to cool overnight.
- rationale_zh: 休会能保全体面，让疲惫的反对者不必带着羞辱离开，但也会让刚浮现的共识在一夜之间冷却。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: scholarly_community
  cooldown_months: 6
```

## Difference From Same Issue Events
- Unlike G16 Committee Exhaustion, this event finds real intellectual convergence inside fatigue rather than using fatigue as a reason to force procedure.
- Unlike G05 Private Lecture at Dusk, the late-night pressure comes from collective debate, not from the Chief Scientist personally tutoring decisive listeners.
- Unlike G15 Formal Challenge, the outcome is accidental consensus rather than victory under strict adversarial rules.
