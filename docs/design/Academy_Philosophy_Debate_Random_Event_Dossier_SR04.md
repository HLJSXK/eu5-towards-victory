# SR04 - Instrument Maker's Claim

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Instrument Maker's Claim
- description: An instrument maker brings lenses, screws, brass fittings, and the serene confidence of someone who knows scholars need better hands. Better tools, they insist, do not make better toys; they make better truth.
- option_a: Fund new instruments.
- option_b: Distrust tool-made claims.

## Chinese Text
- title: 仪器匠的主张
- description: 一名仪器匠带来镜片、螺丝、黄铜部件，以及那种明白学者其实需要更好双手的平静自信。他坚持说，更好的工具造出的不是更好的玩物，而是更好的真理。
- option_a: 资助新仪器。
- option_b: 不信任工具造出的主张。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding instruments makes the debate materially testable: the Academy admits that truth may depend on calibrated tools as well as learned eyes. The cost is real, but toolmakers and experimental scholars gain a seat at the argument.
- rationale_zh: 资助仪器会让辩论获得可实际检验的条件：学院承认真理不仅依靠博学的眼睛，也可能依靠校准过的工具。花费确实存在，但工匠和实验学者会在争论中获得位置。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Distrusting tool-made claims protects old scholarly habits from dependence on artisans and devices. It sharply reverses acceptance because the new method looks like mechanical trickery rather than disciplined inquiry.
- rationale_zh: 不信任工具造出的主张，可以保护旧学术习惯不必依赖工匠和器具。它会明显拉低接受度，因为新方法会显得像机械花招，而不是严谨探究。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: burghers_estate
  value: -0.03
```

## Difference From Same Issue Events
- Unlike SR03 Mathematical Proof, SR04 is about material mediation and craft skill rather than formal reasoning.
- Unlike SR10 Natural History Cabinet, this event funds tools for producing evidence, not a collection for arranging specimens after evidence is gathered.
- Unlike SR16 Royal Observatory, SR04 concerns flexible instrument-making capacity rather than a permanent astronomical institution.
