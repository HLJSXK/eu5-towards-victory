# GUI Risk Card

Load this card before editing `.gui` files or GUI-bound localization expressions.

## Required Checks

1. Verify datacontext assumptions.
   `action_button_diamond` evaluates parameters in its own action context. Do not rely on
   parent `datacontext`; pass full chains such as `Scope.GetCharacter`.

2. Use GUI-native variable guards.
   Script triggers such as `has_variable` do not exist in GUI expressions. Use
   `MakeScope.GetVariable('name').IsSet` before reading optional variables.

3. Use typed comparison functions.
   GUI expressions do not support inline `>`, `>=`, or `==`. Use functions such as
   `GreaterThanOrEqualTo_CFixedPoint(...)` and `EqualTo_CFixedPoint(...)`.

4. Keep text layout bounded.
   Multiline text inside elastic `hbox`/`vbox` columns needs explicit width or `text_multi`
   with `max_width`; otherwise natural text width can resize the parent.
   The opposite failure is just as common and easier to miss: an `hbox`/`vbox` that sets an
   explicit `size = { W H }` alongside a fixed column (icon, portrait) plus an expanding
   `text_multi` must also declare `layoutpolicy_horizontal = expanding` on the container
   itself. Without it, the container ignores its own declared `size` and instead sizes off
   the sum of children's intrinsic minimums — a `text_multi` with no `minimumsize` has ~0
   intrinsic width — so the whole row silently collapses toward the fixed column's width and
   the text column renders at effectively 0 width (unselectable/unhoverable), with no error
   in the log. `max_width`/`autoresize` on the `text_multi` does not substitute for this
   container-level property; both are required together. See
   `docs/knowledge/anti_patterns.yaml` rule
   `hbox_explicit_size_without_layoutpolicy_horizontal_collapses_to_content_width`.

5. Verify blockoverride shape from vanilla.
   Some blockoverrides replace scalar properties, not widget containers. Read the template
   source before adding child widgets inside a blockoverride.

6. Distinguish game concept links from plain localization keys.
   In GUI-bound localized text, `[key|E]` requires `key` to be registered in
   `main_menu/common/game_concepts`. For ordinary building or action names, use
   `$key$` localization substitution.

7. Use localization helpers for database display names.
   Building-type names in localization should use `ShowBuildingTypeName('key')`
   or `ShowBuildingTypeNameWithNoTooltip('key')`. Do not use
   `GetBuilding('key').GetName`; it is not a valid localization data function.

8. Keep layout-only properties on layout containers.
   `ignoreinvisible` is valid on container-style layouts such as `hbox`/`vbox`,
   but a plain `widget`/`uberwidget` logs an unsupported-property error. For
   image wrappers, hide the wrapper with `visible = ...` and omit
   `ignoreinvisible`.

9. Pass typed objects to build-location selectors.
   `SelectLocationToBuildDefault` and related functions need a `BuildingType` object
   such as `BuildingItem.GetBuildingType`, not a literal building key string. If the
   panel has no typed building context, use a generic action with a location selector.

10. Keep localization substitutions out of `raw_text`.
   `raw_text` renders literal strings and dynamic expressions; it does not expand
   `$LOCALIZATION_KEY$`. Use `text = "KEY"` for static localized labels, and put
   inline icons such as `@trade!` in the localization value when needed.

11. Do not promote GUI variables into typed objects with invented accessors.
    `MakeScope.GetVariable('x')` does not expose `.GetGoods` or
    `.GetInternationalOrganization`. For goods, use a typed datamodel accessor
    such as `Trade.GetGoods`/`GoodsMarketEntry.GetGoods`, or static branches keyed
    by a numeric id. For IO panels, pass a typed InternationalOrganization object
    from an existing view/datamodel chain.

12. Keep tooltip-only widgets inside real tooltip contexts.
    `TooltipTextBlock` inherits `tooltip_text_block_template`, which reads
    `ExtraTooltipInfo.GetTintColor`. Use it only under `tooltipwidget` / 
    `ContextualTooltipType` / `AlertTooltipType` content. For always-visible panel
    text, use `text_single` / `text_multi` instead.

13. Give conditional image branches explicit bounds.
    When a wrapper contains mutually exclusive background-image widgets, do not
    rely on `layoutpolicy_expanding` alone. If the preview sits inside a plain
    `widget`/`button`, make that clickable wrapper fill its parent first, then
    give the image column fixed bounds and size each visible preview child with
    fixed pixels that match the content area. Otherwise the hbox can shrink to
    the image column's natural width, leaving text and image stacked at the
    parent's left edge.

