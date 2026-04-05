---
page_id: WS-2026-04-05-008
date: 2026-04-05
title: 首屏骨架与延后图标加载
status: draft
related_commit_message: "perf(ui): show card skeletons before deferred icon loading"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - startup
  - performance
  - lazy-load
  - skeleton
---
在用户反馈“图标磁盘缓存后首开仍约 3 秒, 目标是 1 秒内可见窗口”后, 将首屏提速方向从缓存优化升级为界面初始化拆分。

本次改动把启动路径改为:

- `MainWindow` 初始化时先创建窗口骨架和 3 张卡片。
- 卡片初始只显示标题和加载占位, 不在 `show()` 前同步准备全部图标。
- 进入事件循环后再按卡片维度分批调用图标加载, 减少窗口首次可见前的阻塞时间。
- 菜单图标缓存也随卡片图标加载一起延后, 不再阻塞首屏。

这条记录沉淀的核心反馈是:

- 图标磁盘缓存确实有效, 但只能把首开从约 4 秒拉到约 3 秒。
- 1 秒级首屏体验不能继续靠缓存细节小修实现, 必须把“窗口显示”和“图标准备”解耦。
- 灰化图标位置问题仍存在, 但已按用户要求暂缓处理。
