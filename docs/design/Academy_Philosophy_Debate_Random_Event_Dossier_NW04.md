# NW04 - Merchants Want Charter

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Merchants Want Charter
- description: Merchants offer to fund voyages if the Crown lets them name harbors they have not yet seen. Their confidence is useful, expensive, and already trying to put a seal on empty water.
- option_a: Issue a charter.
- option_b: Keep discovery under Crown lock.

## Chinese Text
- title: 商人索要特许状
- description: 商人提出资助远航，条件是王权允许他们给尚未见过的港湾命名。他们的信心有用、昂贵，而且已经迫不及待地想把印章盖在空白海面上。
- option_a: 颁发特许状。
- option_b: 将发现权锁在王权之下。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: A charter turns the New World claim into financed action and gives merchants a stake in proving the Academy right. Acceptance rises strongly because private capital starts treating discovery as an investable reality.
- rationale_zh: 特许状会把新世界主张转化为有资金支持的行动，也让商人有理由证明学院是对的。私人资本开始把发现视为可投资的现实，因此接受度会大幅上升。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
```

### Option B
- progress_delta: -5
- rationale_en: Keeping discovery under Crown lock preserves legitimacy and central control, but it leaves voyages dependent on cautious official timing. The debate loses momentum because interested backers are kept at arm's length.
- rationale_zh: 将发现权锁在王权之下可以维护正统性和中央控制，却也让远航继续受谨慎的官方节奏支配。由于有意资助者被保持距离，辩论的势头会减弱。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
- type: temporary_country_modifier
  key: tv_academy_debate_crown_discovery_lock
  months: 18
  effects:
    centralized control over overseas claims: 0.02
```

## Difference From Same Issue Events
- Unlike NW10 Naval Officers Demand Funds, NW04 asks whether commercial backers receive legal rights, not whether the state pays for ocean-capable fleets.
- Unlike NW15 Colonial Charter Abuse, this event happens before charter failure and tests the initial bargain between capital, naming rights, and discovery.
- Unlike NW19 Port Investors Panic, merchants here are still eager to commit money rather than retreating after losses at sea.
