# P10 - Scribes' Protest

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Scribes' Protest
- description: Scribes warn that movable type will starve honest hands and dishonest abbreviations alike.
- option_a: Retrain scribes for presses.
- option_b: Protect manuscript work.

## Chinese Text
- title: 抄写员抗议
- description: 抄写员警告说，活字印刷会让诚实的双手和不诚实的缩写一起挨饿。
- option_a: 重新训练抄写员操作印刷机。
- option_b: 保护手抄行业。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Retraining scribes makes the labor shock manageable and turns a threatened old profession into a bridge toward practical acceptance of the press.
- rationale_zh: 重新训练抄写员能缓和劳动力冲击，把受到威胁的旧职业变成通向实际接受印刷机的桥梁。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
```

### Option B
- progress_delta: -5
- rationale_en: Protecting manuscript work reassures old literate professions, but it deliberately slows the replacement of hand copying with reproducible type.
- rationale_zh: 保护手抄行业能安抚旧有文书职业，却有意放慢可复制活字取代手抄的进程。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike P07, this event is about displaced skilled labor rather than the paper supply needed for large print runs.
- Unlike P02, printers are not seeking legal recognition; manuscript workers are asking not to be made obsolete.
- Unlike P19, the social pressure comes from threatened scribes, not from a printer's new public fame.
