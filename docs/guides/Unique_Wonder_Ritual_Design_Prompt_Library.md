# Unique Wonder Ritual Design Prompt Library

## Purpose

This library is prompt material for designing unique wonder rituals. It distills
vanilla EU5 mechanism affordances into reusable design prompts for the Unique
Wonder Ritual Harness without copying vanilla scripts or treating the current
archetype registry as a mechanism whitelist.

Use it when drafting `node_graph.mechanic_signature`,
`node_graph.cadence_signature`, event chains, listener contracts, runtime
variables, UI models, and failure/retry branches for the 123 unique wonders.
Do not use it as a reason to generate formal ritual specs in bulk. It is a
design prompt library, not executable data.

The core bias of this guide is simple: a ritual should prove that the state can
use the wonder. Completion should come from a player choice, real validation
point, event branch, listener, resource movement, appointment, construction
hook, or crisis resolution - not from a default monthly progress bar.

## How To Use This Prompt Library

1. Pick the wonder's historical mechanism first: defense, water control,
   scholarship, pilgrimage, dynastic authority, trade certification, civic
   ordering, sacred settlement, resource logistics, or crisis legitimacy.
2. Pick a cadence from the inspiration table. Prefer a non-monthly cadence. Use
   `monthly_institutionalization` only when the history is genuinely an
   institutional process that makes sense as periodic work.
3. Add 2-4 mechanic prompt atoms. Combine atoms across subsystems when the
   wonder deserves a bespoke loop, such as route plus actor assignment plus
   incident branch.
4. Translate the atoms into Harness concepts: node kinds, capabilities,
   variables, UI bindings, event chain, retry branch, hidden executor handoff,
   and the existing supported listeners only.
5. Keep every EU5 interface conservative: event IDs below 10000, variables with
   the ritual prefix, declared readers/writers, resolved localization refs,
   tooltip/pre-evaluation safety, valid `listener_contract`, verified templates,
   and no unsupported capability or node-kind invention.

## Cadence Inspiration From Vanilla

### 1. `instant_but_branching`

- Vanilla reference: `reference_game_files/game/in_game/events/economy/trade.txt:290`
  (`trade.7`), `reference_game_files/game/in_game/events/economy/trade.txt:569`
  (`trade.17`), and institution branch events such as
  `reference_game_files/game/in_game/events/institution_events.txt:7`.
- How it triggers: a valid event appears when the economic, estate, or
  institution state is already true; player options immediately branch rewards
  and penalties.
- Player agency: choose which social group or economic channel absorbs the cost.
- Best ritual fit: markets, guild halls, academies, law courts, religious
  schools, civic plazas, and wonders whose inaugural act is a public bargain.
- Anti-progress-bar translation: do not tick progress. Gate the ritual on a
  concrete precondition, then branch instantly into 2-3 options with different
  costs, flags, and reward expression.

### 2. `event_driven`

- Vanilla reference: mission setup and follow-up events in
  `reference_game_files/game/in_game/events/missionevents/generic_mission_events.txt:14`,
  plus privilege follow-ups in
  `reference_game_files/game/in_game/events/privilege_events.txt:177`.
- How it triggers: a cooldown/eligibility variable opens an event; the event
  saves scopes, sets temporary state, and later resolves through a follow-up
  event.
- Player agency: choose whether to fund, suppress, redirect, or escalate the
  issue.
- Best ritual fit: patronage conflicts, consecration disputes, scholarly
  controversies, migration openings, and civic inauguration debates.
- Anti-progress-bar translation: make the event branch itself the progress. A
  retry or crisis path should change state before the next event can fire.

### 3. `player_action_sequence`

- Vanilla reference: multi-step country interaction selectors in
  `reference_game_files/game/in_game/common/country_interactions/bribe_vote.txt:46`,
  `:73`, `:96`, `:115`, and `:139`.
- How it triggers: the player walks through explicit selection steps for target
  country, organization, law, policy, and value; the final effect/reject effect
  depends on those selected scopes.
- Player agency: select the target sequence and accept the political price.
- Best ritual fit: diplomatic monuments, assembly halls, law codes, treaty
  sites, coronation venues, and wonders that need formal certification.
- Anti-progress-bar translation: require a short action chain with visible
  selections. Completion follows the final confirmed action, not elapsed time.

### 4. `construction_or_auxiliary_building`

- Vanilla reference: building type lifecycle fields in
  `reference_game_files/game/in_game/common/building_types/readme.txt:14`,
  `:24`, `:40`, and `:41`; university construction event in
  `reference_game_files/game/in_game/events/economy/building_events.txt:78`.
- How it triggers: a building or upgrade is constructed, then `on_built`,
  construction completion, or a scripted event validates the new local state.
- Player agency: choose where to place an annex, whether to tolerate disruption,
  or which auxiliary building proves the wonder can operate.
- Best ritual fit: canals, walls, harbors, dams, observatories, universities,
  granaries, fortified gates, and industrial works.
- Anti-progress-bar translation: the construction task is already the timer.
  Add a completion validation or local incident instead of another monthly gate.

### 5. `war_validated`

- Vanilla reference: hardcoded war hooks in
  `reference_game_files/game/in_game/common/on_action/_hardcoded.txt:1518`
  (`on_pre_winning_war`) and `:1575` (`on_ending_war`), plus siege/occupation
  hooks at `:201`, `:266`, and `:314`.
- How it triggers: the country is about to win or end a war, or a key location
  changes siege/occupation state.
- Player agency: fight a real war, defend or recover a target, negotiate
  settlement timing, or choose what victory proves.
- Best ritual fit: walls, fortresses, arsenals, military roads, watchtowers,
  sacred defensive sites, and triumphal monuments.
