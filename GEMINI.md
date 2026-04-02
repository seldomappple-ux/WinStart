<!--
managed-by: vibe-governance 1.2.1
upstream-repo: https://github.com/example/vibe-governance
upstream-version: 1.2.1
upstream-published-at: 2026-04-01T00:00:00Z
checksum-sha256: 76f90a68580c7c37185eaa55d6bee323e07799e29af4b9b31546a05c8daea9cd
managed-note-en: DO NOT EDIT DIRECTLY. Regenerate with `vibe-governance render`.
managed-note-zh: 请勿直接编辑此文件, 请运行 `vibe-governance render` 重新生成.
-->
# GEMINI / Gemini 适配说明

这是一个轻量适配文件. 请先阅读 `AGENTS.md`, 再查看 `.agents/` 中的结构化配置.

This is a thin adapter file. Read `AGENTS.md` first, then consult `.agents/` for structured configuration.

当前项目版本: `2.0.0`

Current project version: `2.0.0`

- `governance.entrypoint`:
  中文: 根目录 AGENTS.md 是稳定的人类入口, `.agents/` 是 profile、本地规则、结构化 override 与 progress 记录的规范真源目录.
  English: Root AGENTS.md is the stable human entrypoint. Treat .agents/ as the canonical source tree for profile, local rules, structured overrides, and progress records.
- `governance.managed_outputs`:
  中文: 不要直接编辑生成的适配文件. 持久规则变更应写入 `.agents/profile.yaml`、`.agents/overrides/rules.yaml` 或上游 canonical 模板, 然后重新渲染.
  English: Do not edit generated adapter files directly. Apply durable changes in .agents/profile.yaml, .agents/overrides/rules.yaml, or canonical upstream templates, then rerender.
- `governance.onboarding_sequence`:
  中文: 接手仓库时, 先阅读 README.md、docs/SOURCE_MATERIALS.md、ARCHITECTURE.md 和 .agents/PROGRESS.md, 再依赖生成的适配文件. 先对齐本地上下文, 再执行修改.
  English: When taking over the repository, read README.md, docs/SOURCE_MATERIALS.md, ARCHITECTURE.md, and .agents/PROGRESS.md before relying on generated adapter files. Align on local context first, then act.
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
- `docs.directory_readme`:
  中文: 每个稳定且人工维护的目录都必须包含一份中文 Markdown 说明文件, 默认使用 `README_中文.md`. 如果目录里已经有承担目录说明职责的中文 `README.md`, 也可视为满足要求. Git 内部目录、缓存目录和生成态临时目录除外.
  English: Every stable manually maintained directory must include a Chinese Markdown explainer file, preferably `README_中文.md`. A Chinese `README.md` also counts if it already explains the directory's purpose. Skip VCS internals, caches, and generated transient directories.
- `progress.lifecycle`:
  中文: Progress entry 必须经历 draft、promotable、upstreamed 三种状态. PROGRESS.md 是滑动索引, 不是完整流水账. 较旧或已沉淀的条目应归档, 不应无限膨胀.
  English: Progress entries must move through draft, promotable, and upstreamed states. PROGRESS.md is a sliding index, not a full transcript. Archive older or upstreamed entries instead of expanding the index forever.
