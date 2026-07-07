# MF07 - Clock Discipline

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clock Discipline
- description: Managers hang bells and clocks where masters once relied on habit. Workers quickly discover that time can become a supervisor with no patience and no need to sleep.
- option_a: Accept clock discipline.
- option_b: Limit work rules.

## Chinese Text
- title: 钟表纪律
- description: 管事们把钟和铃挂在从前只靠习惯运转的地方。工人很快发现，时间也能变成一名既无耐心也不需要睡眠的监督者。
- option_a: 接受钟表纪律。
- option_b: 限制作坊规章。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Accepting clock discipline makes manufactories a new social order of measured labor, not just a larger room of tools. The sharp progress gain is balanced by peasant and worker resentment at being ruled by the bell.
- rationale_zh: 接受钟表纪律会让手工业工场成为一种以计时劳动为核心的新秩序，而不只是更大的工具房。强烈的进度推进以农民和工人的不满作为代价，因为他们被铃声支配。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: -0.04
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_clock_discipline
  months: 18
  effects:
    measured workshop schedules: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Limiting work rules reassures laboring households that manufactories will not turn every hour into a command. It only mildly weakens acceptance because the model can still continue, but without its most disciplined schedule.
- rationale_zh: 限制作坊规章会安抚劳动家庭，使他们相信手工业工场不会把每个时辰都变成命令。它只会轻微削弱接受倾向，因为工场模式仍可继续，只是少了最严密的时间安排。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.03
- type: seat_stance
  group: peasants
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike MF20 The First Whistle, MF07 concerns a full regime of bells, clocks, and work rules rather than one hated public signal.
- Unlike MF16 Piecework Pay, MF07 disciplines time itself instead of changing wages through output incentives.
- Unlike MF13 Rural Displacement, MF07 focuses on conditions inside the workshop rather than the movement of labor out of rural households.
