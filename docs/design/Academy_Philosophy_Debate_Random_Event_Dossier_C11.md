# C11 - Confessional Schoolbooks

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Confessional Schoolbooks
- description: New schoolbooks arrive at the Academy with doctrine printed beside spelling, sums, and civic maxims. Children will learn their letters and the realm's confession from the same page.
- option_a: Approve them.
- option_b: Keep schools doctrinally local.

## Chinese Text
- title: 宗派教义课本
- description: 新课本被送到学院，教义与拼写、算术和臣民格言并排印在纸上。孩子们将从同一页上学会字母，也学会国家希望他们信奉的教义。
- option_a: 批准使用这些课本。
- option_b: 让各地学校自行讲授教义。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Approving the schoolbooks turns confession into basic civic literacy, giving the accepting side a broad generational argument instead of another narrow clerical order.
- rationale_zh: 批准课本会把宗派教义变成基本的臣民读写教育，使支持接纳的一方获得面向下一代的广泛理由，而不只是又一道狭窄的教会命令。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
- type: seat_cooldown
  group: scholarly_community
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Leaving doctrine to local schools preserves clerical and parish autonomy, but it also keeps confession fragmented enough that the Academy's policy case weakens.
- rationale_zh: 让各地学校自行讲授教义能保留教士和堂区的自主权，但也会让宗派教义继续分散，削弱学院把它上升为国家政策的论证。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike C05, which concerns the wording of a catechism itself, C11 is about embedding doctrine into ordinary childhood education.
- Unlike C16, which funds confessional schools through taxation, C11 changes what schools teach without making revenue the central dispute.
- Unlike C02, where the state wants parish records, C11 shapes belief through literacy and curriculum rather than through administrative registration.
