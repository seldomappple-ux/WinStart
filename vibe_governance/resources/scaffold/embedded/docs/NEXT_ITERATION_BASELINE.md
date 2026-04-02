# Next Iteration Baseline

This file is a pure index for the next human or AI iteration.

It should not repeat design content or summarize delta bodies. It only points to what must be read next.

## Current Version

- current_iteration: `__PROJECT_VERSION__`
- current_repo_version: `__PROJECT_VERSION__`

## Notes

- `current_iteration` is the current project iteration label.
- `current_repo_version` is the current formal project version.
- Keep both fields aligned on day 0, then update them deliberately if the project later separates iteration tags from release versions.

## Suggested Read Order

1. `README.md`
2. `docs/DEVELOPMENT_PLAN.md`
3. `docs/DELTA_DECISIONS.md`
4. `docs/PROTOCOL_SPEC.md`
5. `docs/HARDWARE_BRINGUP.md`
6. `docs/VALIDATION_PLAN.md`
7. `docs/schema/protocol.schema.json`

## Required Sources

- `README.md`
  - project entry and reading order
- `docs/DEVELOPMENT_PLAN.md`
  - current phase goals and work split
- `docs/DELTA_DECISIONS.md`
  - active delta decisions
- `docs/PROTOCOL_SPEC.md`
  - protocol contract
- `docs/HARDWARE_BRINGUP.md`
  - hardware assumptions and bring-up rules
- `docs/VALIDATION_PLAN.md`
  - validation stages and acceptance path
- `docs/schema/protocol.schema.json`
  - machine-readable schema example

## Active Delta IDs

Start empty and list only active `delta_id` values here.

## Fixed Regression Checks

- Protocol, schema, and validation plan stay on the same `project_version`
- Required docs still exist
- Active deltas are not duplicated into other documents
