---
page_id: WS-2026-06-17-002
date: 2026-06-17
title: 版本化发布目录规则
status: draft
related_commit_message: "chore(release): collect artifacts in versioned dist folder"
related_commit_hash: ""
upstream_reference: ".agents/progress/entries/2026/2026-06-16-onedir-release-v305.md"
keywords:
  - release
  - packaging
  - version
  - dist
  - onedir
---

用户要求后续每次打包都在 `dist` 下新增一个带版本号的独立目录, 例如 `dist/WinStart_v3.0.5/`, 且每次发布版本号必须递增。

本次固化的发布规则:

- 正式发布目录为 `dist/WinStart_vX.Y.Z/`。
- 每个发布目录下只放三类交付内容: 安装版 `WinStart_Setup_vX.Y.Z.exe`, 便携版目录 `WinStart_vX.Y.Z/`, 以及带版本号的简短说明 `WinStart_vX.Y.Z_说明.txt`。
- 发布目录下不要放便携 zip。
- 打包方式沿用当前已验证的方案: 主程序 PyInstaller `onedir`, 安装器 PyInstaller `onefile`。
- 不恢复发布 `WinStart_vX.Y.Z.exe` 单文件主程序, 避免 `_MEI` 清理告警复发。

实现:

- 更新 `scripts/build_release.ps1`, 将最终产物收拢到 `dist/WinStart_v$Version/`。
- 构建脚本自动生成 `WinStart_v$Version_说明.txt`, 写明安装版/便携版用法、onedir 原因和 SHA256。为避免 Windows PowerShell 5.1 脚本源码编码导致中文内容乱码, 文件内容暂用 ASCII 英文。
- 后续升级: 说明文件改为中英双语。英文说明直接写在脚本中, 中文说明以 UTF-8 Base64 模板保存并在运行时解码, 避免 PowerShell 5.1 脚本源码编码导致中文乱码。
- 后续升级: 说明文件增加"本版本升级内容 / What's new in this version"段落。打包时可通过 `-ReleaseNotesEn` 和 `-ReleaseNotesZh` 传入中英说明; 未传入时使用默认提示文案。本次只更新模板, 不重新打包。
- 更新 `.agents/overrides/rules.yaml`, `.agents/RULES.md`, `README.md` 以记录 durable 发布规则。

验证建议:

- 运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_release.ps1 -Version <新版本号>`。当前默认版本已推进到 `3.0.6`, 后续发布应继续递增。
- 确认 `dist/WinStart_v<新版本号>/` 下包含安装版、便携版目录、带版本号的说明文件。
- 确认根 `dist` 下没有同版本 `WinStart_v<新版本号>.exe` 单文件主程序。
