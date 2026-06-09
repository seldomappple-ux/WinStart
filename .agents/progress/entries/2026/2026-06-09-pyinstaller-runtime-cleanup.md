---
page_id: WS-2026-06-09-003
date: 2026-06-09
title: PyInstaller 运行时目录清理与 onedir 切换
status: draft
related_commit_message: "fix(packaging): switch installed app to onedir"
related_commit_hash: ""
upstream_reference: ".agents/progress/entries/2026/2026-04-09-pyinstaller-mei-warning.md"
keywords:
  - pyinstaller
  - _MEI
  - runtime
  - packaging
  - cleanup
  - onefile
  - onedir
---

今天继续处理 2026-04-09 记录的 PyInstaller `_MEI` 临时目录清理告警。

用户补充确认:

- 告警是在关闭程序后一段时间出现。
- 这与 `PyInstaller onefile` bootloader 在业务进程退出后清理 `_MEI` 解压目录的阶段相符, 不是 WinStart 主窗口关闭逻辑直接抛出的错误。
- 由于告警发生在 Python 业务代码结束之后, 应用内部关闭事件或 `try/except` 不能可靠拦截。

阶段性处理:

- 曾尝试通过 `WinStart.spec` 的 `runtime_tmpdir` 将 onefile 解压目录从 `%TEMP%` 移到 `%LOCALAPPDATA%\WinStart\_runtime`。
- 曾增加 `src/core/runtime_cleanup.py`, 在 frozen 模式启动早期清理旧 `_MEI*` 残留目录。
- 用户随后反馈打开程序有概率失败, 弹出 Qt 错误: `This application failed to start because no Qt platform plugin could be initialized`。
- 复盘判断: 启动时清理近期 `_MEI*` 对 onefile 连续启动或多实例不安全, 可能误删另一个实例尚未加载完成的 Qt `platforms/qwindows.dll` 所在目录。
- 因此清理策略改为保守模式: 只清理最后修改时间至少 7 天前的 `_MEI*` 目录。

最终处理方向:

- 将已安装的主程序从 PyInstaller `onefile` 切换为 `onedir`。
- `onedir` 主程序不会在每次启动时解压到 `_MEI` 目录, 日常关闭 WinStart 时也就不再触发主程序 `_MEI` 清理告警。
- 安装器本身仍是 onefile, 但它只是分发工具; 用户日常运行的是 `%LOCALAPPDATA%\WinStart\WinStart.exe` 目录版主程序。
- `scripts/build_release.ps1` 现在构建 `dist/WinStart/` 目录版主程序, 生成 `dist/WinStart_v3.0.4.zip`, 并将 `dist/WinStart/` 作为 `WinStart_app` 打入安装器。
- `src/installer_gui.py` 支持从安装器资源中的 `WinStart_app` 目录复制整个应用目录到 `%LOCALAPPDATA%\WinStart`。

验证:

- `python -m compileall src` 通过。
- 模拟 frozen 状态验证: 当前 `_MEI` 与近期 `_MEI` 不会被清理。
- `dist/WinStart/WinStart.exe` 已生成, 旁边包含 `_internal` 依赖目录。
- `dist/WinStart_Setup_v3.0.4.exe` 已生成, 内含目录版主程序。

后续规则:

- 若目标是彻底规避 WinStart 主程序关闭后的 `_MEI` 告警, 发布安装版应优先使用 `onedir` 主程序。
- 不应在启动时删除近期 `_MEI` 目录; 如需清理, 只处理足够旧的残留。
