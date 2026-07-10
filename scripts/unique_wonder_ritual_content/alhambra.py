"""Alhambra (unique_alhambra) ritual content.

Bespoke rewrite (2026-07) replacing the previous dice-driven `_entity_ritual`
implementation (6 "treaty clause" + 5 "palace-risk point" rows, each rolling
favorable/contested via `random_list`, resolved by a retry event). That shape
was itself a second instance of the "choice -> deterministic branch marking a
fixed subset of entities at risk -> retry (pay-to-fix vs accept-narrower) ->
threshold-scaled reward" template that Dome of the Rock / Bank of Saint George
/ St. Peter's Basilica converged on after their own bespoke rewrite (see
docs/knowledge/risk_cards/wonders.md rule 13). This module replaces it with a
genuinely different mechanic grounded in the Alhambra's actual history: the
1492 Treaty of Granada did not just transfer a building, it transferred an
entire palace-city's *institutions* -- its treasury office, its garrison, its
scribal chancery (which literally drafted the capitulation terms), its acequia
water administration, and its religious endowments -- from the Nasrid emirate
to the Catholic Monarchs. The player inherits those five offices and, one at a
time, permanently disposes of each: Preserve it intact (legitimacy), Repurpose
it into the new administration (efficiency), or Dismantle it for immediate
value (extraction). There is no dice roll and no fixed "at-risk" subset -- the
5 choices are a portfolio the player builds deliberately, the mix determines a
dominant governance path (concord / administration / extraction) at a single
"Reckoning" event, and the final reward is branched by that path rather than a
literal favorable-count threshold. Tension comes from the choices being
mutually exclusive and irreversible (an inherited institution cannot be
un-dismantled), not from a costed-fix-vs-free-accept retry.

This is also the only one of the 6 wonders whose spec declares a real
`pre_winning_war` / `ending_war` listener_contract (node `alhambra_war_validation`
in data/unique_wonder_ritual_specs.yaml): the inheritance cannot be opened
until the sponsor has actually *won* a war while holding Granada. That is
implemented here as a real war-validation gate
(`tv_wonder_alhambra_war_validated_trigger`), set by a dedicated on_action
bridge (src/in_game/common/on_action/tv_wonder_unique_alhambra_ritual_on_actions.txt)
following the exact `tv_engineering_department_ritual_on_pre_winning_war` /
`_on_ending_war` pattern already proven in
src/in_game/common/on_action/tv_engineering_department_on_action.txt, gating
the opening event (1686) the same way the old engine's `gate_trigger` gated
the treaty_clause_register row set's opening stage.

Fixed incident (kept unchanged from the previous implementation, still live):
the gate previously validated on *any* war ending while root held Granada, win
or lose -- see `build_on_action_body` below for the `scope:winner = { this =
root }` fix and its verification evidence.

Event IDs 1686-1693 (the same 8 IDs previously allocated to this wonder) are
reused for the new mechanic: 1686 opening, 1687-1691 one event per inherited
office (treasury/garrison/chancery/waterworks/endowment), 1692 the Reckoning
(computes the dominant path from the 5 disposition choices and applies an
immediate one-time consequence), 1693 the final resolution (grants the
path-branched permanent reward). No new event IDs were needed.
"""

T = "\t"
DASH = "-" * 46

WONDER_ID = 106
WONDER_KEY = "unique_alhambra"
NAME_SLUG = "alhambra"
RUNTIME_PREFIX = "tv_wonder_alhambra"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_alhambra_cropped.dds"
LOCATION = "granada"

GATE_TRIGGER = "tv_wonder_alhambra_war_validated_trigger"
SITE_CONTROL_TRIGGER = f"{RUNTIME_PREFIX}_site_control_trigger"
ACTIVE_TRIGGER = f"{RUNTIME_PREFIX}_active_trigger"

# Disposition codes, persisted per office on tv_wonder_alhambra_holding_<key>_disposition.
DISPOSITION_PRESERVE = 1
DISPOSITION_REPURPOSE = 2
DISPOSITION_DISMANTLE = 3

