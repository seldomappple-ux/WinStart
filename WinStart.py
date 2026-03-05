# -*- coding: utf-8 -*-
"""
WinStart - 专业级工作流启动器 (Professional Workflow Launcher)
=========================================================

项目背景：
    专为创意工作者（摄影师、设计师、开发者）打造的轻量级启动工具。
    解决 Windows 启动项管理混乱、第三方工具臃肿的问题。
    支持一键启动整套设计/渲染/开发软件环境。

核心特性：
    1. 极简主义设计：深色模式、卡片式布局、现代 UI 风格。
    2. 纯净无依赖：基于 Python 标准库 tkinter 构建，无需 pip install。
    3. 灵活分组：支持自定义多组工作流（如：修图模式、建模模式、开发模式）。
    4. 稳定高效：底层调用 Windows 原生启动命令，响应迅速。

作者：seldomappple-ux
版本：2.0.0 (Refactored)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import subprocess
import sys
from pathlib import Path

# --- 配置常量 (UI Design System) ---
class Theme:
    """深色主题设计系统"""
    # 基础色调
    BG_COLOR = "#1e1e1e"          # 窗口背景深灰
    CARD_BG = "#252526"           # 卡片背景（稍亮）
    HEADER_BG = "#333333"         # 标题栏背景
    
    # 文字颜色
    TEXT_PRIMARY = "#ffffff"      # 主要文字
    TEXT_SECONDARY = "#cccccc"    # 次要文字
    TEXT_HINT = "#858585"         # 提示文字
    
    # 交互色
    ACCENT_COLOR = "#007acc"      # 强调色 (VS Code Blue)
    ACCENT_HOVER = "#0098ff"      # 悬停色
    DANGER_COLOR = "#f44336"      # 危险色
    SUCCESS_COLOR = "#4caf50"     # 成功色
    
    # 字体配置
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_H1 = (FONT_FAMILY, 16, "bold")
    FONT_H2 = (FONT_FAMILY, 12, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_SMALL = (FONT_FAMILY, 9)
    
    # 布局参数
    PADDING_MAIN = 20
    PADDING_CARD = 15
    GAP = 10

class ConfigManager:
    """配置管理模块：负责数据的持久化"""
    
    CONFIG_FILE = "winstart_config.json"
    DEFAULT_GROUPS = [
        {'title': '🎨 设计模式', 'apps': []},
        {'title': '💻 开发模式', 'apps': []},
        {'title': '🎮 娱乐模式', 'apps': []}
    ]

    @classmethod
    def get_config_path(cls):
        """获取配置文件绝对路径，兼容打包环境"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, cls.CONFIG_FILE)

    @classmethod
    def load(cls):
        """加载配置"""
        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 简单校验数据结构
                    if 'groups' in data and isinstance(data['groups'], list):
                        return data
            except Exception as e:
                print(f"[Config] Load failed: {e}")
        
        return {'groups': cls.DEFAULT_GROUPS}

    @classmethod
    def save(cls, data):
        """保存配置"""
        path = cls.get_config_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[Config] Save failed: {e}")
            return False

class AppLauncher:
    """业务逻辑模块：负责软件启动"""
    
    @staticmethod
    def launch_app(path):
        """启动单个应用"""
        if not os.path.exists(path):
            return False, "路径不存在"
        
        try:
            # 使用 start 命令启动，非阻塞，且不依赖 python 进程
            # cwd 设置为程序所在目录，避免某些程序读不到相对路径资源
            subprocess.Popen(
                f'start "" "{path}"',
                shell=True,
                cwd=os.path.dirname(path)
            )
            return True, "启动成功"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def launch_group(app_list):
        """批量启动一组应用"""
        results = {'success': 0, 'fail': []}
        
        for app in app_list:
            ok, msg = AppLauncher.launch_app(app['path'])
            if ok:
                results['success'] += 1
            else:
                results['fail'].append(f"{app['name']}: {msg}")
        return results

class ModernButton(tk.Button):
    """自定义现代风格按钮（模拟 hover 效果）"""
    def __init__(self, master, bg=Theme.ACCENT_COLOR, fg=Theme.TEXT_PRIMARY, hover_bg=Theme.ACCENT_HOVER, **kwargs):
        super().__init__(
            master, 
            bg=bg, 
            fg=fg, 
            activebackground=hover_bg,
            activeforeground=fg,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=Theme.FONT_BODY,
            **kwargs
        )
        self.default_bg = bg
        self.hover_bg = hover_bg
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self.hover_bg

    def on_leave(self, e):
        self['background'] = self.default_bg

