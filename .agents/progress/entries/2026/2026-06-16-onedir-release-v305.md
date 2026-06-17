---
page_id: WS-2026-06-16-001
date: 2026-06-16
title: v3.0.5 目录版发布口径固化
status: promotable
related_commit_message: "fix(runtime): distribute main app as onedir to avoid _MEI warning"
related_commit_hash: "a2ba965"
upstream_reference: ".agents/progress/entries/2026/2026-06-09-pyinstaller-runtime-cleanup.md"
keywords:
  - pyinstaller
  - _MEI
  - onedir
  - release
  - installer
---

用户再次反馈关闭 WinStart 后仍出现 `Failed to remove temporary directory` 警告, 但截图路径已经是 `%LOCALAPPDATA%\WinStart\_runtime\_MEI...`, 说明此前 `runtime_tmpdir` 已生效, 问题已经不是临时目录位置, 而是主程序 onefile 退出阶段仍可能无法删除当前 `_MEI` 解包目录。

本次决策:

- 正式修复目标是消除用户日常运行 WinStart 时的 `_MEI` 退出告警。
- 主程序正式分发形态固定为 PyInstaller `onedir`, 不再推荐发布 `WinStart_v*.exe` 单文件主程序。
- 安装器仍可使用 onefile, 因为它只是一次性分发工具; 安装后的日常入口是 `%LOCALAPPDATA%\WinStart\WinStart.exe` 目录版主程序。

本次实现:

- `scripts/build_release.ps1` 默认版本更新为 `3.0.5`, 继续输出 `dist/WinStart_v3.0.5.zip` 与 `dist/WinStart_Setup_v3.0.5.exe`。
- 构建脚本会删除同版本遗留的 `WinStart_v3.0.5.exe`, 防止把 onefile 主程序误当作正式发布物。
- 旧版 `scripts/install.bat` 改为复制 `dist/WinStart/` 整个目录, 不再复制单个 `dist\WinStart.exe`。
- `README.md`, `USER_GUIDE.md`, `RELEASE_NOTES.md` 统一说明便携版是 ZIP 目录版, 运行时必须保留 `_internal` 目录。

验证要求:

- 运行 `.\scripts\build_release.ps1 -Version 3.0.5`。
- 确认生成 `dist\WinStart_v3.0.5.zip` 和 `dist\WinStart_Setup_v3.0.5.exe`。
- 安装后确认 `%LOCALAPPDATA%\WinStart\WinStart.exe` 与同级 `_internal\` 存在。
- 从安装版或解压后的便携版启动并关闭 WinStart, 不应再出现主程序 `_MEI` 清理警告。

## 跟进 (2026-06-17)

用户确认问题未复发。onedir 发布形态有效消除了 `Failed to remove temporary directory` 警告，验证通过，状态升级为 promotable。
