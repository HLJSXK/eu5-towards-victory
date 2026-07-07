# B18 - Contract in Plain Language

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Contract in Plain Language
- description: Reformers bring a financial contract written so ordinary readers can understand what binds them. The lawyers look as if someone has opened a window in winter.
- option_a: Require plain contracts.
- option_b: Keep elite legal forms.

## Chinese Text
- title: 白话契约
- description: 改革者呈上一份金融契约，普通读者也能看懂自己受何约束。律师们的神情像是有人在寒冬里突然开了窗。
- option_a: 要求契约使用明白文句。
- option_b: 保留精英法律格式。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Plain contracts make banking reform visible to people who normally meet finance only as fine print. Public opinion warms because reform now protects comprehension, not just balance sheets.
- rationale_zh: 明白文句让通常只在细小字句里接触金融的人也能看见银行改革。公众舆论会转向支持，因为改革保护的不只是账面，也包括理解权。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_plain_contract_forms
  months: 18
  effects:
    popular trust in banking courts: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping elite forms preserves professional control and reassures bankers that clever wording will not be overturned by sudden popular scrutiny. The debate loses public force because ordinary debtors remain dependent on interpreters.
- rationale_zh: 保留精英格式能维护专业阶层的控制，也让银行家相信精巧措辞不会突然遭到大众审视。但普通债务人仍要依赖解释者，辩论因此失去公共力量。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike B13 Scholar of Interest, this event is not about teaching financial mathematics but about making legal obligations readable before harm occurs.
- Unlike B06 Widow's Deposit, B18 does not begin with one injured petitioner; it changes the language every borrower and depositor must face.
- Unlike B08 Bills of Exchange, the issue is not whether paper instruments should exist, but whether their terms can be understood outside elite legal circles.
