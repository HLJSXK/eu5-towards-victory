# M15 - Scholar Demand for Open Chairs

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Scholar Demand for Open Chairs
- description: Academy scholars demand that teaching posts be competed for, not inherited from patrons.
- option_a: Open the chairs.
- option_b: Confirm patron rights.

## Chinese Text
- title: 学者要求公开教席
- description: 学院学者要求教席通过竞争取得，而不是从庇护人手中继承下来。
- option_a: 开放教席竞争。
- option_b: 确认庇护权利。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Opening the chairs applies meritocracy inside the Academy itself, proving that the institution will test its own posts before lecturing the realm. Scholars gain support because their careers no longer depend solely on patrons.
- rationale_zh: 开放教席竞争把任人唯才用于学院自身，证明学院在规劝国家之前也愿意考核自己的职位。学者获得支持，因为他们的前途不再只取决于庇护人。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_open_chair_competition
  months: 24
  effects:
    "academy teaching competition": 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Confirming patron rights reassures those who fund and protect Academy posts, but it leaves scholarship tied to inherited favors rather than open comparison.
- rationale_zh: 确认庇护权利安抚了资助并保护学院职位的人，却也让学问继续依附于继承下来的人情，而不是公开比较。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
- type: temporary_country_modifier
  key: tv_academy_debate_patron_rights_confirmed
  months: 18
  effects:
    "academy patron confidence": 0.02
```

## Difference From Same Issue Events
- Unlike M08 Guild Tests, this event concerns Academy teaching posts rather than practical tests for civic and technical offices.
- Unlike M07 Clerical Certificates, the gatekeeper is patronage over academic posts, not clerical moral certification for public office.
- Unlike M06 The Tutor's Nephew, the dispute is structural competition for chairs rather than one relative seeking one cabinet post.
