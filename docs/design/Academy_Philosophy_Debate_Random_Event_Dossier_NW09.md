# NW09 - Mapmaker's Correction

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Mapmaker's Correction
- description: A mapmaker erases a traditional boundary in front of witnesses and inks a coast where certainty used to sit. The scrape of the knife sounds small until everyone realizes what authority has just lost.
- option_a: Accept the correction.
- option_b: Restore the old map.

## Chinese Text
- title: 制图师的修正
- description: 制图师当着众人的面擦去旧有边界，在曾经写着确定性的地方画上新的海岸。刮刀的声音很轻，直到众人意识到刚刚失去墨迹的是哪一种权威。
- option_a: 接受修正。
- option_b: 恢复旧地图。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Accepting the correction makes the New World debate an institutional act of revision, not merely a traveler's claim. Scholarly authority shifts toward evidence that can redraw inherited knowledge.
- rationale_zh: 接受修正会让新世界辩论变成一种制度性的修订，而不只是旅行者的说法。学术权威会转向那些能够改写继承知识的证据。
- effect_blocks:
```yaml
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_corrected_charts
  months: 24
  effects:
    survey credibility and map revision: 0.03
```

### Option B
- progress_delta: -10
- rationale_en: Restoring the old map protects inherited geography from public embarrassment. Conservatives gain confidence because the Academy chooses continuity over the unsettling discipline of correction.
- rationale_zh: 恢复旧地图可以保护继承下来的地理知识免于公开难堪。保守派会更有信心，因为学院选择了延续，而不是令人不安的修正纪律。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.03
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike NW01 The Sailor's Chart, NW09 centers on an Academy-recognized specialist revising accepted knowledge rather than on whether to trust a battered external chart.
- Unlike NW13 Cosmographer's Error, the correction is a visible public redrawing of boundaries, not an abstract admission about distance estimates.
- Unlike NW20 School Globe, NW09 is about who has authority to change maps before witnesses, not about teaching the public with a finished educational object.
