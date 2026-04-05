---
page_id: WS-2026-04-05-001
date: 2026-04-05
title: 引入 Taotaotao 治理骨架
status: draft
related_commit_message: "chore(governance): bootstrap Taotaotao governance scaffold"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - governance
  - onboarding
  - taotaotao
---
为现有 `WinStart` 项目引入 `Taotaotao` 的治理体系, 目标是补齐接手入口、规则真源、进度沉淀和多 AI 适配文件, 同时不破坏现有业务代码和原有 README / USER_GUIDE / RELEASE_NOTES 的角色分工。

本次引入采用“局部接管”而不是对现有仓库重新 bootstrap:

- 使用 `vibe-governance init` 生成 `.agents/` 真源骨架。
- 将 profile 调整为 `software` 项目类型。
- 新增 `START_HERE.md` 作为当前项目的人机共用启动入口。
- 新增本地 skills 和 architecture decisions, 让后续会话能快速恢复上下文。
- 通过 render 生成 `AGENTS.md`、`.cursor/`、`.github/`、`CLAUDE.md`、`GEMINI.md`、`.opencode/AGENTS.md` 和 `.agents/PROGRESS.md`。

这一步的重点不是增加流程负担, 而是让后续需求实现时能先读本地规则和项目状态, 减少“每次重新解释项目”的成本。
