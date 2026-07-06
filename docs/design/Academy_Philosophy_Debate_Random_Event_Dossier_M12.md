# M12 - Public Ranking List

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Public Ranking List
- description: Reformers want the results posted where every family can see what influence did not buy.
- option_a: Post the rankings.
- option_b: Keep rankings private.

## Chinese Text
- title: 公开排名榜
- description: 改革者要求把成绩张贴在每个家族都看得见的地方，好让人明白有哪些东西并非权势可以买到。
- option_a: 张贴排名。
- option_b: 保持排名私密。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Posting the rankings turns private evaluation into public evidence, making patronage harder to disguise. Public opinion gains a concrete standard, while nobles see family influence publicly outpaced.
- rationale_zh: 张贴排名把私下评定变成公开证据，使庇护关系更难伪装。舆论获得了可以比较的标准，而贵族会看到家族影响力被公开超越。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.04
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping rankings private lets court offices manage embarrassment and favors behind closed doors. It preserves bureaucratic discretion, but weakens the claim that merit can stand in the open.
- rationale_zh: 保持排名私密让宫廷机构可以在门后处理尴尬与人情。官僚裁量得到保全，但任人唯才能够公开站立的主张被削弱。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 3
- type: temporary_country_modifier
  key: tv_academy_debate_private_rankings
  months: 12
  effects:
    "bureaucratic discretion": 0.02
```

## Difference From Same Issue Events
- Unlike M01 Anonymous Examination, this event concerns publication after scoring, not anonymity during scoring.
- Unlike M10 Boycott by Old Families, no noble withdrawal has happened yet; the pressure comes from deciding whether transparent rankings exist at all.
- Unlike M20 Oath of the Examiners, the test is public visibility of results rather than legal protection for officials before they publish.
