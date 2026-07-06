# SR09 - Artisan Knowledge

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Artisan Knowledge
- description: An artisan solves a practical problem that scholars have spent weeks dressing in Latin. When the tool chest is set on the table, several elegant commentaries suddenly look very heavy.
- option_a: Admit artisan evidence.
- option_b: Keep scholarly hierarchy.

## Chinese Text
- title: 工匠的知识
- description: 一名工匠解决了学者们用拉丁文包装了数周的实际难题。当工具箱被放上桌面时，几篇精致的注释忽然显得格外沉重。
- option_a: 接纳工匠证据。
- option_b: 维持学术等级。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Admitting artisan evidence broadens truth-making beyond classical learning and shows that tested practice can correct learned theory.
- rationale_zh: 接纳工匠证据会把求真范围扩展到古典学问之外，并表明经受检验的实践可以修正书本理论。
- effect_blocks:
```yaml
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_artisan_demonstrations
  months: 24
  effects:
    practical problem solving in academy debates: 0.03
```

### Option B
- progress_delta: -5
- rationale_en: Keeping scholarly hierarchy reassures learned elites that social rank still decides whose evidence counts, but it discards useful proof because it arrived with rough hands.
- rationale_zh: 维持学术等级能让博学精英相信社会身份仍决定何种证据有效，但这也会因为证据来自粗糙双手而丢掉有用证明。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike SR17, where a mechanical model serves as an explanatory analogy, SR09 gives practical artisan evidence direct authority inside the debate.
- Unlike SR04, which concerns whether instrument makers deserve funding for better tools, SR09 asks whether makers and practitioners can challenge scholarly hierarchy.
- Unlike SR03, where abstract mathematics clarifies nature, SR09 argues from workshop competence and hands-on proof.
