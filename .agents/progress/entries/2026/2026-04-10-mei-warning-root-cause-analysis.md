---
page_id: WS-2026-04-10-002
date: 2026-04-10
title: _MEI 临时目录清理告警根因分析
status: draft
related_commit_message: "docs(runtime): analyze root cause of persistent _MEI cleanup warning"
related_commit_hash: ""
upstream_reference: "WS-2026-04-09-001, WS-2026-04-10-001"
keywords:
  - pyinstaller
  - _MEI
  - temp
  - qt
  - threading
  - resource-cleanup
---

## 问题回顾

用户在 2026-04-10 再次反馈 `_MEI` 临时目录清理告警，截图显示路径仍为 `C:\Users\20271\AppData\Local\Temp\_MEI71442`，说明前期的缓解方案未在实际运行中生效。

## 代码审查发现

### 1. 配置已存在但未生效（首要问题）

**证据**：
- `WinStart.spec:35` 已配置 `runtime_tmpdir=os.path.join('%LOCALAPPDATA%', 'WinStart', '_runtime')`
- 用户截图显示路径仍落在系统 `%TEMP%` 下，而非 `%LOCALAPPDATA%\WinStart\_runtime`

**结论**：
- 用户测试的 exe 极可能不是用当前 `.spec` 文件打包的最新版本
- 或打包过程中 `runtime_tmpdir` 参数未被 PyInstaller 正确应用

### 2. Qt 资源清理时序问题（次要但持久）

即使临时目录迁移生效，以下代码模式仍可能导致退出时资源占用：

**后台线程**：
- `src/core/launcher.py:14` 使用 `daemon=True` 的后台线程启动程序
- 线程中的 `subprocess.Popen` 或 `os.startfile` 可能在主进程退出时仍持有 VC++ 运行时 DLL 的文件句柄
- 虽然是 daemon 线程，但 Windows 的文件句柄释放有内核级延迟

**Qt 定时器**：
- `src/ui/main_window.py:57,66` 使用 `QTimer.singleShot` 延迟加载卡片
- 如果用户在卡片加载过程中关闭窗口，定时器回调可能还在事件队列中
- Qt 事件循环退出时，未完成的定时器可能导致资源清理延迟

**退出流程**：
- `src/main.py:36` 使用 `sys.exit(app.exec())` 直接退出
- Qt 的事件循环退出后，资源清理不是立即完成的
- PyInstaller bootloader 在主进程退出时立即尝试删除 `_MEI` 目录，时机过于激进

## 根本原因推测

**主因**：用户运行的 exe 不是最新打包版本，`runtime_tmpdir` 配置未生效

**次因**：Qt 应用的异步资源（后台线程、定时器、事件循环）在退出时未完全释放，导致 VC++ 运行时 DLL 仍被占用

## 建议的验证与改进方案

### 立即验证
1. 确认用户是否使用 `pyinstaller WinStart.spec` 重新打包了 exe
2. 检查新打包的 exe 运行时是否真的在 `%LOCALAPPDATA%\WinStart\_runtime` 下解压

### 代码改进（如果迁移目录后仍有问题）

在 `src/main.py` 中改进退出逻辑，给 Qt 更多时间清理资源：

```python
def main():
    # ... 现有代码 ...
    
    window = MainWindow()
    window.show()
    
    exit_code = app.exec()
    
    # 给 Qt 事件循环一点时间处理剩余事件和清理资源
    app.processEvents()
    
    sys.exit(exit_code)
```

或考虑在 `MainWindow.closeEvent` 中显式清理资源：

```python
def closeEvent(self, event):
    # 取消所有待处理的定时器
    self.pending_card_loads.clear()
    
    # 等待后台线程（如果有非 daemon 线程）
    # ...
    
    event.accept()
```

### 长期方案

如果上述方案仍无法完全消除告警，可考虑：
- 放弃 `--onefile` 模式，改用 `--onedir` 分发（无需运行时解压）
- 或接受该告警为 PyInstaller onefile 模式的固有限制，在用户文档中说明

## 下一步行动

1. 优先验证用户是否使用了最新打包的 exe
2. 如果确认使用最新版但路径仍在 `%TEMP%`，需排查 PyInstaller 对 `runtime_tmpdir` 参数的支持情况
3. 如果迁移目录后告警仍存在，再实施退出逻辑改进
