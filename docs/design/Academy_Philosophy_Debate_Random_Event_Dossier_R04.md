# R04 - Patronage Ledger

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Patronage Ledger
- description: Artists bring a ledger showing which workshops changed when patrons paid, and which sermons merely praised change after it was already carved, painted, and delivered. Inspiration, the ledger suggests, has a treasurer.
- option_a: Expand court patronage.
- option_b: Keep patronage ceremonial.

## Chinese Text
- title: 赞助账册
- description: 艺术家带来一册账簿，列出哪些工坊在赞助到来后发生改变，哪些布道只是在作品已经雕好、画好、交付之后才赞美变化。账簿暗示，灵感也有司库。
- option_a: 扩大宫廷赞助。
- option_b: 将赞助保持为礼仪事务。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Expanding patronage admits that institutions can manufacture artistic renewal, strongly advancing Renaissance acceptance at an immediate fiscal cost.
- rationale_zh: 扩大赞助等于承认制度可以制造艺术更新，因此会强力推动对文艺复兴的接受，但需要立刻付出财政代价。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
- type: seat_stance
  group: artists
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Keeping patronage ceremonial protects the treasury and keeps art subordinate to court display, but it leaves innovation dependent on private accidents rather than public commitment.
- rationale_zh: 将赞助保持为礼仪事务可以保护国库，也让艺术继续服从宫廷展示；但创新仍只能依赖私人偶然，而不是公共承诺。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_ceremonial_patronage
  months: 12
  effects:
    court expenditure restraint: 0.02
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R01 and R03, which focus on objects and methods, R04 asks whether the state will finance the conditions that make Renaissance art repeatable.
- Unlike R08's court masque, R04 is administrative and durable rather than a single prestigious performance.
- Unlike R19's urban program, R04 funds court-centered patronage rather than remaking streets, squares, and facades as a civic classroom.
