# NW06 - Disease Report

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Disease Report
- description: Physicians warn the Academy that new shores may bring fevers as well as coastlines. Supporters of discovery must now prove that prudence can travel on the same ships as curiosity.
- option_a: Fund precautions and proceed.
- option_b: Use disease as warning.

## Chinese Text
- title: 疾病报告
- description: 医师提醒学院，新海岸带来的不只海图，也可能有港口从未见过的热病。发现的支持者必须证明，谨慎和好奇心可以登上同一批船。
- option_a: 资助防疫并继续探索。
- option_b: 把疾病视为警告。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Funding precautions accepts the medical warning without letting fear define the whole question. The debate moves modestly toward acceptance because discovery is presented as manageable, regulated risk rather than reckless appetite.
- rationale_zh: 资助防疫意味着承认医师的警告，却不让恐惧决定整个议题。由于探索被塑造成可管理、可规制的风险，而不是鲁莽欲望，辩论会小幅转向接受。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: temporary_country_modifier
  key: tv_academy_debate_quarantine_precautions
  months: 24
  effects:
    port health inspections and voyage precautions: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Treating illness as the lesson makes caution sound responsible and gives conservative listeners a concrete danger to rally around, slowing acceptance of the New World argument.
- rationale_zh: 把疾病当作主要教训，会让谨慎显得负责任，也给保守听众一个可以共同强调的具体危险，从而减缓对新世界论点的接受。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW07 Missing Expedition, NW06 is about anticipated health risk and prevention rather than the political shock of a voyage that has already vanished.
- Unlike NW14 Sailors' Superstitions, the fear here is answered through physicians, port rules, and spending, not omens or religious reassurance.
- Unlike NW16 Imported Crop, NW06 treats biological exchange as a hazard to manage, while NW16 turns a living specimen into evidence that the unknown can become useful.
