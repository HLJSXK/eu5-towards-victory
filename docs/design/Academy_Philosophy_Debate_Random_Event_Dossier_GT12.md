# GT12 - Merchant School

- pool: global_trade
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Merchant School
- description: Burghers propose teaching navigation, contracts, and languages as serious public knowledge. The suggestion unsettles everyone who prefers commerce to remain a family secret with a counting table attached.
- option_a: Fund the school.
- option_b: Leave training to families.

## Chinese Text
- title: 商人学校
- description: 市民阶层提议把航海、契约和语言作为严肃的公共知识来教授。这个主张让所有偏爱把商业保留为家族秘传技艺的人感到不安，仿佛账桌旁的私学忽然要搬进国家课堂。
- option_a: 资助这所学校。
- option_b: 让训练继续由家族承担。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Funding the school turns global trade from inherited merchant craft into teachable public expertise. Acceptance rises sharply because navigation, contracts, and language become state-recognized knowledge, while the Crown pays for the institution.
- rationale_zh: 资助这所学校，会把全球贸易从继承而来的商人手艺变成可以公开教授的专业知识。航海、契约和语言获得国家承认，接受度因此大幅上升，但王冠也必须承担办学费用。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -1
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Leaving training to families protects guild elders and merchant houses from public standards. The debate shifts backward because trade knowledge remains private inheritance rather than a shared tool of global commerce.
- rationale_zh: 让训练继续由家族承担，会保护行会长老和商人家族免受公共标准约束。辩论会向后退，因为贸易知识仍然是私人继承物，而不是全球商业共享的工具。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike GT17 Language of Contracts, which standardizes wording in commercial documents, GT12 creates a teaching institution for the people who will use those documents.
- Unlike GT20 Map of Trade Winds, this event is about building a curriculum around trade knowledge rather than adopting one navigational discovery.
- Unlike GT01 Harbor Ledgers, which uses existing records as evidence, GT12 invests in future expertise.