- Anti-progress-bar translation: validate against a real war outcome or
  occupation check. If no war occurs, leave the ritual pending or offer a costly
  non-war fallback with weaker rewards.

### 6. `succession_validated`

- Vanilla reference: ruler/character death pulse cleanup in
  `reference_game_files/game/in_game/common/on_action/character_death_pulses.txt:1`,
  succession crisis disaster start/end in
  `reference_game_files/game/in_game/common/disasters/byzantine_succession_crisis.txt:47`,
  and succession end triggers in
  `reference_game_files/game/in_game/common/scripted_triggers/disaster_triggers.txt:260`.
- How it triggers: a ruler, heir, claimant, patriarch, hostage, or assigned
  character dies or the state resolves a succession crisis.
- Player agency: appoint a successor, back a claimant, stabilize legitimacy, or
  accept a costly oath.
- Best ritual fit: dynastic tombs, palaces, ancestral temples, coronation sites,
  sacred thrones, and monuments tied to mandate continuity.
- Anti-progress-bar translation: wait for or force a succession validation
  point, then branch on legitimacy/stability/claimant state.

### 7. `route_certification`

- Vanilla reference: treasure voyage route setup and travel state in
  `reference_game_files/game/in_game/common/scripted_effects/country_effects.txt:1718`,
  `:1734`, `:1765`, `:1802`, and `:1971`, plus
  `reference_game_files/game/in_game/common/on_action/treasure_voyage.txt`.
- How it triggers: a route is selected, distance/travel state is stored, movement
  or visit events fire, and cleanup occurs at the end.
- Player agency: choose or qualify route endpoints, protect the voyage, and
  decide how to handle foreign reception or cargo.
- Best ritual fit: lighthouses, canals, caravanserais, harbors, bridges,
  road networks, pilgrimage roads, and river systems.
- Anti-progress-bar translation: represent waypoints, certification, and first
  completed transfer. The player should know what route is being proven.

### 8. `actor_assignment`

- Vanilla reference: character selector and dynasty scoping in
  `reference_game_files/game/in_game/common/country_interactions/change_ruler.txt:53`,
  imperial examination character creation in
  `reference_game_files/game/in_game/events/imperial_examination_events.txt:15`,
  and learning-building candidate quality at `:638`.
- How it triggers: the player assigns, creates, or selects an actor with a
  relevant estate, dynasty, literacy, role, or attribute.
- Player agency: pick the official/scholar/religious figure/general and accept
  the estate or legitimacy consequence.
- Best ritual fit: academies, libraries, temples, tomb complexes, courts,
  observatories, naval schools, and administrative monuments.
- Anti-progress-bar translation: actor quality and branch outcome carry pacing.
  A bad appointment should create a retry or incident, not just slower progress.

### 9. `resource_delivery`

- Vanilla reference: market/export choices in
  `reference_game_files/game/in_game/events/economy/trade.txt:300`,
  goods supply in `:605`, and treasure voyage cargo variables in
  `reference_game_files/game/in_game/common/scripted_effects/country_effects.txt:1816`.
- How it triggers: a good, cargo amount, export, market relation, or supply
  condition is selected and consumed/resolved.
- Player agency: decide which resource to deliver, whether to pay extra, and
  which group receives the benefit.
- Best ritual fit: granaries, canals, trade depots, workshops, mint sites,
  feast halls, pilgrimage kitchens, shipyards, and resource-specific wonders.
- Anti-progress-bar translation: require a named delivery or market event. Do
  not convert all resources into anonymous monthly points.

### 10. `hybrid`

- Vanilla reference: disasters combine monthly pressure with event branches in
  `reference_game_files/game/in_game/common/disasters/ambrosian_republic.txt:46`,
  `reference_game_files/game/in_game/common/disasters/aspiration_for_liberty.txt:47`,
  and `reference_game_files/game/in_game/common/disasters/byzantine_succession_crisis.txt:67`;
  on-action concurrency constraints are documented at
  `reference_game_files/game/in_game/common/on_action/on_actions.info:62`.
- How it triggers: a large state machine mixes incidents, stored variables,
  listener checks, periodic pressure, and final validation.
- Player agency: choose which incident to absorb, which actor to trust, and
  which final validation path to pursue.
- Best ritual fit: mega-wonders whose history involved administration, crisis,
  supply, and legitimacy all at once.
- Anti-progress-bar translation: monthly pressure may exist only as one local
  support role. The main loop must still include non-monthly events, listener
  validation, player action, or resource/route proof.

## Mechanic Prompt Atoms

Each atom is written to be pasted into an AI design prompt. The "listeners /
triggers / effects" field intentionally distinguishes vanilla affordances from
Harness v1 listener support. Do not declare unsupported listeners in specs.

### Atom 01 - Real War Proves The Defensive System

- Prompt atom: "Require the country to validate the wonder in a real war, such
  as winning while the wonder province remains held or recovering it before the
  peace settlement."
- Applies to: walls, forts, gates, arsenals, frontier roads, sacred defenses.
- Cadence type: `war_validated`.
- Listeners / triggers / effects: Harness listeners `pre_winning_war` or
  `ending_war`; trigger scripts can check war outcome and location ownership.
- Risk or failure mode: ritual can stall in peacetime; offer a costly fallback
  only if historically plausible.
- Recommended player_agency_model: strategic validation by military timing.

### Atom 02 - Siege Damage Becomes The Ritual Crisis

- Prompt atom: "A siege or occupation exposes flaws in the monument; the ritual
  succeeds only after the player chooses repair, reprisal, or reform."
