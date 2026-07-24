# MF15 - Coal Smoke Argument

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Coal Smoke Argument
- description: Urban residents remind the Academy that productive smoke is still smoke. Window ledges, lungs, and laundry lines become witnesses against any theory that treats output as proof enough.
- option_a: Regulate smoke and continue.
- option_b: Limit industrial sites.

## Chinese Text
- title: 煤烟之争
- description: 城中居民提醒学院，能带来产量的烟雾依旧是烟雾。窗台、肺部和晾晒的衣物一起作证，反驳那种只要产出增加便足以自证其正当性的理论。
- option_a: 管控烟尘并继续推进。
- option_b: 限制工业场址。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Regulating smoke concedes the harm without abandoning manufactories, so acceptance can advance in a more politically durable form. Gold is spent because cleaner production requires oversight and equipment.
- rationale_zh: 管控烟尘承认了伤害，却没有放弃工场，因此接受派能以更耐久的政治形式前进。由于更清洁的生产需要监督和设备，国库必须支出。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Limiting industrial sites calms local complaints and makes the old urban fabric feel protected. The debate turns slightly against acceptance because production is treated as something that must be contained.
- rationale_zh: 限制工业场址会平息地方怨言，让旧有城市肌理显得受到保护。辩论会小幅转向拒绝，因为生产被视为必须加以圈限的东西。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike MF06 Fire in the Yard, which uses a sudden accident to justify regulation, MF15 addresses chronic pollution that persists even when production succeeds.
- Unlike MF20 The First Whistle, which concerns noise and labor discipline, MF15 concerns smoke as a public-health and urban-order objection.
- Unlike MF13 Rural Displacement, which frames disruption through villages and households, MF15 frames it through townspeople living beside industrial sites.
