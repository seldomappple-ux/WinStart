---
page_id: WS-2026-04-10-001
date: 2026-04-10
title: _MEI 临时目录清理告警仍然存在
status: draft
related_commit_message: "docs(runtime): record persistent _MEI temp cleanup warning feedback"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - pyinstaller
  - _MEI
  - temp
  - runtime
  - warning
  - feedback
---

用户在 2026-04-10 再次反馈，`PyInstaller onefile` 退出时的临时目录清理告警依旧存在，说明前一轮记录的缓解方案尚未在实际使用路径上消除问题。

本次反馈对应的现场现象：

- 弹窗文案仍为 `Failed to remove temporary directory`
- 截图中的目录为 `C:\Users\20271\AppData\Local\Temp\_MEI71442`
- 路径仍落在系统 `%TEMP%` 下，而不是前一轮计划中的 `%LOCALAPPDATA%\WinStart\_runtime`

这带来的直接判断：

- 当前用户实际运行的产物，仍然在使用默认 `_MEI` 临时解压目录，或相关改动未真正进入本次测试包
- 即使已有缓解实现，至少在当前打包与运行链路上，它还没有稳定生效
- 该问题目前应继续视为未解决，而不是“已有方案待观察”

对后续排查的提示：

- 优先核对用户当前测试的 `WinStart.exe` / 安装版是否来自包含 runtime temp 定向配置的最新构建
- 核对打包脚本、`.spec` 文件或运行时参数是否真正把 `_MEIPASS` 解压目录迁移到 `%LOCALAPPDATA%\WinStart\_runtime`
- 如果确认最新包已生效但仍落到 `%TEMP%`，则需要重新评估该方案是否受 `PyInstaller` 行为限制

当前结论：

- 图标缓存与首屏提速优化可以继续推进
- `_MEI` 临时目录清理告警仍是独立遗留问题，需要单独验证打包链路与运行时目录策略