# The five inherited Nasrid palace-city offices, in the order the treaty court
# processes them. Each holding gets its own event (1687-1691) and its own
# three named disposition effects. `extra` lines are one-time, verified EU5
# effect calls (add_prestige / change_gold_effect / a location-scoped
# change_prosperity) appended after the shared disposition bookkeeping; they
# are deliberately differentiated per holding so no two offices resolve
# identically.
HOLDINGS = [
    {
        "key": "treasury",
        "event_id": 1687,
        "loc_stub": "TREASURY",
        "preserve_extra": ["add_prestige = 1"],
        "repurpose_extra": ["change_gold_effect = { scale = -1 }"],
        "dismantle_extra": ["change_gold_effect = { scale = 2 }", "add_prestige = -1"],
    },
    {
        "key": "garrison",
        "event_id": 1688,
        "loc_stub": "GARRISON",
        "preserve_extra": ["add_prestige = 1"],
        "repurpose_extra": ["change_gold_effect = { scale = -1 }"],
        "dismantle_extra": ["change_gold_effect = { scale = 1 }", "add_prestige = -1"],
    },
    {
        "key": "chancery",
        "event_id": 1689,
        "loc_stub": "CHANCERY",
        "preserve_extra": ["add_prestige = 1"],
        "repurpose_extra": ["change_gold_effect = { scale = -1 }"],
        # Seizing the chancery's own treaty archive is a symbolic/prestige
        # extraction, not a financial one -- deliberately no gold delta here.
        "dismantle_extra": ["add_prestige = 1"],
    },
    {
        "key": "waterworks",
        "event_id": 1690,
        "loc_stub": "WATERWORKS",
        "preserve_extra": ["add_prestige = 1", "location:granada = { change_prosperity = 0.05 }"],
        "repurpose_extra": ["change_gold_effect = { scale = -1 }"],
        "dismantle_extra": ["change_gold_effect = { scale = 1 }", "location:granada = { change_prosperity = -0.05 }"],
    },
    {
        "key": "endowment",
        "event_id": 1691,
        "loc_stub": "ENDOWMENT",
        "preserve_extra": ["add_prestige = 2"],
        "repurpose_extra": ["change_gold_effect = { scale = -1 }"],
        "dismantle_extra": ["change_gold_effect = { scale = 1 }", "add_prestige = -2"],
    },
]

RECKONING_EVENT_ID = 1692
RESOLUTION_EVENT_ID = 1693
OPENING_EVENT_ID = 1686

WONDER = {
    "wonder_id": WONDER_ID,
    "wonder_key": WONDER_KEY,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "location": LOCATION,
    "modifier_bundles": {
        "tv_wonder_alhambra_concord_reward_modifier": {"monthly_prestige": 0.15, "diplomatic_reputation": 2},
        "tv_wonder_alhambra_administration_reward_modifier": {"monthly_prestige": 0.08, "global_build_buildings_efficiency": 0.1},
        "tv_wonder_alhambra_extraction_reward_modifier": {"monthly_prestige": 0.05, "diplomatic_reputation": -1},
        "tv_wonder_alhambra_palace_concord_location_modifier": {"local_unrest": -0.05},
        "tv_wonder_alhambra_palace_administration_location_modifier": {"local_build_buildings_efficiency": 0.1},
        "tv_wonder_alhambra_palace_extraction_location_modifier": {"local_unrest": 0.05},
    },
}


# ---------------------------------------------------------------------------
# Triggers
# ---------------------------------------------------------------------------

