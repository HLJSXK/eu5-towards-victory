# M08 - Guild Tests

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Guild Tests
- description: City guilds offer practical trials for accountants, engineers, and clerks, insisting that a hand steady over real work can prove what polished quotations cannot.
- option_a: Add practical tests.
- option_b: Keep classical credentials.

## Chinese Text
- title: 行会测验
- description: 城市行会提出为会计、工程师和文吏设置实务测验，坚称能处理真事务的双手，比漂亮引文更能证明才干。
- option_a: 加入实务测验。
- option_b: 保留古典资历。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Practical tests strongly advance meritocracy because they make officeholding depend on demonstrable work, while rewarding burgher institutions that can supply those tests.
- rationale_zh: 实务测验以可展示的工作能力决定任用，强力推动任人唯才，同时奖励能提供测验的市民机构。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.05
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Classical credentials keep office culture legible to conservative scholars, but they soften the demand that candidates prove useful ability directly.
- rationale_zh: 古典资历让保守学者熟悉的任官方式得以延续，却削弱了候选人直接证明实用能力的要求。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike M01's anonymous scoring, M08 changes what is tested by adding practical tasks rather than changing how written papers are judged.
- Unlike M15's open competition for teaching posts, M08 focuses on administrative and technical offices where guild expertise can judge competence.
- Unlike M16's veterans' service rolls, M08 values civilian skill trials rather than years of disciplined service.
