# WinStart Pro - 专业工作流启动器

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

WinStart Pro 是一款专为创意工作者（摄影师、设计师、开发者）打造的轻量级 Windows 软件启动管理工具。通过分组管理，实现一键启动整套工作流环境，解决多软件逐个开启的繁琐痛点。

## ✨ 核心特性

- **🎨 现代深色 UI**：精心调配的 Dark Mode 界面，符合专业软件审美，长时间使用不刺眼。
- **🚀 一键工作流**：支持自定义多个工作流（如“修图模式”、“开发模式”），一键启动组内所有软件。
- **📦 零依赖**：基于 Python 标准库 `tkinter` 构建，无需安装任何第三方 pip 包，下载即用。
- **⚡ 极速响应**：底层直接调用 Windows API，启动速度快，占用资源极低。
- **🛠️ 灵活配置**：支持可视化添加、编辑、删除软件路径，支持拖拽排序（规划中）。

## 📸 界面预览

> （此处可插入运行截图）
> *界面采用卡片式布局，清晰展示不同工作流分组。*

## 🚀 快速开始

### 方式一：直接运行源码

1. 确保已安装 [Python 3.x](https://www.python.org/downloads/)。
2. 克隆本项目或下载源码：
   ```bash
   git clone https://github.com/seldomappple-ux/WinStart.git
   cd WinStart
   ```
3. 运行主程序：
   ```bash
   python WinStart.py
   ```

### 方式二：打包为 EXE (可选)

如果你希望生成独立的 `.exe` 文件：

```bash
pip install pyinstaller
pyinstaller -F -w -i icon.ico WinStart.py
```
*(注：需自备 `icon.ico` 图标文件，否则可移除 `-i` 参数)*

## 📖 使用指南

1. **添加软件**：点击卡片右上角的 **⚙️ (设置)** 按钮，选择 **➕ 添加程序**。
2. **选择文件**：支持 `.exe` 可执行文件、`.bat` 批处理脚本或任意快捷方式。
3. **一键启动**：点击卡片底部的 **🚀 一键启动** 按钮，程序将依次启动该组下的所有软件。
4. **管理分组**：点击 **⚙️** 按钮可重命名工作流标题（如将“工作流 1”改为“后期修图”）。

## ⚙️ 配置文件

所有配置自动保存在程序同级目录下的 `winstart_config.json` 文件中。支持手动备份或迁移该文件。

```json
{
  "groups": [
    {
      "title": "🎨 设计模式",
      "apps": [
        {"name": "Photoshop 2024", "path": "C:\\Program Files\\Adobe\\...\\Photoshop.exe"},
        {"name": "Lightroom", "path": "C:\\Program Files\\Adobe\\...\\Lightroom.exe"}
      ]
    }
    // ...
  ]
}
```

## 🛠️ 开发计划

- [ ] 支持拖拽文件直接添加
- [ ] 支持自定义图标
- [ ] 启动延时设置（避免瞬间高负载）
- [ ] 快捷键呼出

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

**作者**：seldomappple-ux  
**版本**：2.0.0 (Refactored)