- Applies to: fortified cities, walls, citadels, river gates.
- Cadence type: `event_driven` or `war_validated`.
- Listeners / triggers / effects: vanilla has siege/occupation hooks; in Harness
  v1 model this through trigger_script checks and event branches unless listener
  support is extended later.
- Risk or failure mode: unsupported listener declaration; keep listener list to
  supported Harness names.
- Recommended player_agency_model: crisis response choice.

### Atom 03 - Recapture Certification

- Prompt atom: "The monument is not consecrated until its province is lost,
  threatened, or recovered, proving the state can reassert control."
- Applies to: border wonders, holy cities, capitals, coastal fortresses.
- Cadence type: `war_validated`.
- Listeners / triggers / effects: `ending_war`, location owner/controller checks,
  one-shot flag for completed recapture.
- Risk or failure mode: punishing peaceful players too hard; allow an expensive
  garrison review branch when no war has occurred.
- Recommended player_agency_model: territorial recovery validation.

### Atom 04 - Great Battle Dedication

- Prompt atom: "A major victory supplies captives, banners, or legitimacy for
  the dedication; defeat forces a humbled retry branch."
- Applies to: triumphal monuments, warrior temples, arsenals, cavalry fields.
- Cadence type: `war_validated`.
- Listeners / triggers / effects: vanilla great-battle hook is reference
  material; Harness v1 should validate via supported war listeners or explicit
  checks.
- Risk or failure mode: battle hook not supported by Harness; do not invent it
  in `node_graph.listeners`.
- Recommended player_agency_model: risk-backed military proof.

### Atom 05 - Peace Settlement Seal

- Prompt atom: "The final treaty is the ritual seal: the player chooses whether
  to make the wonder a symbol of mercy, tribute, or deterrence."
- Applies to: palaces, victory arches, law monuments, defensive wonders.
- Cadence type: `war_validated`.
- Listeners / triggers / effects: `ending_war`, event option branch, permanent
  reward handoff through hidden executor.
- Risk or failure mode: tooltip effects mutating peace-related state; keep heavy
  cleanup in hidden executor.
- Recommended player_agency_model: diplomatic-military settlement choice.

### Atom 06 - Certified Route With Named Waypoints

- Prompt atom: "Require a named route to be charted and certified through
  endpoints or waypoints before the wonder's benefit activates."
- Applies to: canals, bridges, lighthouses, caravanserais, pilgrimage roads.
- Cadence type: `route_certification`.
- Listeners / triggers / effects: route_gate capability, route variables,
  location scopes, event_chain.
- Risk or failure mode: route becomes flavor-only; show the chosen endpoint or
  waypoint in UI state.
- Recommended player_agency_model: choose and protect the route.

### Atom 07 - First Cargo Flow

- Prompt atom: "The ritual completes when the first cargo, tax convoy, grain
  shipment, or sacred offering reaches the wonder."
- Applies to: canals, harbors, granaries, markets, feast halls, temples.
- Cadence type: `resource_delivery`.
- Listeners / triggers / effects: resource_gate, route_gate, goods/cargo
  variables, event resolution.
- Risk or failure mode: anonymous stockpile points feel generic; name the good or
  cargo class.
- Recommended player_agency_model: logistics delivery choice.

### Atom 08 - Foreign Market Recognition

- Prompt atom: "The wonder's trade ritual requires recognition in a foreign or
  rival market, then asks whether to privilege merchants or the crown."
- Applies to: entrepots, markets, ports, canals, bridges.
- Cadence type: `route_certification` or `instant_but_branching`.
- Listeners / triggers / effects: market/export trigger checks, merchant power,
  estate satisfaction branch.
- Risk or failure mode: no foreign market exists; provide a domestic certification
  branch with lower reward.
- Recommended player_agency_model: economic target selection.

### Atom 09 - Guild Exclusivity Bargain

- Prompt atom: "A guild or estate demands exclusive access to the wonder; the
  player chooses output efficiency, social peace, or open access."
- Applies to: workshops, markets, mines, ports, craft districts.
- Cadence type: `instant_but_branching`.
- Listeners / triggers / effects: estate satisfaction, goods supply,
  country/location modifier branch.
- Risk or failure mode: all options become pure buffs; include at least one real
  social or production cost.
- Recommended player_agency_model: political economy bargain.

### Atom 10 - Scarce Goods Substitution Trial

- Prompt atom: "The ceremony needs a scarce good; the player may deliver the
  authentic material, substitute a local good, or delay for a stronger reward."
- Applies to: temples, tombs, palaces, workshops, shipyards, observatories.
- Cadence type: `resource_delivery`.
- Listeners / triggers / effects: goods variable, resource_gate, retry_event,
  custom tooltip for available delivery.
- Risk or failure mode: retry loop without consequence; failed substitution
  should alter estate/culture/religion response.
- Recommended player_agency_model: material authenticity choice.

### Atom 11 - Auxiliary Annex Completion

- Prompt atom: "The wonder must be paired with a practical annex - dock, school,
  gatehouse, archive, cistern, storehouse - and the ritual resolves when that
  annex is completed."
- Applies to: nearly all infrastructure and institution wonders.
- Cadence type: `construction_or_auxiliary_building`.
- Listeners / triggers / effects: construction completion hook, building check,
  location variable.
- Risk or failure mode: duplicating the main wonder build; make the annex prove a
  distinct function.
- Recommended player_agency_model: site and investment choice.

### Atom 12 - Rival Institution Relocation

- Prompt atom: "A rival old institution resists the wonder; the player may
  migrate scholars/workers, compensate the old site, or suppress protests."
- Applies to: universities, libraries, academies, courts, temples.
- Cadence type: `event_driven`.
- Listeners / triggers / effects: save old/new location scopes, construct or
  validate building, local unrest/protest modifier.
