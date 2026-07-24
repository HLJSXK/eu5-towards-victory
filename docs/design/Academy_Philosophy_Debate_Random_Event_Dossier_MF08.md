# MF08 - Military Contract

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Military Contract
- description: The army offers a contract large enough to make every workshop owner count their benches twice. The catch is simple: the Crown wants parts and cloth that match, not charming local variations.
- option_a: Accept standard production.
- option_b: Keep bespoke supply.

## Chinese Text
- title: 军需合同
- description: 军队开出一份大到足以让每个作坊主重新清点工台的合同。条件也很简单：王权要的是一致的零件和布匹，而不是各地各有风味的差异。
- option_a: 接受标准化生产。
- option_b: 保留定制供应。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Standard production ties manufactories to state capacity: weapons, uniforms, and supplies become reliable because workshops can repeat the same specification. The professional military supports the reform because predictability matters in the field.
- rationale_zh: 标准化生产把手工业工场同国家能力连接起来：武器、制服和补给之所以可靠，是因为作坊能够反复执行同一规格。职业军队支持这种改革，因为战场上可预期性极其重要。
- effect_blocks:
```yaml
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_standard_military_contracts
  months: 24
  effects:
    standardized military supply: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Keeping bespoke supply protects older contractors and local methods, but it makes the case for manufactories less urgent. Production remains a network of favors and adaptations rather than a system of repeatable standards.
- rationale_zh: 保留定制供应保护了旧承包商和地方做法，但也削弱了手工业工场的必要性。生产仍是一张人情和临场调整的网络，而不是可重复规格的体系。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_bespoke_supply_networks
  months: 12
  effects:
    familiar supplier networks protected: 0.02
```

## Difference From Same Issue Events
- Unlike MF11 Standard Parts, MF08 frames standardization through a state military contract rather than artisan proof of interchangeable components.
- Unlike MF05 Raw Material Bottleneck, MF08 is about uniform output and procurement discipline, not whether enough inputs can reach production.
- Unlike MF18 Quality Scandal, MF08 debates standardization before delivery instead of repairing confidence after a failed batch.
