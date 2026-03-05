# WinStart

WinStart 是一款轻量级的 Windows 一键启动工具，专为创作者和极简主义者设计。它可以帮助你快速启动整套工作流软件，无需在混乱的桌面或开始菜单中寻找程序。

## ✨ 特性

- **分组管理**：创建不同的启动分组（如“设计工作”、“游戏娱乐”），按需启动。
- **一键启动**：一键启动分组内的所有程序，支持设置启动延迟。
- **极简设计**：采用现代深色主题，界面干净、无干扰。
- **灵活配置**：轻松添加、修改、排序和删除启动项。
- **轻量便携**：单文件运行，配置本地存储，随身携带。

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

使用 PyInstaller 打包为单文件 exe：

```bash
python scripts/build_icon.py
pyinstaller --noconfirm --onefile --windowed --name "WinStart" --icon "assets/app_icon.ico" --add-data "src:src" --add-data "assets:assets" src/main.py
```

生成的文件位于 `dist/WinStart.exe`。
图标资源位于 `assets/app_icon.ico` 和 `assets/app_icon.png`。
如果你有原始长图标，请放到 `assets/app_icon_source.png`，会自动等比缩放并留白，不会拉伸变形。
如果任务栏仍显示旧图标，请先取消固定旧图标，再重新固定 `dist/WinStart.exe`。

### 开机自启动

- WinStart 默认不会开机自启动。
- 安装后会出现在“任务管理器 -> 启动应用”列表里，状态默认为禁用。
- 你可以在任务管理器中手动启用或禁用 WinStart 开机自启动。

## 🛠️ 技术栈

- **Python**: 核心逻辑
- **PySide6 (Qt)**: 现代化 GUI 界面
- **JSON**: 本地数据存储

## 📝 许可证

MIT License