- Risk or failure mode: source/target scope confusion; declare variables and UI
  refs explicitly.
- Recommended player_agency_model: relocation tradeoff.

### Atom 13 - Opening Inspection

- Prompt atom: "After construction, an inspection event finds one weakness; the
  player chooses ceremony, repair, or operational doctrine before finalization."
- Applies to: dams, canals, harbors, walls, bridges, industrial works.
- Cadence type: `construction_or_auxiliary_building`.
- Listeners / triggers / effects: on-completion check, event_chain, hidden
  executor final_reward_handoff.
- Risk or failure mode: option tooltip performs cleanup; use hidden executor for
  state mutation.
- Recommended player_agency_model: operational readiness choice.

### Atom 14 - Appoint A Scholar Or Official

- Prompt atom: "The ritual requires a named scholar, engineer, priest, jurist, or
  commander whose traits shape the first incident."
- Applies to: academies, temples, law courts, palaces, arsenals, observatories.
- Cadence type: `actor_assignment`.
- Listeners / triggers / effects: actor_assignment capability, character
  variable, assignment_gate, event branch.
- Risk or failure mode: actor is only flavor; make their estate/attribute affect
  cost, incident, or reward variant.
- Recommended player_agency_model: personnel selection.

### Atom 15 - Learning Buildings Improve The Candidate

- Prompt atom: "Count nearby or national learning buildings to improve the
  quality of the ritual candidate, but still force a choice among imperfect
  candidates."
- Applies to: universities, libraries, observatories, examination halls.
- Cadence type: `actor_assignment`.
- Listeners / triggers / effects: local/country variable count, create_character
  or saved actor variable, event options.
- Risk or failure mode: deterministic best option; include a social or political
  drawback for the strongest candidate.
- Recommended player_agency_model: merit versus faction choice.

### Atom 16 - Institution Spreads Through The Wonder Site

- Prompt atom: "The wonder becomes a local carrier of an institution only after
  the player resolves who controls that knowledge."
- Applies to: libraries, schools, temples, printing sites, observatories,
  scientific monuments.
- Cadence type: `event_driven` or `hybrid`.
- Listeners / triggers / effects: institution progress checks, location scope,
  estate satisfaction branch.
- Risk or failure mode: generic research bonus; tie the institution to the
  wonder's local role.
- Recommended player_agency_model: knowledge governance choice.

### Atom 17 - Religious Or Legal Codification Dispute

- Prompt atom: "A clerical, legal, or philosophical dispute must be resolved
  before the wonder's authority is accepted."
- Applies to: temples, mosques, cathedrals, law monuments, sacred tombs.
- Cadence type: `instant_but_branching` or `event_driven`.
- Listeners / triggers / effects: religion/culture/institution checks, estate
  satisfaction, custom_tooltip conditions.
- Risk or failure mode: branch text ignores local religion/culture; save the
  relevant scope and expose it in UI/loc references.
- Recommended player_agency_model: doctrine arbitration.

### Atom 18 - Migration Settlement Around The Wonder

- Prompt atom: "The ritual draws settlers, pilgrims, students, or artisans; the
  player chooses how much migration to accept and which group bears the cost."
- Applies to: cities, sacred sites, universities, markets, frontier wonders.
- Cadence type: `event_driven` or `resource_delivery`.
- Listeners / triggers / effects: migration effect, origin/destination scopes,
  estate or pop satisfaction.
- Risk or failure mode: monthly migration becomes the ritual itself; the ritual
  should hinge on the opening choice and follow-up settlement event.
- Recommended player_agency_model: demographic settlement choice.

### Atom 19 - Estate Privilege Bargain

- Prompt atom: "An estate offers to maintain the wonder if granted a privilege;
  refusal creates an incident or lower-cost retry."
- Applies to: guild halls, temples, noble palaces, law courts, trade depots.
- Cadence type: `instant_but_branching`.
- Listeners / triggers / effects: has/revoke/grant privilege checks, estate
  satisfaction, event_chain.
- Risk or failure mode: privilege branch bypasses cleanup; add one-shot ritual
  flags and terminal cleanup.
- Recommended player_agency_model: institutional concession.

### Atom 20 - Privilege Exhaustion Or Revocation

- Prompt atom: "A privilege-enabled stream runs out of eligible people, goods, or
  locations, forcing the player to revoke, renew, or reform it."
- Applies to: settlement wonders, trade privileges, religious schools, markets.
- Cadence type: `event_driven`.
- Listeners / triggers / effects: eligibility trigger, retry branch, revoke
  privilege or remove state variable.
- Risk or failure mode: endless event spam; use cooldown variables and explicit
  terminal branches.
- Recommended player_agency_model: renew versus close the institution.

### Atom 21 - Rebel Allegiance Fork

- Prompt atom: "A ritual dispute creates a rebel or opposition actor; the player
  can reconcile, co-opt, or crush them, with different allegiance outcomes."
- Applies to: contested civic, religious, dynastic, and estate monuments.
- Cadence type: `event_driven` or `hybrid`.
- Listeners / triggers / effects: create/reuse opposition scope, rebel progress,
  pop/character allegiance changes.
- Risk or failure mode: too punitive for a wonder reward; keep the crisis bounded
  and retryable.
- Recommended player_agency_model: conflict resolution branch.

### Atom 22 - Disaster Stress Test

- Prompt atom: "The wonder's ritual is a bounded mini-disaster: it starts under
  instability, fires incidents, and ends only after legitimacy/stability checks."
- Applies to: palaces, capitals, dynastic tombs, sacred thrones, assemblies.
- Cadence type: `hybrid`.
- Listeners / triggers / effects: incident_event, retry_branch, monthly pressure
  only if justified, end trigger check.
