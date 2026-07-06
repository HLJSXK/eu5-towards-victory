# MF13 - Rural Displacement

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Rural Displacement
- description: Peasant spokesmen complain that manufactory demand pulls hands from fields and daughters from household arrangements. The Academy hears not merely an objection to production, but the creaking of an entire rural order.
- option_a: Manage transition.
- option_b: Slow expansion.

## Chinese Text
- title: 乡村流离
- description: 农民代表抱怨，工场的需求把劳力从田地里拉走，也把女儿们从家庭安排里带走。学院听见的不是单纯的生产异议，而是一整个乡村秩序正在摇晃的声音。
- option_a: 管理这场转变。
- option_b: 放慢扩张。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Managing the transition admits that manufactories disrupt rural life while refusing to abandon the new model. Acceptance rises carefully, with public spending used to soften the social shock.
- rationale_zh: 管理转变等于承认工场会冲击乡村生活，但并不放弃新模式。接受度会谨慎上升，同时以公共支出来缓和社会震荡。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_cooldown
  group: peasants
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Slowing expansion gives peasants a clear victory and frames manufactories as something that must wait upon rural custom. The debate turns sharply against acceptance because the old household economy regains authority.
- rationale_zh: 放慢扩张会让农民获得明确胜利，并把工场塑造成必须服从乡村习俗的事物。由于旧有家庭经济重新取得权威，辩论会明显转向拒绝。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: peasants_estate
  value: 0.05
```

## Difference From Same Issue Events
- Unlike MF03 Waterwheel Proposal, where local disruption comes from a specific machine and site, MF13 treats labor migration and household strain as the central issue.
- Unlike MF07 Clock Discipline, which focuses on time rules inside the workplace, MF13 focuses on the village and family consequences before workers even enter the yard.
- Unlike MF16 Piecework Pay, which debates wage arithmetic, MF13 asks whether manufactories should draw rural people away from older social obligations at all.
