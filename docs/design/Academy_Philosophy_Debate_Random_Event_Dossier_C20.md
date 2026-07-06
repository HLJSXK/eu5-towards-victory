# C20 - The Crown's Formula

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Crown's Formula
- description: Advisers draft a royal formula meant to sound ancient by tomorrow morning and inevitable by next week. The words are polished enough to shine, which is not the same as being settled.
- option_a: Proclaim it.
- option_b: Return it for revision.

## Chinese Text
- title: 王室信纲条文
- description: 顾问们草拟了一套王室条文，希望它明早听起来就像古训，下周听起来就像天命。词句已经打磨得发亮，但发亮并不等于尘埃落定。
- option_a: 正式颁布。
- option_b: 退回重修。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Proclaiming the formula gives the debate a royal sentence to rally around, rapidly pushing acceptance, but a formula issued before consensus risks making legitimacy bear the weight of every disputed word.
- rationale_zh: 颁布条文会给辩论一个可供拥护的王室定句，迅速推动接纳；但在共识形成前发布，也会让正统性承担每一个争议词句的重量。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 18
- type: resource
  resource: legitimacy
  amount: -5
- type: temporary_country_modifier
  key: tv_academy_debate_royal_formula
  months: 12
  effects:
    royal confessional language anchors public argument: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Returning the formula for revision avoids staking royal dignity on an unstable text, but it also tells the Academy that the confession still lacks words strong enough to govern.
- rationale_zh: 退回重修可以避免把王室尊严押在一份不稳固的文本上；但这也告诉学院，信纲仍缺少足以治国的措辞。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: court_bureaucrats
  cooldown_months: 12
- type: resource
  resource: prestige
  amount: -5
```

## Difference From Same Issue Events
- Unlike C01 Confession of the Court, C20 assumes the Crown is already ready to speak and focuses on the exact formula of that speech.
- Unlike C05 Catechism Draft, C20 is royal and constitutional in tone rather than a teaching text meant for memorization.
- Unlike C17 Clergy Split, C20 tests the authority of Crown language rather than the internal discipline of the clergy estate.
