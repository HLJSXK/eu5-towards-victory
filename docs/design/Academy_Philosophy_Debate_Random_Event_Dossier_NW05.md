# NW05 - Native Envoy's Account

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Native Envoy's Account
- description: A translated account from across the sea contradicts half the Academy's assumptions without sounding impressed by any of them. The room discovers that the new world has not been waiting silently to be described.
- option_a: Let it reshape the debate.
- option_b: Treat it as curiosity.

## Chinese Text
- title: 原住民使者的叙述
- description: 一份来自海彼岸的译文叙述反驳了学院一半的假设，而且听起来并不为其中任何一种假设所折服。众人这才发现，新世界并不是一直沉默地等待别人来描述。
- option_a: 让它重塑辩论。
- option_b: 将其视为奇闻。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Letting the envoy's account reshape the debate treats New World peoples as sources of knowledge rather than scenery. Acceptance rises sharply because the Academy must revise geography, custom, and authority at once.
- rationale_zh: 让使者的叙述重塑辩论，意味着把新世界的人们视为知识来源，而不是风景。学院必须同时修正地理、习俗和权威，接受度因此会显著上升。
- effect_blocks:
```yaml
- type: seat_stance
  group: minorities
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
```

### Option B
- progress_delta: -10
- rationale_en: Treating the account as a curiosity preserves old geography by placing unfamiliar testimony in a cabinet instead of the argument. The debate retreats sharply because living knowledge is made decorative.
- rationale_zh: 将这份叙述视为奇闻，会把陌生证词放进陈列柜，而不是放进论证中，从而保护旧地理。由于活生生的知识被装饰化，辩论会明显退回保守立场。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_cabinet_of_curiosities
  months: 24
  effects:
    inherited geography protected from foreign testimony: 0.03
```

## Difference From Same Issue Events
- Unlike NW02 Returned Pilot, NW05 centers testimony from across the sea rather than from the realm's own sailor returning home.
- Unlike NW08 Harbor Crowd, the persuasive object is not cargo displayed to the public but an account that challenges the Academy's categories.
- Unlike NW18 Missionary Grammar, NW05 is not clergy-mediated language study; it is a broader intellectual challenge from an envoy's translated narrative.
