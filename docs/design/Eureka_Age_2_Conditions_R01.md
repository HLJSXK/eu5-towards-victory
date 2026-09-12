# Eureka Age 2 Conditions R01

## Decision

Age 2 means every vanilla Advance whose definition contains
`age = age_2_renaissance`. The current reference snapshot contains 647 such
Advances. This includes the 124 universal nodes and the country, culture,
religion, region, government, and other contextual nodes. A country receives
one permanent Eureka condition for each Advance it can research; a condition
is never a prerequisite for starting the Advance.

The implementation contract is a generated registry. It extracts the full
Age 2 set from `reference_game_files/game/in_game/common/advances/`, applies
the explicit universal-node assignments below, then applies the source-class
fallback rules. The generator must fail if an Age 2 Advance has no assignment.
This makes the 647-node coverage complete while leaving a compact reviewable
source of truth.

Every activated Eureka grants `research_speed_modifier = 0.5` while that
Advance is being researched. The GUI retains the existing 40% visual offset;
it must read the selected Advance key from the registry instead of comparing
only with `guilds`.

## Condition Families

| Family | Player-facing condition | Intended evidence |
| --- | --- | --- |
| `capital_town` | Capital is a town or larger | Capital urban development |
| `urban_center` | Own a town or larger | Urban development |
| `city` | Own a city or larger | Mature urban development |
| `market_center` | Own a market center | Commercial integration |
| `port` | Own at least one port | Maritime capability |
| `university` | Own a university | Scholarly infrastructure |
| `army` | Maintain at least 10 regiments | Standing military capacity |
| `fleet` | Maintain at least 5 ships | Naval capacity |
| `subject` | Have at least one subject | Diplomatic administration |
| `state_capacity` | Own at least 10 locations | Administrative capacity |

The implementation must verify each family trigger against the official
defines before generating common-script output. Existing verified forms cover
market centers, ports, building ownership, `any_owned_location`, location
ranks, and `any_subject`; the numerical army, fleet, and location thresholds
need the final checked engine accessor rather than guessed Jomini syntax.

## Universal Advance Assignments

These explicit assignments cover every Age 2 Advance from the universal
vanilla files. An id that appears here always takes this family over a
source-class fallback.

| Family | Advance ids |
| --- | --- |
| `capital_town` | `renaissance_advance`, `renaissance_thought`, `chancery_records`, `crown_power_advance_renaissance`, `late_feudal_relations`, `grant_privilege_cost_modifier_renaissance_advance`, `law_making_renaissance`, `court_accounting`, `state_efficiency`, `nobles_rights_laws_advance`, `bureaucracy_law_advance` |
| `urban_center` | `renaissance_sculptures`, `government_size_renaissance`, `vibrant_court_advance`, `pop_promotion_speed_age_2`, `spy_construction_renaissance`, `rebellion_support`, `rgo_size_advance_renaissance`, `food_advance_renaissance`, `global_nobles_max_literacy_advance`, `global_burghers_max_literacy_advance`, `global_clergy_max_literacy_advance`, `renaissance_urbanisation`, `renaissance_city_rights`, `recovery_efforts`, `rgo_construction_ren`, `construction_speed_renaissance`, `confucian_academy_advance`, `university_advance`, `theater_advance`, `art_school_advance`, `early_council_hall_advance`, `pop_promote_actions_advance`, `paper_guild_cloth_maintenance_advance`, `innovativeness`, `empiricism`, `church_attendance_duty`, `deus_vult`, `integrated_elites`, `marcher_lords`, `claim_fabrication`, `shrewd_commerce_practice`, `experienced_diplomats`, `benign_diplomats`, `tribute_system`, `influence` |
| `city` | `patron_of_art`, `renaissance_court`, `power_projection_advance_2`, `anatomy_advance`, `expanded_aqueduct_system`, `renaissance_development`, `improve_relation_impact_renaissance`, `renaissance_subject_opinions_advance`, `merchant_power_from_maritime_renaissance_advance`, `war_no_cb_cost_modifier_renaissance_advance`, `national_assemblies_advance`, `steppe_horde_tribal_religious_values_law_advance`, `recruitment_law_advance`, `fort_limit_2_advance` |
| `market_center` | `banking_advance`, `merchants_and_trade`, `standardized_coins`, `trade_range_advance_age_2`, `diplomatic_range_age_1`, `route_to_the_indies_advance`, `counting_house_advance`, `entrepot_advance`, `debt_and_loans`, `benefits_for_mercenaries`, `organised_mercenary_recruitment`, `merchant_traditions`, `privateers` |
| `port` | `rudimentary_coastal_ship_repair`, `maritime_advance_age_2`, `pound_lock_canals_advance`, `dock_advance`, `protected_harbor_advance`, `coastal_fort_advance`, `unlock_early_carrack_advance`, `unlock_barque_advance`, `unlock_m_galley_advance`, `unlock_long_fada_2`, `unlock_hulk_advance`, `naval_repair_ren` |
| `university` | `renaissance_sculptures`, `anatomy_advance`, `theater_advance`, `art_school_advance` |
| `army` | `professional_armies_advance`, `gunpowder_advance`, `recruitment_improvements_renaissance`, `drill_army_advance`, `regiment_reinforcement_speed_renaissance`, `supply_depot_advance_age_2_renaissance`, `correct_box_advance_renaissance`, `medieval_military`, `land_morale_recovery_renaissance_advance`, `army_initiative_ren`, `unlock_men_at_arms_advance`, `unlock_crossbowmen_advance`, `unlock_reformed_crusader_knights_advance`, `unlock_peasant_levy_advance`, `unlock_cavalry_advance`, `unlock_heavy_cavalry_advance`, `unlock_houfnice_advance`, `unlock_supply_carts`, `gun_smith_advance`, `unlock_handgonners_advance`, `cannon_maker_advance`, `slave_center_advance`, `armory_advance`, `tolerance_idea`, `glorious_arms`, `battlefield_commisions`, `finest_of_horses`, `regular_levy_training`, `open_levy_standards`, `enforced_service`, `early_anti_piracy_warfare`, `global_supply_limit_modifier_advance_2` |
| `fleet` | `naval_morale_advance_1`, `blockade_tactics`, `naval_initiative_ren`, `naval_glory`, `boarding_parties`, `marine_regiments` |
| `subject` | `subject_integration` |
| `state_capacity` | `government_size_renaissance`, `rgo_size_advance_renaissance`, `food_advance_renaissance`, `global_supply_limit_modifier_advance_2` |

