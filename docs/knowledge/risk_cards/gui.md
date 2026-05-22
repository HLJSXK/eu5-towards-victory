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

## Validation

Run `validate.py --changed --fix --ai-report`, then check the in-game error log after hover
testing the panel. GUI failures often appear only when the widget is rendered or hovered.
