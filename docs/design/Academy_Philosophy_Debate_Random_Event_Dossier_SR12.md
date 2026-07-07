# SR12 - Old Master Contradicted

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Old Master Contradicted
- description: A revered authority is contradicted in a footnote so polite it feels cruel. The page says almost nothing loudly, which somehow makes every defender of inherited wisdom hear it.
- option_a: Keep the footnote.
- option_b: Remove it.

## Chinese Text
- title: 旧大师遭到反驳
- description: 一位备受尊崇的权威在脚注里遭到反驳，措辞礼貌得近乎残酷。那一页几乎没有高声宣告什么，却偏偏让每个维护旧学问的人都听得清清楚楚。
- option_a: 保留脚注。
- option_b: 删除脚注。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Keeping the footnote proves that even revered authorities can be tested against new evidence. Acceptance surges because polite contradiction makes the old hierarchy of knowledge visibly answerable, though clerical prestige and scholarly decorum suffer.
- rationale_zh: 保留脚注证明，即使备受尊崇的权威也必须接受新证据检验。礼貌的反驳使旧有知识等级显得需要回应，因此接纳大幅推进；代价是神职威望与学术体面受到损伤。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -5
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Removing the footnote protects the old master from public correction and lets conservative interpreters claim that reverence still outranks experiment. Rejection gains force because the Academy chooses deference at the exact moment method asks for candor.
- rationale_zh: 删除脚注会保护旧大师免于公开修正，并让保守解释者宣称敬畏仍高于实验。学院在方法要求坦诚的时刻选择恭顺，因此拒斥方向获得强劲推动。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 24
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike SR01 Table of Observations, SR12 centers on a precise textual challenge to a named old authority rather than a broad body of repeated data.
- Unlike SR03 Mathematical Proof, SR12 does not persuade through formal symbols. Its force comes from scholarly etiquette being used to dethrone inherited authority.
- Unlike SR18 Dangerous Publication, SR12's danger is compressed into a small footnote instead of a major treatise that openly threatens doctrine and patrons.
