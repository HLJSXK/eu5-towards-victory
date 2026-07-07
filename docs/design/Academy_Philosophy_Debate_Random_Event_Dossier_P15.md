# P15 - Ballad of the Issue

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Ballad of the Issue
- description: A printed ballad explains the debate badly but memorably.
- option_a: Use popular print.
- option_b: Suppress vulgar argument.

## Chinese Text
- title: 议题歌谣
- description: 一首印刷歌谣把这场辩论解释得不甚准确，却令人难忘。
- option_a: 利用通俗印刷品。
- option_b: 压制粗俗论辩。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Using popular print accepts that simplified songs can carry the debate beyond the Academy even when they sand down the argument.
- rationale_zh: 利用通俗印刷品，就是承认简化过的歌谣即使磨平了论证，也能把辩论带出学院之外。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Suppressing vulgar argument reassures elites that philosophy will not be surrendered to catchy refrains and street interpretation.
- rationale_zh: 压制粗俗论辩会让精英放心，相信哲学不会被朗朗上口的副歌和街头解读接管。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike P01, this event is about popular simplification after print exists, not the first formal pamphlet run.
- Unlike P08, the material is memorable and public rather than anonymous agitation that makes allies nervous.
- Unlike P19, the fame belongs to a printed song and its audience rather than to the printer as a celebrity.