Where an id appears in multiple rows, precedence is deliberate and follows the
family order in `data/eureka_age2_conditions.yaml`; the more thematic family
wins. The generator must reject accidental duplicate assignments that lack an
explicit precedence entry.

## Contextual Advance Assignments

All remaining Age 2 Advances receive exactly one fallback family according to
the filename that defines them:

| Definition source | Family |
| --- | --- |
| `country_*.txt`, `beyliks.txt`, `colonial_nations.txt`, `japanese_unique.txt`, `frankokratia.txt` | `state_capacity` |
| `culture_*.txt`, `culture_group_*.txt`, `religion_*.txt` | `urban_center` |
| `region_*.txt` | `state_capacity` |
| `government_*.txt` | `capital_town` |
| `ctype_*.txt`, `*_unlocks.txt`, `diplomacy_unlocks.txt`, `estate_*.txt`, `4_choices_*.txt` | `urban_center` |
| Any remaining source | `urban_center` |

The fallback is intentionally universal rather than a tag, religion, or
region-specific condition. Those conditions are already gated by the Advance's
vanilla `potential` and `allow` blocks; adding another identity gate would make
an accessible Eureka depend on a source definition that is not visible to the
player.

## Backend Lifecycle

1. Generate one scripted trigger and one permanent country-variable name per
   Advance: `tv_eureka_<advance>_condition_met_trigger` and
   `tv_eureka_boost_active_<advance>`.
2. Generate a single country-scoped refresh effect. It checks only conditions
   whose active variable is not set, then permanently activates each newly met
   Eureka and assigns its visual offset.
3. Register the refresh from `on_game_start` for all countries and a
   player-only yearly-country bridge. Do not use the existing Guilds
   location-acquisition hooks as the authoritative path: manually creating a
   market center otherwise misses activation, and most proposed conditions are
   not location-transfer events.
4. Use the generated `INJECT:<advance>` patch only when the vanilla Advance has
   no `modifier_while_progressing` block. If it has one, generate a full
   `REPLACE:<advance>` preserving every original field plus the Eureka block.
5. The refresh does not test research completion. Activation remains harmless
   after an Advance is researched, and no reliable completion on-action exists.

## GUI And Localization

The GUI generator must generate static key branches from the registry; it must
not try to build localized condition text or a raw variable name dynamically.
For an `AdvanceItem` or `AdvanceNode`, the branch selects that item's condition
text, active variable, and visual boost. Current-research-only surfaces continue
to compare localized advance names, because the raw current-research key has not
been verified in every GUI context.

The five audited surfaces change together through
`scripts_eureka/patch_gui_progress.py`:

| Surface | Required change |
| --- | --- |
| `technology_lateralview.gui` | Node progress, detailed card condition, and effect-row filtering |
| `advances_lateralview.gui` | List progress, condition row, and effect-row filtering |
| `agenda_view.gui` | Current-research progress |
| `hud_topbar.gui` | Current-research progress |
| `advances_tooltips.gui` | Progress slices and one active-Eureka speed line |

Generate English and Simplified Chinese text for every family, rather than one
localization key per Advance. The visible row resolves the condition family
selected by its static branch; it shows the same wording before and after
activation, with the existing condition/boosted state label and icon.

## Acceptance Checks

- The registry parser finds 647 Age 2 ids in the checked-in reference snapshot,
  with zero unassigned ids and zero stale ids.
- Every generated Advance patch contains one Eureka `modifier_while_progressing`
  branch and preserves the original definition content.
- A player country that already meets any family condition receives its active
  variable at game start; a newly qualifying player receives it during the next
  yearly refresh.
- Every condition family has English and Simplified Chinese localization,
  UTF-8 BOM, and straight ASCII quotes.
- Regenerating the five GUI outputs from vanilla succeeds with exact anchor
  counts, then `scripts/validate.py --changed --fix --ai-report` and
  `git diff --check` pass.

## Deferred Verification

R02 implements this design only after confirming the numerical army, fleet,
and owned-location trigger accessors from official definitions or vanilla
examples. It also replaces the Guilds prototype files and removes its debug
event/hook path, which is superseded by the universal refresh lifecycle.
