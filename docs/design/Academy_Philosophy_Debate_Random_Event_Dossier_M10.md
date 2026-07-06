# M10 - Boycott by Old Families

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Boycott by Old Families
- description: Several noble families threaten to withdraw their sons from the Academy if open rankings proceed, mistaking absence for an argument.
- option_a: Let them boycott.
- option_b: Suspend the ranking.

## Chinese Text
- title: 旧家族抵制
- description: 几个贵族家族威胁说，若公开排名继续推行，他们便让子弟退出学院，仿佛缺席本身就是论据。
- option_a: 任其抵制。
- option_b: 暂停排名。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Allowing the boycott proves that open ranking will not be hostage to noble participation, sharply advancing meritocracy at the cost of noble satisfaction.
- rationale_zh: 任其抵制表明公开排名不会被贵族参与绑架，因此显著推动任人唯才，但会牺牲贵族满意度。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.06
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Suspending the ranking gives noble families a public victory and stabilizes their cooperation, but it makes birth strong enough to halt evidence.
- rationale_zh: 暂停排名让贵族家族获得公开胜利，也稳定了他们的配合，却等于承认门第足以叫停证据。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.06
- type: temporary_country_modifier
  key: tv_academy_debate_rankings_suspended
  months: 12
  effects:
    elite academy attendance restored: 0.03
```

## Difference From Same Issue Events
- Unlike M02's appeal to ancestral service, M10 uses collective withdrawal as leverage against a specific transparent ranking process.
- Unlike M12, where reformers choose whether to publish rankings, M10 begins after publication is already politically threatening enough to provoke a boycott.
- Unlike M20, where examiners ask for protection before publishing results, M10 tests whether the Crown will let noble nonparticipation stop the rankings themselves.
