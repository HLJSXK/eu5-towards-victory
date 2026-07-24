# P20 - The Censor's Delay

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Censor's Delay
- description: The censor takes so long that the issue risks dying politely in a locked drawer.
- option_a: Bypass the delay.
- option_b: Respect the process.

## Chinese Text
- title: 审查官的拖延
- description: 审查官拖得太久，以至于这项议题可能体面地死在上锁抽屉里。
- option_a: 绕过拖延程序。
- option_b: 尊重既定流程。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Bypassing the censor prevents procedure from smothering the issue and proves that printing can outrun official delay, though legitimacy suffers from the irregular route.
- rationale_zh: 绕过审查官能防止程序闷死议题，并证明印刷术可以跑过官样拖延，但这种非常规路径会损害正统性。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -5
```

### Option B
- progress_delta: -10
- rationale_en: Respecting the process lets bureaucrats define delay as prudence, sharply weakening the case that printing needs faster channels of approval.
- rationale_zh: 尊重既定流程会让官僚把拖延定义成审慎，从而明显削弱印刷术需要更快审批渠道的论点。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike P01, the timing problem is a mature censorial bottleneck rather than the first pamphlets outrunning definitions.
- Unlike P03, the barrier is bureaucratic delay, not a clerical index meant to classify dangerous books.
- Unlike P13, central control appears as procedural obstruction rather than as a proposed central print office.
