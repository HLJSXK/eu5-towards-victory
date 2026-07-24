# R20 - Satire of the Old Masters

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Satire of the Old Masters
- description: A biting satire makes old authorities look pompous, which is effective and slightly unfair; by noon, half the Academy is laughing and the other half is counting copies.
- option_a: Let satire circulate.
- option_b: Confiscate the copies.

## Chinese Text
- title: 讽刺旧大师
- description: 一篇辛辣讽刺把旧权威写得傲慢可笑，效果显著，也略显不公。到正午时，学院一半人在发笑，另一半人在清点印本。
- option_a: 允许讽刺流传。
- option_b: 没收所有印本。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Allowing satire to circulate gives reformers a popular language against stale authority, but the gain is modest because ridicule persuades unevenly.
- rationale_zh: 允许讽刺流传，会给改革者一种反对陈旧权威的通俗语言；但讥讽的说服力并不稳定，因此推进幅度有限。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_licensed_wit
  months: 12
  effects:
    "pamphlet debate heat": 0.02
```

### Option B
- progress_delta: -10
- rationale_en: Confiscation turns conservative annoyance into institutional victory, chilling the reformers more sharply than a simple refusal to laugh.
- rationale_zh: 没收会把保守派的不满转化为制度性的胜利，比单纯拒绝发笑更强烈地压制改革者。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike R14 Poets at the Debate, this is not simply useful language entering debate; it directly humiliates old authorities, making suppression a much stronger rejection.
- Unlike R06 Classics in the Market, public circulation here depends on ridicule and pamphlet heat rather than broader access to classical learning.
- Unlike R15 The Prince's Portrait, the contested image of authority is not the ruler's presentation but the intellectual prestige of old masters.
