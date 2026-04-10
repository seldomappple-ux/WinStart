---
page_id: WS-2026-04-09-001
date: 2026-04-09
title: PyInstaller _MEI 临时目录清理告警
status: draft
related_commit_message: "docs(runtime): capture initial PyInstaller _MEI temp cleanup warning"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - pyinstaller
  - _MEI
  - temp
  - packaging
  - runtime
  - warning
---

用户反馈程序退出时弹出如下告警：

`Failed to remove temporary directory: C:\Users\L_W\AppData\Local\Temp\_MEI296522`

结合现场截图，当时的判断如下：

- 告警目录名 `_MEIxxxxxx` 符合 `PyInstaller --onefile` 运行时临时解压目录的命名规则
- 截图里残留的文件主要是 `VCRUNTIME140.dll` 和 `VCRUNTIME140_1.dll`，更像是退出清理阶段失败，而不是业务逻辑崩溃
- 该类告警通常发生在程序准备删除 `_MEI` 目录时，目录内文件仍被其它进程或系统组件占用

影响评估：

- 一般不会直接导致配置损坏或启动项数据丢失
- 主要影响是 `%TEMP%` 下残留 `_MEI` 目录，以及用户在退出时看到警告弹窗
- 如果频繁出现，会降低便携版和安装版的整体稳定感知

当时选定的缓解方向：

- 保持 `PyInstaller onefile` 分发方式不变
- 尝试将运行时解压目录从系统 `%TEMP%` 迁移到 `%LOCALAPPDATA%\WinStart\_runtime`
- 目标是降低 `_MEI` 目录被外部进程抢占的概率，从而减少退出清理告警
