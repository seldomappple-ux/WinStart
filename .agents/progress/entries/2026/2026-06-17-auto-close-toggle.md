---
page_id: WS-2026-06-17-001
date: 2026-06-17
title: 新增卡槽"启动后关闭窗口"开关
status: draft
related_commit_message: "feat(ui): add per-slot auto-close toggle after launch"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - auto-close
  - toggle
  - menu
  - slot-settings
---

## 背景

用户希望在执行一键启动任务结束后，WinStart 窗口能自动关闭，且该行为可按卡槽独立控制。

## 实现

- `src/core/config_manager.py`：新增 `set_slot_auto_close(slot_id, value)` 方法，将 `auto_close` 字段写入对应卡槽的 `data.json`。
- `src/ui/components.py`：
  - `LaunchCard` 新增信号 `toggle_auto_close_requested(str, bool)` 和 `close_requested()`。
  - 初始化及 `update_data()` 均从 `slot_data` 读取 `auto_close` 字段。
  - `trigger_launch()` 启动后若 `auto_close` 为真，1600ms 后发出 `close_requested` 信号。
  - `show_menu()` 在"软件开关"区段下方新增"卡槽设置"区段，复用 `ToggleMenuRow` 组件渲染"启动后关闭窗口"开关，样式与上方软件开关完全一致（含白色滑块 knob）。
- `src/ui/main_window.py`：在 `refresh_slots()` 中连接两个新信号：
  - `toggle_auto_close_requested` → `config_manager.set_slot_auto_close`
  - `close_requested` → `self.close`

## 验证

- 开启开关后点击卡片启动，约 1.6s 后窗口自动关闭，符合预期。
- 关闭开关后启动，窗口不关闭。
- 开关状态持久化，重启 WinStart 后保留。
- 重新打包为 v3.0.5，构建产物正常。
