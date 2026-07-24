# SR02 - Failed Replication

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Failed Replication
- description: A celebrated result is repeated before careful witnesses and refuses to appear. The silence after the failed trial is embarrassing, but it is also the first honest sound the chamber has heard all week.
- option_a: Publish the failure.
- option_b: Hide the failed trial.

## Chinese Text
- title: 复验失败
- description: 一项备受称颂的结果在谨慎见证者面前被重新试验，却迟迟不肯出现。失败后的沉默令人难堪，但它也是会场这一周听到的第一种诚实声音。
- option_a: 公布这次失败。
- option_b: 隐瞒失败的试验。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publishing the failure makes correction part of the method rather than a scandal outside it. The Academy loses face in the short term, but the debate moves strongly toward accepting replication as a rule of truth.
- rationale_zh: 公布失败会把纠错变成方法本身的一部分，而不是方法之外的丑闻。学院短期内会失面子，但辩论会明显转向接受复验作为求真的规则。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -10
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Concealing the failed trial protects reputations and keeps patrons calm, but it tells every observer that fame matters more than repeated proof when the result becomes inconvenient.
- rationale_zh: 隐瞒失败可以保护名声、安抚赞助人，但它也会告诉所有旁观者：当结果变得不方便时，声望比反复证明更加重要。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: 5
- type: seat_stance
  group: great_scientist
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike SR01 Table of Observations, SR02 centers on the negative power of repetition: a missing result becomes evidence.
- Unlike SR13 Public Demonstration, this failure occurs under controlled scholarly witnessing rather than before a broader public audience.
- Unlike SR15 Dissection of Error, SR02 is about whether to reveal one specific failed trial, not whether the Academy should institutionalize error records as a general practice.
