# C15 - Border Preachers

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Border Preachers
- description: Preachers cross the frontier with sermons sharp enough to win converts and complaints. Their doctrine strengthens the debate at home, but every border village now has a diplomatic echo.
- option_a: Protect the preachers.
- option_b: Restrain them.

## Chinese Text
- title: 边境传教士
- description: 传教士带着足以赢得皈依者和投诉的布道越过边境。他们的教义强化了国内辩论，但每个边境村庄如今都会在外交厅里产生回声。
- option_a: 保护这些传教士。
- option_b: 约束他们的活动。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Protecting the preachers shows the confession has outward confidence and active champions, sharply advancing acceptance while making neighboring powers feel provoked.
- rationale_zh: 保护传教士说明这一宗派秩序具有外向的自信和积极的倡导者，能显著推动接纳，但也会让邻国感到被挑衅。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 18
- type: foreign_prestige
  amount: -10
```

### Option B
- progress_delta: -10
- rationale_en: Restraining the preachers calms foreign relations, but it signals that diplomatic caution can silence the very agents who would carry the confession beyond the Academy.
- rationale_zh: 约束传教士能平息对外关系，但也表明外交谨慎足以压制那些本该把宗派教义带出学院的人。
- effect_blocks:
```yaml
- type: foreign_prestige
  amount: 10
- type: seat_stance
  group: foreign_power
  stance: neutral
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike C09, where foreign co-religionists send influence inward, C15 sends preachers outward and makes domestic doctrine a border problem.
- Unlike C03, which licenses sermons inside the realm, C15 asks whether preaching should be protected after it crosses into diplomatic space.
- Unlike C01, where the Crown displays confession at court, C15 tests whether the confession can be defended beyond the court and beyond the frontier.
