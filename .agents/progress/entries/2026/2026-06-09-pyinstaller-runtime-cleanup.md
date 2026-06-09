---
page_id: WS-2026-06-09-003
date: 2026-06-09
title: PyInstaller 运行时目录清理实现
status: draft
related_commit_message: "fix(packaging): clean stale PyInstaller runtime dirs"
related_commit_hash: ""
upstream_reference: ".agents/progress/entries/2026/2026-04-09-pyinstaller-mei-warning.md"
keywords:
  - pyinstaller
  - _MEI
  - runtime
  - packaging
  - cleanup
  - onefile
---

今天继续处理 2026-04-09 记录的 PyInstaller `_MEI` 临时目录清理告警。

用户补充确认:

- 告警是在关闭程序后一段时间出现。
- 这与 `PyInstaller onefile` bootloader 在业务进程退出后清理 `_MEI` 解压目录的阶段相符, 不是 WinStart 主窗口关闭逻辑直接抛出的错误。

实现与验证:

- 复查 `WinStart.spec`, 当前 onefile 构建已设置 `runtime_tmpdir=os.path.join('%LOCALAPPDATA%', 'WinStart', '_runtime')`。
- 本机使用 `PyInstaller 6.20.0` 构建后实测, Windows 会将该路径正确展开为 `C:\Users\<user>\AppData\Local\WinStart\_runtime`。
- 实测未再创建 `%TEMP%\_MEI*`, 也未创建字面量 `%LOCALAPPDATA%` 目录。
- 新增 `src/core/runtime_cleanup.py`, 在 frozen 模式启动早期清理 `%LOCALAPPDATA%\WinStart\_runtime` 下非当前进程使用的旧 `_MEI*` 目录。
- 在 `src/main.py` 启动早期调用 `cleanup_stale_pyinstaller_runtime_dirs()`。

后续修正:

- 用户测试反馈打开程序有概率失败, 弹出 Qt 错误: `This application failed to start because no Qt platform plugin could be initialized`。
- 复盘判断: 初版启动清理会删除所有非当前 `_MEI*` 目录, 对 onefile 连续启动或多实例并不安全。如果另一个实例仍在启动或 Qt 尚未加载完 `platforms/qwindows.dll`, 其解压目录可能被新实例清理, 从而触发 Qt platform plugin 初始化失败。
- 修正为保守策略: 只清理最后修改时间至少 7 天前的 `_MEI*` 目录, 当前目录和近期目录都跳过。
- 该策略优先保证启动稳定性, 残留清理退居次要; 如果后续仍需要更积极清理, 应改成显式维护锁文件或切换 `onedir`, 不应在启动时删除近期 `_MEI` 目录。

边界:

- 启动清理只能处理上次异常退出、强制结束或外部进程占用后残留的旧 `_MEI*` 目录。
- 该逻辑不能拦截当次关闭后由 PyInstaller bootloader 发出的清理告警, 因为告警发生在 Python 业务代码结束之后。
- 当次告警仍主要依赖 `runtime_tmpdir` 降低触发概率。
- 如果用户机器仍稳定复现, 下一步应评估 `onedir` 分发, 或在发布说明中说明该 warning 的临时规避方式。

验证:

- `python -m compileall src` 通过。
- `runtime_cleanup` 开发态空调用通过。
- 模拟 frozen 状态验证: 当前 `_MEI` 与近期 `_MEI` 不会被清理。
- Qt 离屏模式下 `MainWindow` 初始化通过。
- v3.0.3 发布构建已包含该修复。
