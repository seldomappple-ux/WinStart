# START HERE

这是 `WinStart` 项目给人和 AI 共用的启动入口。

如果你是在新的 IDE、新的 AI 会话或新的账号里接手这个项目，请先按下面的顺序读取本地文件，不要先递归扫描整个仓库，也不要一上来就直接改代码。

## 给 AI 的固定启动指令

把下面这段原样发给 AI 即可：

```text
请先阅读 START_HERE.md，然后严格按其中的“本地读取顺序”读取文件。
先不要修改任何文件，先输出：
1. 项目定位
2. 当前规则和红线
3. 当前版本和最近进展
4. 如果继续开发，应该改哪一层
5. 我现在最适合做的下一步
```

## 本地读取顺序

1. `START_HERE.md`
2. `README.md`
3. `.agents/profile.yaml`
4. `.agents/RULES.md`
5. `.agents/architecture-decisions.yaml`
6. `.agents/PROGRESS.md`
7. `PROGRESS.md`
8. `USER_GUIDE.md`
9. `RELEASE_NOTES.md`
10. `src/main.py`
11. `src/core/`
12. `src/ui/`
13. `AGENTS.md`
14. `CLAUDE.md` / `GEMINI.md` / `.cursor/` / `.github/` 中实际存在的适配文件

## 当前项目定位

- 项目名称: `WinStart`
- 项目类型: `纯软件 (software)`
- 目标平台: `Windows`
- 技术栈: `Python`, `PySide6`, `PyInstaller`
- 项目说明: 这是一个轻量级 Windows 一键启动工具, 用固定卡槽管理启动项并支持一键批量启动。

## 当前仓库重点

- 业务代码以 `src/core/` 和 `src/ui/` 为主。
- 打包、安装和图标产物分布在 `scripts/`, `assets/`, `WinStart.spec`。
- 根目录现有文档仍然是给人看的主文档, `.agents/` 主要负责治理、接手和持续记忆。

## 本地 skills

- `.agents/skills/project-onboarding/SKILL.md`: 规范接手顺序, 先读规则和上下文再动手。
- `.agents/skills/progress-tracker/SKILL.md`: 记录关键实现背景、边界和踩坑。
- `.agents/skills/software-delivery/SKILL.md`: 帮助把改动落到正确的代码层和文档层。

## 这套治理骨架来自哪里

这个项目的治理层来自本机的 `Taotaotao` 工具仓:

- `D:\code\VS Code\Taotaotao`

如果你需要理解这套治理体系本身为什么这样设计，再去看那个仓库里的:

1. `README.md`
2. `AI_QUICKSTART.md`
3. `ARCHITECTURE.md`
4. `docs/GOVERNANCE_RULES.md`

## 工作纪律

- 先读本地文件, 再动手。
- 优先修改 `.agents/` 真源和业务代码, 不直接改受管生成文件。
- 功能、配置结构、安装流程有 durable 变化时, 及时写 progress entry。
