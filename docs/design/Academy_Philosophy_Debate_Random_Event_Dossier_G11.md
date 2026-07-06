# G11 - Letter from Abroad

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Letter from Abroad
- description: A foreign scholar sends a careful letter, folded like evidence and read like gossip. Its argument is precise enough to help the Academy, and foreign enough to make every listener wonder who benefits from hearing it aloud.
- option_a: Read it aloud.
- option_b: File it quietly.

## Chinese Text
- title: 海外来信
- description: 一位外国学者寄来措辞谨慎的书信，它像证据一样被折好，却像流言一样被传读。信中的论证足以帮助学院，也足够“外来”，让每个听众都怀疑公开朗读究竟会让谁得利。
- option_a: 当众朗读。
- option_b: 悄悄归档。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Reading the letter aloud lets outside scholarship strengthen the accepting side, while giving the foreign-power seat a reason to treat the debate as a live diplomatic-intellectual channel.
- rationale_zh: 当众朗读让外部学术资源为接受方增势，同时也使外国势力席位有理由把这场辩论视为仍在运作的外交与学术渠道。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Filing the letter quietly favors caution over intellectual momentum; the debate retreats from foreign entanglement and dampens the foreign-power seat's short-term involvement.
- rationale_zh: 悄悄归档选择谨慎而非推进论证；辩论因此避开外部牵连，并暂时压低外国势力席位的参与度。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: foreign_power
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike G03, where a dubious quotation tests scholarly honesty, this event uses a credible foreign intervention and makes outside attention the main cost.
- Unlike G17, which turns on translation choices inside the realm, this event is about whether foreign correspondence is admitted into the room at all.
- Unlike G09, the pressure here is diplomatic and intellectual rather than aristocratic ridicule.
