# P08 - Anonymous Broadsides

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Anonymous Broadsides
- description: Anonymous broadsides support the issue with such vigor that even allies look nervous.
- option_a: Tolerate them.
- option_b: Hunt the authors.

## Chinese Text
- title: 匿名传单
- description: 匿名传单用过分热烈的语气支持这项议题，连盟友都显得不安。
- option_a: 容忍这些传单。
- option_b: 搜捕作者。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Tolerating the broadsides accepts messy public enthusiasm as part of print politics, allowing popular pressure to pull the debate toward acceptance.
- rationale_zh: 容忍这些传单就是承认混乱的大众热情也是印刷政治的一部分，让民间压力把辩论推向接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Hunting the authors calms officials and reduces street pressure, but it frames anonymous print as a threat rather than a sign of widening debate.
- rationale_zh: 搜捕作者能安抚官员并减轻街头压力，却把匿名印刷品定义成威胁，而不是辩论扩大的迹象。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_broadsides_watch
  months: 12
  effects:
    anonymous street agitation: -0.03
```

## Difference From Same Issue Events
- Unlike P01, the circulation here is uncontrolled and anonymous rather than an identifiable first pamphlet run.
- Unlike P05, the danger is overzealous support for the issue, not court gossip mixed with serious argument.
- Unlike P15, the popular format is a direct political broadside rather than a memorable but distorted ballad.
