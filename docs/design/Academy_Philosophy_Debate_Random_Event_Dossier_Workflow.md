# Academy Philosophy Debate Random Event Dossier Workflow

Status: design dossier workspace only. These files are not canonical YAML, are not generated `src`, and are not consumed by any generator.

## Write Boundaries

- Workers may write only their assigned `docs/design/Academy_Philosophy_Debate_Random_Event_Dossier_<DESIGN_ID>.md` files.
- Reviewers may write only `docs/design/Academy_Philosophy_Debate_Random_Event_Dossier_Review.md`.
- The lead may merge reviewer-approved dossiers into `docs/design/Academy_Philosophy_Debate_Random_Event_Dossiers_Approved.md`.
- Do not edit `src/`, generated files, generator scripts, `data/generated_files.yaml`, `data/philosophy_debates.yaml`, or any canonical YAML/data source.

## Dossier Template

Each event must be its own Markdown file named with the design id, for example `Academy_Philosophy_Debate_Random_Event_Dossier_G01.md` or `Academy_Philosophy_Debate_Random_Event_Dossier_GT14.md`.

Required sections:

```markdown
# <DESIGN_ID> - <English Title>

- pool: <general | meritocracy | renaissance | banking | new_world | printing_press | confessionalism | global_trade | manufactories | scientific_revolution>
- source: docs/design/Academy_Philosophy_Debate_Random_Events_Design.md
- status: worker_draft

## English Text
- title:
- description:
- option_a:
- option_b:

## Chinese Text
- title:
- description:
- option_a:
- option_b:

## Mechanics
### Option A
- progress_delta: <+5 | +10 | -5 | -10>
- rationale_en:
- rationale_zh:
- effect_blocks:
```yaml
- type: <schema>
```

### Option B
- progress_delta: <+5 | +10 | -5 | -10>
- rationale_en:
- rationale_zh:
- effect_blocks:
```yaml
- type: <schema>
```

## Difference From Same Issue Events
-
```

## Allowed Effect Blocks

Use small, tooltip-safe blocks. Dossiers describe intent; they do not implement EU5 script.

```yaml
- type: seat_stance
  group: <nobility | clergy | burghers | peasants | tribes | dhimmi | cossacks | scholarly_community | public_opinion | court_bureaucrats | maritime_merchants | professional_military | religious_reformers | local_autonomy | minorities | artists | foreign_power | great_scientist>
  stance: <support | oppose | neutral>
  cooldown_months: <integer 6-36>

- type: seat_cooldown
  group: <same as seat_stance group>
  cooldown_months: <integer 6-36>

- type: estate_satisfaction
  estate: <nobles_estate | clergy_estate | burghers_estate | peasants_estate | tribes_estate | dhimmi_estate | cossacks_estate>
  value: <small decimal, usually -0.06 to 0.06>

- type: resource
  resource: <gold | prestige | legitimacy | stability>
  amount: <integer>
  # For gold, prefer scale instead of amount:
  scale: <integer, usually -2 to 2>

- type: scientist_attribute
  adm: <integer>
  dip: <integer>

- type: artist_skill
  amount: <decimal>

- type: foreign_prestige
  amount: <integer>

- type: temporary_country_modifier
  key: <tv_academy_debate_descriptive_key>
  months: <integer>
  effects:
    <plain-language effect summary>: <small value>
```

## Reviewer Rubric

Review each dossier as PASS or FAIL. PASS requires all of the following:

- The file covers exactly one assigned event from the source design.
- English text and Chinese text are complete, natural, and not placeholder/machine-copy duplicates.
- Option A and B progress deltas match the source design and use only `+5`, `+10`, `-5`, or `-10`.
- Both options include a clear mechanism rationale in English and Chinese.
- Both options include non-empty `effect_blocks` using only the allowed schemas.
- The mechanical side effects are lightweight, match the option flavor, and do not duplicate the same A/B pair used by another event in the same issue pool.
- The "Difference From Same Issue Events" section explains how this event differs from at least two neighboring or thematically similar events in the same pool.
- The worker changed only its assigned dossier files.

Reviewer output should be `docs/design/Academy_Philosophy_Debate_Random_Event_Dossier_Review.md`, containing one row per event: `design_id`, `file`, `verdict`, `blocking_issues`, and `merge_notes`.
