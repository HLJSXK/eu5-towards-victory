# G12 - The Missing Manuscript

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Missing Manuscript
- description: A manuscript long rumored to be lost arrives from a private collection just as the debate begins to tire. Its pages smell of dust, money, and the possibility that one side has been missing its strongest witness.
- option_a: Publish extracts.
- option_b: Lock it in the archive.

## Chinese Text
- title: 失踪手稿
- description: 一份传闻早已遗失的手稿，在辩论渐显疲态时从私人藏书中现身。纸页带着尘土、金钱，以及某一方终于找回关键证人的意味。
- option_a: 公布摘录。
- option_b: 锁入档案室。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publishing the extracts gives the accepting side a dramatic evidentiary breakthrough, but the Crown spends prestige to authenticate, copy, and defend a source that came through private hands.
- rationale_zh: 公布摘录为接受方带来戏剧性的证据突破，但王室必须花费威望来鉴定、抄录并维护这份经由私人之手而来的材料。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
```

### Option B
- progress_delta: -5
- rationale_en: Archiving the manuscript prevents the new evidence from changing the room and reassures conservative owners that private collections will not be turned into public weapons overnight.
- rationale_zh: 将手稿锁入档案室阻止新证据改变会场局势，也安抚保守的藏书主人，使他们相信私人收藏不会一夜之间变成公开武器。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike G04, which argues over an old commentary already inside the Academy library, this event introduces a newly recovered private source with ownership politics attached.
- Unlike G17, where the cost is producing a better translation, this event's cost is public authentication and controlled publication.
- Unlike G03, the manuscript is not useful because it is ambiguous; it is useful because it appears materially authoritative.