14. Let tooltip rows grow with their visible content.
    If a tooltip row mixes `TooltipStringPairList`/`TooltipTextBlock` with a
    preview image, do not hard-code the row to a fixed height. Constrain width
    with `size = { W -1 }` or `minimumsize`, set the containing layout to size
    itself from its children, and keep `ignoreinvisible = yes` on the container
    so hidden wonder levels do not reserve space.
    This "size itself from its children" behavior (`set_parent_size_to_minimum = yes`
    on a `vbox`) has a sharp edge that bites specifically on WIDTH: it computes the
    vbox's size from the MINIMUM size each child reports, not from any
    `layoutpolicy_horizontal`/`size` set on the vbox or its own parent `widget`. A bare
    `text_multi` with only `max_width`/`autoresize`/`layoutpolicy_horizontal = expanding`
    (no `minimumsize` of its own) reports a 0 intrinsic width, so it silently zeroes out
    the whole chain — the vbox (and anything wrapping it) collapses to margin-only width,
    and the text renders unselectable at effectively 0 width, with no error in the log.
    Give every bare `text_multi`/leaf that sits inside a `set_parent_size_to_minimum`
    vbox its own `minimumsize = { W -1 }` matching its `max_width`, even though the row/
    container above it already looks correctly constrained — a correctly-sized ancestor
    does not help if the one leaf actually rendering content reports zero width. See
    `docs/knowledge/anti_patterns.yaml` rule
    `set_parent_size_to_minimum_vbox_needs_leaf_minimumsize_for_width`.

15. Match scripted-effect tooltip scopes to the GUI object passed in.
    `ShowScriptedEffectForScope(..., LocationView.GetLocation.MakeScope.Self)`
    runs the effect with the location as root. In that context, do not use
    `location.owner = { ... }`; the `location` prefix is parsed as an event
    target link and can spam scope-mismatch errors. Use `owner ?= { ... }` for
    country effects shown from a location-root tooltip.

16. Keep dynamic concept-link keys raw and registered.
    `SelectGameConcept` and `[...|E]` can use dynamic CString concept ids, but
    the value must already be a registered raw concept id. Do not feed them
    `GetFlagName` or variable-map flag values that can localize to display text.
    For generated routes, store a numeric id and build ids such as
    `tv_wonder_display_<id>`. Use `Localize(Concatenate('game_concept_', key))`
    only when intentionally rendering plain, non-clickable text.

17. Use EU5 image fit enums, not CSS names.
    Vanilla GUI uses `fittype` values such as `centercrop`, `fill`, `start`,
    and `end`. `contain` is not accepted and logs `Unknown fit type 'contain'`
    during GUI loading.

18. Do not treat `GetFlagName` as a raw key.
    A flag stored in a variable or variable map can render through localization
    in GUI, especially for game-concept-like ids. If a widget must build
    modifier names, localization keys, texture keys, or scripted-effect names,
    store a numeric id and generate static id branches, or use a typed object
    with a verified `GetKey` accessor.

19. Do not build raw DDS paths with `Concatenate` inside `texture`.
    Static `texture = "gfx/...dds"` paths are parsed by the GUI loader, but a
    runtime expression that returns a CString path does not behave like a texture
    handle. In the location-window test, `GetConceptTexture(Concatenate(...))`
    rendered while nested, suffix-only, and flat `Concatenate('gfx/...dds', '')`
    path expressions stayed blank without useful log errors. For arbitrary
    dynamic mod images, register image-only game concepts with matching
    `game_concept_*` and `game_concept_*_desc` localization, then route through
    `GetConceptTexture`, preferably with numeric ids such as
    `tv_wonder_display_image_<id>`.

20. Give dynamic `ShowModifierEffect` routes static definitions and script references.
    If GUI builds modifier ids with `Concatenate(...)`, such as
    `tv_wonder_display_<id>_level_<level>` or
    `tv_wonder_display_<id>_local_level_<level>`, generate matching static
    display modifiers, matching `STATIC_MODIFIER_NAME_<id>` localization in
    every supported language, and an unreachable script block with
    `if = { limit = { always = no } ... }` that applies every possible country
    or location display modifier through the correct `add_*_modifier` effect.
    Scripted-effect tooltip previews have the same database boundary:
    `add_country_modifier` must target a static country modifier, not a Country
    Auto modifier from `common/auto_modifiers`. For Engineering Department
    wonders, use static mirrors for GUI `ShowModifierEffect` display only; keep
    auto-driven country effects out of scripted grants and tooltip previews.

