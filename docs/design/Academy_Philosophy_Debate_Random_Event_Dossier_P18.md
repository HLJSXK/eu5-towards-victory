# P18 - Press in the Barracks

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Press in the Barracks
- description: Officers request printed drill manuals and technical sheets.
- option_a: Approve military printing.
- option_b: Keep presses civil.

## Chinese Text
- title: 营房里的印刷机
- description: 军官们请求印制操典手册和技术单页。
- option_a: 批准军事印刷。
- option_b: 让印刷机只服务民政事务。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Military manuals show that print can standardize practice under pressure, winning practical support from officers without turning the debate fully public.
- rationale_zh: 军事手册证明印刷术能在高压环境下统一实践，从军官那里赢得务实支持，但不会把争论完全推向街头。
- effect_blocks:
```yaml
- type: seat_stance
  group: professional_military
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping presses civil reassures conservative officers that barracks discipline will not be rewritten by printed sheets, but it denies the press a useful technical role.
- rationale_zh: 让印刷机只服务民政事务会使保守军官相信营房纪律不会被印刷单页改写，却也否认了印刷术有用的技术角色。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_civil_press_boundary
  months: 12
  effects:
    barracks information discipline: 0.02
```

## Difference From Same Issue Events
- Unlike P06, this event concerns drill and technical standardization rather than school textbooks and corrected diagrams.
- Unlike P10, the affected profession is the officer corps, not scribes displaced by movable type.
- Unlike P14, the military request assumes print can improve precision instead of spreading a single error through many copies.
