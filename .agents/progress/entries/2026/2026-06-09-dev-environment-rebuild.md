---
page_id: WS-2026-06-09-002
date: 2026-06-09
title: 新电脑开发环境重建
status: draft
related_commit_message: "chore(dev-env): rebuild local python environment"
related_commit_hash: ""
upstream_reference: ""
keywords:
  - dev-environment
  - python
  - venv
  - pip
  - dependencies
  - migration
---

用户迁移到新电脑后要求检查当前项目开发环境是否完备, 缺失项直接补齐。

问题确认:

- 仓库中的 `.venv` 是旧电脑迁移过来的虚拟环境, `pyvenv.cfg` 指向 `C:\Users\L_W\AppData\Local\Programs\Python\Python313\python.exe`, 当前机器不存在该解释器。
- 当前机器虽然已通过 winget 安装 `Python 3.12.10`, 但 `py` launcher 和 PATH 未立即识别, 需要使用完整路径 `C:\Users\Wuyu\AppData\Local\Programs\Python\Python312\python.exe` 重建虚拟环境。
- 默认 PyPI 链路执行 `pip install -r requirements.txt` 多次长时间无输出并超时, 但清华源可正常访问和安装。

处理结果:

- 删除旧 `.venv`, 使用当前机器 Python 3.12.10 重建项目虚拟环境。
- 安装 `requirements.txt` 中的运行和打包依赖: `PySide6`, `Pillow`, `pyinstaller`, `pywin32`。
- 将当前 `.venv` 的 site 级 pip 源设置为 `https://pypi.tuna.tsinghua.edu.cn/simple`, 避免后续安装再次卡在默认 PyPI 链路。
- 更新 `.gitignore`, 增加 `.venv/`, 防止本地虚拟环境进入 Git。

验证:

- `python --version`: `Python 3.12.10`。
- `pip check`: 无破损依赖。
- 关键 import 验证通过: `PySide6`, `PIL`, `PyInstaller`, `win32com.client`。
- `scripts/build_icon.py` 可运行。
- Qt 离屏模式下 `MainWindow` 初始化通过。

注意:

- `.venv` 是本机环境, 不应提交。
- 若新机器 pip 安装再次卡住, 优先确认 `.venv\pip.ini` 是否仍指向清华源。
