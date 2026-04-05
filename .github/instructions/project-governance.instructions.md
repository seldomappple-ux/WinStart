<!--
managed-by: vibe-governance 0.1.0
upstream-repo: D:\code\VS Code\Taotaotao
upstream-version: 0.1.0
upstream-published-at: 2026-03-07T00:00:00Z
checksum-sha256: 47d5ff586a77ce01ed60b4440e4d13be8477cad6aa281803f3e9f610d3061ec5
managed-note-en: DO NOT EDIT DIRECTLY. Regenerate with `vibe-governance render`.
managed-note-zh: 请勿直接编辑此文件, 请运行 `vibe-governance render` 重新生成.
-->
# Project Governance Instructions

This file exists for GitHub-specific instruction routing. Keep it aligned with `AGENTS.md` and do not add repository-only rules here.

## `governance.entrypoint`
Root AGENTS.md is the stable human entrypoint. Treat .agents/ as the canonical source tree for profile, local rules, structured overrides, and progress records.

## `governance.managed_outputs`
Do not edit generated adapter files directly. Apply durable changes in .agents/profile.yaml, .agents/overrides/rules.yaml, or canonical upstream templates, then rerender.

## `governance.onboarding_sequence`
When taking over the repository, read START_HERE.md first and then follow the exact local file-reading order defined there before relying on generated adapter files or modifying code.

## `git.flow`
Use a Git Flow style branch strategy with at least main and dev. Feature and release work should branch from dev unless a project-specific workflow overlay says otherwise.

## `git.conventional_commits`
Commit messages must follow Angular or Conventional Commit format. Progress entries must always record Related Commit Message and should also record Related Commit Hash.

## `comments.language`
Code comments must follow the configured comment language in profile.yaml. Use English comments for English projects, and use Chinese comments with half-width punctuation for Chinese projects.

## `code.architecture`
Prefer high cohesion, low coupling, clear module boundaries, and concise Doxygen-style API comments when the language or framework supports them.

## `docs.split`
User documentation and developer documentation must remain separate. The root documentation should link to quick start, deployment, and developer-facing references instead of mixing all detail into one file.

## `progress.lifecycle`
Progress entries must move through draft, promotable, and upstreamed states. PROGRESS.md is a sliding index, not a full transcript. Archive older or upstreamed entries instead of expanding the index forever.

## `copilot.style`
Copilot-facing instructions should stay concise, prefer direct edits over long explanations, and prioritize file-level consistency over speculative rewrites.
