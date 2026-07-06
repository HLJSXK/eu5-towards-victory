# NW16 - Imported Crop

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Imported Crop
- description: A strange crop survives in the Academy test garden, stubbornly green where theory expected only rumor. Farmers, merchants, and skeptics gather around the leaves because the unknown has become something that can be watered.
- option_a: Promote the crop.
- option_b: Keep it contained.

## Chinese Text
- title: 输入作物
- description: 一种陌生作物在学院试验园里活了下来，在理论只期待传闻的地方倔强地泛着绿色。农民、商人和怀疑者都围到叶片旁，因为未知之物终于变成了可以浇水的东西。
- option_a: 推广这种作物。
- option_b: 将它限制在园中。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Promoting the crop makes discovery practical and domestic rather than purely nautical. The gain is modest because a garden cannot prove a continent, but peasants and merchants begin to see New World contact as useful.
- rationale_zh: 推广这种作物会把发现新世界从单纯的航海问题变成务实的国内收益。进展幅度不大，因为一座试验园不能证明整片大陆，但农民和商人会开始把新世界接触视为有用之事。
- effect_blocks:
```yaml
- type: seat_stance
  group: peasants
  stance: support
  cooldown_months: 12
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Containment treats the crop as a possible contamination or disruption. Cautious estates can accept study under lock and fence, but the debate loses momentum because the useful evidence is kept from ordinary life.
- rationale_zh: 将作物限制起来，是把它视作可能的污染或扰动。谨慎的阶层可以接受在围栏和看管下研究它，但由于有用证据被排除在日常生活之外，辩论的势头会减弱。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike NW06 Disease Report, NW16 treats biological exchange as a useful specimen under cultivation rather than a health danger moving through ports.
- Unlike NW08 Harbor Crowd, the persuasive object here is not a public cargo spectacle but a living crop tested slowly in controlled soil.
- Unlike NW11 Rumor of Gold, NW16 uses ordinary subsistence and market usefulness rather than greed for treasure to make discovery attractive.