- Risk or failure mode: becoming a generic monthly disaster; require at least one
  non-monthly choice or listener validation.
- Recommended player_agency_model: crisis management.

### Atom 23 - Succession Oath

- Prompt atom: "The ritual is completed only when the next ruler or heir swears
  at the wonder, proving continuity across a succession."
- Applies to: dynastic tombs, palaces, temples, coronation sites.
- Cadence type: `succession_validated`.
- Listeners / triggers / effects: Harness listener `ruler_death`, legitimacy
  checks, ruler/heir variables.
- Risk or failure mode: passive waiting; allow the player to prepare oath terms
  before succession.
- Recommended player_agency_model: pre-commitment plus succession validation.

### Atom 24 - Claimant Or Dynasty Selection

- Prompt atom: "The player chooses a claimant, dynastic representative, or ritual
  guardian; legitimacy changes when the choice is validated."
- Applies to: palaces, tombs, clan sites, mandate monuments.
- Cadence type: `actor_assignment` or `succession_validated`.
- Listeners / triggers / effects: character selector, dynasty scope, character
  variable, event resolution.
- Risk or failure mode: selector pre-evaluation reads unset scopes; declare
  tooltip safety and guard variables.
- Recommended player_agency_model: claimant selection.

### Atom 25 - Subject Or Overlord Confirmation

- Prompt atom: "A subject, overlord, or client polity must confirm the wonder's
  authority, creating a branch between autonomy and centralization."
- Applies to: imperial capitals, tribute halls, frontier monuments, canals.
- Cadence type: `player_action_sequence`.
- Listeners / triggers / effects: diplomatic action, target country scope,
  approval/refusal branch.
- Risk or failure mode: scope target absent in tooltip pre-eval; use explicit
  scope_contract and hidden executor for final mutation.
- Recommended player_agency_model: diplomatic negotiation.

### Atom 26 - Formal Vote Or Policy Certification

- Prompt atom: "The ritual requires a formal vote, law, or policy choice, so the
  player must select the institution and the exact concession."
- Applies to: assemblies, law courts, trade leagues, city halls.
- Cadence type: `player_action_sequence`.
- Listeners / triggers / effects: select_trigger-style sequence, action effect
  and reject_effect, policy/law variable.
- Risk or failure mode: complex selector scopes are brittle; keep the Harness
  spec explicit about each target and reader/writer.
- Recommended player_agency_model: multi-step institutional choice.

### Atom 27 - Baseline Task Challenge

- Prompt atom: "Save a baseline state at ritual start, then require the player to
  maintain or improve it while completing a separate event choice."
- Applies to: courts, administrations, observatories, schools, palaces.
- Cadence type: `player_action_sequence` or `event_driven`.
- Listeners / triggers / effects: on_start variable, enabled checks, on_abort and
  on_completion cleanup.
- Risk or failure mode: stale baseline variables; specify cleanup at every
  terminal and abort path.
- Recommended player_agency_model: maintain-state challenge.

### Atom 28 - One-Shot Cooldown Incident

- Prompt atom: "The ritual has a single memorable incident guarded by a cooldown
  or one-shot variable, not a recurring monthly pulse."
- Applies to: any wonder needing a small risk beat.
- Cadence type: `event_driven`.
- Listeners / triggers / effects: one-shot variable, retry_event, event_chain.
- Risk or failure mode: forgotten cleanup blocks future rituals; use ritual
  prefix and declared cleanup point.
- Recommended player_agency_model: bounded incident choice.

### Atom 29 - Hidden Finalization Handoff

- Prompt atom: "Player-facing options describe rewards, then a hidden executor
  performs heavy cleanup, reward dispatch, and state clearing."
- Applies to: every implementation-ready unique ritual.
- Cadence type: any non-monthly cadence.
- Listeners / triggers / effects: hidden_executor_handoff,
  final_reward_handoff, terminal node.
- Risk or failure mode: option tooltip pre-evaluates mutation; keep tooltip-safe
  preview separate from hidden executor work.
- Recommended player_agency_model: clear visible choice, safe backend handoff.

### Atom 30 - Composite Proof: Actor Plus Route Plus Incident

- Prompt atom: "The wonder is certified by assigning a specialist, sending them
  through a route or resource delivery, then resolving the incident they uncover."
- Applies to: complex wonders such as great canals, observatories, imperial road
  systems, libraries, pilgrimage networks, and maritime monuments.
- Cadence type: `hybrid`.
- Listeners / triggers / effects: actor_assignment, route_gate or resource_gate,
  event_chain, retry_branch, hidden executor.
- Risk or failure mode: overfitting into existing archetypes; explain the custom
  mechanic in `mechanic_signature` rather than forcing one template.
- Recommended player_agency_model: staged operational proof.

## Script Pattern Inventory

### Pattern 01 - Event Chain With Visible Branches

- Vanilla reference: `reference_game_files/game/in_game/events/economy/trade.txt:290`,
  `reference_game_files/game/in_game/events/missionevents/generic_mission_events.txt:14`.
- Explanation: eligibility opens an event, options change different systems, and
  later events may reuse saved state.
- Ritual use: opening debate, crisis, retry, and resolution nodes.
- Harness boundary: every event node needs declared IDs, localization refs,
  reachable edges, and at least one failure/retry route for rich rituals.

### Pattern 02 - Hidden Executor Handoff

- Vanilla reference: hidden cleanup patterns in
  `reference_game_files/game/in_game/events/missionevents/generic_mission_events.txt:610`
  and `:881`.
- Explanation: visible event options remain readable while hidden effects perform
  non-tooltip bookkeeping.
