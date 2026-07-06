# NW12 - Foreign Claim

- pool: new_world
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Foreign Claim
- description: A rival court claims the new coast first and sends letters polished smooth by confidence. Suddenly the Academy's question is not only whether the coast exists, but whether silence would make it belong to someone else.
- option_a: Contest the claim.
- option_b: Avoid provocation.

## Chinese Text
- title: 外国声索
- description: 一个敌对宫廷宣称自己率先发现了新海岸，并送来措辞自信得发亮的书信。学院的问题突然不再只是那片海岸是否存在，而是沉默是否会让它属于别人。
- option_a: 争辩这项声索。
- option_b: 避免挑衅。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Contesting the foreign claim forces the realm to treat discovery as a real geopolitical issue, not a rumor for seminar rooms. Acceptance rises sharply because denying the rival requires asserting that the new coast matters, even at diplomatic cost.
- rationale_zh: 争辩外国声索会迫使王国把发现视为真实的地缘政治问题，而不是讲堂里的传闻。接受度会大幅上升，因为否认对手的主张就必须承认新海岸具有实际意义，即使这会付出外交代价。
- effect_blocks:
```yaml
- type: seat_stance
  group: foreign_power
  stance: oppose
  cooldown_months: 24
- type: resource
  resource: prestige
  amount: -10
```

### Option B
- progress_delta: -10
- rationale_en: Avoiding provocation lets caution define policy. Stability is protected because the court refuses a distant quarrel, but the debate retreats hard from accepting discovery as something worth contesting.
- rationale_zh: 避免挑衅会让谨慎来定义政策。宫廷拒绝卷入遥远争端，因此国内稳定得以保全；但辩论也会明显后退，不再把发现视为值得争夺的事业。
- effect_blocks:
```yaml
- type: temporary_country_modifier
  key: tv_academy_debate_avoided_foreign_claim_crisis
  months: 18
  effects:
    domestic calm from diplomatic restraint: 0.02
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 24
```

## Difference From Same Issue Events
- Unlike NW17 Treaty of Unknown Shores, NW12 is a direct rival claim over priority, not a broader legal question about dividing lands that remain poorly known.
- Unlike NW10 Naval Officers Demand Funds, this event tests diplomatic nerve and prestige rather than the material readiness of ships and dockyards.
- Unlike NW05 Native Envoy's Account, the outside voice here is a competing court seeking ownership, not testimony that challenges inherited geography.
