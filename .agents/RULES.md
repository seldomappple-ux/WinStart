# WinStart Local Rules

This file records durable local rules for the `WinStart` desktop launcher project. Treat it as the human-readable explanation layer for this repository, while `.agents/profile.yaml` and `.agents/overrides/rules.yaml` remain the structured source of truth.

## Protection

- Treat `.agents/` as maintained source, not generated output.
- Do not directly edit generated adapter files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/`, `.github/`, or `.opencode/`.
- When durable rules change, update `.agents/` first, then run `vibe-governance validate --target .` and `vibe-governance render --target .`.

## Project Focus

- `WinStart` is a Windows desktop productivity launcher built with `PySide6`.
- Runtime code lives under `src/`; packaging and installer assets live under `scripts/`, `assets/`, and `WinStart.spec`.
- User-facing behavior changes must be reflected in `README.md`, `USER_GUIDE.md`, or `RELEASE_NOTES.md` when relevant.

## Repository Boundaries

- Keep GUI behavior inside `src/ui/` and business/runtime logic inside `src/core/`.
- Prefer additive changes over broad refactors because this repo is small and currently organized around a simple launcher workflow.
- Avoid introducing governance ceremony that blocks feature delivery; use the governance layer to clarify context, rules, and project memory.

## Delivery Rules

- New launcher behavior should include the corresponding persistence update in `src/core/config_manager.py` when config shape changes.
- Changes that affect startup, launching, or installer behavior should be verified on Windows before release.
- Release builds must increment the app version and collect final distributables under `dist/WinStart_vX.Y.Z/`.
- Each release folder must contain exactly the installation package `WinStart_Setup_vX.Y.Z.exe`, the portable onedir folder `WinStart_vX.Y.Z/`, and a short versioned note file `WinStart_vX.Y.Z_说明.txt`; do not include a portable zip.
- Keep the main app packaged as PyInstaller `onedir`; do not publish `WinStart_vX.Y.Z.exe` onefile main executables.
- If a change modifies how users operate the app, add a progress entry first or alongside the implementation so future sessions can recover the intent quickly.
