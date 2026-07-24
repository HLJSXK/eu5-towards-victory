# C14 - Icon Debate

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Icon Debate
- description: A church image becomes more than paint and wood once preachers, worshippers, and officials all insist it proves their point. The question is no longer whether the image is beautiful, but who may say what devotion means.
- option_a: Set a confessional rule.
- option_b: Avoid ruling.

## Chinese Text
- title: 圣像之争
- description: 一幅教堂图像在布道者、信众和官员都坚持它能证明己方立场之后，便不再只是颜料与木板。问题已不再是图像是否美丽，而是谁有权解释虔敬的含义。
- option_a: 制定宗派规则。
- option_b: 暂不裁决。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: A clear rule lets religious reformers turn a symbolic quarrel into enforceable discipline, modestly advancing acceptance by defining acceptable devotion.
- rationale_zh: 明确规则能让宗教改革派把象征性的争吵变成可执行的纪律，通过界定可接受的虔敬方式，适度推动接纳。
- effect_blocks:
```yaml
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 12
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.02
```

### Option B
- progress_delta: -5
- rationale_en: Avoiding a ruling preserves local calm around the image, but it leaves devotion undefined and weakens the case for a disciplined confession.
- rationale_zh: 暂不裁决能维持围绕圣像的地方平静，但会让虔敬继续缺乏明确界定，削弱建立有纪律宗派秩序的论证。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_icon_local_truce
  months: 12
  effects:
    local devotional calm: 0.02
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike C05, which fixes doctrine in a teachable text, C14 tests doctrine through visual devotion and public religious symbols.
- Unlike C12, where a pilgrimage threatens public order, C14 is localized around an object whose meaning different authorities claim.
- Unlike C17, which splits clergy over institutional privilege, C14 highlights religious reformers pushing for a rule over worship practice.
