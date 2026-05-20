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

## Validation

Run `validate.py --changed --fix --ai-report`, then check the in-game error log after hover
testing the panel. GUI failures often appear only when the widget is rendered or hovered.
