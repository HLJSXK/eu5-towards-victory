# G06 - Minutes for the Ministries

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Minutes for the Ministries
- description: Before the Academy's arguments can touch policy, ministry clerks demand minutes exact enough to file, quote, and delay.
- option_a: Give them exact minutes
- option_b: Keep the argument informal

## Chinese Text
- title: 各部所需的会议记录
- description: 在学院的争论影响政策之前，各部文吏要求取得足以归档、引用并拖延程序的详尽记录。
- option_a: 提交详尽记录
- option_b: 让争论保持非正式

## Mechanics
### Option A
- progress_delta: -5
- rationale_en: Exact minutes turn the debate into an administrative object ministries can control, slowing acceptance while giving court bureaucrats procedural leverage.
- rationale_zh: 详尽记录会把辩论变成各部可以掌控的行政文件，减缓接受新主张的速度，同时让宫廷官僚取得程序上的筹码。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

### Option B
- progress_delta: +5
- rationale_en: Keeping the argument informal lets the new proposition keep moving before ministries can pin it down, but the Crown appears less procedurally careful.
- rationale_zh: 让争论保持非正式，可以在各部将其固定成公文之前继续推动新主张，但王权会显得不够重视程序。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -5
```

## Difference From Same Issue Events
- Unlike G01, this event is about whether the debate becomes administratively admissible, not whether the chair makes the argument intelligible.
- Unlike G15 and G16, the pressure comes from ministry record-keeping rather than a formal intellectual challenge or sheer committee exhaustion.
