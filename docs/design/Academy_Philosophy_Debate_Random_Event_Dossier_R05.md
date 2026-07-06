# R05 - The Humanist Tutor

- pool: renaissance
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: The Humanist Tutor
- description: A humanist tutor argues that rulers should read history as instruction, not ornament. Several nobles hear the word "instruction" and immediately wonder who is being instructed to surrender old habits.
- option_a: Invite them to lecture.
- option_b: Keep tutors private.

## Chinese Text
- title: 人文主义导师
- description: 一位人文主义导师主张，统治者阅读历史应当是为了受教，而不是为了装点门面。几位贵族一听见“受教”二字，立刻开始怀疑是谁要被教着放下旧习惯。
- option_a: 邀请其公开讲学。
- option_b: 让导师留在私人场合。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Inviting the tutor makes humanist learning part of public political formation, nudging the debate forward while making nobles uncomfortable with history being used to judge rank and custom.
- rationale_zh: 邀请导师公开讲学，会把人文主义学问纳入公开的政治塑造，温和推进辩论；同时，贵族会因历史被用来评判等级与习俗而感到不适。
- effect_blocks:
```yaml
- type: estate_satisfaction
  estate: nobles_estate
  value: -0.03
- type: seat_stance
  group: scholarly_community
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Keeping tutors private preserves court order and noble comfort, but it turns humanist history back into decoration for elites rather than an argument for public renewal.
- rationale_zh: 让导师留在私人场合可以维持宫廷秩序与贵族舒适感，却会把人文主义历史重新变成精英的装饰，而不是公共更新的论证。
- effect_blocks:
```yaml
- type: resource
  resource: legitimacy
  amount: 5
- type: seat_stance
  group: nobility
  stance: oppose
  cooldown_months: 12
```

## Difference From Same Issue Events
- Unlike R04's patronage argument, R05 is about education and political reading rather than funding workshops.
- Unlike R06's cheap classics in the market, R05 brings humanist learning into elite instruction before it reaches a broader public.
- Unlike R18's library reordering, R05 changes who interprets history for rulers rather than how books are classified inside the Academy.