21. Keep progressbar offsets on a wrapper.
    `progressbar` does not handle `margin_top`; GUI loading logs an unsupported
    property error. If a bar needs vertical centering or offset inside an
    `hbox`/`vbox`, put a fixed-size `widget` in the layout and anchor the
    `progressbar` inside that wrapper.

22. Keep IO member-list filters on real item predicates.
    In `InternationalOrganizationsView.GetMemberItems`, the outer
    `MemberTypeItem` rows should use predicates such as `MemberTypeItem.IsAllMembers`.
    Do not compare `MemberTypeItem.GetName` to a special-status localization helper
    to find members; that can hide every item.

23. Compare row countries to IO leader countries with matching object shape.
    In an IO member country row, prefer `ObjectsEqual(Country.Self,
    InternationalOrganizationsView.GetInternationalOrganization.GetLeaderCountry.Self)`.
    Do not call `IsIOLeaderCountry(Country.Self)` from this GUI context; it has
    produced `FetchData failed` runtime errors.

24. Do not assume `UIAction` exists inside custom action buttons.
    Do not write direct `enabled = "[UIAction.IsEnabled]"` in a custom-panel
    button unless the surrounding datacontext is verified to expose `UIAction`.
    Conventional `action_button` / `action_button_diamond` widgets may still use
    their normal action templates when they define a real `left_action`.

25. Be wary of GUI hot reload after changing action widgets.
    A hot-reloaded panel can keep stale widget/action bindings and continue to
    report the old line's `FetchData failed` error. If an action-button error
    persists after reverting the expression, restart the game or fully reload the
    panel before treating the current source as the culprit.

26. Pass country action targets as script scopes.
    For custom row buttons that feed a generic action's `scope:target`, use a
    button-level `parameter = { parameter_value = "[Country.MakeScope]" }`.
    `Country.Self` is a GUI object shape for comparisons such as `ObjectsEqual`,
    not a reliable script scope for action effects. If `scope:target` is absent,
    guarded effects can no-op silently with no cost and no error.

27. Preserve existing panel structure.
    Do not collapse staged rows, per-target display branches, target-specific labels,
    or generated per-id GUI entries into generic fallback UI merely to make a data-list
    change smaller. Preserve the established player-facing shape, or extend the
    generator/data source and regenerate.

28. Cache scripted-trigger results for list/row filtering.
    GUI expressions cannot evaluate scripted triggers at all (rule 2 covers `has_variable`
    specifically; this generalizes to any scripted_trigger, such as an age-gate or
    `has_advance` eligibility check). If a widget needs to filter or show/hide rows based on
    trigger logic, mirror that trigger's result into a country variable via a scripted_effect,
    and refresh it from a real lifecycle point (join/founding effect plus the feature's existing
    monthly_country_pulse hook) — never from a GUI/tooltip read path. Bind the GUI `visible=`
    expression to the mirrored variable.

29. `TooltipTextBlock` does not shrink to match a row-sized `TooltipRequirementsList`/`text_single`.
    `TooltipTextBlock` (vanilla `main_menu_cooltip_types.gui`) wraps its text in a fixed
    `vbox { margin = { @tooltip_inner_margin @tooltip_inner_margin } }` (10px each side) around a
    `text_multi_template` textbox, with no exposed blockoverride for font size or row height.
    Setting `blockoverride "row_size"` / `blockoverride "field_text_format"` on a sibling
    `TooltipRequirementsList` (or a plain `text_single`) does not affect `TooltipTextBlock`, so a
    mutually-exclusive-visibility swap between the two (e.g. "has effect" vs "no effect" rows in
    the same slot) shows a visible height jump. When a fallback/empty-state line must match a
    sized row's height, use a plain `text_single` with the same `fontsize`/fixed `size` instead of
    `TooltipTextBlock`.

## Validation

Run `validate.py --changed --fix --ai-report`, then check the in-game error log after hover
testing the panel. GUI failures often appear only when the widget is rendered or hovered.

## Relevant Anti-Patterns

- `gui_list_filter_needs_cached_variable` [advisory]: GUI row/list visibility cannot bind to a
  scripted_trigger directly; mirror it into a country variable refreshed from a lifecycle hook.
- `hbox_explicit_size_without_layoutpolicy_horizontal_collapses_to_content_width` [advisory]: an
  hbox/vbox with an explicit `size` and mixed fixed/expanding children also needs
  `layoutpolicy_horizontal = expanding` on itself, or it collapses to children's intrinsic width.
