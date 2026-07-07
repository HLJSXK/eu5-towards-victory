# MF10 - Child Labor Petition

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Child Labor Petition
- description: Parish leaders arrive with names, ages, and smaller hands than the debate has been willing to imagine. The question is no longer whether manufactories produce more, but what kind of labor they are allowed to consume.
- option_a: Set labor rules and continue.
- option_b: Shut the model down.

## Chinese Text
- title: 童工请愿
- description: 堂区领袖带着姓名、年龄，以及辩论此前不愿认真想象的一双双小手来到学院。问题不再是手工业工场能否生产更多，而是它被允许消耗怎样的劳动。
- option_a: 制定劳动规则并继续。
- option_b: 关闭这种模式。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Labor rules keep the manufactory argument alive while conceding that production cannot be separated from moral supervision. Clergy and peasants partly approve because the reform now includes limits rather than pure expansion.
- rationale_zh: 劳动规则让手工业工场的论点继续成立，同时承认生产不能同道德监督分离。神职人员和农民部分赞同，是因为改革现在包含限制，而不只是扩张。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.02
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.02
- type: temporary_country_modifier
  key: tv_academy_debate_child_labor_rules
  months: 18
  effects:
    regulated workshop labor: 0.02
```

### Option B
- progress_delta: -10
- rationale_en: Shutting the model down lets conservative critics treat child labor as proof that proto-factory organization is morally rotten at the root. It strongly rejects acceptance while giving protective estates a clear victory.
- rationale_zh: 关闭这种模式会让保守批评者把童工视为原始工厂组织在道德上根本腐坏的证据。它强烈推动否定，同时让主张保护的阶层取得明确胜利。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 24
- type: seat_stance
  group: peasants
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike MF04 Women at the Looms, MF10 focuses on age, parish guardianship, and moral protection rather than gendered wage work.
- Unlike MF07 Clock Discipline, MF10 debates who may be employed at all, not how strictly the working day is measured.
- Unlike MF13 Rural Displacement, MF10 centers child welfare inside proto-factory labor rather than the broader loss of rural household labor.
