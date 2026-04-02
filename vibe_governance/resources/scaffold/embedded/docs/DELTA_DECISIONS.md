# Delta Decisions

Use this file as the only source of truth for active incremental decisions that have not yet been fully promoted back into the long-term sources of truth.

## File Header

- current_iteration: `__PROJECT_VERSION__`
- current_repo_version: `__PROJECT_VERSION__`
- last_cleanup_version: `__PROJECT_VERSION__`
- next_cleanup_due: `__NEXT_CLEANUP_VERSION__`

## Notes

- `current_iteration` is the current project iteration label.
- `current_repo_version` is the current formal project version.
- They can stay the same at init time, but keep the distinction explicit once the project starts evolving.

## Fields

- `delta_id`
- `status`
- `level`
- `created`
- `expires`
- `promotion_target`
- `source_entries`

## Levels

- `L0`: implementation-only, does not change cross-layer contracts
- `L1`: affects next-iteration understanding, but not yet a formal contract
- `L2`: affects cross-layer contracts and must be written back to source documents

## Active Decisions

Start empty. Add the first entry only when the first post-init change is classified as `L1` or `L2`.

```yaml
- delta_id: DELTA-YYYY-MM-001
  status: active
  level: L1
  created: __PROJECT_VERSION__
  expires: __NEXT_CLEANUP_VERSION__
  promotion_target: ""
  source_entries: []
```

## Promoted Decisions

Keep recently promoted entries here for one version cycle before archiving them elsewhere.

## Deprecated Decisions

Move expired or no-longer-needed entries here before archival cleanup.
