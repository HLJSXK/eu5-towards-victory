# M13 - Local Language Answers

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Local Language Answers
- description: Provincial candidates ask to answer in local administrative language rather than courtly style.
- option_a: Permit local answers.
- option_b: Require court style.

## Chinese Text
- title: 地方语言答卷
- description: 省份候选人请求用地方行政语言作答，而不是用宫廷偏爱的文体装饰自己的能力。
- option_a: 允许地方语言作答。
- option_b: 要求使用宫廷文体。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Permitting local answers separates competence from courtly polish and lets provincial talent be judged on administration rather than accent. Local communities gain confidence that access is not reserved for the capital's style.
- rationale_zh: 允许地方语言作答把能力与宫廷修辞分开，使省份人才可以按行政本领而不是口音文风受评。地方社群会相信晋身之门并非只为首都文体而开。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_local_language_access
  months: 18
  effects:
    "provincial candidate trust": 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Requiring court style keeps standards uniform and comfortable for central officials, but it lets cultivated language filter candidates before ability can speak plainly.
- rationale_zh: 要求宫廷文体让标准保持统一，也让中央官员更安心，但它会让修辞教养在能力开口之前先行筛人。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_court_style_uniformity
  months: 18
  effects:
    "central examination uniformity": 0.02
```

## Difference From Same Issue Events
- Unlike M03 The Provincial Prodigy, this event is about examination language for many provincial candidates rather than one outsider's proven brilliance.
- Unlike M09 A Peasant's Petition, the candidates have already reached the examination process; the dispute is over how their answers may be expressed.
- Unlike M19 A School Outside the Capital, this event does not recognize a provincial institution, only the language through which candidates demonstrate merit.
