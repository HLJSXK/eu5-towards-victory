# MF06 - Fire in the Yard

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Fire in the Yard
- description: A workshop fire leaves scorched beams, ruined stock, and a crowd of witnesses ready to decide what the flames have proven. Some see danger in concentration; others see danger in leaving concentration unregulated.
- option_a: Regulate manufactories.
- option_b: Condemn large workshops.

## Chinese Text
- title: 院中失火
- description: 一场作坊大火留下焦黑梁木、毁坏存货，以及一群急着解释火焰含义的目击者。有人认为集中生产本身危险，也有人认为真正危险的是集中生产却无人监管。
- option_a: 监管手工业工场。
- option_b: 谴责大型作坊。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Regulation admits that large workshops carry new risks, but treats those risks as a reason to govern manufactories rather than abandon them. The gold cost represents inspections, firebreaks, and safer storage.
- rationale_zh: 监管承认大型作坊带来了新的风险，但把这些风险视为治理手工业工场的理由，而不是放弃它们的理由。花费金币代表检查、防火隔离和更安全的储料安排。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_manufactory_fire_codes
  months: 18
  effects:
    inspected workshop safety codes: 0.02
```

### Option B
- progress_delta: -10
- rationale_en: Condemning large workshops lets guild critics turn the fire into a verdict against concentration itself. It strongly pushes rejection because safety failure becomes proof that scale should not be trusted.
- rationale_zh: 谴责大型作坊会让行会批评者把火灾变成对集中生产本身的判决。这会强烈推动否定，因为安全事故被说成了规模化不可信的证据。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 24
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike MF02 Guild Master's Complaint, MF06 is about public safety after a visible accident rather than craft quality standards raised before disaster.
- Unlike MF18 Quality Scandal, MF06 concerns fire, storage, and concentration risk rather than defective output failing inspection.
- Unlike MF15 Coal Smoke Argument, MF06 asks whether dangerous workshops can be regulated after a crisis, not whether industrial pollution should limit siting.
