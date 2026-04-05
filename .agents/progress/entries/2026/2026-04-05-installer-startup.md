---
page_id: WS-2026-04-05-005
date: 2026-04-05
title: 安装器版本与启动项注册
status: draft
related_commit_message: "feat(installer): build setup exe and register startup option during install"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - installer
  - startup
  - task-manager
  - setup
---
为 `WinStart` 增加了可分发的 Windows 安装器版本, 并把“启动应用”注册前移到安装阶段。

本次改动包含:

- 新增 `WinStart_Setup.spec`, 用 PyInstaller 将 `src/installer_gui.py` 和已构建的 `dist/WinStart.exe` 一起打成 `dist/WinStart_Setup.exe`。
- 安装时在复制主程序后立即注册 `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run` 和 `StartupApproved\\Run` 下的 `WinStart` 项, 默认保持可在任务管理器里启用/禁用。
- 卸载脚本同时清理对应注册表项, 避免卸载后残留启动应用记录。

durable lesson:

如果希望用户在“任务管理器 -> 启动应用”里立刻看到并控制开机自启, 不能只依赖应用首次运行时再注册, 安装器本身就应完成这一步。
