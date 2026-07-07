# Project Memory

Instructions here apply to this project and are shared with team members.

## Context
# currentDate
Today's date is 2026/07/04.

      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.

## Required Project Instructions

Read the repository-root `CLAUDE.md` before acting.

Claude subagents and managed sandboxes must not run `conda run -n eu5`; it can
hang on this machine. Run project Python scripts with the direct environment
interpreter instead:

```
C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\<script>.py ...
```
