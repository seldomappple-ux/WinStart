# Local Rules

This file is owned by the project maintainer. Keep durable local preferences here in prose, but do not expect this file alone to affect generated adapters.

## Protection

- Treat this file as manually maintained source.
- Generated files must never overwrite this file.
- Immutable upstream rules still win over anything written here.

## How To Apply A Durable Override

1. Confirm the target rule is listed in `.agents/profile.yaml -> override_whitelist`.
2. Mirror the enforceable override in `.agents/overrides/rules.yaml`.
3. Run `vibe-governance validate` and `vibe-governance render`.

## Notes

- Use this file for repository-specific rationale, not for generated adapter content.
- Hard hardware safety rules, flashing rules, and other future red-line overlays are expected to stay immutable.
