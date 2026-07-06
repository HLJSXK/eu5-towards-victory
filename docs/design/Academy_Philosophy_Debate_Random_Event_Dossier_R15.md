# R15 - The Prince's Portrait

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Prince's Portrait
- description: The royal portraitist proposes painting the ruler in humanist style rather than sacred distance.
- option_a: Accept the style
- option_b: Keep the old iconography

## Chinese Text
- title: 王子的肖像
- description: 王室肖像画师提议以人文主义风格描绘统治者，而不是维持神圣而遥远的姿态。
- option_a: 接受这种风格
- option_b: 保留旧图像传统

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Accepting the humanist portrait places the ruler inside the Renaissance argument without making policy text do all the work. Prestige may rise because the court appears learned, confident, and modern.
- rationale_zh: 接受人文主义肖像，会让统治者亲自进入文艺复兴论证，而不必只依靠政策文字。宫廷显得博学、自信且新颖，因此威望可能上升。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: 10
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Keeping old iconography protects sacred distance and reassures clerical interpreters of royal image-making. The debate slows because the Crown declines to model the new humanist language publicly.
- rationale_zh: 保留旧图像传统会维护神圣距离，并安抚负责解释王室形象的神职人员。王权拒绝公开示范新的人文主义语言，因此辩论进度放缓。
- effect_blocks:
```yaml
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
```

## Difference From Same Issue Events
- Unlike R01, A Newly Found Torso, this event concerns the living ruler's public representation rather than the recovery of ancient art.
- Unlike R12, Fresco of the New Age, this event centers dynastic image and royal authority rather than a broad allegory of the realm.
- Unlike R05, The Humanist Tutor, this event communicates humanism through portraiture instead of through direct instruction to rulers.
