# M06 - The Tutor's Nephew

- pool: meritocracy
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Tutor's Nephew
- description: The royal tutor requests a cabinet post for a brilliant nephew, though every witness seems more certain of the family tie than of the brilliance.
- option_a: Demand open assessment.
- option_b: Grant the favor.

## Chinese Text
- title: 王室教师的侄子
- description: 王室教师请求为一位聪慧的侄子谋取内阁职位，只是旁人似乎更确信他的亲缘，而不是他的才干。
- option_a: 要求公开考核。
- option_b: 准许这份人情。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Open assessment moves the appointment away from household access and toward measured competence, so it advances meritocracy while irritating officials who prefer quiet recommendations.
- rationale_zh: 公开考核把任命从宫廷门路转向可衡量的能力，因此推动任人唯才，但会惹恼习惯私下举荐的官僚。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Granting the favor preserves court calm and eases immediate legitimacy pressure, but it teaches the Academy that kinship can still outrank proof.
- rationale_zh: 准许这份人情能维持宫廷安宁、缓和眼前的正统性压力，却也等于告诉学院，亲缘仍可压过实证。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
```

## Difference From Same Issue Events
- Unlike M02, which argues for hereditary service through public genealogy, M06 is a narrower patronage test built around one intimate court request.
- Unlike M12, which concerns system-wide publication of rankings, M06 asks whether a single appointment must pass an open assessment before procedure hardens into precedent.
- Unlike M17, where a favorite has already failed visibly, M06 occurs before proof exists and focuses on whether access can substitute for testing.
