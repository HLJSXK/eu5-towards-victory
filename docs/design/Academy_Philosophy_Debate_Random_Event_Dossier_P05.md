# P05 - Scandal Sheet

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Scandal Sheet
- description: A printer publishes court gossip beside serious argument and sells both equally well.
- option_a: Defend press freedom.
- option_b: Punish the printer.

## Chinese Text
- title: 丑闻小报
- description: 一名印刷商把宫廷流言和严肃论辩印在一起出售，两者卖得一样好。
- option_a: 捍卫出版自由。
- option_b: 惩罚印刷商。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Defending the press despite vulgar misuse protects the principle of open publication, but the Crown pays a legitimacy cost for tolerating scandal.
- rationale_zh: 即便印刷被低俗滥用仍然加以维护，能够保护公开出版的原则，但王权会因容忍丑闻而付出正统性代价。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -5
```

### Option B
- progress_delta: -10
- rationale_en: Punishing the printer restores visible order by making scandal an example, but it also teaches observers that press freedom ends at court embarrassment.
- rationale_zh: 惩罚印刷商把丑闻变成警示，恢复可见秩序，却也让旁观者明白出版自由止步于宫廷难堪。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_scandal_sheet_crackdown
  months: 12
  effects:
    public-order enforcement: 0.03
```

## Difference From Same Issue Events
- Unlike P01, the challenge is not whether print can circulate but whether an ugly use of circulation should invalidate the medium.
- Unlike P16, the offense is general court scandal rather than a formal noble libel suit over privilege.
- Unlike P19, the printer's notoriety damages legitimacy instead of being harnessed as useful celebrity.
