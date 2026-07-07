# B19 - Bankruptcy Shame

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Bankruptcy Shame
- description: A ruined merchant argues that orderly bankruptcy saves workshops, creditors, and families better than public disgrace ever has. The moralists hear mercy; the bankers hear salvage.
- option_a: Legalize orderly bankruptcy.
- option_b: Keep disgrace as punishment.

## Chinese Text
- title: 破产之耻
- description: 一名破产商人辩称，有秩序的破产比公开羞辱更能保住作坊、债权人和家庭。道德家听见的是宽纵，银行家听见的是残值。
- option_a: 使有序破产合法化。
- option_b: 保留羞辱作为惩罚。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Legal bankruptcy treats failure as a managed financial event rather than a moral collapse, which strengthens the banking argument for predictable rules. Conservative moral authorities object because disgrace loses some disciplinary power.
- rationale_zh: 合法破产把失败视为可管理的金融事件，而不是单纯的道德崩塌，从而强化银行制度需要可预期规则的主张。保守道德权威会反对，因为羞辱失去了一部分惩戒力量。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
- type: temporary_country_modifier
  key: tv_academy_debate_orderly_bankruptcy
  months: 24
  effects:
    commercial recovery confidence: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Keeping disgrace as punishment satisfies those who see debt failure as moral failure, but it leaves trade exposed to panic, concealment, and ruin without procedure.
- rationale_zh: 保留羞辱作为惩罚，会安抚那些把债务失败视为道德失败的人；但贸易仍会暴露在恐慌、隐瞒和无程序崩坏之中。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B14 Merchant Widow Fund, which recognizes pooled risk before disaster, B19 decides what happens after commercial failure has already arrived.
- Unlike B06 Widow's Deposit, the focus is not depositor protection against a banker but a general legal path for failed merchants and creditors.
- Unlike B03 Sermon on Usury, moral resistance here targets the meaning of insolvency rather than the legitimacy of interest itself.
