# P13 - University Printer

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: University Printer
- description: A university requests its own press to avoid begging city printers for sober priorities.
- option_a: Grant the press.
- option_b: Centralize printing.

## Chinese Text
- title: 大学印刷所
- description: 一所大学请求拥有自己的印刷机，免得总要央求城中印工优先处理严肃文本。
- option_a: 准许设立印刷所。
- option_b: 集中管理印刷事务。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Granting the university a press makes printing a scholarly instrument instead of merely an urban trade, giving learned supporters a direct stake in acceptance.
- rationale_zh: 准许大学设立印刷所，会让印刷术成为学术工具，而不只是城市行业，使学者支持者直接从接纳中受益。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Centralizing printing satisfies officials who prefer every press to answer upward, but it denies universities a practical demonstration of scholarly self-direction.
- rationale_zh: 集中管理印刷事务能满足希望所有印刷机向上负责的官员，却剥夺了大学展示学术自治能力的实践机会。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_central_print_office
  months: 18
  effects:
    licensing consistency: 0.02
```

## Difference From Same Issue Events
- Unlike P02, this event is about a learned institution seeking its own press rather than printers seeking guild recognition.
- Unlike P06, the concern is control over production capacity, not whether a corrected textbook should be adopted.
- Unlike P11, the administrative benefit is central oversight of presses rather than standardized publication of royal law.