def _append_extra_triggers(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {GATE_TRIGGER} {DASH}")
    lines.append(f"{GATE_TRIGGER} = {{")
    lines.append(f"{T}has_variable = tv_wonder_alhambra_war_validation")
    lines.append(f"{T}var:tv_wonder_alhambra_war_validation ?= 1")
    lines.append("}")


def append_triggers(lines: list[str]) -> None:
    lines.append(f"# -- {SITE_CONTROL_TRIGGER} {DASH}")
    lines.append(f"{SITE_CONTROL_TRIGGER} = {{")
    lines.append(f"{T}owns = location:{LOCATION}")
    lines.append("}")
    lines.append("")
    lines.append(f"# -- {ACTIVE_TRIGGER} {DASH}")
    lines.append(f"{ACTIVE_TRIGGER} = {{")
    lines.append(f"{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}var:tv_wonder_locked ?= {WONDER_ID}")
    lines.append(f"{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append(f"{T}has_variable = tv_wonder_alhambra_office_step")
    lines.append(f"{T}NOT = {{ has_variable = tv_wonder_alhambra_ritual_completed }}")
    lines.append("}")
    _append_extra_triggers(lines)


# ---------------------------------------------------------------------------
# Effects
# ---------------------------------------------------------------------------

def _disposition_effect_lines(holding_key: str, choice_name: str, disposition_value: int, score_var: str, extra: list[str]) -> list[str]:
    effect_name = f"tv_wonder_alhambra_{holding_key}_{choice_name}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    lines.append(f"{T}set_variable = {{ name = tv_wonder_alhambra_holding_{holding_key}_disposition value = {disposition_value} }}")
    lines.append(f"{T}change_variable = {{ name = tv_wonder_alhambra_{score_var} add = 1 }}")
    for extra_line in extra:
        lines.append(f"{T}{extra_line}")
    lines.append(f"{T}tv_wonder_alhambra_advance_office_step_effect = yes")
    lines.append("}")
    lines.append("")
    return lines


def append_effects(lines: list[str]) -> None:
    lines.append(f"# -- tv_wonder_alhambra_ritual_start_effect {DASH}")
    lines.append("tv_wonder_alhambra_ritual_start_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_alhambra_office_step value = 0 }}")
    lines.append(f"{T}remove_variable = tv_wonder_alhambra_pending_event")
    for holding in HOLDINGS:
        lines.append(f"{T}remove_variable = tv_wonder_alhambra_holding_{holding['key']}_disposition")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_alhambra_legitimacy_score value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_alhambra_efficiency_score value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_alhambra_extraction_score value = 0 }}")
    lines.append(f"{T}remove_variable = tv_wonder_alhambra_dominant_path")
    lines.append(f"{T}remove_variable = tv_wonder_alhambra_ritual_completed")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- tv_wonder_alhambra_advance_office_step_effect {DASH}")
    lines.append("tv_wonder_alhambra_advance_office_step_effect = {")
    lines.append(f"{T}change_variable = {{ name = tv_wonder_alhambra_office_step add = 1 }}")
    lines.append(f"{T}remove_variable = tv_wonder_alhambra_pending_event")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- tv_wonder_alhambra_fire_office_event_effect {DASH}")
    lines.append("tv_wonder_alhambra_fire_office_event_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_office_step ?= 0  {GATE_TRIGGER} = yes }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_pending_event value = 0 }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{OPENING_EVENT_ID} days = 1 }}")
    lines.append(f"{T}}}")
    for holding in HOLDINGS:
        step = HOLDINGS.index(holding) + 1
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_office_step ?= {step} }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_pending_event value = {step} }}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{holding['event_id']} days = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_office_step ?= {len(HOLDINGS) + 1} }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_pending_event value = {len(HOLDINGS) + 1} }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{RECKONING_EVENT_ID} days = 1 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_office_step ?= {len(HOLDINGS) + 2} }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_pending_event value = {len(HOLDINGS) + 2} }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{RESOLUTION_EVENT_ID} days = 1 }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- tv_wonder_alhambra_ritual_monthly_progress_effect {DASH}")
    lines.append("tv_wonder_alhambra_ritual_monthly_progress_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{ACTIVE_TRIGGER} = yes")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = tv_wonder_alhambra_pending_event }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_alhambra_fire_office_event_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    for holding in HOLDINGS:
        lines.extend(
            _disposition_effect_lines(holding["key"], "preserve", DISPOSITION_PRESERVE, "legitimacy_score", holding["preserve_extra"])
        )
        lines.extend(
            _disposition_effect_lines(holding["key"], "repurpose", DISPOSITION_REPURPOSE, "efficiency_score", holding["repurpose_extra"])
        )
        lines.extend(
            _disposition_effect_lines(holding["key"], "dismantle", DISPOSITION_DISMANTLE, "extraction_score", holding["dismantle_extra"])
        )

    lines.append(f"# -- tv_wonder_alhambra_apply_reckoning_effect {DASH}")
    lines.append("tv_wonder_alhambra_apply_reckoning_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}var:tv_wonder_alhambra_legitimacy_score >= var:tv_wonder_alhambra_efficiency_score")
    lines.append(f"{T}{T}{T}var:tv_wonder_alhambra_legitimacy_score >= var:tv_wonder_alhambra_extraction_score")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_dominant_path value = 1 }}")
    lines.append(f"{T}{T}add_prestige = 5")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_efficiency_score >= var:tv_wonder_alhambra_extraction_score }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_dominant_path value = 2 }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_alhambra_dominant_path value = 3 }}")
    lines.append(f"{T}{T}add_prestige = -3")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_alhambra_advance_office_step_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- tv_wonder_alhambra_grant_final_reward_effect {DASH}")
    lines.append("tv_wonder_alhambra_grant_final_reward_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_dominant_path ?= 1 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = tv_wonder_alhambra_concord_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}location:{LOCATION} = {{")
    lines.append(f"{T}{T}{T}add_location_modifier = {{ modifier = tv_wonder_alhambra_palace_concord_location_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}add_prestige = 15")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_alhambra_dominant_path ?= 2 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = tv_wonder_alhambra_administration_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}location:{LOCATION} = {{")
    lines.append(f"{T}{T}{T}add_location_modifier = {{ modifier = tv_wonder_alhambra_palace_administration_location_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}add_prestige = 8")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = tv_wonder_alhambra_extraction_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}location:{LOCATION} = {{")
    lines.append(f"{T}{T}{T}add_location_modifier = {{ modifier = tv_wonder_alhambra_palace_extraction_location_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}add_prestige = 3")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 2 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_alhambra_ritual_completed value = 1 }}")
    lines.append(f"{T}tv_wonder_alhambra_advance_office_step_effect = yes")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")
    lines.append("")


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

EVENTS_TEXT = {
    1686: {
        "title": {"english": "The Palace Changes Hands", "simp_chinese": "王宫易主"},
        "desc": {
            "english": (
                "Granada has fallen, and the war that decided it is won. The Alhambra's treasury, "
                "garrison, chancery, water administration, and religious endowments must now pass "
                "from the Nasrid order to the new sovereign, office by office."
            ),
            "simp_chinese": (
                "格拉纳达已经陷落，决定其命运的战争已经胜利。阿尔罕布拉宫的国库、卫戍军、书记厅、"
                "水务衙署与宗教基金，如今必须逐一从纳斯里德王朝移交给新的君主。"
            ),
        },
        "options": {
            "a": {"english": "Take up the inheritance.", "simp_chinese": "接管这份遗产。"},
        },
    },
    1687: {
        "title": {"english": "The Treasury Ledgers", "simp_chinese": "国库账册"},
        "desc": {
            "english": (
                "The Nasrid treasury office holds the tax rolls, tribute records, and coin reserves "
                "of the emirate. Its fate will shape how the new order is remembered."
            ),
            "simp_chinese": (
                "纳斯里德王朝的国库衙署保管着埃米尔国的税册、贡赋记录与现钱储备。它的命运，将决定"
                "新秩序在人们记忆中的模样。"
            ),
        },
        "options": {
            "a": {"english": "Keep the treasury officials at their posts.", "simp_chinese": "让国库官员留任原职。"},
            "b": {"english": "Retrain the office for the new administration.", "simp_chinese": "改编该衙署以服务新政。"},
            "c": {"english": "Seize the reserves and dismiss the officials.", "simp_chinese": "没收储备并遣散官员。"},
        },
    },
    1688: {
        "title": {"english": "The Alcazaba Garrison", "simp_chinese": "城堡卫戍军"},
        "desc": {
            "english": (
                "The Alcazaba's garrison, the palace's old defenders, awaits word on whether it will "
                "serve, be reformed, or be disbanded outright."
            ),
            "simp_chinese": (
                "阿尔卡萨瓦城堡的卫戍军，昔日宫殿的守卫者，正等候消息：他们将被留用、改编，还是"
                "彻底解散。"
            ),
        },
        "options": {
            "a": {"english": "Take the garrison into service.", "simp_chinese": "将卫戍军收编为己用。"},
            "b": {"english": "Reform the garrison under new officers.", "simp_chinese": "由新任军官改编该卫戍军。"},
            "c": {"english": "Disband the garrison and sell its arms.", "simp_chinese": "解散卫戍军并出售其军械。"},
        },
    },
    1689: {
        "title": {"english": "The Scribal Chancery", "simp_chinese": "书记厅"},
        "desc": {
            "english": (
                "The chancery's translators and notaries drafted the very terms of capitulation. "
                "Their pens, and their loyalties, are now in question."
            ),
            "simp_chinese": (
                "书记厅的译员与公证人曾亲手起草了投降条款本身。他们的笔，以及他们的忠诚，如今都"
                "悬而未决。"
            ),
        },
        "options": {
            "a": {"english": "Retain the scribes in their offices.", "simp_chinese": "让书记留任原职。"},
            "b": {"english": "Fold the chancery into your own administration.", "simp_chinese": "将书记厅并入自己的行政体系。"},
            "c": {"english": "Disperse the scribes and claim their archive.", "simp_chinese": "遣散书记并夺取其档案。"},
        },
    },
    1690: {
        "title": {"english": "The Acequia Administration", "simp_chinese": "灌渠衙署"},
        "desc": {
            "english": (
                "The acequia courts govern the channels that carry water from the Sierra Nevada into "
                "the palace gardens and the city below. Whoever controls them controls Granada's "
                "lifeblood."
            ),
            "simp_chinese": (
                "灌渠法庭管理着将内华达山脉的水源引入宫廷花园与山下城市的渠道。掌控它们，便掌控了"
                "格拉纳达的命脉。"
            ),
        },
        "options": {
            "a": {"english": "Leave the water courts to their own judges.", "simp_chinese": "让水法庭继续由原有法官管理。"},
            "b": {"english": "Reorganize the water rights under new officials.", "simp_chinese": "由新任官员重新编排水权。"},
            "c": {"english": "Strip the channels' revenues and sell the water rights.", "simp_chinese": "榨取渠道收益并出售水权。"},
        },
    },
    1691: {
        "title": {"english": "The Religious Endowments", "simp_chinese": "宗教基金"},
        "desc": {
            "english": (
                "The waqf endowments fund mosques, hospices, and charitable foundations across the "
                "city, including the palace's own mosque. Their disposition will be watched closely, "
                "by the faithful and by foreign courts alike."
            ),
            "simp_chinese": (
                "瓦克夫宗教基金资助着全城的清真寺、济贫院与慈善机构，也包括宫殿本身的清真寺。它们"
                "的处置，将受到信众与外邦宫廷的密切关注。"
            ),
        },
        "options": {
            "a": {"english": "Leave the endowments to their founders' intent.", "simp_chinese": "让基金依创设者的本意继续运作。"},
            "b": {"english": "Redirect the endowments to the new order's foundations.", "simp_chinese": "将基金转向新秩序的机构。"},
            "c": {"english": "Liquidate the endowments and claim their revenues.", "simp_chinese": "清算基金并占有其收益。"},
        },
    },
    1692: {
        "title": {"english": "The Reckoning Of Governance", "simp_chinese": "治理的清算"},
        "desc": {
            "english": (
                "Five offices have passed from one order to another. Whether Granada remembers this "
                "as a concord, an efficient administration, or a plunder now depends on the balance "
                "of what was kept, reformed, and seized."
            ),
            "simp_chinese": (
                "五个衙署已经完成了从旧秩序到新秩序的移交。格拉纳达将把这段历史记作和睦、良治，"
                "还是掠夺，取决于保留、改编与没收之间的平衡。"
            ),
        },
        "options": {
            "a": {"english": "Read the reckoning.", "simp_chinese": "细读这份清算。"},
        },
    },
    1693: {
        "title": {"english": "The Alhambra Endures", "simp_chinese": "阿尔罕布拉宫长存"},
        "desc": {
            "english": "The palace's fate is now settled.",
            "simp_chinese": "王宫的命运如今已经确定。",
        },
        "triggered_desc": {
            "concord": {
                "english": (
                    "Mercy has governed the transfer. The treasury, garrison, chancery, waterworks, "
                    "and endowments alike were kept intact wherever possible, and foreign courts "
                    "speak of the Alhambra as proof that conquest need not consume what it wins."
                ),
                "simp_chinese": (
                    "仁慈主导了这场移交。国库、卫戍军、书记厅、灌渠与宗教基金，尽可能地被完整保留，"
                    "外邦宫廷都称阿尔罕布拉宫证明了征服未必要吞噬它所赢得的一切。"
                ),
            },
            "administration": {
                "english": (
                    "Reform has governed the transfer. Office after office was reorganized under the "
                    "new order, and the Alhambra now stands as a working palace of efficient, if "
                    "unsentimental, governance."
                ),
                "simp_chinese": (
                    "改革主导了这场移交。一个又一个衙署被纳入新秩序重组，阿尔罕布拉宫如今成为一座"
                    "运作良好、却不带多少温情的治理宫殿。"
                ),
            },
            "extraction": {
                "english": (
                    "Extraction has governed the transfer. The palace's offices were stripped of what "
                    "they held, and the Alhambra now stands garrisoned rather than governed, its "
                    "treasures gone to fund the crown that took it."
                ),
                "simp_chinese": (
                    "掠夺主导了这场移交。宫中各衙署被榨取一空，阿尔罕布拉宫如今更像是一座驻防要塞，"
                    "而非治理中心，其财富已流入夺取它的王室。"
                ),
            },
        },
        "options": {
            "a": {"english": "Confirm the Alhambra's new order.", "simp_chinese": "确认阿尔罕布拉宫的新秩序。"},
        },
    },
}


def _render_option(event_id: int, letter: str, effect_lines: list[str]) -> list[str]:
    lines = [f"{T}option = {{", f"{T}{T}name = tv_engineering_department.{event_id}.{letter}"]
    for effect_line in effect_lines:
        lines.append(f"{T}{T}{effect_line}")
    lines.append(f"{T}}}")
    return lines


def _render_simple_event(event_id: int, outcome: str, option_effects: dict[str, list[str]]) -> list[str]:
    lines = [
        f"# -- tv_engineering_department.{event_id} {DASH}",
        f"tv_engineering_department.{event_id} = {{",
        f"{T}type = country_event",
        f"{T}title = tv_engineering_department.{event_id}.t",
        f"{T}desc = tv_engineering_department.{event_id}.d",
        f'{T}image = "{IMAGE}"',
        f"{T}outcome = {outcome}",
        "",
    ]
    letters = sorted(option_effects.keys())
    for index, letter in enumerate(letters):
        if index:
            lines.append("")
        lines.extend(_render_option(event_id, letter, option_effects[letter]))
    lines.append("}")
    return lines


def _render_resolution_event() -> list[str]:
    event_id = RESOLUTION_EVENT_ID
    lines = [
        f"# -- tv_engineering_department.{event_id} {DASH}",
        f"tv_engineering_department.{event_id} = {{",
        f"{T}type = country_event",
        f"{T}title = tv_engineering_department.{event_id}.t",
        f"{T}desc = tv_engineering_department.{event_id}.d",
        f"{T}triggered_desc = {{",
        f"{T}{T}trigger = {{ var:tv_wonder_alhambra_dominant_path ?= 1 }}",
        f"{T}{T}desc = tv_engineering_department.{event_id}.concord.d",
        f"{T}}}",
        f"{T}triggered_desc = {{",
        f"{T}{T}trigger = {{ var:tv_wonder_alhambra_dominant_path ?= 2 }}",
        f"{T}{T}desc = tv_engineering_department.{event_id}.administration.d",
        f"{T}}}",
        f"{T}triggered_desc = {{",
        f"{T}{T}trigger = {{ var:tv_wonder_alhambra_dominant_path ?= 3 }}",
        f"{T}{T}desc = tv_engineering_department.{event_id}.extraction.d",
        f"{T}}}",
        f'{T}image = "{IMAGE}"',
        f"{T}outcome = positive",
        "",
    ]
    lines.extend(_render_option(event_id, "a", ["tv_wonder_alhambra_grant_final_reward_effect = yes"]))
    lines.append("}")
    return lines


def build_events_body() -> list[str]:
    lines: list[str] = []

    lines.extend(_render_simple_event(OPENING_EVENT_ID, "neutral", {"a": ["tv_wonder_alhambra_advance_office_step_effect = yes"]}))
    lines.append("")

    for holding in HOLDINGS:
        option_effects = {
            "a": [f"tv_wonder_alhambra_{holding['key']}_preserve_effect = yes"],
            "b": [f"tv_wonder_alhambra_{holding['key']}_repurpose_effect = yes"],
            "c": [f"tv_wonder_alhambra_{holding['key']}_dismantle_effect = yes"],
        }
        lines.extend(_render_simple_event(holding["event_id"], "neutral", option_effects))
        lines.append("")

    lines.extend(_render_simple_event(RECKONING_EVENT_ID, "neutral", {"a": ["tv_wonder_alhambra_apply_reckoning_effect = yes"]}))
    lines.append("")

    lines.extend(_render_resolution_event())
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Localization
# ---------------------------------------------------------------------------

GUI_LOC = {
    "TV_ENGINEERING_ALHAMBRA_INHERITANCE_TITLE": {"english": "The Alhambra Inheritance", "simp_chinese": "阿尔罕布拉宫的遗产"},
    "TV_ENGINEERING_ALHAMBRA_HOLDING_TREASURY": {"english": "Treasury Office", "simp_chinese": "国库衙署"},
    "TV_ENGINEERING_ALHAMBRA_HOLDING_GARRISON": {"english": "Alcazaba Garrison", "simp_chinese": "城堡卫戍军"},
    "TV_ENGINEERING_ALHAMBRA_HOLDING_CHANCERY": {"english": "Scribal Chancery", "simp_chinese": "书记厅"},
    "TV_ENGINEERING_ALHAMBRA_HOLDING_WATERWORKS": {"english": "Acequia Administration", "simp_chinese": "灌渠衙署"},
    "TV_ENGINEERING_ALHAMBRA_HOLDING_ENDOWMENT": {"english": "Religious Endowments", "simp_chinese": "宗教基金"},
    "TV_ENGINEERING_ALHAMBRA_DISPOSITION_PENDING": {"english": "Undecided", "simp_chinese": "尚未决定"},
    "TV_ENGINEERING_ALHAMBRA_DISPOSITION_PRESERVE": {"english": "Preserved", "simp_chinese": "已保留"},
    "TV_ENGINEERING_ALHAMBRA_DISPOSITION_REPURPOSE": {"english": "Repurposed", "simp_chinese": "已改编"},
    "TV_ENGINEERING_ALHAMBRA_DISPOSITION_DISMANTLE": {"english": "Dismantled", "simp_chinese": "已没收"},
    "TV_ENGINEERING_ALHAMBRA_PATH_CONCORD": {"english": "Path Of Concord", "simp_chinese": "和睦之路"},
    "TV_ENGINEERING_ALHAMBRA_PATH_ADMINISTRATION": {"english": "Path Of Administration", "simp_chinese": "良治之路"},
    "TV_ENGINEERING_ALHAMBRA_PATH_EXTRACTION": {"english": "Path Of Extraction", "simp_chinese": "掠夺之路"},
    "TV_ENGINEERING_ALHAMBRA_RECKONING_PENDING": {"english": "Awaiting the reckoning", "simp_chinese": "等候清算"},
}

MODIFIER_LOC = {
    "tv_wonder_alhambra_concord_reward_modifier": {"english": "Alhambra Concord", "simp_chinese": "阿尔罕布拉的和睦"},
    "tv_wonder_alhambra_administration_reward_modifier": {"english": "Alhambra Administration", "simp_chinese": "阿尔罕布拉的良治"},
    "tv_wonder_alhambra_extraction_reward_modifier": {"english": "Alhambra Extraction", "simp_chinese": "阿尔罕布拉的掠夺"},
    "tv_wonder_alhambra_palace_concord_location_modifier": {"english": "Palace Of Concord", "simp_chinese": "和睦之宫"},
    "tv_wonder_alhambra_palace_administration_location_modifier": {"english": "Palace Of Administration", "simp_chinese": "良治之宫"},
    "tv_wonder_alhambra_palace_extraction_location_modifier": {"english": "Palace Of Extraction", "simp_chinese": "掠夺之宫"},
}


def build_localization(language: str) -> list[str]:
    lines: list[str] = []
    for event_id in sorted(EVENTS_TEXT.keys()):
        text = EVENTS_TEXT[event_id]
        lines.append(f' tv_engineering_department.{event_id}.t:0 "{text["title"][language]}"')
        lines.append(f' tv_engineering_department.{event_id}.d:0 "{text["desc"][language]}"')
        for path_key, path_text in text.get("triggered_desc", {}).items():
            lines.append(f' tv_engineering_department.{event_id}.{path_key}.d:0 "{path_text[language]}"')
        for letter, option_text in text["options"].items():
            lines.append(f' tv_engineering_department.{event_id}.{letter}:0 "{option_text[language]}"')
    for key, value in GUI_LOC.items():
        lines.append(f' {key}:0 "{value[language]}"')
    for modifier_name, value in MODIFIER_LOC.items():
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{value[language]}"')
    return lines


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

CARD_WIDTH = 462
ROW_HEIGHT = 26

GUI_HOLDING_LOC_KEYS = {
    "treasury": "TV_ENGINEERING_ALHAMBRA_HOLDING_TREASURY",
    "garrison": "TV_ENGINEERING_ALHAMBRA_HOLDING_GARRISON",
    "chancery": "TV_ENGINEERING_ALHAMBRA_HOLDING_CHANCERY",
    "waterworks": "TV_ENGINEERING_ALHAMBRA_HOLDING_WATERWORKS",
    "endowment": "TV_ENGINEERING_ALHAMBRA_HOLDING_ENDOWMENT",
}


def _alhambra_locked_expr() -> str:
    return f"And({player_var('tv_wonder_locked')}.IsSet, {eq('tv_wonder_locked', WONDER_ID)})"


def _alhambra_visible_expr() -> str:
    return fold_bool("And", [active_ritual_visible(), _alhambra_locked_expr()])


def _disposition_visible(holding_key: str, code: int) -> str:
    var = f"tv_wonder_alhambra_holding_{holding_key}_disposition"
    return f"And({var_is_set(var)}, {eq(var, code)})"


def _holding_row(holding_key: str, indent: int) -> list[str]:
    prefix = T * indent
    label_key = GUI_HOLDING_LOC_KEYS[holding_key]
    preserved = _disposition_visible(holding_key, DISPOSITION_PRESERVE)
    repurposed = _disposition_visible(holding_key, DISPOSITION_REPURPOSE)
    dismantled = _disposition_visible(holding_key, DISPOSITION_DISMANTLE)
    pending = f"Not({var_is_set(f'tv_wonder_alhambra_holding_{holding_key}_disposition')})"
    return [
        f"{prefix}widget = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {CARD_WIDTH - 16} {ROW_HEIGHT} }}",
        f"{prefix}{T}alwaystransparent = yes",
        f"{prefix}{T}widget = {{",
        f'{prefix}{T}{T}visible = "[{preserved}]"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}alwaystransparent = yes",
        f"{prefix}{T}{T}background = {{ using = color_market_green_texture alpha = 0.22 }}",
        f"{prefix}{T}}}",
        f"{prefix}{T}widget = {{",
        f'{prefix}{T}{T}visible = "[{repurposed}]"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}alwaystransparent = yes",
        f"{prefix}{T}{T}background = {{ using = color_yellow_texture alpha = 0.18 }}",
        f"{prefix}{T}}}",
        f"{prefix}{T}widget = {{",
        f'{prefix}{T}{T}visible = "[{dismantled}]"',
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}alwaystransparent = yes",
        f"{prefix}{T}{T}background = {{ using = color_mid_red_texture alpha = 0.22 }}",
        f"{prefix}{T}}}",
        f"{prefix}{T}hbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}margin = {{ 6 3 }}",
        f"{prefix}{T}{T}spacing = 4",
        f'{prefix}{T}{T}text_single = {{ size = {{ 220 22 }} text = "{label_key}" fontsize = 13 align = nobaseline|left }}',
        f"{prefix}{T}{T}expand = {{}}",
        f'{prefix}{T}{T}text_single = {{ visible = "[{pending}]" size = {{ 140 22 }} text = "TV_ENGINEERING_ALHAMBRA_DISPOSITION_PENDING" fontsize = 13 align = nobaseline|right }}',
        f'{prefix}{T}{T}text_single = {{ visible = "[{preserved}]" size = {{ 140 22 }} text = "TV_ENGINEERING_ALHAMBRA_DISPOSITION_PRESERVE" fontsize = 13 align = nobaseline|right }}',
        f'{prefix}{T}{T}text_single = {{ visible = "[{repurposed}]" size = {{ 140 22 }} text = "TV_ENGINEERING_ALHAMBRA_DISPOSITION_REPURPOSE" fontsize = 13 align = nobaseline|right }}',
        f'{prefix}{T}{T}text_single = {{ visible = "[{dismantled}]" size = {{ 140 22 }} text = "TV_ENGINEERING_ALHAMBRA_DISPOSITION_DISMANTLE" fontsize = 13 align = nobaseline|right }}',
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def _reckoning_row(indent: int) -> list[str]:
    prefix = T * indent
    path_var = "tv_wonder_alhambra_dominant_path"
    path_set = var_is_set(path_var)
    concord = f"And({path_set}, {eq(path_var, 1)})"
    administration = f"And({path_set}, {eq(path_var, 2)})"
    extraction = f"And({path_set}, {eq(path_var, 3)})"
    return [
        f"{prefix}widget = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {CARD_WIDTH - 16} {ROW_HEIGHT} }}",
        f"{prefix}{T}alwaystransparent = yes",
        f"{prefix}{T}hbox = {{",
        f"{prefix}{T}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}{T}size = {{ 100% 100% }}",
        f"{prefix}{T}{T}margin = {{ 6 3 }}",
        f'{prefix}{T}{T}text_single = {{ visible = "[Not({path_set})]" size = {{ 360 22 }} text = "TV_ENGINEERING_ALHAMBRA_RECKONING_PENDING" fontsize = 13 align = nobaseline|left }}',
        f'{prefix}{T}{T}text_single = {{ visible = "[{concord}]" size = {{ 360 22 }} text = "TV_ENGINEERING_ALHAMBRA_PATH_CONCORD" fontsize = 13 align = nobaseline|left }}',
        f'{prefix}{T}{T}text_single = {{ visible = "[{administration}]" size = {{ 360 22 }} text = "TV_ENGINEERING_ALHAMBRA_PATH_ADMINISTRATION" fontsize = 13 align = nobaseline|left }}',
        f'{prefix}{T}{T}text_single = {{ visible = "[{extraction}]" size = {{ 360 22 }} text = "TV_ENGINEERING_ALHAMBRA_PATH_EXTRACTION" fontsize = 13 align = nobaseline|left }}',
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    globals().update(helpers)
    prefix = T * indent
    card_height = 26 + ROW_HEIGHT * (len(HOLDINGS) + 1)
    lines.append(f"{prefix}widget = {{")
    lines.append(f'{prefix}{T}visible = "[{_alhambra_visible_expr()}]"')
    lines.append(f"{prefix}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}size = {{ {CARD_WIDTH} {card_height} }}")
    lines.append(f"{prefix}{T}using = bg_text_mask_container_dark_blue")
    lines.append("")
    lines.append(f"{prefix}{T}vbox = {{")
    lines.append(f"{prefix}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}{T}margin = {{ 8 8 }}")
    lines.append(f"{prefix}{T}{T}spacing = 2")
    lines.append(f'{prefix}{T}{T}text_multi = {{ max_width = {CARD_WIDTH - 16} autoresize = yes text = "TV_ENGINEERING_ALHAMBRA_INHERITANCE_TITLE" align = nobaseline|left }}')
    for holding in HOLDINGS:
        lines.extend(_holding_row(holding["key"], indent + 2))
    lines.extend(_reckoning_row(indent + 2))
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


# ---------------------------------------------------------------------------
# War-validation on_action bridge (kept unchanged; see module docstring).
# ---------------------------------------------------------------------------

def build_on_action_body() -> list[str]:
    """Alhambra-only war-validation bridge.

    Fixed incident: this previously set `tv_wonder_alhambra_war_validation`
    whenever *any* war concluded while root held Granada, win or lose, which
    let a lost war "validate" a capitulation treaty. `on_pre_winning_war` and
    `on_ending_war` both expose `scope:winner`/`scope:loser` alongside `root`
    (root fires for both participants -- see
    reference_game_files/game/in_game/common/on_action/_hardcoded.txt:1518-1576),
    and `this = root` is the verified scope-equality idiom for comparing a
    saved scope back to root (same file, e.g. line 3292 `leader_country ?= { this = root }`;
    also used throughout src/in_game/common/generic_actions/tv_arts_exhibition_actions.txt).
    The gate now requires root to actually be the war's winner, not merely a
    participant in a war that happened to end."""
    trigger_lines = [
        f"{T}has_variable = tv_wonder_locked",
        f"{T}var:tv_wonder_locked ?= {WONDER_ID}",
        f"{T}has_variable = tv_wonder_ritual_in_progress",
        f"{T}{SITE_CONTROL_TRIGGER} = yes",
        f"{T}scope:winner = {{ this = root }}",
    ]
    lines: list[str] = []
    for on_action_name in (
        "tv_wonder_unique_alhambra_ritual_on_pre_winning_war",
        "tv_wonder_unique_alhambra_ritual_on_ending_war",
    ):
        lines.append(f"{on_action_name} = {{")
        lines.append(f"{T}trigger = {{")
        lines.extend(trigger_lines)
        lines.append(f"{T}}}")
        lines.append(f"{T}effect = {{")
        lines.append(f"{T}{T}hidden_effect = {{")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_alhambra_war_validation value = 1 }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")
    return lines
