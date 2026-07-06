# NW03 - Clergy Ask for Mission Rights

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Clergy Ask for Mission Rights
- description: Clerics argue that discovery without conversion is only wandering with better maps. The Academy's debate is pulled between souls, surveys, and the uncomfortable question of who gets to define a new shore first.
- option_a: Grant mission priority.
- option_b: Balance mission with survey.

## Chinese Text
- title: 神职人员索要传教权
- description: 神职人员主张，没有皈依的发现不过是带着更好地图的游荡。学院的辩论被拉扯在灵魂、测绘和一个令人不安的问题之间：谁有资格首先定义一片新海岸？
- option_a: 授予传教优先权。
- option_b: 让传教与测绘并重。

## Mechanics
### Option A
- progress_delta: -5
- rationale_en: Mission priority narrows discovery into a clerical mandate before the Academy can treat new lands as an empirical problem. Clergy approve, but acceptance slows because survey, trade, and testimony become subordinate to conversion.
- rationale_zh: 传教优先会在学院把新土地视为经验问题之前，先把发现缩窄成神职使命。神职人员会认可这一安排，但测绘、贸易和证词都被置于皈依之下，接受进程因此放缓。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.04
- type: temporary_country_modifier
  key: tv_academy_debate_mission_priority
  months: 18
  effects:
    missionary access ahead of geographic survey: 0.02
```

### Option B
- progress_delta: +5
- rationale_en: Balancing mission with survey keeps religious purpose present while refusing to let it monopolize the meaning of discovery. The debate gains modestly because scholars can still collect evidence, though clergy satisfaction falls.
- rationale_zh: 让传教与测绘并重，既保留宗教目的，又拒绝让它垄断发现的意义。学者仍能收集证据，所以辩论会小幅转向接受，但神职人员的满意度会下降。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.03
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW18 Missionary Grammar, NW03 is about institutional priority before knowledge is gathered, not about a linguistic artifact that already proves new voices exist.
- Unlike NW06 Disease Report, the constraining force is religious jurisdiction rather than medical caution and port health.
- Unlike NW14 Sailors' Superstitions, clergy influence here comes through formal mission rights, not through answering sailors' fears and omens.
