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

5. Verify blockoverride shape from vanilla.
   Some blockoverrides replace scalar properties, not widget containers. Read the template
   source before adding child widgets inside a blockoverride.

6. Distinguish game concept links from plain localization keys.
   In GUI-bound localized text, `[key|E]` requires `key` to be registered in
   `main_menu/common/game_concepts`. For ordinary building or action names, use
   `$key$` localization substitution.

7. Keep layout-only properties on layout containers.
   `ignoreinvisible` is valid on container-style layouts such as `hbox`/`vbox`,
   but a plain `widget`/`uberwidget` logs an unsupported-property error. For
   image wrappers, hide the wrapper with `visible = ...` and omit
   `ignoreinvisible`.

8. Pass typed objects to build-location selectors.
   `SelectLocationToBuildDefault` and related functions need a `BuildingType` object
   such as `BuildingItem.GetBuildingType`, not a literal building key string. If the
   panel has no typed building context, use a generic action with a location selector.

9. Keep localization substitutions out of `raw_text`.
   `raw_text` renders literal strings and dynamic expressions; it does not expand
   `$LOCALIZATION_KEY$`. Use `text = "KEY"` for static localized labels, and put
   inline icons such as `@trade!` in the localization value when needed.

10. Do not promote GUI variables into typed objects with invented accessors.
    `MakeScope.GetVariable('x')` does not expose `.GetGoods` or
    `.GetInternationalOrganization`. For goods, use a typed datamodel accessor
    such as `Trade.GetGoods`/`GoodsMarketEntry.GetGoods`, or static branches keyed
    by a numeric id. For IO panels, pass a typed InternationalOrganization object
    from an existing view/datamodel chain.

11. Keep tooltip-only widgets inside real tooltip contexts.
    `TooltipTextBlock` inherits `tooltip_text_block_template`, which reads
    `ExtraTooltipInfo.GetTintColor`. Use it only under `tooltipwidget` / 
    `ContextualTooltipType` / `AlertTooltipType` content. For always-visible panel
    text, use `text_single` / `text_multi` instead.

12. Give conditional image branches explicit bounds.
    When a wrapper contains mutually exclusive background-image widgets, do not
    rely on `layoutpolicy_expanding` alone. If the preview sits inside a plain
    `widget`/`button`, make that clickable wrapper fill its parent first, then
    give the image column fixed bounds and size each visible preview child with
    fixed pixels that match the content area. Otherwise the hbox can shrink to
    the image column's natural width, leaving text and image stacked at the
    parent's left edge.

13. Let tooltip rows grow with their visible content.
    If a tooltip row mixes `TooltipStringPairList`/`TooltipTextBlock` with a
    preview image, do not hard-code the row to a fixed height. Constrain width
    with `size = { W -1 }` or `minimumsize`, set the containing layout to size
    itself from its children, and keep `ignoreinvisible = yes` on the container
    so hidden wonder levels do not reserve space.

14. Match scripted-effect tooltip scopes to the GUI object passed in.
    `ShowScriptedEffectForScope(..., LocationView.GetLocation.MakeScope.Self)`
    runs the effect with the location as root. In that context, do not use
    `location.owner = { ... }`; the `location` prefix is parsed as an event
    target link and can spam scope-mismatch errors. Use `owner ?= { ... }` for
    country effects shown from a location-root tooltip.

15. Keep dynamic concept-link keys raw and registered.
    `SelectGameConcept` and `[...|E]` can use dynamic CString concept ids, but
    the value must already be a registered raw concept id. Do not feed them
    `GetFlagName` or variable-map flag values that can localize to display text.
    For generated routes, store a numeric id and build ids such as
    `tv_wonder_display_<id>`. Use `Localize(Concatenate('game_concept_', key))`
    only when intentionally rendering plain, non-clickable text.

16. Use EU5 image fit enums, not CSS names.
    Vanilla GUI uses `fittype` values such as `centercrop`, `fill`, `start`,
    and `end`. `contain` is not accepted and logs `Unknown fit type 'contain'`
    during GUI loading.

17. Do not treat `GetFlagName` as a raw key.
    A flag stored in a variable or variable map can render through localization
    in GUI, especially for game-concept-like ids. If a widget must build
    modifier names, localization keys, texture keys, or scripted-effect names,
    store a numeric id and generate static id branches, or use a typed object
    with a verified `GetKey` accessor.

18. Do not build raw DDS paths with `Concatenate` inside `texture`.
    Static `texture = "gfx/...dds"` paths are parsed by the GUI loader, but a
    runtime expression that returns a CString path does not behave like a texture
    handle. In the location-window test, `GetConceptTexture(Concatenate(...))`
    rendered while nested, suffix-only, and flat `Concatenate('gfx/...dds', '')`
    path expressions stayed blank without useful log errors. For arbitrary
    dynamic mod images, register image-only game concepts with matching
    `game_concept_*` and `game_concept_*_desc` localization, then route through
    `GetConceptTexture`, preferably with numeric ids such as
    `tv_wonder_display_image_<id>`.

19. Give dynamic `ShowModifierEffect` routes static script references.
    If GUI builds modifier ids with `Concatenate(...)`, such as
    `tv_wonder_display_<id>_level_<level>`, do not rely on the GUI expression as
    the only reference. Generate an unreachable script block with
    `if = { limit = { always = no } ... }` that applies every possible country or
    location display modifier through the correct `add_*_modifier` effect.

20. Keep progressbar offsets on a wrapper.
    `progressbar` does not handle `margin_top`; GUI loading logs an unsupported
    property error. If a bar needs vertical centering or offset inside an
    `hbox`/`vbox`, put a fixed-size `widget` in the layout and anchor the
    `progressbar` inside that wrapper.

## Validation

Run `validate.py --changed --fix --ai-report`, then check the in-game error log after hover
testing the panel. GUI failures often appear only when the widget is rendered or hovered.
