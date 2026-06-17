# WinStart

WinStart 是一款轻量级的 Windows 一键启动工具，专为创作者和极简主义者设计。它可以帮助你快速启动整套工作流软件，无需在混乱的桌面或开始菜单中寻找程序。
<img width="1367" height="808" alt="image" src="https://github.com/user-attachments/assets/bb6dff33-d056-4be2-87cf-56ce0530aa5f" />

## ✨ 特性

- **分组管理**：创建不同的启动分组（如“设计工作”、“游戏娱乐”），按需启动。
- **一键启动**：一键启动分组内的所有程序，支持设置启动延迟。
- **极简设计**：采用现代深色主题，界面干净、无干扰。
- **灵活配置**：轻松添加、修改、排序和删除启动项。
- **轻量便携**：目录版免安装运行，配置本地存储，随身携带。

## 🚀 快速开始

### 运行环境

- Windows 10/11
- Python 3.9+ (如果从源码运行)

### 从源码运行

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/WinStart.git
   cd WinStart
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行程序：
   ```bash
   python src/main.py
   ```

### 构建可执行文件

使用统一发布脚本打包，主程序固定为 PyInstaller `onedir` 目录版，避免日常退出时触发 onefile `_MEI` 临时目录清理告警：

```bash
python scripts/build_icon.py
.\scripts\build_release.ps1 -Version 3.0.5
```

生成的正式发布文件为 `dist/WinStart_v3.0.5.zip` 和 `dist/WinStart_Setup_v3.0.5.exe`。
`dist/WinStart/WinStart.exe` 是目录版主程序，旁边必须保留 `_internal/` 依赖目录；不要把它单独拷走运行。
不要再发布 `WinStart_v*.exe` 这种单文件主程序，否则仍可能触发 PyInstaller onefile `_MEI` 清理警告。
图标资源位于 `assets/app_icon.ico` 和 `assets/app_icon.png`。
如果你有原始长图标，请放到 `assets/app_icon_source.png`，会自动等比缩放并留白，不会拉伸变形。
如果任务栏仍显示旧图标，请先取消固定旧图标，再重新固定安装后的 `%LOCALAPPDATA%\WinStart\WinStart.exe` 或便携目录中的 `WinStart.exe`。

### 开机自启动

- WinStart 默认不会开机自启动
- 安装后会出现在"任务管理器 -> 启动应用"列表里，状态默认为禁用
- 你可以在任务管理器中手动启用或禁用 WinStart 开机自启动

## 🛠️ 技术栈

- **Python**: 核心逻辑
- **PySide6 (Qt)**: 现代化 GUI 界面
- **JSON**: 本地数据存储

## 📝 许可证

MIT License
