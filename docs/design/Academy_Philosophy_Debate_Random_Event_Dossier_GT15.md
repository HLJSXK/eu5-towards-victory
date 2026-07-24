# GT15 - Naval Escort Debate

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Naval Escort Debate
- description: Merchants demand escorts and admirals demand funds, a partnership no one calls cheap. The Academy hears a simple question in expensive clothing: if trade is now global, must the state guard every horizon it profits from?
- option_a: Fund escorts.
- option_b: Let merchants self-insure.

## Chinese Text
- title: 海军护航之辩
- description: 商人要求护航，海军将领要求拨款，这种合作没人会称之为便宜。学院听见了一个穿着昂贵外衣的简单问题：如果贸易已经走向全球，国家是否必须守卫每一条让它获利的天际线？
- option_a: 资助护航。
- option_b: 让商人自行投保。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding escorts makes global trade a state-backed strategic project rather than a private gamble. Acceptance rises sharply because the Crown visibly protects distant commerce, but the treasury is strained and maritime merchants become invested in the debate.
- rationale_zh: 资助护航，会把全球贸易变成由国家背书的战略事业，而不是私人冒险。王冠明确保护远方商业，接受度因此大幅上升，但国库会承压，海贸商人也会更深地卷入辩论。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_funded_trade_escorts
  months: 24
  effects:
    protected shipping confidence: 0.04
```

### Option B
- progress_delta: -5
- rationale_en: Letting merchants self-insure keeps state spending low and leaves ocean risk in private hands. The debate retreats because the Crown refuses to treat global trade protection as a public responsibility.
- rationale_zh: 让商人自行投保，可以维持较低的国家开支，并把海上风险留在私人手中。辩论因此后退，因为王冠拒绝把全球贸易保护视为公共责任。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_stance
  group: professional_military
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT06 Insurance for Ships, which accepts private maritime risk pooling, GT15 asks whether the state should pay for armed protection.
- Unlike GT11 Caravan and Convoy, this event is not about linking route systems but about defending sea lanes with public funds.
- Unlike GT14 Port Quarantine, GT15's security problem is violence and naval capacity rather than disease control.
