# Wonder Ceremony Risk Card

Load this card for shared unique-wonder ceremony data, ceremony option text,
ceremony cost generators, finalization events, and ceremony GUI fragments.

## Required Checks

1. Keep ceremony cost data in the current schema.
   Each stage cost is `{catalog, type, value}` from `data/cost_reward_units.yaml`.
   Do not reintroduce the older style-derived vocabulary.

2. Do not round-trip `data/unique_wonders.yaml` casually.
   The ceremony cost-option merge helper uses anchored text splicing to preserve
   hand-authored YAML shape. Use the existing helper path when updating many
   ceremony stages.

3. Keep option text per wonder and per stage.
   Shared "Pay the price" / "Not yet" text is obsolete. Pay/decline option text
   is routed through generated Customizable Localization dispatch blocks.

4. Keep event-option `hidden_effect` cheap.
   Hover rendering can still evaluate hidden effect chains. Schedule heavy
   finalization through a hidden event and put the heavy work in that event's
   `immediate` block.

5. Register effect tooltip text.
   Any ceremony/wonder `custom_description` inside a scripted effect needs
   effect-localization coverage with the right perspective.

6. Use semantic localization tags.
   Positive effects use `#G`, negative effects use `#R`, neutral thresholds/costs
   use `#Y`, important emphasis uses `#high`, tips use `#weak`, and pure flavor
   uses the established flavor tag from the localization card.

## Validation

```powershell
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report
```
