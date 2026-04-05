---
page_id: WS-2026-04-05-006
date: 2026-04-05
title: 首次启动卡顿原因分析
status: draft
related_commit_message: "docs(perf): record startup lag root cause analysis"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - startup
  - performance
  - icon-loading
  - ui
---
在验收“软件首次打开也有点卡”时, 复查了当前启动路径, 结论是卡顿主要发生在首屏展示之前的同步初始化阶段, 不是窗口显示之后的动画问题。

当前最主要的阻塞点有三类:

- `MainWindow.__init__()` 会在窗口 `show()` 之前立刻执行 `refresh_slots()`, 为每个卡槽创建 `LaunchCard`。
- 每个 `LaunchCard.refresh_icons()` 会同步调用 `PhysicsIconWidget.set_items()`, 对卡槽内每个启动项执行 `IconLoader.get_pixmap()`。
- `IconLoader.get_pixmap()` 对 `.exe` 和 `.lnk` 图标仍可能触发高分辨率图标提取、快捷方式解析、透明边界扫描和缩放, 这些都在 UI 线程里同步完成。

另外还有两个次要放大因素:

- `LaunchCard.refresh_icons()` 现在还会预生成菜单用的 `20x20` 图标缓存, 这部分工作也发生在首屏展示前。
- `ConfigManager._ensure_three_slots()` 无论数据是否变化都会 `_save_data()`, 会在应用启动早期多做一次磁盘写入。

durable lesson:

如果希望桌面应用首开更顺滑, 首屏之前不应同步做“全量图标准备 + 全量菜单图标预热”这类工作。更合适的做法是先显示骨架界面, 再按卡槽或按需懒加载图标资源。
