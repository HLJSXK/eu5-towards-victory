# MF11 - Standard Parts

- pool: manufactories
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Standard Parts
- description: Artisans bring a neat row of parts that can trade places without complaint. Half the chamber sees a future of faster repair and steadier supply; the other half hears the quiet funeral bell of individual craft.
- option_a: Promote standard parts.
- option_b: Keep craft variation.

## Chinese Text
- title: 标准部件
- description: 工匠们带来一排可以互换的部件，演示一件工具如何不再只属于一双手的习惯。半个会场为这种精确鼓掌，另一半则像是在为手艺的灵魂守丧。
- option_a: 推广标准部件。
- option_b: 保留手工差异。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Standard parts make manufactories look like a new system of reliable production rather than merely larger workshops. The debate moves strongly toward acceptance, while artists and craft advocates resist the loss of distinctive workmanship.
- rationale_zh: 标准部件让工场看起来不只是更大的作坊，而是一套可靠生产的新体系。因此辩论会明显转向接受，但艺术家与手艺维护者会反感独特技艺被削平。
- effect_blocks:
```yaml
- type: seat_stance
  group: artists
  stance: oppose
  cooldown_months: 18
```

### Option B
- progress_delta: -5
- rationale_en: Preserving craft variation reassures guild-minded burghers that skill and local reputation still matter. Acceptance slips because interchangeable production remains an affront to valued workmanship.
- rationale_zh: 保留手工差异会安抚重视行会传统的市民阶层，使他们相信技艺和地方名声仍然重要。由于互换式生产仍被视为对精工的冒犯，接受度随之下降。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: burghers_estate
  value: 0.04
```

## Difference From Same Issue Events
- Unlike MF08 Military Contract, which supports standardization through army procurement, MF11 focuses on the philosophical shock of interchangeable objects replacing individual craft.
- Unlike MF17 Workshop School, which challenges guild apprenticeship through training, MF11 challenges guild culture through the product itself.
- Unlike MF18 Quality Scandal, which asks how to respond after mass production fails, MF11 asks whether precision and sameness should be treated as virtues before a scandal occurs.
