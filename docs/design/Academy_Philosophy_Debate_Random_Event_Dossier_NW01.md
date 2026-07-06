# NW01 - The Sailor's Chart

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Sailor's Chart
- description: A battered chart reaches the Academy with coastlines that refuse to fit any known map. Its stains look like tavern evidence until the room notices that every wrong line still points west.
- option_a: Trust the chart.
- option_b: Dismiss it as tavern ink.

## Chinese Text
- title: 水手的海图
- description: 一张破旧海图被送进学院，上面的海岸线无法塞进任何已知地图。它的污痕起初像酒馆里的证据，直到众人发现，每一条不合旧图的线仍然指向西方。
- option_a: 信任这张海图。
- option_b: 将其斥为酒馆墨迹。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Trusting the chart lets practical seafaring evidence challenge inherited geography directly. The debate moves strongly toward acceptance because maritime merchants can now point to a usable route rather than a rumor.
- rationale_zh: 信任这张海图，等于让航海实践的证据直接挑战继承下来的地理知识。由于海商终于能指向一条可用航路，而不只是重复传闻，辩论会强烈转向接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: maritime_merchants
  stance: support
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_battered_chart
  months: 24
  effects:
    private chart copying and voyage subscriptions: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Dismissing the chart protects the old map by attacking the witness rather than the coastline. Conservative listeners gain confidence because uncertain sailor knowledge is kept outside Academy authority.
- rationale_zh: 将海图斥为酒馆墨迹，是通过贬低见证者而不是检验海岸线来保护旧地图。保守听众会更有信心，因为不稳定的水手知识被挡在学院权威之外。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike NW02 Returned Pilot, NW01 turns on a physical navigation document rather than living testimony that can be questioned in person.
- Unlike NW09 Mapmaker's Correction, this event starts outside official scholarly authority and asks whether the Academy will admit rough seafaring evidence before a specialist has regularized it.
- Unlike NW20 School Globe, NW01 is about a contested working chart arriving before consensus, not a polished teaching object displayed after the argument has matured.
