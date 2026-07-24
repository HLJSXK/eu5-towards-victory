# G14 - A Street Song

- pool: general
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title: A Street Song
- description: The issue escapes the Academy as a street song, half misunderstanding and half recruitment. By sunset, people who could not name the proposition can hum its sharpest insult.
- option_a: Let the song spread.
- option_b: Suppress the song.

## Chinese Text
- title: 街头歌谣
- description: 这项议题化作一首街头歌谣逃出了学院，一半是误解，一半是动员。到日落时，许多说不出命题名称的人已经会哼其中最尖刻的一句。
- option_a: 任由歌谣流传。
- option_b: 压制这首歌。

## Mechanics
### Option A
- progress_delta: +5
- rationale_en: Letting the song spread turns imperfect popular attention into accepting momentum, bringing public opinion into the debate even though the message is noisy.
- rationale_zh: 任由歌谣流传把不完美的民间关注转化为接受方的势头，让公众舆论进入辩论，哪怕其中充满噪音。
- effect_blocks:
```yaml
- type: seat_stance
  group: public_opinion
  stance: support
  cooldown_months: 12
```

### Option B
- progress_delta: -5
- rationale_en: Suppression prevents the argument from spreading through unruly channels and eases immediate stability pressure, but the debate loses the popular energy it might have gained.
- rationale_zh: 压制歌谣阻止论点通过难以控制的渠道扩散，并缓和眼前的稳定压力，但辩论也失去了本可借用的民间热度。
- effect_blocks:
```yaml
- type: resource
  resource: stability
  amount: 1
```

## Difference From Same Issue Events
- Unlike G02, which opens or clears a physical gallery, this event deals with uncontrolled circulation outside the Academy.
- Unlike G10, where students stage a recognizable disputation, this event is popular culture turning the issue into a memorable but distorted refrain.
- Unlike G18, which uses a commissioned artwork, this event's public pressure is anonymous, cheap, and difficult to own.
