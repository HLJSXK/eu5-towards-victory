# NW02 - Returned Pilot

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Returned Pilot
- description: A pilot returns with salt in their clothes, fever in their bones, and a story that repeats itself too clearly to be waved away. The Academy must decide whether the realm hears the tale as evidence or as a secret.
- option_a: Hear them publicly.
- option_b: Question them privately.

## Chinese Text
- title: 归来的领航员
- description: 一名领航员归来，衣上带着盐迹，骨子里还留着热病，讲出的故事却前后一致，难以随手抹去。学院必须决定，是让王国把这段经历当作证据来听，还是当作秘密来审。
- option_a: 公开听取其证词。
- option_b: 私下盘问。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: A public hearing turns the pilot from a rumor carrier into a witnessed source. Acceptance rises sharply because the story becomes communal evidence, although the Crown spends some prestige if the testimony later proves imperfect.
- rationale_zh: 公开听证会会把领航员从传闻携带者变成有见证的来源。由于这段故事变成了共同听到的证据，接受度会显著上升，但若证词日后被证明有瑕疵，王权也会消耗一些声望。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
- type: resource
  resource: prestige
  amount: -5
```

### Option B
- progress_delta: -5
- rationale_en: Private questioning keeps the pilot useful to officials but denies the debate a public witness. Court caution slows acceptance without fully rejecting the possibility that the story is true.
- rationale_zh: 私下盘问可以让官员继续利用领航员，却不给辩论一个公开见证人。宫廷谨慎会减缓接受进程，但并不会彻底否认这段经历可能是真的。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: court_bureaucrats
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_private_pilot_interrogation
  months: 12
  effects:
    controlled handling of exploration testimony: 0.02
```

## Difference From Same Issue Events
- Unlike NW01 The Sailor's Chart, NW02 depends on a living witness whose credibility is shaped by the hearing format.
- Unlike NW07 Missing Expedition, the voyage has returned and produces testimony rather than absence, grief, and speculation.
- Unlike NW13 Cosmographer's Error, the pressure comes from firsthand experience at sea, not from a scholar revising an abstract distance estimate.
