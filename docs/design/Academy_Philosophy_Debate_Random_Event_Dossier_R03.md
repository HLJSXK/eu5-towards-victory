# R03 - Perspective in the Chapel

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Perspective in the Chapel
- description: A painter unveils a chapel design where arches, saints, and shadows obey the same measured vanishing point. Some call it reverence made clearer; others call it geometry standing too close to the altar.
- option_a: Celebrate the method.
- option_b: Demand traditional forms.

## Chinese Text
- title: 礼拜堂中的透视
- description: 一位画家展示了新的礼拜堂设计，拱券、圣像与阴影都服从同一个可测量的消失点。有人说这是更清晰的敬虔，也有人说几何站得离祭坛太近了。
- option_a: 赞扬这种方法。
- option_b: 要求沿用传统形式。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Celebrating perspective lets artistic technique serve sacred space without breaking it, giving artists favor and a modest push toward accepting Renaissance methods.
- rationale_zh: 赞扬透视法意味着让艺术技巧服务于神圣空间而不摧毁它，这会提高艺术家的地位，并温和推动对文艺复兴方法的接受。
- effect_blocks:
```yaml
- type: artist_skill
  amount: 0.03
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Demanding older forms reassures religious patrons that novelty will not redraw devotion without permission, but it blunts the argument that measurement can deepen art.
- rationale_zh: 要求旧形式会让宗教赞助者放心，确信新奇手法不能未经许可重画虔敬；但这也削弱了“测量可以加深艺术”的论点。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.03
- type: seat_cooldown
  group: artists
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R02, which provokes the clergy through anatomical spectacle, R03 negotiates conflict inside sacred art and therefore uses a smaller progress swing.
- Unlike R09's measured ruins, R03 applies measurement to a living religious commission rather than to antiquarian survey work.
- Unlike R15's prince portrait, R03 is not about the ruler's image; it asks whether sacred space itself can be organized by Renaissance technique.