- Ritual use: final reward dispatch, cleanup, ownership registration, and
  one-shot variable clearing.
- Harness boundary: player-facing tooltip paths must not contain unsafe heavy
  mutation; use `hidden_executor_handoff` plus `final_reward_handoff`.

### Pattern 03 - Triggered Effect Branch

- Vanilla reference: institution and trade event options in
  `reference_game_files/game/in_game/events/institution_events.txt:27` and
  `reference_game_files/game/in_game/events/economy/trade.txt:314`.
- Explanation: an option or effect tests current state before applying a local
  branch.
- Ritual use: branch reward by estate, religion, trade good, institution, or
  local site condition.
- Harness boundary: pre-evaluated tooltips must not read variables that only the
  option effect will create.

### Pattern 04 - Delayed Validation

- Vanilla reference: on-action delay semantics in
  `reference_game_files/game/in_game/common/on_action/on_actions.info:16` and
  `:18`.
- Explanation: delayed events must be valid at both scheduling and firing time.
- Ritual use: schedule a later validation event after a route, construction, or
  political promise.
- Harness boundary: declare the saved variables needed at both moments, and add a
  retry/failure path if the state expires.

### Pattern 05 - One-Shot Or Cooldown Variable

- Vanilla reference: mission event cooldown variables in
  `reference_game_files/game/in_game/events/missionevents/generic_mission_events.txt:14`
  and disaster completion variables in
  `reference_game_files/game/in_game/common/disasters/aspiration_for_liberty.txt:67`.
- Explanation: variables prevent repeated firing or mark completed historical
  state.
- Ritual use: prevent duplicate opening incidents and mark completed validation.
- Harness boundary: variable names must use the ritual prefix, with exact
  writer/reader/cleanup declarations.

### Pattern 06 - Retry Branch With Changed State

- Vanilla reference: disaster monthly incidents and retry-like branches in
  `reference_game_files/game/in_game/common/disasters/byzantine_succession_crisis.txt:67`.
- Explanation: repeated events are meaningful because state, cooldowns, or risk
  changes between attempts.
- Ritual use: failed inspection, rejected scholar, broken route, or unresolved
  estate dispute.
- Harness boundary: retry targets cannot point directly to terminal nodes and
  should not produce endless no-op loops.

### Pattern 07 - Scoped Variable Handoff

- Vanilla reference: saved scopes in
  `reference_game_files/game/in_game/events/economy/building_events.txt:53`,
  `:59`, and mission event scope setup in
  `reference_game_files/game/in_game/events/missionevents/generic_mission_events.txt:22`.
- Explanation: events capture a target location, character, estate, culture, or
  good for later effect branches.
- Ritual use: chosen site, route endpoint, assigned actor, delivered good, or
  rival institution.
- Harness boundary: every runtime variable needs owner scope, type, writer node,
  reader node, and cleanup.

### Pattern 08 - Actor Assignment

- Vanilla reference: `reference_game_files/game/in_game/common/country_interactions/change_ruler.txt:53`
  and `reference_game_files/game/in_game/events/imperial_examination_events.txt:15`.
- Explanation: a selected or created actor carries identity into downstream
  choices.
- Ritual use: appoint ritual engineer, scholar, priest, jurist, admiral, or
  guardian.
- Harness boundary: use `actor_assignment` capability and an `assignment_gate`;
  guard fresh character variables in tooltip-pre-evaluated contexts.

### Pattern 09 - Construction Completion Hook

- Vanilla reference: building lifecycle docs at
  `reference_game_files/game/in_game/common/building_types/readme.txt:40` and
  building construction in
  `reference_game_files/game/in_game/events/economy/building_events.txt:78`.
- Explanation: a constructed building can trigger follow-up effects or validate
  local readiness.
- Ritual use: auxiliary annex, inspection gate, or local reward building.
- Harness boundary: do not depend on same-tick building level reads after
  construction; use explicit completion hooks and safe validation.

### Pattern 10 - War Listener Gate

- Vanilla reference: `reference_game_files/game/in_game/common/on_action/_hardcoded.txt:1518`
  and `:1575`.
- Explanation: war outcome windows can validate victory before or as war ends.
- Ritual use: defense proof, treaty seal, triumphal dedication.
- Harness boundary: only declare supported Harness listeners:
  `pre_winning_war` and `ending_war`.

### Pattern 11 - Siege Or Occupation Validation

- Vanilla reference: `reference_game_files/game/in_game/common/on_action/_hardcoded.txt:201`,
  `:266`, and `:314`.
- Explanation: location state can react to siege victory, loss, or occupation.
- Ritual use: wall repair, recapture oath, occupied shrine purification.
- Harness boundary: these vanilla hooks are inspiration only unless the Harness
  supports them later; model with checks or supported war listeners for now.

### Pattern 12 - Route And Cargo Validation

- Vanilla reference: treasure voyage route/cargo effects in
  `reference_game_files/game/in_game/common/scripted_effects/country_effects.txt:1718`,
  `:1765`, `:1816`, and `:1971`.
- Explanation: global/location lists, distance variables, cargo variables, and
  cleanup define a voyage lifecycle.
- Ritual use: certify canal, lighthouse, pilgrimage road, river route, or first
  merchant convoy.
- Harness boundary: use `route_gate` and/or `resource_gate`; expose route state
  in UI instead of hiding it in prose.

### Pattern 13 - Market And Goods Interaction

- Vanilla reference: exports and merchant choices in
  `reference_game_files/game/in_game/events/economy/trade.txt:300`,
  merchant power at `:350`, and goods supply at `:605`.
- Explanation: a market/good is selected, then player choices alter economic and
  estate outcomes.
- Ritual use: first shipment, guild bargain, staple certification, trade-route
  recognition.
