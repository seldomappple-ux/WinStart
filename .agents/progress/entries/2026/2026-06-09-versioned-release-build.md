---
page_id: WS-2026-06-09-001
date: 2026-06-09
title: v3.0.3 版本化发布打包
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
---

用户要求重新打包安装包, 并明确以后每次打包都需要附带版本号。

处理结果:

- 使用 `scripts/build_release.ps1 -Version 3.0.3` 构建发布产物。
- 生成便携版 `dist/WinStart_v3.0.3.exe`。
- 生成安装包 `dist/WinStart_Setup_v3.0.3.exe`。
- 新增 `scripts/build_release.ps1`, 将主程序打包、版本化便携版复制、Python 安装向导打包串成一个稳定流程。
- 更新 `scripts/WinStart_Setup.iss`, 将 Inno Setup 输出名也改为 `WinStart_Setup_v3.0.3`, 以便未来如恢复 Inno 流程时仍遵守版本化命名。
- 在 `.agents/overrides/rules.yaml` 和 `.agents/RULES.md` 中记录 durable 规则: 发布产物文件名必须带应用版本号。

验证:

- `dist/WinStart_v3.0.3.exe` 已生成。
- `dist/WinStart_Setup_v3.0.3.exe` 已生成。
- `dist/WinStart_v3.0.3.exe` SHA256: `0E72B39AF82B493242E255926131D2442CDF48DA6093A5E221A6864AA5E7FE30`。
- `dist/WinStart_Setup_v3.0.3.exe` SHA256: `9A45098388536449417917D8E996CA2A24F6E318246FBC4A6D66AC98C8377795`。
