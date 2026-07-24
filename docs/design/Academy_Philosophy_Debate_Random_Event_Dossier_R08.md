# R08 - Court Masque of Renewal

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Court Masque of Renewal
- description: Courtiers propose a grand performance celebrating rebirth, order, and the Crown's excellent taste. Everyone agrees the doctrine would be more convincing with music, costumes, and invoices.
- option_a: Fund the masque.
- option_b: Avoid theatrical doctrine.

## Chinese Text
- title: 宫廷新生假面剧
- description: 朝臣提议举办一场盛大演出，歌颂新生、秩序，以及王室无可挑剔的品味。众人一致认为，只要有音乐、服饰和账单，教义就会更有说服力。
- option_a: 资助这场假面剧。
- option_b: 避免把学说搬上舞台。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Funding the masque turns Renaissance renewal into a public court ritual, modestly helping acceptance by attaching the issue to spectacle and prestige at a real treasury cost.
- rationale_zh: 资助假面剧会把文艺复兴式新生包装成公开的宫廷仪式，借声望和盛典略微推动接受，但国库必须承担成本。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: temporary_country_modifier
  key: tv_academy_debate_court_masque
  months: 12
  effects:
    courtly prestige display: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Avoiding theatrical doctrine keeps the treasury quiet and prevents courtiers from dressing the issue as royal fashion, but it also denies the Renaissance side a persuasive ceremonial stage.
- rationale_zh: 避免把学说搬上舞台可以让国库安静，也防止朝臣把议题装扮成王室风尚，但这会剥夺文艺复兴一方有说服力的仪式舞台。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
- type: seat_cooldown
  group: artists
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R04 Patronage Ledger, R08 spends money on court spectacle and symbolic persuasion rather than on the long patronage structure behind artistic innovation.
- Unlike R12 Fresco of the New Age, the medium is a temporary performance with courtiers and public ceremony, not a permanent image inside the Academy.
- Unlike R16 New Calendar of Festivals, the masque is a single court-centered display rather than a broad reshaping of civic festival life.
