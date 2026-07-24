# C03 - Sermon Licensing

- pool: confessionalism
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Sermon Licensing
- description: As doctrine becomes government, the pulpit no longer feels merely local. Preachers ask who may speak for orthodoxy when every sermon can sound like policy.
- option_a: License sermons centrally.
- option_b: Preserve local preaching custom.

## Chinese Text
- title: 讲道许可
- description: 当教义开始成为政务，布道坛便不再只是地方事务。传道人要求说明，当每篇讲道都可能像政策一样被听见时，谁才有资格代表正统发声。
- option_a: 由中央许可讲道。
- option_b: 保留地方布道惯例。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Central licensing gives the confessional settlement a controlled voice and reduces contradictory preaching, nudging acceptance through order rather than sweeping reform.
- rationale_zh: 由中央许可讲道，会让信仰定制获得受控的声音，并减少彼此矛盾的布道，因此它是通过秩序而非激烈改革来推动接受。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: court_bureaucrats
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Preserving local preaching custom reassures parishes that the settlement will not silence familiar voices, but it leaves doctrine too uneven to carry acceptance strongly.
- rationale_zh: 保留地方布道惯例会安抚各堂区，让他们相信新的信仰安排不会压制熟悉的声音，但也会使教义过于参差，难以有力推动接受。
- effect_blocks:
```yaml
- type: seat_stance
  group: local_autonomy
  stance: oppose
  cooldown_months: 18
- type: temporary_country_modifier
  key: tv_academy_debate_local_pulpits
  months: 12
  effects:
    local preaching discretion preserved: 0.02
```

## Difference From Same Issue Events
- Unlike C02 Parish Registers, C03 concerns who may speak doctrine aloud rather than who records births, marriages, and belief.
- Unlike C14 Icon Debate, C03 controls the human voice of doctrine instead of settling a rule for devotional images.
- Unlike C15 Border Preachers, C03 is an internal licensing question; it does not depend on foreign crossings or diplomatic suspicion.