- Harness boundary: keep goods IDs and market scopes verified before codegen;
  prompt material should not invent unverified goods.

### Pattern 14 - Institution Or Location Spread

- Vanilla reference: institution progress events in
  `reference_game_files/game/in_game/events/institution_events.txt:7` and
  location progress branches around `:3398`.
- Explanation: knowledge can be advanced globally or at a specific site through
  branch choices.
- Ritual use: library, academy, observatory, temple school, printing hall.
- Harness boundary: tie the institution to the wonder-specific mechanism, not a
  generic research bonus.

### Pattern 15 - Estate Privilege Bargain

- Vanilla reference: migration/privilege event in
  `reference_game_files/game/in_game/events/privilege_events.txt:177`,
  options at `:320`, `:346`, `:373`, and `:386`.
- Explanation: a privilege creates continuing opportunities until eligibility or
  political tolerance ends.
- Ritual use: estate-funded maintenance, guild access, clerical guardianship,
  noble patronage.
- Harness boundary: add terminal cleanup and avoid recurring events without
  cooldown or eligibility checks.

### Pattern 16 - Disaster Escalation

- Vanilla reference: disasters at
  `reference_game_files/game/in_game/common/disasters/ambrosian_republic.txt:46`,
  `reference_game_files/game/in_game/common/disasters/aspiration_for_liberty.txt:47`,
  and end triggers in
  `reference_game_files/game/in_game/common/scripted_triggers/disaster_triggers.txt:507`.
- Explanation: pressure, incidents, and end triggers create a bounded crisis
  state.
- Ritual use: legitimacy trial, contested consecration, dynastic oath, civic
  unrest around a wonder.
- Harness boundary: monthly pressure must be justified as `hybrid` or
  `monthly_institutionalization` and still include non-monthly agency.

### Pattern 17 - Rebel Or Opposition Allegiance Fork

- Vanilla reference: `reference_game_files/game/in_game/events/rebels.txt:42`,
  `:116`, `:129`, and `:140`.
- Explanation: a rebel/opposition scope can gain characters, pop allegiance, and
  progress based on player choice.
- Ritual use: make an inauguration dispute concrete without turning it into a
  full unbounded disaster.
- Harness boundary: keep crisis scope bounded, visible, and retryable; do not
  surprise the player with hidden large-scale punishment.

### Pattern 18 - On-Action Concurrency Boundary

- Vanilla reference: `reference_game_files/game/in_game/common/on_action/on_actions.info:62`.
- Explanation: on-action effects run concurrently with events and cannot safely
  create locals/scopes for same-fire events to read.
- Ritual use: listener gates and hidden executor scheduling.
- Harness boundary: do not rely on same-fire on_action effects to prepare event
  scopes; save required state before firing or use a separate hidden executor
  chain.

## Anti-Monthly Bias Checklist

Before accepting a ritual design, answer every item:

- Does the design have at least one non-monthly player choice, event branch,
  risk point, listener, trigger, route validation, actor assignment, resource
  delivery, construction completion, war result, or succession validation?
- Is `cadence_type` one of the non-monthly types unless the historical mechanism
  truly needs periodic institutionalization?
- If `monthly` appears in listeners, a `monthly_progress_gate` node, a
  `monthly_progress` capability, a monthly listener contract, or a
  `monthly_progress_gate` template, is `cadence_type` exactly
  `monthly_institutionalization` or `hybrid`?
- If `monthly_institutionalization` is used, does
  `non_monthly_triggers_or_reason` name a concrete non-monthly decision, risk,
  listener, branch, trigger, or player action?
- If `hybrid` is used, is monthly pressure only a local/supporting process rather
  than the whole ritual?
- Could the ritual be completed by waiting N months with no meaningful state
  change? If yes, redesign it.
- Is the chosen archetype a helpful contract tag rather than a fixed mechanism
  mold?
- Does `mechanic_signature` explain why this loop belongs to this wonder, not
  merely to its broad category?
- Does `cadence_signature` explain why this pacing fits the wonder and how it can
  fail?
- Are tooltip and pre-evaluation hazards kept away from option effects, selector
  chains, and hidden cleanup?

## Ritual Generation Prompt Template

Use this template when asking an AI author to design one unique wonder ritual.
The answer must be a design spec draft, not loadable script and not a bulk edit
to `data/unique_wonder_ritual_specs.yaml`.

