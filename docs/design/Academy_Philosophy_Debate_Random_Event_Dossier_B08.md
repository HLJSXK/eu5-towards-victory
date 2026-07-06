# B08 - Bills of Exchange

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Bills of Exchange
- description: Merchants lay out letters, seals, and signatures showing how wealth can cross borders while guarded carts are still choosing a road. The paper looks fragile until everyone notices how much coin it commands.
- option_a: Endorse bills of exchange.
- option_b: Restrict paper instruments.

## Chinese Text
- title: 汇票
- description: 商人摊开书信、印章和签名，证明财富可以在护送钱车还未选路时就已越过边境。纸张看似脆弱，直到众人看见它能调动多少硬币。
- option_a: 认可汇票。
- option_b: 限制纸面工具。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Endorsing bills of exchange makes banking reform useful to trade rather than merely tidy in ledgers, giving maritime merchants a practical reason to support the new system.
- rationale_zh: 认可汇票会让银行改革不只是账本整洁，而是真正服务贸易，使海商有切身理由支持新制度。
- effect_blocks:
```yaml
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_bills_of_exchange
  months: 24
  effects:
    commercial transfer confidence: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Restricting paper instruments reassures estates that prefer visible coin and familiar routes, but it leaves the debate suspicious of financial abstraction.
- rationale_zh: 限制纸面工具会安抚偏好实物硬币和旧有路线的等级势力，却也会让这场辩论继续怀疑金融抽象化本身。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike B01 Double-Entry Demonstration, B08 concerns portable credit between markets rather than accounting standards inside a single ledger.
- Unlike B15 Foreign Banker Arrives, B08 does not depend on an outside banking house; the pressure comes from domestic merchants demonstrating a financial instrument.
- Unlike B20 Crown Account Published, B08 asks whether paper can move private wealth efficiently, not whether the state should make its own accounts visible.
