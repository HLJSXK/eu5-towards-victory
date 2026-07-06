# R06 - Classics in the Market

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Classics in the Market
- description: Cheap copies of classical verses appear beside account books and salt fish. The Academy discovers that old authors sound different when read by people who paid market price for them.
- option_a: Let the market read.
- option_b: Restrict copies to scholars.

## Chinese Text
- title: 市场上的古典诗篇
- description: 廉价的古典诗篇抄本出现在账簿和咸鱼旁边。学会发现，当普通人以市价买下旧作者时，那些旧文字听起来便不再只属于书斋。
- option_a: 让市场读下去。
- option_b: 只准学者持有抄本。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Allowing cheap copies to circulate turns Renaissance learning into a public habit instead of a guarded elite possession, so public opinion becomes more receptive to accepting the issue.
- rationale_zh: 放任廉价抄本流通，会把文艺复兴式学问从精英守护的藏品变成市民日常，因此民意更容易倾向接受该议题。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.02
```

### Option B
- progress_delta: -5
- rationale_en: Restricting the copies protects elite control over interpretation, reassuring high-status readers while making the Renaissance argument look too delicate for broad acceptance.
- rationale_zh: 限制抄本能保护精英对解释权的控制，安抚高位读者，却也让文艺复兴论点显得过于脆弱，难以被广泛接纳。
- effect_blocks:
```yaml
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.02
```

## Difference From Same Issue Events
- Unlike R04 Patronage Ledger, R06 is not about court financing or artist dependence; it tests whether classical learning can escape elite channels through cheap urban circulation.
- Unlike R11 Translation of a Greek Text, this event does not hinge on scholarly ambiguity or a costly translation project, but on already-copied texts becoming socially available.
- Unlike R14 Poets at the Debate, the pressure comes from market readership and book circulation rather than poets actively turning the debate into memorable slogans.
