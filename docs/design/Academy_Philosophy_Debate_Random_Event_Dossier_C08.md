# C08 - Synod Summons

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Synod Summons
- description: A formal synod is proposed, with witnesses numerous enough that no faction can later pretend the hard words were never spoken. Doctrine would leave the Academy as a public settlement, not a rumor.
- option_a: Summon the synod.
- option_b: Avoid spectacle.

## Chinese Text
- title: 召集宗教会议
- description: 有人提议召开一场正式宗教会议，列席见证者多到足以让任何派别都无法事后装作尖锐言辞从未出现。教义将以公开决议的形式离开学院，而不是以传闻流散。
- option_a: 召集宗教会议。
- option_b: 避免公开场面。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: A witnessed synod gives the confessional settlement institutional weight and makes evasion costly, but convening it spends money and exposes royal legitimacy to open doctrinal conflict.
- rationale_zh: 有见证者的宗教会议会赋予信纲制度分量，并让回避变得代价高昂；但召集会议需要花费金钱，也会让王权合法性暴露在公开教义冲突之中。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: resource
  resource: legitimacy
  amount: -5
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -10
- rationale_en: Avoiding the synod preserves calm by denying the dispute a stage, but it also lets opponents argue that the confession cannot survive formal scrutiny.
- rationale_zh: 避免召开会议可以不给争端搭建舞台，从而保住平静；但这也让反对者有理由宣称，该信纲经不起正式审查。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_cooldown
  group: clergy
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike C05 Catechism Draft, C08 is not about producing a teachable text; it is about public adjudication before witnesses.
- Unlike C17 Clergy Split, C08 forces factions into a formal venue instead of choosing between discipline and corporate privilege inside the clergy.
- Unlike C20 The Crown's Formula, C08 relies on a collective synod rather than a royal phrase drafted from above.
