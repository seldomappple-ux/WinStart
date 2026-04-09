---
page_id: WS-2026-04-09-001
date: 2026-04-09
title: PyInstaller _MEI 临时目录清理告警
status: draft
related_commit_message: ""
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

用户反馈在程序退出时弹出如下警告:

`Failed to remove temporary directory: C:\Users\L_W\AppData\Local\Temp\_MEI296522`

结合现场截图可确认:

- 告警目录名 `_MEIxxxxxx` 符合 `PyInstaller --onefile` 程序的运行时临时解压目录命名规则。
- 截图中的残留文件仅包含 `VCRUNTIME140.dll` 和 `VCRUNTIME140_1.dll`, 更像是运行时退出阶段的清理失败, 而不是业务逻辑异常。
- 该类告警通常发生在程序准备删除 `_MEI` 临时目录时, 目录中的文件仍被占用, 例如被资源管理器、杀毒软件、索引服务或尚未完全退出的进程句柄占住。

当前判断:

- 这属于 `PyInstaller` 单文件运行时层面的退出清理告警, 不是 `WinStart` 业务功能本身抛出的业务错误。
- 如果用户当时运行的是 `WinStart.exe` 便携版, 则该告警很可能由本项目打包产物触发。
- 如果用户运行的是 Inno Setup 生成的安装器, 则安装器本身不使用 `_MEI` 目录, 告警更可能来自被启动的 `WinStart.exe` 或其他 PyInstaller 程序。

影响评估:

- 一般不会导致配置损坏或功能数据丢失。
- 直接影响主要是 `%TEMP%` 下残留 `_MEI` 临时目录, 以及用户看到退出告警。
- 若频繁出现, 会降低便携版体验, 也说明当前 onefile 运行时清理稳定性不足。

后续建议:

- 复现实验时区分便携版 `WinStart.exe` 与安装版 `WinStart_Setup.exe` 的触发路径。
- 复现时避免在资源管理器中打开 `_MEI` 目录, 观察告警是否仍然出现。
- 若问题稳定复现, 可评估改为 `onedir` 分发、减少退出时仍占用的动态库句柄, 或在发布说明中注明该告警的临时规避方式。

已选定处理方案:

- 采用方案 B, 保持 `PyInstaller onefile` 分发不变, 但将运行时解压目录从系统 `%TEMP%` 改为 `%LOCALAPPDATA%\WinStart\_runtime`。
- 该方案的目标不是彻底消除残留, 而是降低 `_MEI` 目录被外部进程抢占的概率, 从而减少退出时的清理告警。
