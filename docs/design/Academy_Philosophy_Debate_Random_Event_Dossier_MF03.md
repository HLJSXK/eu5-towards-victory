# MF03 - Waterwheel Proposal

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Waterwheel Proposal
- description: Engineers sketch a water-powered process that would pull, pound, and turn with an appetite no hand can match. The river suddenly seems less like scenery and more like an employee waiting to be hired.
- option_a: Build the works.
- option_b: Refuse mechanized pressure.

## Chinese Text
- title: 水轮提案
- description: 工程师绘出一种由水力驱动的工序，能拉、捶、转，其胃口远非人手可比。那条河忽然不再只是风景，而像一名等待受雇的工人。
- option_a: 兴建水力工场。
- option_b: 拒绝机械化压力。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Building the works proves that manufactories can command natural force rather than merely gather workers together. The argument surges forward, but nearby communities bear the disruption of channels, rights, and altered routines.
- rationale_zh: 兴建水力工场证明制造工场不仅能集中工人，还能调动自然之力。论点会大幅推进，但附近社区必须承受水渠、水权和日常节奏被改动的扰动。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: -0.04
- type: temporary_country_modifier
  key: tv_academy_debate_waterwheel_disruption
  months: 18
  effects:
    local construction disruption near water sites: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Refusing mechanized pressure protects rural rhythms from being bent around wheels, races, and mill rights. It strongly weakens acceptance because the debate retreats from the most tangible proof that production can be transformed.
- rationale_zh: 拒绝机械化压力能保护乡村节奏，使其不必围着水轮、引水渠和磨坊权利重新安排。它会强烈削弱接受倾向，因为辩论退避了生产可被改造的最直观证据。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.04
- type: seat_stance
  group: peasants
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike MF01 Workshop Under One Roof, MF03 makes mechanical power the decisive issue instead of managerial concentration.
- Unlike MF05 Raw Material Bottleneck, MF03 concerns the energy and process side of production rather than the supply contracts feeding it.
- Unlike MF14 Imported Machine, this event can arise from domestic engineering and water rights rather than dependence on a foreign device.
