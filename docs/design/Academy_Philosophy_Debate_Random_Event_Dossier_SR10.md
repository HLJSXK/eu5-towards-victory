# SR10 - Natural History Cabinet

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Natural History Cabinet
- description: Collectors propose a cabinet where shells, bones, seeds, and stones are arranged by observed likeness rather than inherited categories. The old labels still fit the drawers, which is precisely the problem.
- option_a: Build the cabinet.
- option_b: Keep old classifications.

## Chinese Text
- title: 自然史陈列柜
- description: 收藏家提议建立一座陈列柜，把贝壳、骨骼、种子与石块按亲眼所见的相似性排列，而不是按继承下来的类别摆放。旧标签仍能贴进抽屉，这正是问题所在。
- option_a: 建造陈列柜。
- option_b: 保留旧分类。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Building the cabinet turns observation into a durable institutional habit, though it advances acceptance more gently than a proof, prediction, or public experiment.
- rationale_zh: 建造陈列柜会把观察变成持久的制度习惯，虽然它推动接纳的力度不如证明、预测或公开实验那样猛烈。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_observational_collections
  months: 36
  effects:
    ordered natural history collections: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping old classifications protects familiar scholarly order and avoids new expense, but it leaves observation subordinate to inherited categories.
- rationale_zh: 保留旧分类能保护熟悉的学术秩序并避免新开支，但也会让观察继续服从继承下来的类别。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 18
- type: resource
  resource: gold
  scale: 1
```

## Difference From Same Issue Events
- Unlike SR01, which relies on tables of repeated observations to defeat authority, SR10 creates a physical institution for collecting and arranging observations.
- Unlike SR14, which standardizes measurement across provinces, SR10 focuses on classification, specimens, and the discipline of looking before naming.
- Unlike SR16, where a royal observatory demands a permanent astronomical facility, SR10 is a smaller cabinet-scale investment in natural history.
