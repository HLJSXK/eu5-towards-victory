# G09 - Salon Ridicule

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Salon Ridicule
- description: A noble salon turns the debate into evening entertainment, and by breakfast the sharpest jokes have become arguments of their own.
- option_a: Answer with a formal defense
- option_b: Let the mockery stand

## Chinese Text
- title: 沙龙嘲讽
- description: 一场贵族沙龙把辩论变成夜间消遣；到了早餐时分，最尖刻的笑话已经成了另一种论据。
- option_a: 以正式辩护回应
- option_b: 任由嘲讽流传

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: A formal defense spends prestige to convert ridicule into a public test the new claim can survive, producing a stronger push toward acceptance.
- rationale_zh: 正式辩护会消耗威望，把嘲讽转化为新主张能够经受的公开检验，从而更有力地推动接受。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
```

### Option B
- progress_delta: -5
- rationale_en: Allowing the jokes to stand lets noble opinion enjoy its victory and makes the proposition look unserious without further confrontation.
- rationale_zh: 任由笑话流传，会让贵族舆论享受胜利，也让该主张在没有进一步对抗的情况下显得不够严肃。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike G08, noble approval here comes from social mockery winning the room, not from rejecting merchant publicity.
- Unlike G15, this is not a rule-bound challenge by a respected opponent; it is reputation warfare conducted through wit and status.
