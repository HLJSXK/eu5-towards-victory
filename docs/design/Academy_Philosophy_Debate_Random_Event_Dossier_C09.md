# C09 - Foreign Co-Religionists

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Foreign Co-Religionists
- description: Letters arrive from foreign co-religionists, full of encouragement, advice, and signatures too prominent to ignore. Their support strengthens the argument and makes every listener wonder who else is listening.
- option_a: Accept their letters.
- option_b: Reject foreign influence.

## Chinese Text
- title: 外国同信者
- description: 外国同信者寄来书信，里面满是鼓励、建议，以及显眼到无法忽视的署名。他们的支持加强了论点，也让每个听众都忍不住猜测还有谁在旁听。
- option_a: 接受他们的来信。
- option_b: 拒绝外国影响。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Accepting the letters frames the confession as part of a wider religious community, adding outside credibility while inviting foreign attention into the debate.
- rationale_zh: 接受来信会把本国信纲描绘成更大信仰共同体的一部分，增加外部可信度，同时也把外国关注引入辩论。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: support
  cooldown_months: 18
- type: foreign_prestige
  amount: 5
```

### Option B
- progress_delta: -5
- rationale_en: Rejecting foreign influence reassures nobles who want confession to remain a domestic settlement, but it cuts away useful testimony from allies abroad.
- rationale_zh: 拒绝外国影响会安抚那些希望信纲保持国内事务的贵族，却也切断了来自海外盟友的有用证词。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike C01 Confession of the Court, C09 tests whether foreign religious endorsement may influence the debate rather than whether the Crown should display its own faith.
- Unlike C08 Synod Summons, C09 brings letters from abroad into the chamber instead of gathering domestic witnesses in one formal assembly.
- Unlike C15 Border Preachers, C09 is correspondence and prestige pressure, not the physical movement of preachers across borders.
