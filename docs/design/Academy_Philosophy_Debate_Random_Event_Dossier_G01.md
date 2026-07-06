# G01 - The Chair's Summary

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Chair's Summary
- description: After three days of tangled claims, the chair reduces the argument to a brief that even the restless back benches can follow. The room changes as soon as everyone can see what is truly being disputed.
- option_a: Publish the summary.
- option_b: Redact the dangerous passages.

## Chinese Text
- title: 主席的摘要
- description: 三天缠绕不清的论辩之后，主席把争点压成一份连后排听众也能读懂的简报。众人一旦看清真正的分歧，室内的气氛立刻改变。
- option_a: 公布摘要。
- option_b: 删去危险段落。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Publishing the chair's brief makes the current issue legible outside the inner circle, so wavering listeners become more willing to accept the argument rather than fear it.
- rationale_zh: 公布主席简报会让当前议题不再只属于少数内圈，摇摆的旁听者更容易理解并接受论点，而不是先被它吓退。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Redaction keeps order and spares officials from defending volatile language, but it also makes the issue look too dangerous to embrace openly.
- rationale_zh: 删节能维持秩序，也让官僚免于替尖锐文字辩护，但这会显得该议题过于危险，不宜公开接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike G02, which is about who is allowed to witness the debate, G01 is about whether the Academy's own reasoning becomes clear enough to persuade observers.
- Unlike G03, which hinges on a suspect quotation, G01 uses an official summary and therefore shifts trust through clarity, censorship, and bureaucratic caution.
- Unlike G06, where ministries demand formal records, G01 begins inside the debate chamber with the chair deciding how much of the argument should be made readable.
