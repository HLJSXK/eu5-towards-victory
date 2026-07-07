# B17 - Army Pay Delay

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Army Pay Delay
- description: Soldiers wait outside the pay office while treasurers argue over methods, reserves, and signatures. The debate suddenly has boots, hunger, and a very practical sense of time.
- option_a: Use banking reform to pay them.
- option_b: Borrow informally again.

## Chinese Text
- title: 军饷拖延
- description: 士兵们等在发饷处外，司库们却仍在争论方法、准备金和签押。抽象辩论忽然有了靴声、饥饿，以及极其现实的时间感。
- option_a: 以银行改革解决军饷。
- option_b: 再次私下借款。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Paying the army through clarified banking practice proves reform can solve a hard state problem instead of merely pleasing merchants. The military becomes a practical ally, though the treasury must absorb the transition.
- rationale_zh: 通过清晰的银行制度支付军饷，能证明改革不只是讨好商人，而能解决国家最硬的事务。军方会成为务实盟友，但国库必须承担过渡成本。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Another informal loan gets coin into soldiers' hands without admitting the old financial channels are broken. The price is renewed dependence on private creditors who profit from keeping reform unfinished.
- rationale_zh: 再借一笔私下款项，可以不承认旧财政渠道已经失灵，就把钱发到士兵手中。代价是国家继续依赖从未完成的改革中获利的私人债主。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_informal_army_credit
  months: 18
  effects:
    creditor leverage over army finance: 0.03
```

## Difference From Same Issue Events
- Unlike B07 Royal Loan Refusal, the pressure comes from unpaid soldiers rather than bankers bargaining directly with the Crown.
- Unlike B12 Tax Farm Accounts, B17 is about expenditure and army reliability, not revenue farming or contractor audits.
- Unlike B08 Bills of Exchange, the paper-and-credit question is judged by whether it can meet a military payroll rather than move merchant wealth.
