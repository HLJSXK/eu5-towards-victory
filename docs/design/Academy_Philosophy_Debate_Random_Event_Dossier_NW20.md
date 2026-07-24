# NW20 - School Globe

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: School Globe
- description: A new globe is carried into the Academy schoolroom, round enough to make old wall maps look embarrassed. Students turn it by hand, and the room discovers that geography can change under one's fingers.
- option_a: Make it public teaching.
- option_b: Keep it for experts.

## Chinese Text
- title: 学校地球仪
- description: 一具新的地球仪被搬进学院教室，它的圆弧足以让墙上的旧地图显得窘迫。学生们亲手转动它，整个房间发现，地理知识竟能在人们指尖下改变。
- option_a: 将它用于公共教学。
- option_b: 仅供专家使用。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Public teaching spreads the New World argument through repeated instruction rather than spectacle or crisis. The progress gain is modest, but public opinion moves toward acceptance as students learn new geography as normal knowledge.
- rationale_zh: 公共教学会通过反复授课传播新世界论点，而不是依靠奇观或危机。进展幅度不大，但当学生把新地理当作正常知识来学习时，公众舆论会转向接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_globe_lessons
  months: 12
  effects:
    public geography instruction: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Keeping the globe for experts preserves control over unsettling knowledge, but it also prevents the new map from becoming common sense. The debate slips backward because discovery remains an elite secret rather than public instruction.
- rationale_zh: 将地球仪留给专家，可以保持对令人不安知识的控制，却也阻止新地图成为常识。由于发现仍是精英掌握的秘密，而不是公众教育，辩论会向后退。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike NW09 Mapmaker's Correction, NW20 is about teaching a revised world model after the map exists, not the public act of changing a map's authority.
- Unlike NW08 Harbor Crowd, this event persuades through classrooms and repeated instruction rather than through a harbor crowd reacting to unusual goods.
- Unlike NW16 Imported Crop, NW20 makes the unknown familiar through educational geography rather than through a living specimen in a test garden.
