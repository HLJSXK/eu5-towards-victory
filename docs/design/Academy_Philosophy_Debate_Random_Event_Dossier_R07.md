# R07 - Artist Versus Theologian

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Artist Versus Theologian
- description: An artist and a theologian quarrel over whether beauty teaches truth or merely distracts the soul from it. The Academy listens as brushwork and doctrine accuse each other of vanity.
- option_a: Defend artistic inquiry.
- option_b: Side with theology.

## Chinese Text
- title: 艺术家与神学家
- description: 一位艺术家和一位神学家争论美究竟能教人认识真理，还是只会让灵魂分心。学会听着笔触与教义彼此指责对方虚荣。
- option_a: 捍卫艺术探究。
- option_b: 站在神学一边。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Defending artistic inquiry gives Renaissance method a major victory: beauty is treated as a way to investigate truth, even though clergy lose confidence in the debate's restraint.
- rationale_zh: 捍卫艺术探究会让文艺复兴方法取得重大胜利：美被承认为探求真理的一种方式，尽管神职人员会更不信任这场辩论的分寸。
- effect_blocks:
```yaml
- type: artist_skill
  amount: 0.05
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
```

### Option B
- progress_delta: -10
- rationale_en: Siding with theology makes doctrinal caution stronger than artistic investigation, sharply weakening acceptance while rewarding clerical guardianship and discouraging artists.
- rationale_zh: 站在神学一边，会让教义谨慎压过艺术探究，显著削弱接受趋势，同时奖励神职守护权并打击艺术家。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.05
- type: artist_skill
  amount: -0.04
```

## Difference From Same Issue Events
- Unlike R03 Perspective in the Chapel, R07 is a direct institutional quarrel between artistic and theological authority, not a dispute over one visual method inside sacred space.
- Unlike R12 Fresco of the New Age, the event does not ask where art should be displayed; it asks whether artistic practice can count as inquiry at all.
- Unlike R15 The Prince's Portrait, the stakes are doctrinal and epistemic rather than royal image-making or court prestige.
