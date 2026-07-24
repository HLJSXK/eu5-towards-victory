# SR06 - Clerical Cosmology Objection

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clerical Cosmology Objection
- description: Clergy warn that the new model rearranges more than the heavens. If the sky can be argued from observation, sermons, courts, and crowns may all be asked to explain what else they have inherited without proof.
- option_a: Defend inquiry.
- option_b: Soften the model.

## Chinese Text
- title: 神职宇宙论异议
- description: 神职人员警告说，新的天体模型扰乱的不只是星辰的位置。若天空可以由观察来争辩，讲坛、法庭与王座都会被追问还有什么只是未经证明的继承。
- option_a: 捍卫探究。
- option_b: 缓和模型。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Defending inquiry makes the scientific method a matter of principle rather than a narrow astronomical quarrel, pushing the debate strongly toward acceptance while alienating clerical authority.
- rationale_zh: 捍卫探究会把科学方法提升为原则问题，而不只是狭窄的天文学争执，因此强力推动辩论走向接纳，同时疏远神职权威。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Softening the model reassures religious authorities that doctrine will not be overturned by calculation, but it teaches the Academy to retreat when observation becomes politically dangerous.
- rationale_zh: 缓和模型能让宗教权威相信教义不会被计算推翻，但也会让学院学会在观察变得危险时退让。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.05
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike SR12, where an old authority is contradicted in a scholarly footnote, SR06 makes the conflict explicitly clerical and cosmological.
- Unlike SR18, which concerns whether a dangerous treatise should be published, SR06 is about whether the Academy can defend the model before religious pressure edits it.
- Unlike SR01, which frames old authority against repeated observations in general, SR06 ties the same tension to doctrine, pulpit authority, and the social order of the heavens.
