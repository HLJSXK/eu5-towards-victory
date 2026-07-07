# SR05 - Academy Experiment Code

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Academy Experiment Code
- description: Reformers propose a code for witnessing, recording, and repeating experiments, complete with columns, signatures, and enough procedure to make every informal genius sigh. Trust, they argue, should leave a paper trail.
- option_a: Adopt the code.
- option_b: Keep gentlemanly trust.

## Chinese Text
- title: 学院实验守则
- description: 改革者提议制定一套见证、记录和重复实验的守则，里面有表格、签名，以及足以让每位随性天才叹气的程序。他们说，信任也应当留下纸面踪迹。
- option_a: 采纳这套守则。
- option_b: 保持绅士式信任。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Adopting the code turns experimental credibility into a shared institution rather than a matter of personal honor. The paperwork is burdensome, but it makes acceptance easier because witnesses can compare records across trials.
- rationale_zh: 采纳守则会把实验可信度变成一种共同制度，而不是个人荣誉问题。文书负担会增加，但见证者能够跨试验比较记录，因此更容易接受新方法。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_experiment_code
  months: 24
  effects:
    academy record-keeping burden: -0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping gentlemanly trust preserves elite ease and avoids making honorable witnesses submit to clerks. The issue only slides moderately backward, because private trust still allows experiments, but it weakens repetition as public proof.
- rationale_zh: 保持绅士式信任能维护精英的从容，也避免让体面的见证者服从书记员。议题只会适度后退，因为私人信任仍允许实验存在，但它削弱了重复试验作为公共证明的力量。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike SR02 Failed Replication, SR05 creates standing rules for future repetition rather than deciding how to handle one embarrassing failed trial.
- Unlike SR13 Public Demonstration, this event is about controlled witnessing and written procedure rather than persuading a crowd through spectacle.
- Unlike SR19 Experimental Oath, SR05 protects truth through records and protocols, not through personal guarantees for vulnerable assistants.
