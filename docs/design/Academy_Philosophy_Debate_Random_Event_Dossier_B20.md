# B20 - Crown Account Published

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Crown Account Published
- description: The Academy proposes a simplified royal account: enough figures to prove confidence, not enough to let every court faction sharpen a knife. The room immediately asks where that line is drawn.
- option_a: Publish it.
- option_b: Keep accounts closed.

## Chinese Text
- title: 公布王室账目
- description: 学院提议公布一份简化的王室账目：数字要足以证明财政自信，却又不能多到让宫廷派系人人磨刀。会场立刻追问，这条界线究竟在哪里。
- option_a: 公布账目。
- option_b: 继续封存账目。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publishing the account makes the Crown model the financial discipline it asks others to accept. The gain for reform is large, but legitimacy is risked because every revealed weakness becomes a political argument.
- rationale_zh: 公布账目意味着王权以自身示范它要求他人接受的财政纪律。改革因此大获推动，但每一个暴露出的弱点都会变成政治论据，正当性也随之冒险。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -10
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_royal_account_published
  months: 24
  effects:
    expectation of transparent public finance: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Closed accounts protect court management and keep bureaucrats from defending every number in public. They also make banking reform look like a discipline imposed on subjects while the Crown exempts itself.
- rationale_zh: 继续封存账目可以保护宫廷操作，也让官僚不必公开为每一个数字辩护。但这会让银行改革显得像是只加诸臣民、王权自身却可豁免的纪律。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_closed_royal_accounts
  months: 24
  effects:
    administrative secrecy comfort: 0.02
```

## Difference From Same Issue Events
- Unlike B04 Public Bank Proposal, B20 does not charter a new institution; it tests whether the Crown will submit its own finances to the clarity reform demands.
- Unlike B12 Tax Farm Accounts, the target is the royal account itself rather than delegated revenue contractors and their customary profit.
- Unlike B16 Mint Officer's Confession, B20 is a voluntary act of fiscal transparency from the center, not an embarrassing admission from a technical office.
