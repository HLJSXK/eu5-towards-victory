# SR11 - Open Correspondence

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Open Correspondence
- description: Scientists ask to publish letters and results across borders before rivals do. What began as private ink now looks like a race to decide whether truth belongs to guarded rooms or to everyone quick enough to answer.
- option_a: Open correspondence.
- option_b: Restrict exchange.

## Chinese Text
- title: 公开通信
- description: 科学家请求在竞争者抢先之前，将书信与成果跨境发表。原本私下流动的墨迹，如今变成一场竞赛，要决定真理究竟属于戒备森严的房间，还是属于所有来得及回应的人。
- option_a: 开放通信。
- option_b: 限制交流。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Opening correspondence makes cross-border verification and priority claims part of the Scientific Revolution's appeal. The debate advances strongly because discovery becomes a shared network rather than a court secret, while foreign observers gain a firmer place in the argument.
- rationale_zh: 开放通信会把跨境验证与发现优先权变成科学革命吸引力的一部分。发现不再只是宫廷秘密，而成为共享网络，因此辩论大幅走向接纳；与此同时，外国观察者在争论中的位置也更加稳固。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: support
  cooldown_months: 24
- type: foreign_prestige
  amount: 5
```

### Option B
- progress_delta: -10
- rationale_en: Restricting exchange lets security-minded officials define scientific letters as leakage rather than evidence. That sharply strengthens rejection by making open inquiry look diplomatically reckless.
- rationale_zh: 限制交流会让重视安全的官员把科学书信说成泄密，而不是证据。这会使公开探究显得像外交冒险，从而强烈推动拒斥方向。
- effect_blocks:
```yaml
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
- type: temporary_country_modifier
  key: tv_academy_debate_restricted_correspondence
  months: 18
  effects:
    guarded scholarly channels: 0.01
```

## Difference From Same Issue Events
- Unlike SR04 Instrument Maker's Claim, SR11 is not about buying better tools; it is about whether discoveries travel through an international correspondence network.
- Unlike SR07 A Prediction Comes True, SR11 does not rely on one successful calculation. It treats speed, priority, and verification across borders as the persuasive proof.
- Unlike SR18 Dangerous Publication, SR11 concerns routine letters and results shared before rivals move, not a single explosive treatise that threatens patrons and doctrine.
