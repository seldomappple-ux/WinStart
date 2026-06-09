---
page_id: WS-2026-06-09-004
date: 2026-06-09
title: 安装器快捷方式创建修复
status: draft
related_commit_message: "fix(installer): initialize COM before creating shortcuts"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - installer
  - shortcut
  - win32com
  - desktop
  - start-menu
  - setup
---

用户反馈 `WinStart_Setup_v3.0.1.exe` 显示安装成功后, 桌面没有快捷方式, 开始菜单也搜索不到。

现场确认:

- 主程序已复制到 `C:\Users\Wuyu\AppData\Local\WinStart\WinStart.exe`, 说明安装文件复制成功。
- `%APPDATA%\Microsoft\Windows\Start Menu\Programs\WinStart` 下没有 `WinStart.lnk`。
- 实际桌面下也没有 `WinStart.lnk`。
- 问题集中在 Python 安装向导的快捷方式创建阶段。

原因:

- `src/installer_gui.py` 在后台线程里调用 `win32com.client.Dispatch("WScript.Shell")` 创建 `.lnk`。
- 后台线程没有调用 `pythoncom.CoInitialize()`, COM 初始化缺失会导致快捷方式创建失败。
- 原实现 `create_shortcut()` 捕获异常后只打印并返回 `False`, 调用方没有检查返回值, 因此即使快捷方式失败也会显示安装成功。
- 桌面路径原本使用 `%USERPROFILE%\Desktop`, 如果用户桌面被 OneDrive 或系统策略重定向, 也可能写到不可见位置。

修复:

- 在安装线程开始时调用 `pythoncom.CoInitialize()`, 结束时调用 `pythoncom.CoUninitialize()`。
- `create_shortcut()` 失败时抛出异常, 安装器不再静默吞掉快捷方式失败。
- 创建快捷方式前确保目标目录存在。
- 桌面路径改为通过 `WScript.Shell.SpecialFolders("Desktop")` 获取真实桌面路径。
- 安装成功提示中显示实际安装路径, 便于用户定位。
- 重新打包 `v3.0.2`: `dist/WinStart_Setup_v3.0.2.exe`。

验证:

- `python -m compileall src\installer_gui.py` 通过。
- 本机使用相同 COM 逻辑在临时目录创建 `.lnk` 成功。
- `dist/WinStart_Setup_v3.0.2.exe` 已生成。
