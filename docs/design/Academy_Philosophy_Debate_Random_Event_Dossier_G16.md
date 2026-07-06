# G16 - Committee Exhaustion

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Committee Exhaustion
- description: Everyone knows another month of debate will produce longer speeches, not better reasons. The committee has begun perfecting its objections instead of testing them.
- option_a: Force a decision
- option_b: Postpone

## Chinese Text
- title: 委员会疲惫
- description: 人人都明白，再辩一个月只会让发言更长，而不会让理由更好。委员会已经开始打磨反对意见，而不是检验它们。
- option_a: 强行作出决定
- option_b: 暂且延期

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Forcing the committee to decide converts procedural fatigue into decisive movement toward acceptance, but it makes hesitant observers feel pressured rather than persuaded.
- rationale_zh: 强迫委员会作出决定，会把程序性的疲惫转化为推动接受的明确动力，但也会让犹疑的旁观者觉得自己是被压服，而不是被说服。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
```

### Option B
- progress_delta: -5
- rationale_en: Postponement avoids an ugly procedural fight and gives doubters room to breathe, but it signals that the new claim cannot yet survive a verdict.
- rationale_zh: 延期可以避免难看的程序冲突，也给怀疑者喘息空间，但这等于承认新论点尚经不起裁决。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: court_bureaucrats
  cooldown_months: 6
```

## Difference From Same Issue Events
- Unlike G15 Formal Challenge, this event is about procedural fatigue rather than a rule-bound intellectual test.
- Unlike G20 Consensus After Midnight, pressure here comes from institutional impatience, not from exhausted opponents accidentally conceding substance.
- Unlike G06 Minutes for the Ministries, the bureaucratic form has already failed to clarify the dispute; the choice is whether to end the process.
