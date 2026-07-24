# M07 - Clerical Certificates

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clerical Certificates
- description: Clergy propose that no one should hold public office without moral certification, making virtue the gate through which ability must ask permission.
- option_a: Require ability first.
- option_b: Accept moral certification.

## Chinese Text
- title: 教士证明
- description: 教士们提出，凡任公职者都应先取得道德证明，让德行成为才能必须叩问的门槛。
- option_a: 先考能力。
- option_b: 接受道德证明。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Prioritizing ability keeps appointment standards testable and secular enough for meritocratic debate, but it costs clerical satisfaction by limiting religious veto power.
- rationale_zh: 优先考察能力能让任命标准保持可检验，并使任人唯才的讨论不被宗教否决权先行截断，但会降低教士满意度。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.04
```

### Option B
- progress_delta: -5
- rationale_en: Accepting moral certificates reassures the clergy, yet it places a corporate approval filter ahead of demonstrated competence.
- rationale_zh: 接受道德证明能安抚教士，却把团体认可置于实际才干之前。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike M01, which hides names to judge written performance, M07 debates whether a non-technical moral gate should precede any assessment at all.
- Unlike M15, which centers on Academy teaching chairs and patron rights, M07 concerns public appointments and clerical certification outside the Academy's own offices.
- Unlike M13, which tests language access for provincial candidates, M07 tests institutional access controlled by religious authority.
