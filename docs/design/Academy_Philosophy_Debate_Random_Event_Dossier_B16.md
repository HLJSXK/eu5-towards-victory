# B16 - Mint Officer's Confession

- pool: banking
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Mint Officer's Confession
- description: A tired mint officer admits that the old coinage routine survives on tolerated confusion: clipped weights, private exceptions, and ledgers no one quite dares to reconcile.
- option_a: Publicize the confession.
- option_b: Retire them quietly.

## Chinese Text
- title: 铸币官的供认
- description: 一名疲惫的铸币官承认，旧有铸币流程靠被默许的混乱维持：被削薄的成色、私下通融的例外，以及无人真正敢对清的账册。
- option_a: 公开这份供认。
- option_b: 让其悄然退休。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Publicizing the confession turns monetary confusion from a technical inconvenience into evidence that banking reform is necessary for public trust. The realm's legitimacy suffers because the Crown appears to have tolerated the confusion for years.
- rationale_zh: 公开供认会把货币混乱从技术麻烦变成改革银行制度、重建公共信任的证据。王权正当性会受损，因为这等于承认朝廷多年来默许了这种含混。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: -10
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 18
```

### Option B
- progress_delta: -10
- rationale_en: Quiet retirement protects the immediate calm of the mint and lets officials claim the matter was only personal weakness, but it buries the systemic proof reformers needed.
- rationale_zh: 悄然退休可以保护铸币体系的短期平静，也让官员把问题说成个人失职；但它会埋掉改革派最需要的制度性证据。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
- type: seat_stance
  group: court_bureaucrats
  stance: oppose
  cooldown_months: 18
```

## Difference From Same Issue Events
- Unlike B05 Debased Coin Panic, this event starts inside the mint bureaucracy rather than in market rumor, so the side effect pressures legitimacy instead of treasury cost.
- Unlike B09 Fraudulent Ledger, the problem is not one elegant crime but a tolerated administrative habit that exposes the need for systemic standards.
- Unlike B20 Crown Account Published, B16 is a confession forced upward from a technical office, not a voluntary transparency gesture from the Crown.