```text
Design one Unique Wonder Ritual Harness ritual for:
- wonder_id:
- wonder_name:
- location:
- historical anchor:
- existing base reward and local wonder role:

Hard requirements:
- Do not default to monthly pacing.
- If any monthly listener, monthly_progress_gate node, monthly_progress
  capability, monthly listener_contract, or monthly_progress_gate template is
  used, cadence_type must be monthly_institutionalization or hybrid.
- If monthly_institutionalization is used, explain whether the process is a
  local institutional phase or genuinely historical monthly institutionalization.
- Every ritual must include at least one non-monthly player choice, risk, event
  branch, listener, trigger, actor assignment, route/resource validation,
  construction completion, war result, or succession validation.
- Do not choose the safest mature template merely to pass the Harness.
- Do not relax event ID uniqueness, variable reader/writer declarations, UI refs,
  localization refs, tooltip/pre-evaluation safety, listener_contract, hidden
  executor, capability, node-kind, template, or verified-interface checks.
- Do not copy vanilla script. Use vanilla mechanisms only as design inspiration.

Required output fields:

design_intent:
  Explain what the ritual lets the player prove about the state and the wonder.

historical_mechanism:
  Identify the historical operation being modeled, such as war validation,
  water logistics, route certification, scholarly appointment, dynastic oath,
  estate bargain, institution spread, pilgrimage settlement, or crisis control.

mechanic_signature:
  wonder_specific_hook:
  core_interaction_loop:
  player_decision_pattern:
  state_feedback:
  failure_tension_model:
  reward_expression:
  reuse_risk_mitigation:
  custom_archetype_statement: null unless using a custom_* archetype

cadence_signature:
  cadence_type:
    Must be one of instant_but_branching, event_driven,
    player_action_sequence, construction_or_auxiliary_building, war_validated,
    succession_validated, route_certification, actor_assignment,
    resource_delivery, monthly_institutionalization, or hybrid.
  cadence_rationale:
  player_agency_model:
  non_monthly_triggers_or_reason:
  pacing_failure_mode:

listeners:
  Declare only supported Harness listeners: monthly, ruler_death,
  pre_winning_war, ending_war. If vanilla inspiration uses siege, occupation,
  battle, construction, trade, or route hooks not supported by the Harness,
  describe them as trigger/check inspiration rather than node_graph.listeners.

variables:
  For each runtime variable, provide name, scope, type, initial value, writer
  nodes, reader nodes, UI binding if any, and cleanup node. Use the ritual prefix.

event chain:
  Provide at least three player-visible nodes for implementation-ready designs.
  Include opening, complication/validation, retry or failure branch, and final
  resolution/hidden executor handoff.

retry/failure branch:
  Explain what can go wrong, how the player sees it, how they retry or accept a
  lesser result, and which variables prevent event spam or stale state.

ui_model:
  Choose suitable components from checklist, route_map, actor_slots,
  material_stockpile, incident_log, or progress_track. Do not add UI state that
  has no declared variable.

capabilities and node kinds:
  Use only Harness-supported capabilities and node/action/check kinds. Explain
  any custom_* archetype through mechanic_signature rather than inventing
  unsupported registry keys.

tooltip and hidden executor safety:
  Identify any option or action that must avoid unsafe pre-evaluation. Put heavy
  cleanup, reward dispatch, and final state mutation in a hidden executor handoff.

why this ritual is unique to this wonder:
  State why the same ritual would not fit most other unique wonders.
```

## Source File References

Scanned vanilla categories and representative files:

- Events: `reference_game_files/game/in_game/events/economy/trade.txt`,
  `reference_game_files/game/in_game/events/economy/building_events.txt`,
  `reference_game_files/game/in_game/events/institution_events.txt`,
  `reference_game_files/game/in_game/events/imperial_examination_events.txt`,
  `reference_game_files/game/in_game/events/missionevents/generic_mission_events.txt`,
  `reference_game_files/game/in_game/events/privilege_events.txt`,
  `reference_game_files/game/in_game/events/rebels.txt`.
- Decisions, journal entries, missions, and tasks:
  `reference_game_files/game/in_game/common/missions/generic_capable_cabinet_mission_pack.txt`
  and mission event follow-ups.
- Laws, government reforms, estates, and privileges:
  `reference_game_files/game/in_game/common/country_interactions/bribe_vote.txt`,
  `reference_game_files/game/in_game/common/country_interactions/change_ruler.txt`,
  and `reference_game_files/game/in_game/events/privilege_events.txt`.
- Buildings, monuments, and great-project-like construction affordances:
  `reference_game_files/game/in_game/common/building_types/readme.txt` and
  `reference_game_files/game/in_game/events/economy/building_events.txt`.
- Modifiers, scripted triggers, and scripted effects:
  `reference_game_files/game/in_game/common/scripted_triggers/disaster_triggers.txt`
  and `reference_game_files/game/in_game/common/scripted_effects/country_effects.txt`.
- On-actions and listeners:
  `reference_game_files/game/in_game/common/on_action/on_actions.info`,
  `reference_game_files/game/in_game/common/on_action/_hardcoded.txt`,
  `reference_game_files/game/in_game/common/on_action/character_death_pulses.txt`,
  and `reference_game_files/game/in_game/common/on_action/treasure_voyage.txt`.
- Diplomatic actions:
  `reference_game_files/game/in_game/common/country_interactions/bribe_vote.txt`
  and `reference_game_files/game/in_game/common/country_interactions/change_ruler.txt`.
- War, siege, occupation, battle, peace, subject, succession, ruler, heir, and
  dynasty affordances:
  `_hardcoded.txt`, `character_death_pulses.txt`,
  `common/disasters/byzantine_succession_crisis.txt`, and
  `common/scripted_triggers/disaster_triggers.txt`.
- Trade, route, market, goods, production, infrastructure, and construction:
  `events/economy/trade.txt`, `common/scripted_effects/country_effects.txt`,
  `common/on_action/treasure_voyage.txt`, and building references above.
- Culture, religion, institution, technology, literacy, and scholarship:
  `events/institution_events.txt`,
  `events/imperial_examination_events.txt`, and mission event culture scopes.
- Character, actor, advisor, estate, and office assignment:
  `common/country_interactions/change_ruler.txt`,
  `events/imperial_examination_events.txt`, and
  `common/on_action/character_death_pulses.txt`.
- Disasters, incidents, crises, rebellions, legitimacy, and stability:
  `common/disasters/ambrosian_republic.txt`,
  `common/disasters/aspiration_for_liberty.txt`,
  `common/disasters/byzantine_succession_crisis.txt`,
  `common/scripted_triggers/disaster_triggers.txt`, and `events/rebels.txt`.
- Province, state, country variable, flag, and scope usage:
  mission event saved scopes, disaster variables, treasure voyage cargo/route
  variables, and country interaction selected target scopes in the files listed
  above.

This document contains 10 cadence inspirations, 30 mechanic prompt atoms, and 18
script patterns.
