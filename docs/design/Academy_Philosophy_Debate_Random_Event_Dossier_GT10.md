# GT10 - Standard Weights

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Standard Weights
- description: Traders arrive with scales, stones, stamped bars, and accusations from half the market towns in the realm. Fraud has become local enough to defend as tradition.
- option_a: Standardize weights.
- option_b: Preserve local measures.

## Chinese Text
- title: 标准度量衡
- description: 商人带着天平、砝码、打印金属条和来自半数集镇的控诉来到学院。欺诈已经地方化到可以被辩称为传统的程度。
- option_a: 统一度量衡。
- option_b: 保留地方量制。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Standard weights make distant markets comparable and enforceable, so global trade appears as a lawful system rather than a chain of local tricks. Bureaucrats and merchants both gain a usable language of measurement.
- rationale_zh: 统一度量衡会让远方市场变得可比较、可执行，使全球贸易显得是一套法定制度，而不是一串地方把戏。官僚和商人都会获得可用的计量语言。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: temporary_country_modifier
  key: tv_academy_debate_standard_weights
  months: 24
  effects:
    market measurement fraud reduced: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Preserving local measures protects customary market authority and lets towns keep familiar frauds inside familiar names. It strongly weakens acceptance because global trade cannot scale without shared measures.
- rationale_zh: 保留地方量制会保护各地市场惯例，让城镇继续把熟悉的欺诈藏在熟悉的名称里。这会强烈削弱接受倾向，因为全球贸易若无共同度量就难以扩展。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_local_measures_preserved
  months: 18
  effects:
    local market custom protected: 0.02
```

## Difference From Same Issue Events
- Unlike GT17 Language of Contracts, GT10 standardizes physical measurement rather than the words used to describe obligations.
- Unlike GT03 Tariff Confusion, GT10 targets market fraud and comparability rather than the customs schedule at the border.
- Unlike GT16 Guild Monopoly Challenge, GT10 affects measurement across many markets instead of breaking one organized privilege.
