# R17 - Imported Master

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Imported Master
- description: A foreign master offers techniques that local artists resent for being both foreign and better, and every compliment paid to the visitor lands like a correction.
- option_a: Hire the master.
- option_b: Decline politely.

## Chinese Text
- title: 外来的大师
- description: 一位外国大师带来新技法，本地艺术家因其既是外来之物又确实更高明而心生怨气。每一句赞美听起来都像在纠正他们。
- option_a: 聘用这位大师。
- option_b: 礼貌谢绝。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Hiring the master makes Renaissance technique immediately visible and teachable, so the debate surges forward; the cost is local resentment from workshops that feel displaced.
- rationale_zh: 聘用大师会让文艺复兴技法立刻变得可见、可学，因此辩论大幅推进；代价是本地作坊会感到被取代并滋生怨气。
- effect_blocks:
```yaml
- type: artist_skill
  amount: 0.05
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 18
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Refusing the foreign master protects local pride and avoids a workshop quarrel, but it also lets caution define the Academy's answer to superior technique.
- rationale_zh: 拒绝外国大师能维护本地自尊，避免作坊争端；但这也等于让谨慎成为学院面对高明技法时的答案。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike R11 Translation of a Greek Text, the imported knowledge is embodied by a living practitioner whose presence changes workshop politics.
- Unlike R13 Old Workshop Resists, the opposition is not only traditional curriculum versus new proportions; it is local status versus foreign expertise.
- Unlike R04 Patronage Ledger, the key pressure is not whether patrons fund innovation, but whether the Academy legitimizes an outsider as a teacher.
