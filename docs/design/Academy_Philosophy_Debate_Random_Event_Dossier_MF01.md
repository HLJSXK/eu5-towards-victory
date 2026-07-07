# MF01 - Workshop Under One Roof

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Workshop Under One Roof
- description: A merchant lays out the case for bringing spinners, finishers, clerks, and overseers beneath one roof. The bell above the yard sounds less like a tool than a new argument about how work should be ordered.
- option_a: Back the model.
- option_b: Keep dispersed workshops.

## Chinese Text
- title: 同檐工坊
- description: 一名商人陈述把纺工、整饰工、账房和监工集中到同一屋檐下的好处。院门上方的钟声听起来不像工具，更像一场关于劳动秩序的新论证。
- option_a: 支持这种模式。
- option_b: 保留分散工坊。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Backing the shared-roof model turns manufactory theory into a visible institution: labor can be sequenced, supervised, and compared in one place. That strongly advances acceptance, while older guild households resent losing control over pace and custom.
- rationale_zh: 支持同檐模式会把工场理论变成可见制度：劳动可以在一处被排序、监督和比较。因此它会强力推动接受制造工场理念，但旧式行会家庭会怨恨节奏与惯例不再由自己掌握。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.04
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Keeping work dispersed protects guild habits and household production from the discipline of a centralized bell. The debate moves sharply toward rejection because manufactories remain easy to describe as an unnecessary assault on proven custom.
- rationale_zh: 保留分散生产能保护行会习惯和家庭工坊，使其不受集中钟声的约束。辩论会明显转向拒绝，因为制造工场仍可被说成是对可靠旧俗的不必要侵犯。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike MF02 Guild Master's Complaint, MF01 is not about quality inspection; it asks whether concentrated labor itself is legitimate.
- Unlike MF03 Waterwheel Proposal, MF01 centers on social organization and supervision rather than mechanical power or disruption around a water site.
- Unlike MF17 Workshop School, this event concerns where workers labor, not whether manufactories replace guild apprenticeship as a training system.
