# P11 - Royal Proclamation Printed

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Royal Proclamation Printed
- description: Officials discover that printed proclamations reach people before rumor edits them.
- option_a: Standardize printed law.
- option_b: Keep proclamations traditional.

## Chinese Text
- title: 印刷王室公告
- description: 官员们发现，印刷公告能在谣言替它改写之前抵达民众手中。
- option_a: 统一印刷法令。
- option_b: 保留传统公告方式。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Standardized printed law proves that the press can serve royal administration with speed and consistency, so acceptance gains a strong institutional argument.
- rationale_zh: 统一印刷法令证明印刷术能以速度和一致性服务王室行政，因此接纳印刷应用获得了强有力的制度论据。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_printed_law_standardization
  months: 18
  effects:
    administrative reach and consistency: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Keeping proclamations traditional preserves local channels of interpretation and lets regional elites remain useful gatekeepers of the law.
- rationale_zh: 保留传统公告方式会维持地方解释渠道，让地方精英继续充当法令传播的有用把关人。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike P04, this event concerns state law and administrative reach rather than cheap religious instruction in villages.
- Unlike P13, the press is used by central government rather than requested as a university privilege.
- Unlike P20, the issue is not censorial obstruction but whether official communication should become standardized through print.
