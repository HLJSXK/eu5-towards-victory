# SR07 - A Prediction Comes True

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Prediction Comes True
- description: A calculation names the hour of a natural event, and the event arrives with uncomfortable punctuality. For a moment, even the skeptics have to decide whether coincidence has learned mathematics.
- option_a: Publicize the prediction.
- option_b: Call it coincidence.

## Chinese Text
- title: 预言成真
- description: 一项计算预告了一场自然现象的时刻，而那现象竟准时到来。片刻之间，连怀疑者也不得不判断：巧合是否已经学会了数学。
- option_a: 宣扬这次预测。
- option_b: 称它只是巧合。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publicizing the prediction gives the new method a visible victory: it did not merely explain the past, it anticipated the world before witnesses.
- rationale_zh: 宣扬这次预测会让新方法获得一场可见的胜利：它不只是解释过去，而是在众人面前预见了世界。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: 10
- type: temporary_country_modifier
  key: tv_academy_debate_prediction_expectations
  months: 24
  effects:
    public expectation after accurate prediction: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Calling the success coincidence calms conservative listeners and avoids giving reformers a triumphal example, but it makes predictive evidence easier to dismiss.
- rationale_zh: 称其为巧合能安抚保守听众，也避免给改革派一个胜利样本，但这会让预测性证据更容易被轻视。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike SR03, where mathematics persuades through proof inside the chamber, SR07 lets a timed event outside the chamber verify the calculation.
- Unlike SR13, which risks a public experiment that could fail in front of witnesses, SR07 begins after the result has already embarrassed skeptics by coming true.
- Unlike SR01, which relies on repeated tables of observation, SR07 centers on prediction as the distinctive power of the new method.
