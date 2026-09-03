# Eureka Advance Surface Map

`Advance` is the EU5 research-project concept, not the name of one GUI file.
Eureka work must preserve the full feature boundary:

- `technology_lateralview.gui`: technology-tree Advance nodes and current-research display.
- `advances_lateralview.gui`: the Advance list/card surface and effect rows.
- `agenda_view.gui`: current research in the agenda sidebar.
- `hud_topbar.gui`: current research in the top-bar widget.
- `main_menu/gui/shared/advances_tooltips.gui`: shared Advance tooltip content.
- `scripts_eureka/patch_gui_progress.py`: generator ownership for these GUI overrides.
- `src_eureka/in_game/common/advances/` and related triggers/effects/on_actions: backend condition and research-speed behavior.

When a task names Advance, research, or Eureka, inspect the relevant backend and
all affected display surfaces before narrowing the edit. Generated GUI outputs
must be changed through the generator and then regenerated.
