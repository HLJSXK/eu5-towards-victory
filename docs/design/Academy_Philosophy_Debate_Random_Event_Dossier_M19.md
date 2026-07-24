# M19 - A School Outside the Capital

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A School Outside the Capital
- description: A provincial school claims it can train officials without court polish.
- option_a: Recognize the school.
- option_b: Require capital certification.

## Chinese Text
- title: 首都之外的学校
- description: 一所地方学校宣称，即使没有宫廷修饰，它也能培养官员。
- option_a: 承认这所学校。
- option_b: 要求首都认证。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Recognizing the school admits that administrative ability can be trained outside the capital's manners and patronage circuits. Local autonomy gains confidence because provincial institutions are treated as producers of talent.
- rationale_zh: 承认这所学校，就是承认行政才能可以在首都礼法和庇护圈之外培养。地方自治会因此更有信心，因为地方机构被视为人才的来源，而不是等待核准的边缘。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_provincial_training
  months: 24
  effects:
    "provincial official recruitment": 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Requiring capital certification keeps provincial training subordinate to the center. Central bureaucrats approve because competence remains filtered through familiar offices, seals, and courtly standards.
- rationale_zh: 要求首都认证会让地方训练继续服从中央。中央官僚会赞成，因为才能仍须经过熟悉的机关、印信和宫廷标准筛选。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_capital_certification
  months: 18
  effects:
    "central examination control": 0.02
```

## Difference From Same Issue Events
- Unlike M03 The Provincial Prodigy, this event evaluates a durable provincial school rather than one exceptional candidate from a distant province.
- Unlike M13 Local Language Answers, the dispute is over institutional certification, not which administrative language candidates may use.
- Unlike M15 Scholar Demand for Open Chairs, the contested posts are state offices trained outside the capital, not Academy teaching chairs opened to competition.
