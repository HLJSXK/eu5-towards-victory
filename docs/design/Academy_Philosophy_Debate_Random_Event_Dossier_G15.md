# G15 - Formal Challenge

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Formal Challenge
- description: A respected opponent challenges the new claim under rules strict enough to make evasion visible. The hall grows quieter, not because tempers have cooled, but because everyone can now count the blows.
- option_a: Back the new argument.
- option_b: Back the old reading.

## Chinese Text
- title: 正式挑战
- description: 一位受人尊重的反对者依照严密规则挑战新主张，严密到任何回避都会显形。大厅安静下来，并非怒气消散，而是因为每个人都能数清交锋的回合。
- option_a: 支持新论证。
- option_b: 支持旧解读。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Backing the new argument rewards open contest and gives the scholarly community confidence that rigorous challenge can strengthen acceptance rather than freeze it.
- rationale_zh: 支持新论证奖励公开交锋，也让学术共同体相信严密挑战能够巩固接受方，而不是让辩论停滞。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Backing the old reading lets conservative seats claim that the rules exposed weakness in the new claim, increasing their confidence in resistance.
- rationale_zh: 支持旧解读使保守席位能够声称严密规则暴露了新主张的弱点，从而增强其反对的信心。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike G13, which asks whether to trust a demonstration, this event asks which side wins under formal argumentative rules.
- Unlike G09, social prestige and ridicule are secondary; the pressure comes from a respected opponent forcing a structured contest.
- Unlike G19, no accusation or panic drives the choice: the challenge is legitimate, public, and procedurally clean.
