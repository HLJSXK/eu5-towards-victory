# NW18 - Missionary Grammar

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Missionary Grammar
- description: A missionary arrives with a grammar of a language no courtier can pronounce without humility. The pages prove that discovery has voices, rules, and meanings of its own, not merely coastlines waiting to be named.
- option_a: Circulate the grammar.
- option_b: Keep it for missions only.

## Chinese Text
- title: 传教士语法书
- description: 一名传教士带来了一部新语言的语法书，宫廷中无人能不带谦卑地读出那些音节。书页证明，发现新世界面对的是自有声音、规则和意义的人群，而不只是等待命名的海岸线。
- option_a: 传阅这部语法书。
- option_b: 仅供传教使用。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Circulating the grammar lets scholars and clergy both treat the New World as a society that can be studied, translated, and addressed. Acceptance advances strongly because the unknown gains language rather than remaining blank space.
- rationale_zh: 传阅语法书会让学者和神职人员都把新世界视为可以研究、翻译和对话的社会。由于未知之地获得了语言，而不再只是空白空间，接受方向会大幅推进。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
- type: seat_stance
  group: clergy
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Restricting the grammar to missions preserves clerical control and keeps linguistic knowledge from becoming a general Academy argument. The debate slows because voices from the New World are filtered through a single institution.
- rationale_zh: 将语法书限于传教用途，可以保留神职控制，也阻止语言知识成为学院内部更广泛的论据。由于新世界的声音被单一机构过滤，辩论会放慢脚步。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike NW03 Clergy Ask for Mission Rights, NW18 begins from a concrete linguistic artifact rather than an institutional demand for mission priority.
- Unlike NW05 Native Envoy's Account, this event centers on the rules of language and translation, not on a single translated testimony that contradicts Academy assumptions.
- Unlike NW13 Cosmographer's Error, NW18 revises the debate through human voices and grammar rather than through corrected measurements of distance.
