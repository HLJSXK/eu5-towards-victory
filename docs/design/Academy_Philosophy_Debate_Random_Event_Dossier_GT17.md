# GT17 - Language of Contracts

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Language of Contracts
- description: Translators bring three versions of the same trade contract to the Academy, and only one of them would have spared the cargo. The room discovers that profit can drown in a single ambiguous clause.
- option_a: Standardize trade languages.
- option_b: Keep local contract forms.

## Chinese Text
- title: 契约语言
- description: 译员把同一份贸易契约的三种文本带到学院，而其中只有一种本能保住那批货物。众人这才发现，利润也会淹没在一个含混条款之中。
- option_a: 统一贸易语言。
- option_b: 保留本地契约格式。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Standardized trade language turns Global Trade into a shared legal and scholarly discipline. It gives merchants clearer instruments while letting scholars prove that words can protect commerce as surely as escorts.
- rationale_zh: 统一贸易语言会把全球贸易变成共同的法律与学术规范。商人得到更清晰的工具，学者也能证明文字和护航一样能保护商业。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Keeping local contract forms preserves familiar authority in each market, but it leaves long-distance exchange vulnerable to mistranslation and keeps the issue provincial.
- rationale_zh: 保留本地契约格式能维护各市场熟悉的权威，却也让远距离交换继续暴露在误译之下，使这个议题停留在地方层面。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_local_contract_forms
  months: 18
  effects:
    local legal custom preserved: 0.02
```

## Difference From Same Issue Events
- Unlike GT10 Standard Weights, GT17 standardizes contractual language rather than physical measures across markets.
- Unlike GT11 Caravan and Convoy, GT17 does not decide which routes deserve support; it decides whether agreements can travel safely between routes.
- Unlike GT20 Map of Trade Winds, GT17 concerns legal translation and commercial trust on paper, not navigation practice at sea.
