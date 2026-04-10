---
page_id: WS-2026-04-11-001
date: 2026-04-11
title: _MEI 告警打包链路修正与重打包
status: draft
related_commit_message: "build(runtime): route packaging through spec files and rebuild installer"
related_commit_hash: ""
upstream_reference: "WS-2026-04-10-001, WS-2026-04-10-002"
keywords:
  - pyinstaller
  - _MEI
  - runtime_tmpdir
  - packaging
  - installer
  - build
---

本次工作不是直接修改 `_MEI` 清理逻辑，而是先确认前一轮提出的 `runtime_tmpdir` 方案为什么没有在用户实际测试中生效。

本次确认到的关键事实：

- `WinStart.spec` 已包含 `runtime_tmpdir=os.path.join('%LOCALAPPDATA%', 'WinStart', '_runtime')`
- `build/WinStart/EXE-00.toc` 与 `build/WinStart/PKG-00.toc` 中都能看到 `pyi-runtime-tmpdir %LOCALAPPDATA%\WinStart\_runtime`
- 仓库里的旧 `README.md` 仍指导使用裸命令 `pyinstaller ... src/main.py` 打包主程序
- 裸命令会绕过 `.spec` 中的项目级配置，导致用户拿到的 exe 可能仍使用默认 `%TEMP%\_MEI*` 路径

据此形成的结论：

- `_MEI` 告警持续存在的首要原因，不一定是修复方案失效，而更可能是打包链路没有统一走 `.spec`
- 在没有确认打包入口统一之前，继续分析 Qt 退出清理时序会混入噪音

本次已执行的修正：

- 更新 `README.md` 中的打包说明，明确要求使用 `WinStart.spec` 与 `WinStart_Setup.spec`
- 明确注明不要再使用 `pyinstaller ... src/main.py` 这种会绕过 `runtime_tmpdir` 的裸命令
- 按最新 `.spec` 重新构建 `dist/WinStart.exe` 与 `dist/WinStart_Setup.exe`

本次产物状态：

- 新 `dist/WinStart.exe` 已于 2026-04-10 23:56 左右重新生成
- 新 `dist/WinStart_Setup.exe` 已于 2026-04-10 23:56 左右重新生成
- 新安装包应作为下一轮 `_MEI` 告警验证的唯一测试基线

后续验证要求：

- 必须先用这次重打包后的安装版或主程序复测 `_MEI` 告警
- 如果新版仍然落到 `%TEMP%\_MEI*`，再继续排查 PyInstaller 对 `runtime_tmpdir` 的实际行为
- 如果路径已迁移但仍有告警，再转入 Qt 退出资源清理时序问题排查
