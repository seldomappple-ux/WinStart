<!--
managed-by: vibe-governance 0.1.0
upstream-repo: D:\code\VS Code\Taotaotao
upstream-version: 0.1.0
upstream-published-at: 2026-03-07T00:00:00Z
checksum-sha256: 72e2cdbd8e6b9e5f536243d277a5af5f421b67c544336cad37856c9f561ed1b9
managed-note-en: DO NOT EDIT DIRECTLY. Regenerate with `vibe-governance render`.
managed-note-zh: 请勿直接编辑此文件, 请运行 `vibe-governance render` 重新生成.
-->
# PROGRESS

## Purpose

Use this file as a sliding index, not a long-form journal. Detailed history lives under `.agents/progress/entries/` and `.agents/progress/archived/`.

## Active Architecture Decisions

| ID | Status | Title | Summary |
| --- | --- | --- | --- |
| `ADR-0001` | `active` | Deterministic adapter generation | Adapter files are rendered by the Python CLI from structured sources. LLM output is never used as a translation layer. |
| `ADR-0002` | `active` | Managed outputs stay read-only | Durable policy changes must flow through .agents source files and the canonical rule catalog, not direct edits to generated adapters. |
| `ADR-0003` | `active` | Sliding-window progress index | PROGRESS.md only tracks current architecture decisions and the latest active entries, while older or upstreamed records stay searchable on disk. |
| `ADR-WS-0001` | `active` | WinStart keeps a lightweight PySide6 desktop architecture | The app remains a small Windows desktop launcher with `src/core` for state and launching logic and `src/ui` for the PySide6 interface. |
| `ADR-WS-0002` | `active` | Existing project docs remain the user-facing primary docs | Governance files support onboarding and AI alignment, while `README.md`, `USER_GUIDE.md`, and `RELEASE_NOTES.md` remain the main human-facing product docs. |

## Active Entries

| Page ID | Date | Title | Status | Path | Related Commit Message |
| --- | --- | --- | --- | --- | --- |
| `WS-2026-04-11-001` | `2026-04-11` | _MEI 告警打包链路修正与重打包 | `draft` | `.agents/progress/entries/2026/2026-04-11-mei-packaging-path-fix.md` | build(runtime): route packaging through spec files and rebuild installer |
| `WS-2026-04-10-002` | `2026-04-10` | _MEI 临时目录清理告警根因分析 | `draft` | `.agents/progress/entries/2026/2026-04-10-mei-warning-root-cause-analysis.md` | docs(runtime): analyze root cause of persistent _MEI cleanup warning |
| `WS-2026-04-10-001` | `2026-04-10` | _MEI 临时目录清理告警仍然存在 | `draft` | `.agents/progress/entries/2026/2026-04-10-mei-warning-still-persists.md` | docs(runtime): record persistent _MEI temp cleanup warning feedback |
| `WS-2026-04-09-001` | `2026-04-09` | PyInstaller _MEI 临时目录清理告警 | `draft` | `.agents/progress/entries/2026/2026-04-09-pyinstaller-mei-warning.md` | docs(runtime): capture initial PyInstaller _MEI temp cleanup warning |
| `WS-2026-04-05-008` | `2026-04-05` | 首屏骨架与延后图标加载 | `draft` | `.agents/progress/entries/2026/2026-04-05-startup-skeleton-loading.md` | perf(ui): show card skeletons before deferred icon loading |
| `WS-2026-04-05-007` | `2026-04-05` | 图标磁盘缓存优化首开性能 | `draft` | `.agents/progress/entries/2026/2026-04-05-icon-disk-cache.md` | feat(perf): add persistent disk cache for extracted icons |
| `WS-2026-04-05-006` | `2026-04-05` | 首次启动卡顿原因分析 | `draft` | `.agents/progress/entries/2026/2026-04-05-startup-lag-analysis.md` | docs(perf): record startup lag root cause analysis |
| `WS-2026-04-05-005` | `2026-04-05` | 安装器版本与启动项注册 | `draft` | `.agents/progress/entries/2026/2026-04-05-installer-startup.md` | feat(installer): build setup exe and register startup option during install |
| `WS-2026-04-05-004` | `2026-04-05` | 三个 UI bug 修复 | `promotable` | `.agents/progress/entries/2026/2026-04-05-ui-bugs.md` | fix(ui): grayscale position, icon label bg, toggle lag |
| `WS-2026-04-05-003` | `2026-04-05` | 软件开关菜单交互回归修复 | `draft` | `.agents/progress/entries/2026/2026-04-05-toggle-menu-regression.md` | fix(ui): flatten toggle menu and keep it open for batch changes |

## Archive

- Active entries older than the latest 10 should remain in `.agents/progress/entries/` and be located by search or tooling.
- Entries that have already been promoted upstream belong in `.agents/progress/archived/`.
- Upstream promotion must go through human-reviewed pull requests.
