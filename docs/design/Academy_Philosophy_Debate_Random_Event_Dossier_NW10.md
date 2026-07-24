# NW10 - Naval Officers Demand Funds

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Naval Officers Demand Funds
- description: Naval officers tell the Academy that discovery cannot be sailed on ceremonial timber. If the realm wants the ocean to become a road, it must pay for ships prepared to survive more than a parade.
- option_a: Fund oceanic preparation.
- option_b: Keep fleets coastal.

## Chinese Text
- title: 海军军官索要经费
- description: 海军军官告诉学院，发现新世界不能靠礼仪用的木头航行。如果王国想让海洋成为道路，就必须出钱准备那些不只会参加检阅的船。
- option_a: 资助远洋准备。
- option_b: 让舰队留在近海。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding oceanic preparation converts discovery from speculation into state capacity. The debate moves strongly toward acceptance because officers, dockyards, and planners begin treating the New World as reachable policy.
- rationale_zh: 资助远洋准备会把发现从猜想转化为国家能力。由于军官、船坞和规划者开始把新世界视为可以抵达的政策目标，辩论会大幅转向接受。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -5
- rationale_en: Keeping fleets coastal preserves money and familiar naval priorities, but it makes discovery look like rhetoric without hulls. Fiscal caution slows acceptance without fully repudiating the idea.
- rationale_zh: 让舰队留在近海可以保存财力，也维持熟悉的海军优先事项，但这会让发现显得像没有船壳支撑的空话。财政谨慎会拖慢接受，却不至于彻底否定这个想法。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW04 Merchants Want Charter, NW10 is about direct state naval capacity rather than granting commercial rights to private backers.
- Unlike NW07 Missing Expedition, this event happens before catastrophe and asks whether the realm will invest enough to make long voyages plausible.
- Unlike NW15 Colonial Charter Abuse, NW10 focuses on ships, preparation, and treasury pressure rather than the governance failures of distant charter holders.
