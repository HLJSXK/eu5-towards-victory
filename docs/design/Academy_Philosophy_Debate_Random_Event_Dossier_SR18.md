# SR18 - Dangerous Publication

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Dangerous Publication
- description: A treatise lies ready for the printer, sharp enough to overturn a doctrine and expensive enough to offend nearly everyone who funds the Academy. The pages are dry; only the courage is still wet.
- option_a: Publish it.
- option_b: Delay publication.

## Chinese Text
- title: 危险的出版
- description: 一部论著已经准备交给印刷匠，锋利得足以推翻一条旧教义，也昂贵得足以冒犯几乎所有资助学院的人。纸页已经干透，尚未干透的只有勇气。
- option_a: 将其出版。
- option_b: 推迟出版。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publishing the treatise forces the Academy to stand behind dangerous evidence in public. Acceptance surges because the claim can no longer be confined to private murmurs, but prestige and clerical comfort suffer.
- rationale_zh: 出版这部论著，会迫使学院公开支持危险的证据。主张不再能被关在私下低语之中，因此接受度大幅上升，但声望与神职阶层的安稳都会受损。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.05
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Delaying publication protects patrons from embarrassment and keeps dangerous doctrine off the street. The reversal is sharp because the Academy chooses sponsorship peace over the open circulation of evidence.
- rationale_zh: 推迟出版可以保护赞助人免于难堪，也让危险学说暂时无法流入街巷。辩论会大幅后退，因为学院选择了赞助和平，而不是证据的公开流通。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike SR06 Clerical Cosmology Objection, SR18 centers on the publication decision itself rather than a direct theological challenge inside the debate chamber.
- Unlike SR11 Open Correspondence, SR18 is not about cross-border exchange among scientists; it is about whether one explosive treatise can enter public circulation at all.
- Unlike SR13 Public Demonstration, SR18 risks reputation through print and patron anger rather than through a live experiment that might fail in front of witnesses.
