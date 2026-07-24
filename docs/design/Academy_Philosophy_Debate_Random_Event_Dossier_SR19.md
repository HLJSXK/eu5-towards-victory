# SR19 - Experimental Oath

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Experimental Oath
- description: Assistants ask for protection if results contradict patrons, teachers, or the Crown's favorite theory. They are willing to measure honestly, but not to be ruined for noticing what the instruments say.
- option_a: Protect the assistants.
- option_b: Require deference.

## Chinese Text
- title: 实验誓约
- description: 助手们请求得到保护，以免结果违背赞助人、导师或王室偏爱的理论时遭到清算。他们愿意诚实测量，却不愿因为看见仪器所显示的事实而毁掉前程。
- option_a: 保护助手。
- option_b: 要求他们服从。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Protecting assistants makes contradictory results safer to report, which strengthens experiment as a collective method rather than a performance controlled by patrons. Legitimacy strains because hierarchy is asked to tolerate unwelcome truth.
- rationale_zh: 保护助手会让相互矛盾的结果更容易被报告出来，从而把实验强化为一种集体方法，而不是受赞助人操纵的表演。由于等级秩序必须容忍不合意的真相，正统性会承受压力。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -10
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
- type: seat_stance
  group: great_scientist
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Requiring deference keeps assistants, teachers, and patrons in their expected places. The hierarchy approves, but the debate turns sharply away from a method that depends on witnesses speaking against power.
- rationale_zh: 要求服从可以让助手、导师和赞助人继续待在各自应在的位置。等级秩序会赞同此举，但辩论会急剧远离那种依赖见证者敢于违逆权势发声的方法。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike SR05 Academy Experiment Code, SR19 protects the people who report results rather than the paperwork used to record them.
- Unlike SR02 Failed Replication, SR19 is not about one failed trial; it is about whether future contradictions can be reported without retaliation.
- Unlike SR18 Dangerous Publication, SR19 concerns vulnerable assistants inside the experimental process, not the public release of a finished treatise.
