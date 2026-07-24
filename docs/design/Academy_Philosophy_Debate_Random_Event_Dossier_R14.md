# R14 - Poets at the Debate

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Poets at the Debate
- description: Poets begin turning the issue into quotable lines, which may be useful and is definitely dangerous.
- option_a: Use their language
- option_b: Expel the poets

## Chinese Text
- title: 辩论中的诗人
- description: 诗人开始把议题改写成可传诵的句子。这也许有用，但绝对危险。
- option_a: 借用他们的语言
- option_b: 驱逐诗人

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Adopting the poets' phrasing lets Renaissance ideas travel as memorable speech. The progress gain is modest because popularity helps persuasion, but poetic language also makes the issue harder to control.
- rationale_zh: 采纳诗人的措辞，会让文艺复兴观念以易于传诵的语言扩散。进度小幅上升，因为流行表达有助于说服，但诗性语言也让议题更难被控制。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: resource
  resource: prestige
  amount: 5
```

### Option B
- progress_delta: -5
- rationale_en: Expelling the poets preserves procedural seriousness but drains the debate of public energy. Bureaucratic guardians of orderly deliberation are strengthened as the issue retreats back into controlled rooms.
- rationale_zh: 驱逐诗人可以维护程序上的严肃性，却会抽走辩论的公共活力。维护有序议事的官僚因此得到加强，议题也退回受控的房间之中。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_orderly_proceedings
  months: 12
  effects:
    academy procedural calm: 0.01
```

## Difference From Same Issue Events
- Unlike R20, Satire of the Old Masters, this event uses poetic condensation to recruit attention rather than ridicule to attack old authorities.
- Unlike R08, Court Masque of Renewal, this event enters the debate chamber through language, not through court spectacle and staged performance.
- Unlike R12, Fresco of the New Age, this event is portable and quotable rather than fixed to an Academy wall.
