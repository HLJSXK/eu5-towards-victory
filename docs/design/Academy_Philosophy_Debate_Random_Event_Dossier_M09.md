# M09 - A Peasant's Petition

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Peasant's Petition
- description: A village schoolmaster asks whether talent born beneath a thatched roof is still talent, and the question enters the chamber with mud on its shoes.
- option_a: Admit the petition.
- option_b: Return it to local authorities.

## Chinese Text
- title: 农民的请愿
- description: 一位乡村塾师询问，茅屋之下诞生的才智是否仍算才智。这个问题带着泥点走进了辩论厅。
- option_a: 接纳请愿。
- option_b: 交还地方处理。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Hearing the petition makes meritocracy socially broader, proving that origin cannot disqualify talent before ability is even examined.
- rationale_zh: 接纳请愿扩大了任人唯才的社会边界，证明出身不能在能力被检验前就取消一个人的资格。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.05
- type: seat_stance
  group: peasants
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Returning the petition protects administrative order, but it lets local hierarchy decide whether lowborn talent may even be heard.
- rationale_zh: 交还地方能维护行政秩序，却也让地方等级决定寒门才智是否有资格被听见。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_local_order_preserved
  months: 12
  effects:
    local administrative calm: 0.03
```

## Difference From Same Issue Events
- Unlike M03, where a provincial prodigy has already solved a hard problem, M09 begins with an unanswered petition from a low-status schoolmaster.
- Unlike M13, which debates what language provincial candidates may use, M09 debates whether rural and lowborn petitioners may enter the meritocratic conversation at all.
- Unlike M19, which evaluates a provincial school as an institution, M09 gives the human claim of one village petitioner center stage.
