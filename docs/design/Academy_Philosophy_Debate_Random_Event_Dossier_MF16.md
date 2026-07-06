# MF16 - Piecework Pay

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Piecework Pay
- description: Owners propose paying by the piece, so every finished length of cloth, polished tool, or packed crate becomes both wage and accusation. Workers hear arithmetic trying to become a foreman.
- option_a: Permit regulated piecework.
- option_b: Ban piecework.

## Chinese Text
- title: 计件工资
- description: 业主提议按件付薪，于是每一匹织好的布、每一件磨亮的工具、每一箱封好的货物，都既是工资，也是责备。工人听见算术正试图变成监工。
- option_a: 允许受规制的计件工资。
- option_b: 禁止计件工资。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Regulated piecework makes manufactory labor measurable and ties reward directly to output, which strongly advances the argument for production by scale. The cost is social: workers and rural households suspect that the new arithmetic will squeeze more labor from the same hands.
- rationale_zh: 受规制的计件工资让制造工场劳动可以被衡量，并把报酬直接系在产量上，因此会有力推动规模化生产的论点。代价在于社会层面：工人和乡村家庭会怀疑这种新算术只是要从同一双手里压出更多劳动。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: -0.04
- type: seat_stance
  group: peasants
  stance: oppose
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Banning piecework protects older expectations about fair wages, household rhythm, and guild bargaining. The debate moves sharply toward rejection because manufactories lose one of their clearest tools for turning labor into counted output.
- rationale_zh: 禁止计件工资保护了关于公平工资、家庭节奏和行会议价的旧有期待。辩论会明显转向拒绝，因为制造工场失去了把劳动转化为可计量产出的最清楚工具之一。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.04
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike MF07 Clock Discipline, MF16 is about how wages are calculated rather than how the working day is timed.
- Unlike MF12 Factory Accounts, this event makes accounting touch workers' pay directly instead of merely revealing waste to owners and officials.
- Unlike MF20 The First Whistle, MF16 turns on incentives inside the pay packet, not the public noise and schedule imposed around the workshop.
