# Great Project — GitHub Wiki (English)

> Mod: **Towards Victory - Great Project**
> Mod ID: `hades.towards_victory.great_project`
> Requires: Community Mod Framework (CMF) 2.x
> Standalone: yes — no dependency on any other mod. The main *Towards Victory* mod depends on this one, not the other way around.

## Table of Contents
1. [Why this mod exists](#why-this-mod-exists)
2. [Requirements & compatibility](#requirements--compatibility)
3. [The Engineering Department](#the-engineering-department)
4. [Wonder catalog](#wonder-catalog)
5. [The six-stage construction system](#the-six-stage-construction-system)
6. [Wonders Atlas companion site](#wonders-atlas-companion-site)
7. [FAQ](#faq)

---

## Why this mod exists

In vanilla EU5, a "wonder" is a location with a flavor tooltip attached. It has no mechanical effect, no build process, and most players never interact with it. Great Project replaces that with a real system: a national organization, a multi-stage construction process, and a permanent country-wide payoff when a wonder is finished.

## Requirements & compatibility

- **Hard dependency:** Community Mod Framework 2.x (needed for its custom `on_game_load` callback).
- **No dependency on the main *Towards Victory* mod.** Great Project is fully playable on its own.
- If you also run the main *Towards Victory* mod, note that it declares a dependency on Great Project (not the reverse) — one of its milestone effects calls into this mod's wonder-establishment logic.

## The Engineering Department

Great Project adds a new international organization, the **Engineering Department**, which owns the entire wonder lifecycle:
- It is **non-unique** — any number of instances can theoretically exist depending on scope rules, and it never triggers vanilla IO elections.
- Its "Great Engineer" character is a country-level appointment, not the country's ruler, and drives the Concept and Survey stages described below.
- Founding-country control is locked: the organization cannot silently reassign its leader country the way vanilla IOs can.

## Wonder catalog

- **56 generic wonders** — buildable by any nation that meets a wonder's requirements. Each generic wonder offers a choice of ceremony style (see Stage 5) that shapes its final bonuses.
- **136 historical unique wonders** — stronger, bespoke variants of a generic wonder type, restricted to the nation that owns the specific historical location. Examples:
  - **Persian Qanat** — Qom
  - **Longjiang Shipyard** — Jiangyin
  - **Pharos Lighthouse** — Alexandria
  - **Hagia Sophia** — Constantinople
  - **Dome of the Rock** — Jerusalem
  - **Angkor Wat** — Angkor
  - **Alhambra** — Granada
  - **Taj Mahal** — Agra
  - **Forbidden City** — Dadu
  - **Topkapi Palace** — Constantinople
  - **St. Peter's Basilica** — Rome
  - **Bank of Saint George** — Genoa
  - **Kremlin** — Moscow
  - **Great Zimbabwe**
  - **Machu Picchu** — Picchu
  - **Grand Canal** — Shangyuan
  - **Amsterdam Canal Ring**
  - ...and more.

## The six-stage construction system

Every wonder — generic or unique — goes through the same six stages.

### 1. Concept
Your appointed Great Engineer proposes a feasible wonder based on your country's current conditions — this is not a free player choice. You can:
- **Accept** the proposal
- **Request a revision** (costs 10 prestige) to have the Engineer propose again
- **Fund a redraft** for a fresh set of candidate proposals

### 2. Debate
Before construction can begin, you need domestic backing. Nobles, burghers, and clergy each raise demands; satisfying them raises a **Domestic Support** meter (0–200). Reaching 100+ support unlocks the survey stage.

### 3. Survey
The Great Engineer surveys the chosen site and scores three factors — **Scale**, **Logistics**, and **Organization** (0–100% each). These are derived from the site's hidden affinity, some randomness, and the Engineer's personal skill. They permanently fix the wonder's maximum level, total build cost, and build time — there is no re-roll.

### 4. Construction
You build the supporting infrastructure — a Labor Camp for manpower and a Materials Depot for logistics — then spend stockpiled materials to advance four parts of the wonder in parallel: **foundation, body, function, and decoration**.

### 5. Ceremony
Before the wonder is finished, you choose how it's consecrated:
- **Generic wonders** offer a choice of **3 ceremony styles**, each producing different bonuses.
- **Unique wonders** (Alhambra, Hagia Sophia, Pharos, etc.) have a single bespoke ceremony tailored to their history.

This choice determines the wonder's actual gameplay effects.

### 6. Finalization
The final wonder building is constructed. You receive completion rewards and a nationwide celebratory modifier, and the completion is broadcast as world news.

## Wonders Atlas companion site

A standalone website (outside the game) maps every one of the 136 unique wonders as a pin on a world map, with click-through detail cards. Generic wonders are listed alongside in a sidebar. Useful for browsing the full wonder catalog without loading a save.

## FAQ

**Does this require the main Towards Victory mod?**
No. Great Project is fully standalone and only needs CMF 2.x.

**Can I use it with Towards Victory?**
Yes — the main mod depends on Great Project and integrates with it (e.g. one of its victory-path milestones triggers wonder-system setup), but Great Project itself doesn't require the main mod.

**Are unique wonder locations fixed?**
Yes, each unique wonder is tied to one specific historical location (e.g. Persian Qanat at Qom, Longjiang Shipyard at Jiangyin). Only the nation controlling that location can build it.

**How is the ceremony choice different for unique wonders?**
Generic wonders let you pick from 3 styles. Unique wonders have one dedicated ceremony written for their specific history, rather than a choice of 3.
