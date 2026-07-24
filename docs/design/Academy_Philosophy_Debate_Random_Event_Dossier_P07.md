# P07 - Paper Shortage

- pool: printing_press
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: Paper Shortage
- description: Paper makers warn that debate cannot be printed on enthusiasm alone.
- option_a: Subsidize paper.
- option_b: Limit print runs.

## Chinese Text
- title: 纸张短缺
- description: 造纸匠警告说，辩论不能只靠热情印在纸上。
- option_a: 补贴纸张供应。
- option_b: 限制印刷数量。

## Mechanics
### Option A
- progress_delta: +10
- rationale_en: Subsidizing paper turns a material bottleneck into state-backed capacity, letting the debate expand through actual sheets rather than hopeful speeches.
- rationale_zh: 补贴纸张供应把物资瓶颈变成国家支持的产能，让辩论依靠真实纸页扩散，而不是停留在热切演说中。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: -2
```

### Option B
- progress_delta: -10
- rationale_en: Limiting print runs protects the treasury, but it proves that the new medium can be stopped by supply discipline before it reshapes opinion.
- rationale_zh: 限制印刷数量能保护国库，却也证明新媒介在重塑舆论前就会被供应纪律拦住。
- effect_blocks:
```yaml
- type: resource
  resource: gold
  scale: 1
```

## Difference From Same Issue Events
- Unlike P02, the obstacle is raw material supply rather than the legal organization of printers.
- Unlike P10, the cost is for consumable production capacity, not retraining older scribal labor.
- Unlike P14, the question is whether enough copies can be made at all, not whether bad copies spread a mistaken table.
