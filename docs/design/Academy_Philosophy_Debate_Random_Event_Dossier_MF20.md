# MF20 - The First Whistle

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The First Whistle
- description: A new factory whistle divides the day with admirable efficiency and unbearable certainty. It tells workers when to begin, neighbors when to complain, and reformers that discipline can be heard from three streets away.
- option_a: Defend the new discipline.
- option_b: Silence the whistle.

## Chinese Text
- title: 第一声汽笛
- description: 一只新的工场汽笛以令人赞叹的效率、也以令人难忍的确定性切分一天。它告诉工人何时开工，告诉邻人何时抱怨，也告诉改革者：纪律隔着三条街也能被听见。
- option_a: 捍卫新的纪律。
- option_b: 让汽笛安静。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Defending the whistle accepts that manufactories need public, audible discipline to coordinate many workers at once. Acceptance rises modestly because the symbol is practical but irritating, pleasing production supporters while angering nearby laboring households.
- rationale_zh: 捍卫汽笛，就是承认制造工场需要公开且可听见的纪律，才能同时协调许多工人。接受度会小幅上升，因为这个象征很实用也很恼人：生产支持者满意，附近劳动家庭却会愤怒。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
- type: estate_satisfaction
  estate: peasants_estate
  value: -0.02
```

### Option B
- progress_delta: -5
- rationale_en: Silencing the whistle restores local quiet and makes factory discipline look negotiable. The debate slips toward rejection because the manufactory must retreat from one of its simplest tools for organizing time.
- rationale_zh: 让汽笛安静可以恢复地方安宁，也会让工场纪律显得可以讨价还价。辩论会转向拒绝，因为制造工场不得不放弃组织时间的最简单工具之一。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike MF07 Clock Discipline, MF20 is about the public signal that enforces time rather than the broader managerial rule of clocks and bells.
- Unlike MF15 Coal Smoke Argument, the nuisance here is sound and schedule, not environmental smoke from industrial sites.
- Unlike MF16 Piecework Pay, this event pressures the surrounding community through audible discipline rather than changing the worker's wage incentive.
