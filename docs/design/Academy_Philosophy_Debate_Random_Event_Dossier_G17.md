# G17 - Translation Quarrel

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Translation Quarrel
- description: Two translations of the same key term produce two different futures for the realm. Each side insists the other has mistranslated both the word and the age.
- option_a: Sponsor a new translation
- option_b: Keep the traditional wording

## Chinese Text
- title: 译词之争
- description: 同一个关键词的两种译法，为国家勾勒出两个不同的未来。双方都坚称，对方不仅译错了词，也译错了时代。
- option_a: 资助新的译本
- option_b: 保留传统措辞

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Commissioning a new translation gives reformers a legitimate path to clarify the disputed term, but the work costs money and temporarily empowers scholars over inherited wording.
- rationale_zh: 委托新译本能让改革派以正当方式澄清争议词义，但这需要花费资金，也会暂时让学者的判断压过继承下来的措辞。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Keeping the old wording preserves continuity and reassures conservative readers, but it lets inherited language narrow what the debate can imagine.
- rationale_zh: 保留旧措辞可以维持连续性，并安抚保守读者，但也会让继承下来的语言限制辩论能够想象的未来。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike G03 Useful Misquotation, the dispute is openly philological rather than a questionable quotation that happens to help one side.
- Unlike G04 Margins of the Old Book, authority rests in translation choice, not in whether an old commentary should be treated as evidence.
- Unlike G12 Missing Manuscript, the key object is not a recovered source but the political meaning created by rendering an existing source.
