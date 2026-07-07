# SR13 - Public Demonstration

- pool: scientific_revolution
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Public Demonstration
- description: The Chief Scientist wants a public experiment where failure would be impossible to hide. The proposal thrills the galleries and terrifies everyone who prefers uncertainty to have closed doors.
- option_a: Hold it publicly.
- option_b: Keep trials private.

## Chinese Text
- title: 公开演示
- description: 首席科学家希望举行一场公开实验，让失败无法被掩藏。这个提议让旁听席兴奋不已，也让所有希望不确定性能留在闭门之后的人感到恐惧。
- option_a: 公开举行。
- option_b: 保持试验私密。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: A public demonstration turns experimental risk into persuasive theater. Acceptance rises sharply because witnesses see the method stake its reputation on visible results, even though a failed display would cost prestige.
- rationale_zh: 公开演示会把实验风险变成具有说服力的剧场。见证者看到新方法把声誉押在可见结果上，因此接纳大幅上升；但若演示失败，威望也会付出代价。
- effect_blocks:
```yaml
- type: resource
  resource: prestige
  amount: -5
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping trials private preserves caution and prevents one visible mistake from humiliating the Academy, but it also denies the Scientific Revolution the public proof its supporters wanted.
- rationale_zh: 保持试验私密能够保留谨慎，并防止一次可见失误羞辱学院；但这也剥夺了科学革命支持者所需要的公共证明。
- effect_blocks:
```yaml
- type: seat_cooldown
  group: public_opinion
  cooldown_months: 12
- type: temporary_country_modifier
  key: tv_academy_debate_private_trials
  months: 12
  effects:
    reduced public experimental scandal: 0.01
```

## Difference From Same Issue Events
- Unlike SR08 Laboratory Accident, SR13 is about choosing public exposure before anything goes wrong, not reacting after a dramatic failure.
- Unlike SR07 A Prediction Comes True, SR13 asks whether proof should be staged before witnesses rather than inferred from an accurate calculation.
- Unlike SR05 Academy Experiment Code, SR13 concerns the visibility and political risk of one demonstration, not the general rules for witnessing and recording experiments.
