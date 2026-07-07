# P09 - Foreign Press Copies Us

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Foreign Press Copies Us
- description: A foreign press reprints Academy arguments with errors, insults, and impressive speed.
- option_a: Answer in print.
- option_b: Ignore foreign noise.

## Chinese Text
- title: 外国印刷所转载我方论点
- description: 一家外国印刷所带着错误、讥讽和惊人的速度转载了学院论点。
- option_a: 以印刷回应。
- option_b: 忽视外国噪音。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Answering in print shows that the Academy can fight distortion with the same medium, though defending intellectual authority abroad costs prestige.
- rationale_zh: 以印刷回应表明学院能用同一种媒介反击歪曲，但在国外维护学术权威需要消耗威望。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -5
```

### Option B
- progress_delta: -5
- rationale_en: Ignoring the reprint keeps diplomatic tempers lower, but it leaves foreign printers to define the Academy's argument without reply.
- rationale_zh: 忽视转载能降低外交火气，却把学院论点的解释权交给外国印刷者而不作回应。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: foreign_power
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike P11, the printed text crossing distance is an uncontrolled foreign reprint, not a standardized domestic proclamation.
- Unlike P17, the issue is hostile or careless reproduction abroad rather than deliberate multilingual access at home.
- Unlike P20, the obstacle is foreign distortion, not a domestic censor delaying approval.
