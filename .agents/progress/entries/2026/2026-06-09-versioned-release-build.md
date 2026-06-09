---
page_id: WS-2026-06-09-001
date: 2026-06-09
title: v3.0.4 版本化发布打包
status: draft
related_commit_message: "chore(release): add versioned release packaging"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - release
  - packaging
  - version
  - installer
  - pyinstaller
  - onedir
---

用户要求重新打包安装包, 并明确以后每次打包都需要附带版本号。

处理结果:

- 使用 `scripts/build_release.ps1 -Version 3.0.4` 构建发布产物。
- 主程序发布形态改为 PyInstaller `onedir`, 产物目录为 `dist/WinStart/`。
- 生成便携压缩包 `dist/WinStart_v3.0.4.zip`, 内含目录版主程序。
- 生成安装包 `dist/WinStart_Setup_v3.0.4.exe`, 安装器会将目录版主程序复制到 `%LOCALAPPDATA%\WinStart`。
- 新增/更新 `scripts/build_release.ps1`, 将主程序 onedir 打包、版本化 ZIP、安装器打包串成稳定流程。
- 更新 `scripts/WinStart_Setup.iss`, 将 Inno Setup 输出名和文件规则也改为 `WinStart_Setup_v3.0.4`, 如未来恢复 Inno 流程仍遵守版本化命名。
- 在 `.agents/overrides/rules.yaml` 和 `.agents/RULES.md` 中记录 durable 规则: 发布产物文件名必须带应用版本号。

验证:

- `dist/WinStart_v3.0.4.zip` 已生成。
- `dist/WinStart_Setup_v3.0.4.exe` 已生成。
- `dist/WinStart_v3.0.4.zip` SHA256: `3148DA59103F3C5590DFF9EC9DAC8F2A65CBC8ED1CED301B9B52192799834537`。
- `dist/WinStart_Setup_v3.0.4.exe` SHA256: `5239929776424AF71AD7D7F4873692D5879F71EDFBE53475AA0C6C920008DB58`。

注意:

- `v3.0.1` 到 `v3.0.3` 的便携版为单 exe onefile 或过渡版本, 不再作为推荐测试版本。
- 当前推荐测试版本是 `v3.0.4`。
