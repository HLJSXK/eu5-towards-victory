# R13 - Old Workshop Resists

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Old Workshop Resists
- description: Traditional masters refuse new proportions, calling them foreign vanity.
- option_a: Enforce the new curriculum
- option_b: Respect workshop custom

## Chinese Text
- title: 旧工坊的抵制
- description: 传统大师拒绝新的比例法，称其为外来的虚荣。
- option_a: 强制推行新课程
- option_b: 尊重工坊惯例

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Enforcing the curriculum makes Renaissance method a taught standard instead of an optional fashion. The large progress gain reflects the Crown turning workshop practice into institutional doctrine, while guild-linked burghers resent the intrusion.
- rationale_zh: 强制推行课程会把文艺复兴方法变成教学标准，而不是可有可无的风尚。大幅推进来自王权将工坊技艺纳入制度教义，但与行会相连的市民会反感这种干预。
- effect_blocks:
```yaml
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.05
```

### Option B
- progress_delta: -10
- rationale_en: Respecting workshop custom concedes that inherited craft authority outranks the new proportions. The debate loses ground sharply because conservative practice wins a practical veto, while guild interests feel protected.
- rationale_zh: 尊重工坊惯例等于承认传统技艺权威高于新的比例法。保守实践获得了事实上的否决权，因此辩论大幅后退，而行会利益则感到受到保护。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.05
```

## Difference From Same Issue Events
- Unlike R09, A Ruin Measured, this event is about forcing new standards into living workshops rather than publishing measurements from ancient ruins.
- Unlike R04, Patronage Ledger, this event does not buy innovation through patrons; it imposes curriculum through institutional authority.
- Unlike R17, Imported Master, this event's resistance comes from domestic traditional masters, not resentment of a specific foreign expert.
