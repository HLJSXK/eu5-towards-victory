# SR14 - Measurement Standard

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Measurement Standard
- description: Researchers complain that every province measures nature with different tools and pride. The Academy realizes that a fact can travel only so far when every ruler, weight, and vessel speaks its own dialect.
- option_a: Standardize measurement.
- option_b: Accept local measures.

## Chinese Text
- title: 度量标准
- description: 研究者抱怨各省都用不同的器具和自尊来衡量自然。学院终于意识到，当每把尺、每个砝码、每只量器都说着自己的方言时，事实能走出的距离也十分有限。
- option_a: 统一度量。
- option_b: 接受地方度量。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Standard measurement makes observations comparable across provinces, giving the Scientific Revolution a practical infrastructure for shared evidence. The strong progress comes from turning scattered experiments into a common language, at a material cost.
- rationale_zh: 统一度量会让各省观察结果彼此可比，为科学革命提供共享证据的实际基础设施。分散实验被转化为共同语言，因此进度大幅推进；代价则是实际支出。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: temporary_country_modifier
  key: tv_academy_debate_measurement_standard
  months: 24
  effects:
    shared research protocols: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Accepting local measures keeps provincial practice intact and reassures those who distrust central standards. It slows acceptance because evidence remains harder to compare, but the resistance is moderate rather than decisive.
- rationale_zh: 接受地方度量会保留各省惯例，并安抚不信任中央标准的人。由于证据仍难以比较，接纳受到拖慢；不过这种阻力只是温和的，而非决定性的。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_local_measures_preserved
  months: 12
  effects:
    local measuring customs protected: 0.01
```

## Difference From Same Issue Events
- Unlike SR04 Instrument Maker's Claim, SR14 is not about funding superior tools themselves, but about making every tool answer to shared units.
- Unlike SR10 Natural History Cabinet, SR14 standardizes the way evidence is measured before classification, rather than arranging specimens after collection.
- Unlike SR05 Academy Experiment Code, SR14 focuses on material units and provincial comparability, not the broader social rules for witnessing and recording experiments.
