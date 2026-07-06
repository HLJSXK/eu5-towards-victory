# G10 - Student Disputation

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Student Disputation
- description: Students stage their own version of the debate and demonstrate that enthusiasm can be louder than preparation.
- option_a: Let them argue
- option_b: Ban the gathering

## Chinese Text
- title: 学生论辩
- description: 学生们自行举办了一场辩论，并证明热情有时确实比准备更响亮。
- option_a: 让他们争辩
- option_b: 禁止集会

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Letting students argue draws public opinion into the issue and gives the new proposition noisy life outside the formal chamber.
- rationale_zh: 允许学生争辩会把公众舆论卷入议题，并让新主张在正式会场之外获得喧闹的生命力。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Banning the gathering preserves order by preventing amateur disputation from becoming a street argument, but it also cools momentum toward acceptance.
- rationale_zh: 禁止集会能防止业余论辩演变为街头争执，从而维护秩序，但也会削弱接受新主张的势头。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_quiet_courtyards
  months: 12
  effects:
    public order confidence: 0.03
```

## Difference From Same Issue Events
- Unlike G02, this event is about students creating a parallel debate, not spectators crowding the official galleries.
- Unlike G14, the issue spreads through improvised disputation rather than popular song, so the side effect is organized public opinion or order rather than street culture.
