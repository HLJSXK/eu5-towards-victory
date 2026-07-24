# C05 - Catechism Draft

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Catechism Draft
- description: Scholars produce a catechism brief enough for children to memorize and sharp enough for adults to argue over. Its margins already look like a battlefield.
- option_a: Print and teach it.
- option_b: Delay for consensus.

## Chinese Text
- title: 教理问答草案
- description: 学者们写出一份教理问答，短到儿童也能背诵，锋利到成年人也会争执。它的页边空白已经像一片战场。
- option_a: 印行并教授教理问答。
- option_b: 延后，等待共识。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Printing the catechism turns confessional doctrine into repeatable instruction, pushing acceptance through classrooms and pulpits while provoking clergy who dislike the chosen wording.
- rationale_zh: 印行教理问答会把信仰教义变成可反复教授的文本，通过课堂与讲坛推动接受，同时也会激怒不满具体措辞的教士。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.02
- type: temporary_country_modifier
  key: tv_academy_debate_catechism_lessons
  months: 18
  effects:
    doctrinal teaching reach: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Delaying for consensus keeps the peace among rival clerical readers, but every extra revision weakens the claim that the settlement is ready to be accepted.
- rationale_zh: 延后等待共识可以维持相互竞争的教士读者之间的和平，但每多一轮修订，都会削弱这项信仰定制已经可以被接受的说服力。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: clergy
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_consensus_delay
  months: 12
  effects:
    religious peacekeeping: 0.02
```

## Difference From Same Issue Events
- Unlike C03 Sermon Licensing, C05 standardizes teachable doctrine in text rather than deciding which preachers may speak.
- Unlike C11 Confessional Schoolbooks, C05 is the first contested doctrinal core itself, while C11 spreads doctrine through broader civic school material.
- Unlike C20 The Crown's Formula, C05 is a scholarly teaching instrument, not a royal proclamation meant to settle the realm by authority.
