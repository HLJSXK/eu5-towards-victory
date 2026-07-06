# B01 - Double-Entry Demonstration

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Double-Entry Demonstration
- description: A merchant accountant opens a ledger before the Academy and matches every claim to a counterclaim. The arithmetic is dry, merciless, and suddenly more persuasive than rhetoric.
- option_a: Adopt double-entry standards.
- option_b: Keep older accounts.

## Chinese Text
- title: 复式记账演示
- description: 一位商人会计在学院众人面前摊开账簿，把每一笔收入都同对应的支出相互勾连。算术枯燥、冷静，却忽然比修辞更能说服人。
- option_a: 采用复式记账标准。
- option_b: 保留旧式账目。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Double-entry standards make banking reform look like a practical discipline rather than a merchant trick, so supporters can point to a method that reveals fraud and steadies trust.
- rationale_zh: 复式记账标准会让银行改革显得是一门可执行的制度，而不是商人的花招；支持者因此能指向一种既能揭露欺诈、又能稳住信任的方法。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping older accounts avoids upsetting clerks and offices that know the old forms, but it lets ambiguity remain respectable and slows acceptance of banking discipline.
- rationale_zh: 保留旧式账目可以避免惊扰熟悉旧格式的书吏和官署，却也让含混继续披着体面的外衣，拖慢对银行制度纪律的接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_familiar_accounts
  months: 18
  effects:
    old-account routine preserved: 0.02
```

## Difference From Same Issue Events
- Unlike B02 Noble Debt Roll, B01 is not a political exposure of who owes money; it is a technical demonstration of how accounts should be structured.
- Unlike B09 Fraudulent Ledger, B01 begins from a clean method rather than a discovered crime, so its side effect rewards burgher confidence instead of scandal management.
- Unlike B12 Tax Farm Accounts, B01 concerns general bookkeeping standards rather than the state revenue contractors who profit from opacity.