class WorkflowCard(tk.Frame):
    """单个工作流卡片组件"""
    
    def __init__(self, parent, title, app_list, on_update, index):
        super().__init__(parent, bg=Theme.CARD_BG, padx=1, pady=1) # 1px border simulation
        self.title = title
        self.app_list = app_list
        self.on_update = on_update
        self.index = index
        
        # 内部容器（用于实现边框效果，如果有需要的话。这里直接用 Frame 背景）
        self.container = tk.Frame(self, bg=Theme.CARD_BG)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self._create_header()
        self._create_list()
        self._create_footer()
        
    def _create_header(self):
        """卡片头部"""
        header = tk.Frame(self.container, bg=Theme.CARD_BG)
        header.pack(fill=tk.X, pady=(Theme.PADDING_CARD, 10), padx=Theme.PADDING_CARD)
        
        # 标题
        self.lbl_title = tk.Label(
            header, 
            text=self.title, 
            font=Theme.FONT_H2, 
            bg=Theme.CARD_BG, 
            fg=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 菜单按钮
        btn_menu = tk.Label(
            header,
            text="⚙️",
            font=Theme.FONT_BODY,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_SECONDARY,
            cursor="hand2"
        )
        btn_menu.pack(side=tk.RIGHT)
        btn_menu.bind("<Button-1>", lambda e: self._show_menu(e))
        
    def _create_list(self):
        """软件列表"""
        list_frame = tk.Frame(self.container, bg=Theme.CARD_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=Theme.PADDING_CARD)
        
        # 滚动条样式定制（使用原生 Listbox 配合深色）
        self.listbox = tk.Listbox(
            list_frame,
            font=Theme.FONT_BODY,
            bg="#2d2d30",            # 列表背景比卡片略深
            fg=Theme.TEXT_PRIMARY,
            selectbackground=Theme.ACCENT_COLOR,
            selectforeground=Theme.TEXT_PRIMARY,
            highlightthickness=0,
            relief=tk.FLAT,
            height=10,
            activestyle="none"       # 去除选中时的下划线
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 简单的滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.refresh_list()
        
    def _create_footer(self):
        """底部启动按钮"""
        footer = tk.Frame(self.container, bg=Theme.CARD_BG)
        footer.pack(fill=tk.X, padx=Theme.PADDING_CARD, pady=Theme.PADDING_CARD)
        
        self.btn_launch = ModernButton(
            footer,
            text="🚀 一键启动",
            command=self._launch_workflow,
            height=2
        )
        self.btn_launch.pack(fill=tk.X)

    def refresh_list(self):
        """刷新列表数据"""
        self.listbox.delete(0, tk.END)
        for app in self.app_list:
            icon = "📄"
            if app['path'].lower().endswith('.exe'):
                icon = "📦"
            elif app['path'].lower().endswith('.bat'):
                icon = "⚙️"
                
            self.listbox.insert(tk.END, f" {icon}  {app['name']}")

    def _launch_workflow(self):
        """启动逻辑"""
        if not self.app_list:
            messagebox.showinfo("提示", "该工作流暂无软件，请点击右上角齿轮添加。")
            return
            
        res = AppLauncher.launch_group(self.app_list)
        
        if res['fail']:
            msg = f"已启动 {res['success']} 个应用。\n以下启动失败：\n" + "\n".join(res['fail'])
            messagebox.showwarning("启动报告", msg)
        else:
            # 成功反馈：短暂改变按钮颜色或弹窗（这里选择弹窗更稳妥，但可以优化体验）
            # messagebox.showinfo("完成", f"工作流「{self.title}」已全部启动！")
            # 这种工具类软件最好是无打扰的，所以如果不报错，就不弹窗，只在控制台或状态栏显示
            # 鉴于当前没有状态栏，还是弹个自动关闭的窗或者只在失败时弹窗比较好
            # 这里为了用户感知，我们做个简单的 Print，或者只在失败时弹窗
            pass 

    def _show_menu(self, event):
        """上下文菜单"""
        menu = tk.Menu(self, tearoff=0, bg=Theme.CARD_BG, fg=Theme.TEXT_PRIMARY, activebackground=Theme.ACCENT_COLOR)
        menu.add_command(label="➕ 添加程序", command=self._add_app)
        menu.add_command(label="✏️ 编辑选中", command=self._edit_app)
        menu.add_command(label="🗑️ 删除选中", command=self._delete_app)
        menu.add_separator()
        menu.add_command(label="🏷️ 重命名工作流", command=self._rename_group)
        menu.post(event.x_root, event.y_root)

    def _add_app(self):
        path = filedialog.askopenfilename(
            title="选择应用程序",
            filetypes=[("可执行文件", "*.exe;*.bat;*.cmd"), ("所有文件", "*.*")]
        )
        if path:
            default_name = os.path.splitext(os.path.basename(path))[0]
            name = simpledialog.askstring("添加程序", "请输入显示名称：", initialvalue=default_name)
            if name:
                self.app_list.append({'name': name, 'path': path})
                self.refresh_list()
                self.on_update()

    def _edit_app(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        app = self.app_list[idx]
        
        new_path = filedialog.askopenfilename(initialfile=app['path'])
        if new_path:
            new_name = simpledialog.askstring("编辑程序", "显示名称：", initialvalue=app['name'])
            if new_name:
                self.app_list[idx] = {'name': new_name, 'path': new_path}
                self.refresh_list()
                self.on_update()

    def _delete_app(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        if messagebox.askyesno("确认", f"删除「{self.app_list[idx]['name']}」？"):
            self.app_list.pop(idx)
            self.refresh_list()
            self.on_update()

    def _rename_group(self):
        new_title = simpledialog.askstring("重命名", "请输入新的工作流名称：", initialvalue=self.title)
        if new_title:
            self.title = new_title
            self.lbl_title.config(text=new_title)
            self.on_update()

class WinStartPro:
    """主程序"""
    
    def __init__(self, root):
        self.root = root
        self.config_data = ConfigManager.load()
        self.cards = []
        
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self):
        self.root.title("WinStart Pro")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        self.root.configure(bg=Theme.BG_COLOR)
        
        # 尝试设置图标（如果有）
        # try: self.root.iconbitmap('icon.ico')
        # except: pass
        
        # 配置全局样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 滚动条深色适配（ttk比较难完全定制深色滚动条，这里做个基础适配）
        style.configure("Vertical.TScrollbar", gripcount=0, background="#444", darkcolor="#444", lightcolor="#444", troughcolor="#2d2d30", bordercolor="#2d2d30", arrowcolor="white")

    def _setup_ui(self):
        # 1. 顶部 Header
        header = tk.Frame(self.root, bg=Theme.BG_COLOR, height=60)
        header.pack(fill=tk.X, padx=Theme.PADDING_MAIN, pady=(Theme.PADDING_MAIN, 0))
        
        tk.Label(
            header, 
            text="WinStart Pro", 
            font=Theme.FONT_H1, 
            bg=Theme.BG_COLOR, 
            fg=Theme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header,
            text=" |  Your Workflow Launcher",
            font=Theme.FONT_BODY,
            bg=Theme.BG_COLOR,
            fg=Theme.TEXT_HINT
        ).pack(side=tk.LEFT, padx=10, pady=(6,0)) # 微调对齐
        
        # 2. 内容区域 (Grid Layout)
        content = tk.Frame(self.root, bg=Theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=Theme.PADDING_MAIN, pady=Theme.PADDING_MAIN)
        
        # 动态创建 3 列布局
        for i in range(3):
            content.columnconfigure(i, weight=1)
            
            # 获取或初始化组数据
            if i < len(self.config_data['groups']):
                group = self.config_data['groups'][i]
            else:
                group = {'title': f'工作流 {i+1}', 'apps': []}
                self.config_data['groups'].append(group)
            
            # 创建卡片
            card_frame = tk.Frame(content, bg=Theme.BG_COLOR)
            card_frame.grid(row=0, column=i, sticky="nsew", padx=Theme.GAP)
            
            card = WorkflowCard(
                card_frame,
                title=group['title'],
                app_list=group['apps'],
                on_update=self._save_config,
                index=i
            )
            card.pack(fill=tk.BOTH, expand=True)
            self.cards.append(card)

        # 3. 底部状态栏
        status_bar = tk.Frame(self.root, bg=Theme.BG_COLOR)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=Theme.PADDING_MAIN, pady=(0, 10))
        
        tk.Label(
            status_bar,
            text="Ready to launch.",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_COLOR,
            fg=Theme.TEXT_HINT
        ).pack(side=tk.LEFT)
        
        tk.Label(
            status_bar,
            text="v2.0.0",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_COLOR,
            fg=Theme.TEXT_HINT
        ).pack(side=tk.RIGHT)

    def _save_config(self):
        """保存当前状态"""
        # 更新数据模型
        new_groups = []
        for card in self.cards:
            new_groups.append({
                'title': card.title,
                'apps': card.app_list
            })
        self.config_data['groups'] = new_groups
        ConfigManager.save(self.config_data)

def main():
    root = tk.Tk()
    app = WinStartPro(root)
    root.mainloop()

if __name__ == '__main__':
    main()
