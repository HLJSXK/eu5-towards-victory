# NW11 - Rumor of Gold

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Rumor of Gold
- description: Reports of gold spread faster than reliable latitude. Supporters argue that greed can be harnessed before it becomes policy by accident, while opponents warn that the Academy is mistaking fever for evidence.
- option_a: Use greed to fund voyages.
- option_b: Denounce the rumor.

## Chinese Text
- title: 黄金传闻
- description: 黄金的消息比可靠的纬度传播得更快。支持者认为，可以先利用贪欲来资助航行，免得它自行变成政策；反对者则警告，学院正在把狂热误当作证据。
- option_a: 用贪欲资助航行。
- option_b: 斥责这则传闻。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Using gold rumors as funding accepts a morally dubious motive while keeping discovery moving. The debate gains modest acceptance because private appetite is redirected into voyages, but the side effects mark the speculative risk around that choice.
- rationale_zh: 利用黄金传闻来筹资，等于承认一种道德上可疑的动机，同时让探索继续前进。辩论会小幅转向接受，因为私人欲望被引导进航行事业；但副作用也标记了随之而来的投机风险。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
- type: temporary_country_modifier
  key: tv_academy_debate_gold_rumor_speculation
  months: 18
  effects:
    speculative expedition pressure: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Denouncing the rumor frames discovery enthusiasm as greed wearing a scholar's coat. Clergy and nobles approve of the restraint, and the debate loses momentum as moral suspicion becomes the safer public language.
- rationale_zh: 斥责传闻会把探索热情描绘成披着学者外衣的贪欲。神职人员和贵族赞成这种克制，而当道德怀疑成为更安全的公共语言时，辩论的推进也会放缓。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW04 Merchants Want Charter, NW11 is not about a formal commercial right but about whether raw rumor and greed can be turned into useful expedition finance.
- Unlike NW08 Harbor Crowd, the persuasive object is not visible cargo in public view but an unverified promise of wealth moving through gossip.
- Unlike NW15 Colonial Charter Abuse, this event concerns the temptation that funds discovery before authority is granted, while NW15 deals with abuse after a charter holder already has power.
