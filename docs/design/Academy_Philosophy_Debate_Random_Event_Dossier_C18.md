# C18 - Public Recantation

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Public Recantation
- description: A prominent opponent offers to recant if the Academy spares them a ritual humiliation. Some see mercy as proof of confidence; others see a missed chance to make resistance tremble.
- option_a: Accept the recantation.
- option_b: Demand public shame.

## Chinese Text
- title: 公开悔认
- description: 一位著名反对者表示，只要学院免去羞辱仪式，自己便愿意悔认。有人认为宽恕证明了自信，也有人觉得这是错过了让反抗者战栗的机会。
- option_a: 接受悔认。
- option_b: 要求公开受辱。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Accepting the recantation turns an opponent into evidence that persuasion can work, moving the debate toward acceptance while improving public order through restraint.
- rationale_zh: 接受悔认会把一名反对者变成劝服有效的证据，使辩论走向接纳；克制的处理也有助于安定公共秩序。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_cooldown
  group: public_opinion
  cooldown_months: 12
```

### Option B
- progress_delta: +10
- rationale_en: Demanding public shame makes the victory unmistakable and intimidates wavering opponents, so acceptance jumps forward, but the spectacle hardens those who fear confession as coercion.
- rationale_zh: 要求公开受辱会让胜利无可误认，并震慑摇摆的反对者，因此接纳大幅前进；但这种场面也会使那些害怕宗派强制的人更加顽固。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
- type: seat_stance
  group: minorities
  stance: oppose
  cooldown_months: 24
- type: resource
  resource: prestige
  amount: -5
```

## Difference From Same Issue Events
- Unlike C04 Noble Chapel Dispute, C18 centers on the treatment of a defeated individual opponent rather than an entrenched noble household practice.
- Unlike C08 Synod Summons, C18 is a visible act of submission after debate pressure, not a formal assembly convened to settle doctrine.
- Unlike C15 Border Preachers, C18 affects domestic opposition and public discipline rather than cross-border religious agitation.
