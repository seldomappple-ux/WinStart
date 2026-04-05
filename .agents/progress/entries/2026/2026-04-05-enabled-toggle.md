---
page_id: WS-2026-04-05-002
date: 2026-04-05
title: 启动项软件开关功能
status: promotable
related_commit_message: "feat(ui): add per-item enabled toggle to launch cards"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - enabled
  - toggle
  - launch-card
  - grayscale
---

在卡槽右上角菜单中用"软件开关"子菜单替换原"重命名卡槽"入口，实现对单个启动项的启用/禁用控制。

## 改动文件

- `src/core/config_manager.py` — `add_item` 新增 `enabled: True`；`update_item` 保留 `enabled`；新增 `toggle_item_enabled(slot_id, item_id, enabled)`
- `src/core/launcher.py` — `launch_group` 入口过滤 `enabled=False` 的项
- `src/ui/components.py` — 新增 `_make_grayscale_pixmap`；disabled 项用灰化 pixmap 且不产生 trail；菜单改为 checkable submenu；`SlotSettingsDialog` 列表加 `checkState`，`closeEvent` 保存 enabled 状态
- `src/ui/main_window.py` — 连接 `toggle_item_requested` 信号到 `config_manager.toggle_item_enabled`

## 关键设计决策

- 菜单用 `QMenu.addMenu` + `setCheckable`，不弹独立 Dialog
- 灰化在 `set_items` 时预生成，不在 `paintEvent` 实时处理
- 旧 `data.json` 无 `enabled` 字段时，所有读取处用 `.get("enabled", True)` 兼容
- Launcher 在入口过滤，LaunchCard 不感知 enabled 逻辑
