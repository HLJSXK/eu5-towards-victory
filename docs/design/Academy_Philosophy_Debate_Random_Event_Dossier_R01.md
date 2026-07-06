# R01 - A Newly Found Torso

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Newly Found Torso
- description: Laborers uncover an ancient marble torso, broken at the limbs but disturbingly complete in its argument. Artists crowd around it and insist that stone has answered questions the commentaries kept postponing.
- option_a: Exhibit it at the Academy.
- option_b: Store it as a curiosity.

## Chinese Text
- title: 新发现的残躯
- description: 工匠掘出一具古代大理石残躯，四肢虽断，论证却完整得令人不安。艺术家围在它周围，坚持说石头已经回答了注疏一再拖延的问题。
- option_a: 在学院展出它。
- option_b: 将它作为珍品收藏。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Exhibiting the torso turns classical recovery into visible evidence for Renaissance inquiry, giving artists a powerful supporting seat while making the clergy uneasy about the body's authority.
- rationale_zh: 展出残躯会把古典复兴变成可见证据，使艺术家更有力地支持文艺复兴式探究，同时也让神职阶层对身体本身获得论证权感到不安。
- effect_blocks:
```yaml
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
```

### Option B
- progress_delta: -5
- rationale_en: Treating the torso as a private curiosity preserves decorum and calms conservative readers, but it denies the debate the public force of a rediscovered classical form.
- rationale_zh: 将残躯当作私人珍品可以维持体面，也能安抚保守派读者，但这会让辩论失去重新发现的古典形体所带来的公共力量。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R02, which tests the living body through sanctioned anatomy, R01 turns a damaged ancient body into public artistic and historical evidence.
- Unlike R03, where sacred architecture is reframed through mathematical perspective, R01 centers on classical material recovery and the authority of antiquity.
- Unlike R12, which uses a newly commissioned fresco as propaganda for renewal, R01 begins with an archaeological find whose persuasive force comes from age rather than patronage.
