---
page_id: WS-2026-04-05-007
date: 2026-04-05
title: 图标磁盘缓存优化首开性能
status: draft
related_commit_message: "feat(perf): add persistent disk cache for extracted icons"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - performance
  - icon-cache
  - startup
  - disk-cache
---
为 `WinStart` 增加了本地图标磁盘缓存, 目标是减少应用每次重启后的首开卡顿。

本次实现采用两层缓存, 但刻意分开键设计:

- 进程内缓存继续使用轻量键 `(normcase(path), size)`, 不引入文件时间戳。
- 磁盘缓存落在 `APPDATA\WinStart\icon_cache\`, 文件名基于稳定哈希生成。
- 普通文件的磁盘缓存键使用 `path + file_mtime + size`。
- `.lnk` 文件的磁盘缓存键仅使用 `.lnk` 自身的 `path + lnk_mtime + size`, 不为算键额外解析目标路径。

关键收益点是:

- 磁盘缓存命中时, `IconLoader.get_pixmap()` 会直接读取本地 PNG 并回填进程内缓存。
- 命中路径完全绕过快捷方式解析、Windows 高分辨率图标提取和 `smart_scale()` 的逐像素扫描。
- 首次遇到某个新图标仍会慢一次, 但后续重启应用会明显更快。

本次改动没有顺手修改 `_ensure_three_slots()` 或灰图位置问题, 避免把启动性能优化和不相关行为混在一起。
