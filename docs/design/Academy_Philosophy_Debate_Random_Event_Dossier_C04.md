# C04 - Noble Chapel Dispute

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Noble Chapel Dispute
- description: A noble house maintains a chapel practice that no longer fits the emerging confession. Its defenders call it family honor; its opponents call it a loophole with candles.
- option_a: Enforce uniformity.
- option_b: Tolerate the chapel.

## Chinese Text
- title: 贵族礼拜堂之争
- description: 一个贵族家族仍在自家礼拜堂中维持旧例，而这种做法已同正在形成的国家信仰不合。辩护者称之为家族荣誉，反对者则说那不过是点着蜡烛的漏洞。
- option_a: 强制执行信仰统一。
- option_b: 容忍贵族礼拜堂。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Enforcing uniformity proves that noble privilege cannot exempt a household from the confessional settlement, giving acceptance a concrete victory at the cost of noble satisfaction.
- rationale_zh: 强制统一证明贵族特权不能让某个家族豁免于信仰定制之外，使接受派获得具体胜利，但代价是贵族满意度下降。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
- type: seat_stance
  group: religious_reformers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Tolerating the chapel buys noble cooperation and preserves household privilege, but it teaches everyone that the confessional settlement bends before rank.
- rationale_zh: 容忍贵族礼拜堂能换取贵族配合并保存家族特权，但它也会让所有人看见，信仰定制会在门第面前弯曲。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.05
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike C01 Confession of the Court, C04 tests whether the policy binds a particular noble house rather than whether the Crown displays faith publicly.
- Unlike C10 Feast Day Reform, C04 is a conflict over elite household worship, not the popular calendar of local holy days.
- Unlike C17 Clergy Split, C04 centers noble exemption from uniformity rather than rivalry inside the clergy estate.
