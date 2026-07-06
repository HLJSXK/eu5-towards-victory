# MF18 - Quality Scandal

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Quality Scandal
- description: A large batch fails inspection in public: seams split, fittings crack, and the opponents of scale look almost grateful for the evidence. The question is whether the failure condemns the system or merely the inspectors.
- option_a: Improve inspection and continue.
- option_b: Blame scale itself.

## Chinese Text
- title: 质量丑闻
- description: 一大批货物当众未能通过检验：缝线裂开，配件崩断，反对规模化的人几乎要感谢这份证据。眼下的问题是，这次失败究竟定罪的是整个制度，还是只是检验者。
- option_a: 改进检验并继续推进。
- option_b: 指责规模本身。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Improving inspection admits the scandal without surrendering the manufactory model. Acceptance rises moderately because reformers show that scale can correct itself, but prestige is spent to survive the embarrassment.
- rationale_zh: 改进检验意味着承认丑闻，却不放弃制造工场模式。接受度会适度上升，因为改革者证明规模化可以自我纠正，但国家必须花费威望来熬过这场难堪。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -5
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Blaming scale itself turns a bad batch into a moral lesson against concentration, speed, and oversight by strangers. The rejection is moderate because the scandal is real, and conservative readers of the evidence gain confidence.
- rationale_zh: 指责规模本身，会把一批劣货变成反对集中、速度和外来监督的道德教训。拒绝幅度适中，因为丑闻确实存在，而保守派会从这份证据中获得信心。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike MF02 Guild Master's Complaint, MF18 responds to an actual failed batch rather than a preventive guild warning about standards.
- Unlike MF06 Fire in the Yard, this scandal is about product quality and public trust, not safety damage from a workshop accident.
- Unlike MF11 Standard Parts, MF18 asks whether failed standardization discredits scale, rather than whether standardization should be promoted in the first place.
