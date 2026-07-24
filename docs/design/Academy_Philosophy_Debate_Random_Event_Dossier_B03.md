# B03 - Sermon on Usury

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Sermon on Usury
- description: At dawn a preacher turns interest into a sin that every debtor can understand. By noon the Academy is arguing whether regulation purifies credit or merely gives vice a receipt.
- option_a: Defend regulated interest.
- option_b: Condemn the practice.

## Chinese Text
- title: 反高利贷布道
- description: 黎明时分，一位布道者把利息说成每个债务人都能听懂的罪。到了正午，学院已经在争论：监管能净化信用，还是只给恶习开了一张收据。
- option_a: 为受监管的利息辩护。
- option_b: 谴责这种做法。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Defending regulated interest accepts moral anxiety but argues that law can discipline credit, nudging the debate toward reform while offending clergy who want a clearer condemnation.
- rationale_zh: 为受监管的利息辩护，等于承认道德忧虑却主张法律可以约束信用；这会推动辩论走向改革，也会冒犯希望直接谴责的神职阶层。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: -0.04
- type: seat_stance
  group: burghers
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -10
- rationale_en: Condemnation gives the sermon the last word, pleasing religious authorities but casting the banking system as a moral danger rather than an institution that can be governed.
- rationale_zh: 谴责会让布道成为最后结论，使宗教权威满意，却把银行体系塑造成道德危险，而不是一种可以被治理的制度。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: clergy_estate
  value: 0.05
- type: seat_stance
  group: clergy
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B10 Clerical Credit Chest, B03 is about public doctrine against interest, not bringing church-run lending networks under civil law.
- Unlike B13 Scholar of Interest, B03 frames interest as a moral problem instead of a mathematical lesson in compound calculation.
- Unlike B19 Bankruptcy Shame, B03 debates the legitimacy of lending itself rather than the social punishment attached to failed debtors.
