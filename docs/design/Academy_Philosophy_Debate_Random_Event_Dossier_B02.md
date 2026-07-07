# B02 - Noble Debt Roll

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Noble Debt Roll
- description: Bankers arrive with a roll of noble debts, sealed twice and whispered over once. It shows that several proud estates stand on credit they publicly despise.
- option_a: Use the roll as proof.
- option_b: Suppress the roll.

## Chinese Text
- title: 贵族债册
- description: 银行家带来一卷贵族债册，封蜡盖了两层，传闻却早已绕了一圈。它证明好几家骄傲的庄园，正靠他们公开鄙夷的信用维持门面。
- option_a: 将债册作为证据。
- option_b: 压下这卷债册。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publicly using the roll exposes that old landed power already depends on credit, making banking reform harder to dismiss while angering nobles whose dependence is now visible.
- rationale_zh: 公开使用债册会揭穿旧有土地权势早已依赖信用，使银行改革更难被轻易否定，同时也激怒那些被看见债务依赖的贵族。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Suppression protects noble dignity and keeps the alliance of credit and privilege quiet, but it tells the debate that banking law must yield whenever rank is embarrassed.
- rationale_zh: 压下债册能保护贵族体面，让信用与特权之间的联盟继续保持安静；但这也等于告诉辩论，一旦等级尊严受损，银行法就必须退让。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B01 Double-Entry Demonstration, B02 turns on elite hypocrisy and political leverage rather than bookkeeping method.
- Unlike B12 Tax Farm Accounts, the exposed beneficiaries are noble households and estates, not revenue contractors defending a profitable state custom.
- Unlike B20 Crown Account Published, B02 makes private aristocratic debt visible instead of asking the Crown to expose its own simplified finances.
