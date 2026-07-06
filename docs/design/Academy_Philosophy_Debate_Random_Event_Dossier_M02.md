# M02 - Genealogies on the Table

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Genealogies on the Table
- description: Great houses bring polished family trees to prove that service is inherited like silver.
- option_a: Question the trees.
- option_b: Honor hereditary service.

## Chinese Text
- title: 桌上的族谱
- description: 大家族捧来装帧精美的族谱，想证明效忠与银器一样可以世代相传。
- option_a: 质疑这些族谱。
- option_b: 表彰世袭服务。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Questioning the genealogies makes ancestry answer to evidence instead of etiquette. The Crown spends prestige by publicly challenging houses that are accustomed to being treated as proof in themselves.
- rationale_zh: 质疑族谱，就是要求血统接受证据而不是礼节的审查。王室公开挑战那些习惯把自身当作证据的家族，因此要消耗威望。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Honoring hereditary service grants the noble argument its strongest form: past office becomes a credential for future office. That pushes the debate away from open assessment and toward inherited entitlement.
- rationale_zh: 表彰世袭服务等于把贵族论点推到最有力的位置：祖先任职本身成了后代任职的凭据。这会把辩论从公开考核拉回继承权利。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.05
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike M01 Anonymous Examination, this event attacks or endorses pedigree as evidence before any examination procedure begins.
- Unlike M14 Hereditary Office in Crisis, no hereditary officer has visibly failed; the dispute is over inherited legitimacy in the abstract.
- Unlike M10 Boycott by Old Families, the great houses argue through polished symbols of continuity rather than through institutional withdrawal.
