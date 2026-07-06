# M17 - The Crown's Favorite Fails

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Crown's Favorite Fails
- description: A favored candidate performs badly in a supervised trial and everyone notices.
- option_a: Let the result stand.
- option_b: Order a second trial.

## Chinese Text
- title: 王室宠臣失手
- description: 一名受宠的候选人在监督考核中表现糟糕，而且所有人都看见了。
- option_a: 让结果照常生效。
- option_b: 命令重新考核。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Letting the result stand proves that even royal favor cannot rescue a failed performance. The debate moves sharply toward meritocracy, but the Crown spends legitimacy by allowing its own preference to be publicly overruled.
- rationale_zh: 让结果照常生效，证明即使王室宠信也无法挽救失败的表现。辩论会大幅转向任人唯才，但王冠必须付出正统性代价，因为它公开承认自己的偏好可以被考核推翻。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -10
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Ordering a second trial tells court factions that influence can buy another chance when evidence proves inconvenient. The old patronage logic recovers ground while the bureaucracy learns which candidates are protected.
- rationale_zh: 命令重新考核等于告诉宫廷派系，当证据令人尴尬时，影响力可以换来第二次机会。旧有庇护逻辑因此收复阵地，官僚体系也看清了哪些候选人受到保护。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike M06 The Tutor's Nephew, the favorite has already been tested and failed publicly rather than merely receiving a requested favor.
- Unlike M14 Hereditary Office in Crisis, the embarrassment belongs to current Crown patronage rather than an inherited office failing at its duties.
- Unlike M20 Oath of the Examiners, the pressure falls on accepting one visible result, not on protecting examiners before the results are published.
