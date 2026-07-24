# P16 - Noble Libel Suit

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Noble Libel Suit
- description: A noble sues a printer for making old privilege look ridiculous in affordable type.
- option_a: Protect the printer.
- option_b: Fine the printer.

## Chinese Text
- title: 贵族诽谤诉讼
- description: 一名贵族起诉印刷商，因为廉价铅字把旧特权写得可笑起来。
- option_a: 保护印刷商。
- option_b: 罚款惩戒印刷商。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Protecting the printer turns noble embarrassment into a legal precedent for public criticism, sharply advancing acceptance of printing press applications.
- rationale_zh: 保护印刷商会把贵族的难堪转化为公开批评的法律先例，从而明显推动对印刷术应用的接受。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.05
```

### Option B
- progress_delta: -10
- rationale_en: Fining the printer restores noble honor and makes privilege a boundary that cheap print may not cross, sharply strengthening resistance to the press.
- rationale_zh: 罚款惩戒印刷商能恢复贵族体面，并把特权划成廉价印刷不得越过的界线，从而明显加强对印刷术的抵制。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: 0.05
```

## Difference From Same Issue Events
- Unlike P05, this event is a formal legal suit over noble privilege rather than court gossip sold beside serious argument.
- Unlike P12, the conflict is not about a forbidden book becoming attractive, but about whether satire of rank can be punished as libel.
- Unlike P19, the printer's public profile is dangerous because it attacks privilege, not because celebrity distracts from scholars.
