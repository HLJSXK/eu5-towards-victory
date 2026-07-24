# P01 - First Run of Pamphlets

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: First Run of Pamphlets
- description: The first pamphlet run finishes before the censors finish deciding what a pamphlet is.
- option_a: Distribute it widely.
- option_b: Confine it to scholars.

## Chinese Text
- title: 小册子首印
- description: 第一批小册子刚刚印完，审查官还没决定小册子到底算什么。
- option_a: 广泛散发。
- option_b: 只限学者传阅。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Wide distribution turns the new medium into a public fact before old controls can define it, so the debate moves sharply toward accepting printing press applications.
- rationale_zh: 广泛散发让新媒介先于旧式管制成为公共事实，因此辩论明显转向接受印刷术应用。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Restricting copies to scholars keeps the argument orderly but prevents print from proving its mass political value.
- rationale_zh: 将副本限制在学者圈内能维持秩序，却让印刷术无法证明其大众政治价值。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
```

## Difference From Same Issue Events
- Unlike P08, this event is about an officially visible first circulation, not anonymous agitation that embarrasses allies.
- Unlike P15, the printed matter remains argumentative pamphlets rather than popular song or simplified mass culture.
- Unlike P20, the state has not yet chosen to bypass a censorial process; the timing pressure comes from print outrunning definitions.
