# NW08 - Harbor Crowd

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Harbor Crowd
- description: The harbor fills with people eager to see strange goods unloaded. Each object becomes a small ambassador, giving the Academy's argument color, weight, and something the crowd can point at.
- option_a: Display the goods.
- option_b: Seal the cargo.

## Chinese Text
- title: 港口人群
- description: 港口挤满了想看异域货物卸船的人。每一件物品都像一位小小的使节，让学院的论点有了颜色、重量，以及围观者可以指点的形状。
- option_a: 展示这些货物。
- option_b: 封存货物。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Public display turns distant discovery into tangible evidence for ordinary observers. The progress gain is modest because curiosity is broad but shallow, yet public opinion begins leaning toward acceptance.
- rationale_zh: 公开展示会把遥远的发现变成普通旁观者也能触摸和想象的证据。进展只是小幅增加，因为这种好奇广泛却不深，但舆论会开始倾向接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_harbor_exhibition
  months: 12
  effects:
    public curiosity about overseas goods: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Sealing the cargo prevents disorder and rumor, but it also keeps discovery abstract and controlled by officials. The debate loses momentum because the public is denied its most immediate proof.
- rationale_zh: 封存货物可以防止混乱和谣言，却也让发现继续停留在抽象层面，并由官员独占解释权。由于公众被剥夺了最直接的证据，辩论的势头会减弱。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_sealed_cargo_order
  months: 12
  effects:
    port order and contraband control: 0.02
```

## Difference From Same Issue Events
- Unlike NW01 The Sailor's Chart or NW09 Mapmaker's Correction, NW08 relies on material spectacle rather than cartographic authority.
- Unlike NW16 Imported Crop, the evidence is an immediate public display of cargo, not a slower test of cultivation in a controlled garden.
- Unlike NW20 School Globe, NW08 persuades through a harbor crowd and sensory curiosity rather than through formal Academy teaching.
