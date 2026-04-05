---
page_id: WS-2026-04-05-003
date: 2026-04-05
title: 软件开关菜单交互回归修复
status: draft
related_commit_message: "fix(ui): flatten toggle menu and keep it open for batch changes"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - bugfix
  - toggle
  - menu
  - ui
---
在验收“启动项软件开关功能”时发现两个明确回归:

- 软件列表被放进了“软件开关”二级子菜单, 不符合“和编辑配置同一级可直接操作”的原始交互目标。
- 切换任意一个开关后菜单会自动返回上一级并关闭, 不适合连续修改多个启动项。

本次修复把卡槽右上角菜单重做为一级设置面板:

- 保留“编辑配置”动作。
- 在同一个菜单面板里直接列出当前卡槽全部启动项。
- 每个启动项使用可连续点击的行内开关控件。
- 菜单只在点击空白处或失焦时关闭, 不再因单次切换而退出。

这次修复的 durable lesson 是: 适合批量操作的即时设置, 不应该塞进一次性关闭的二级菜单里, 而应直接放进可停留的一级交互容器。
