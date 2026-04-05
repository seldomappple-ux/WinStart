<!--
managed-by: vibe-governance 0.1.0
upstream-repo: D:\code\VS Code\Taotaotao
upstream-version: 0.1.0
upstream-published-at: 2026-03-07T00:00:00Z
checksum-sha256: 84d735441bcc6d82bd8e2aea7467319da42adaa060beebb7050311f661e783aa
managed-note-en: DO NOT EDIT DIRECTLY. Regenerate with `vibe-governance render`.
managed-note-zh: 请勿直接编辑此文件, 请运行 `vibe-governance render` 重新生成.
-->
# CLAUDE / Claude 适配说明

这是一个轻量适配文件. 稳定治理入口是 `AGENTS.md`.

This is a thin adapter file. The stable governance entrypoint is `AGENTS.md`.

- `governance.entrypoint`:
  中文: 根目录 AGENTS.md 是稳定的人类入口, `.agents/` 是 profile、本地规则、结构化 override 与 progress 记录的规范真源目录.
  English: Root AGENTS.md is the stable human entrypoint. Treat .agents/ as the canonical source tree for profile, local rules, structured overrides, and progress records.
- `governance.managed_outputs`:
  中文: 不要直接编辑生成的适配文件. 持久规则变更应写入 `.agents/profile.yaml`、`.agents/overrides/rules.yaml` 或上游 canonical 模板, 然后重新渲染.
  English: Do not edit generated adapter files directly. Apply durable changes in .agents/profile.yaml, .agents/overrides/rules.yaml, or canonical upstream templates, then rerender.
- `governance.onboarding_sequence`:
  中文: 接手仓库时, 先阅读 START_HERE.md, 再严格按其中定义的本地文件读取顺序建立上下文, 之后才能依赖生成的适配文件或开始修改代码.
  English: When taking over the repository, read START_HERE.md first and then follow the exact local file-reading order defined there before relying on generated adapter files or modifying code.
- `git.flow`:
  中文: 使用 Git Flow 风格的分支策略, 至少包含 main 与 dev. 除非项目 overlay 另有规定, feature 与 release 工作应从 dev 分出.
  English: Use a Git Flow style branch strategy with at least main and dev. Feature and release work should branch from dev unless a project-specific workflow overlay says otherwise.
- `git.conventional_commits`:
  中文: Commit message 必须符合 Angular 或 Conventional Commit 规范. Progress entry 必须记录 Related Commit Message, 并建议记录 Related Commit Hash.
  English: Commit messages must follow Angular or Conventional Commit format. Progress entries must always record Related Commit Message and should also record Related Commit Hash.
- `comments.language`:
  中文: 代码注释必须遵循 profile.yaml 中配置的注释语言. 英文项目使用英文注释, 中文项目允许中文注释, 但应使用半角标点.
  English: Code comments must follow the configured comment language in profile.yaml. Use English comments for English projects, and use Chinese comments with half-width punctuation for Chinese projects.
- `code.architecture`:
  中文: 优先采用高内聚、低耦合、清晰的模块边界, 并在语言或框架支持时使用简洁的 Doxygen 风格 API 注释.
  English: Prefer high cohesion, low coupling, clear module boundaries, and concise Doxygen-style API comments when the language or framework supports them.
- `docs.split`:
  中文: 用户文档与开发文档必须分离. 根文档应链接到快速开始、部署说明与开发资料, 不应把全部细节混在一个文件里.
  English: User documentation and developer documentation must remain separate. The root documentation should link to quick start, deployment, and developer-facing references instead of mixing all detail into one file.
- `progress.lifecycle`:
  中文: Progress entry 必须经历 draft、promotable、upstreamed 三种状态. PROGRESS.md 是滑动索引, 不是完整流水账. 较旧或已沉淀的条目应归档, 不应无限膨胀.
  English: Progress entries must move through draft, promotable, and upstreamed states. PROGRESS.md is a sliding index, not a full transcript. Archive older or upstreamed entries instead of expanding the index forever.

如需持久修改治理规则, 请更新 `.agents/` 源文件后重新渲染, 不要直接编辑本文件.

Before making durable policy changes, update `.agents/` sources and rerender instead of editing this file directly.
