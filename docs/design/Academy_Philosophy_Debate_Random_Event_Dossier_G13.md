# G13 - Instrument in the Hall

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Instrument in the Hall
- description: A working instrument is carried into the debate chamber and placed where theory can no longer pretend to be alone. Its gears, lenses, or measures do not settle every question, but they do make old abstractions sweat.
- option_a: Trust the demonstration.
- option_b: Call it preliminary.

## Chinese Text
- title: 会场中的仪器
- description: 一件能够运作的仪器被抬进辩论厅，摆在理论再也无法假装孤身作战的位置。齿轮、镜片或刻度未必能解决所有问题，却足以让旧有的抽象说法冒汗。
- option_a: 相信演示。
- option_b: 称其仍属初步。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Trusting the demonstration lets visible practice overwhelm hesitation, but conservative estates lose satisfaction because the chamber has allowed a device to outrank inherited authority.
- rationale_zh: 相信演示让可见实践压过犹疑，但保守阶层会降低满意度，因为会场等于承认一件器物可以压过继承而来的权威。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
```

### Option B
- progress_delta: -5
- rationale_en: Calling the result preliminary preserves the older interpretive order, yet scholars resent seeing a working proof treated as if it were only a curiosity.
- rationale_zh: 称其仍属初步可以保住旧有解释秩序，但学者们会不满于一项可运作的证明被降格为单纯奇物。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike G05, where persuasion comes from the Chief Scientist's private lecture, this event centers on a public material demonstration.
- Unlike G03 or G12, the evidence is not textual; the side effect is estate discomfort with practical proof displacing inherited authority.
- Unlike G15, this is not a formal adversarial challenge but a staged encounter between theory and instrument.
