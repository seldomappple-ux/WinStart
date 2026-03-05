# -*- coding: utf-8 -*-
"""
WinStart - Windows 软件启动套装工具
功能：管理多个启动套装，一键启动多款软件
技术：Python + tkinter，纯本地运行
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import subprocess
from pathlib import Path


class LaunchGroup:
    """单个启动套装的管理类"""
    
    def __init__(self, parent_frame, title, app_list, on_config_change, group_index):
        self.parent_frame = parent_frame
        self.title = title
        self.app_list = app_list
        self.on_config_change = on_config_change
        self.group_index = group_index
        self.frame = None
        self.listbox = None
        self.create_widget()
    
    def create_widget(self):
        """创建单个启动套装的界面"""
        self.frame = ttk.LabelFrame(self.parent_frame, text=self.title, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(title_frame, text=self.title, font=('Microsoft YaHei', 11, 'bold')).pack(side=tk.LEFT)
        
        menu_btn = ttk.Button(title_frame, text="⋮", width=3, command=self.show_menu)
        menu_btn.pack(side=tk.RIGHT)
        
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Microsoft YaHei', 9),
            selectmode=tk.SINGLE,
            height=12
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.refresh_list()
        
        launch_btn = ttk.Button(
            self.frame,
            text="🚀 启动本组软件",
            command=self.launch_group
        )
        launch_btn.pack(fill=tk.X, pady=(10, 0))
    
    def refresh_list(self):
        """刷新软件列表显示"""
        self.listbox.delete(0, tk.END)
        for app in self.app_list:
            display_name = app.get('name', os.path.basename(app['path']))
            self.listbox.insert(tk.END, display_name)
    
    def show_menu(self):
        """显示三点菜单"""
        menu = tk.Menu(tearoff=0)
        menu.add_command(label="➕ 添加软件路径", command=self.add_app)
        menu.add_command(label="✏️ 修改软件路径", command=self.edit_app)
        menu.add_command(label="🗑️ 删除软件", command=self.delete_app)
        menu.add_separator()
        menu.add_command(label="📝 修改套装名称", command=self.rename_group)
        
        try:
            menu.tk_popup(
                self.frame.winfo_pointerx(),
                self.frame.winfo_pointery()
            )
        finally:
            menu.grab_release()
    
    def add_app(self):
        """添加软件"""
        file_path = filedialog.askopenfilename(
            title="选择要启动的程序",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        
        if file_path:
            app_name = os.path.basename(file_path)
            name = simpledialog.askstring(
                "软件名称",
                "请输入软件显示名称（留空则使用文件名）：",
                initialvalue=app_name
            )
            
            if name is None:
                return
            
            if not name.strip():
                name = app_name
            
            self.app_list.append({
                'name': name,
                'path': file_path
            })
            self.refresh_list()
            self.on_config_change()
    
    def edit_app(self):
        """修改软件路径"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要修改的软件")
            return
        
        index = selection[0]
        current_app = self.app_list[index]
        
        file_path = filedialog.askopenfilename(
            title="选择新的程序路径",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")],
            initialfile=current_app['path']
        )
        
        if file_path:
            new_name = simpledialog.askstring(
                "软件名称",
                "请输入软件显示名称（留空则使用文件名）：",
                initialvalue=current_app['name']
            )
            
            if new_name is None:
                return
            
            if not new_name.strip():
                new_name = os.path.basename(file_path)
            
            self.app_list[index] = {
                'name': new_name,
                'path': file_path
            }
            self.refresh_list()
            self.on_config_change()
    
    def delete_app(self):
        """删除软件"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的软件")
            return
        
        index = selection[0]
        app_name = self.app_list[index]['name']
        
        if messagebox.askyesno("确认删除", f"确定要删除「{app_name}」吗？"):
            del self.app_list[index]
            self.refresh_list()
            self.on_config_change()
    
    def rename_group(self):
        """重命名套装"""
        new_name = simpledialog.askstring(
            "修改套装名称",
            "请输入新的套装名称：",
            initialvalue=self.title
        )
        
        if new_name and new_name.strip():
            self.title = new_name.strip()
            self.frame.config(text=self.title)
            for widget in self.frame.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Label):
                            child.config(text=self.title)
            self.on_config_change()
    
    def launch_group(self):
        """启动本组所有软件"""
        if not self.app_list:
            messagebox.showinfo("提示", "本组暂无软件，请先添加")
            return
        
        success_count = 0
        fail_list = []
        
        for app in self.app_list:
            path = app['path']
            if os.path.exists(path):
                try:
                    subprocess.Popen(
                        f'start "" "{path}"',
                        shell=True,
                        cwd=os.path.dirname(path)
                    )
                    success_count += 1
                except Exception as e:
                    fail_list.append(f"{app['name']}: {str(e)}")
            else:
                fail_list.append(f"{app['name']}: 路径不存在")
        
        if fail_list:
            messagebox.showwarning(
                "启动结果",
                f"成功启动 {success_count} 个软件\n\n失败：\n" + "\n".join(fail_list)
            )
        else:
            messagebox.showinfo("启动成功", f"已启动 {success_count} 个软件")


class WinStartApp:
    """主应用程序类"""
    
    CONFIG_FILE = "winstart_config.json"
    GROUP_COUNT = 3
    
    def __init__(self, root):
        self.root = root
        self.root.title("WinStart - 软件启动套装")
        self.root.geometry("900x500")
        self.root.minsize(700, 400)
        
        self.config = self.load_config()
        self.launch_groups = []
        
        self.setup_style()
        self.create_ui()
    
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TLabelframe', padding=10)
        style.configure('TLabelframe.Label', font=('Microsoft YaHei', 11, 'bold'))
        style.configure('TButton', font=('Microsoft YaHei', 9), padding=5)
        style.configure('TLabel', font=('Microsoft YaHei', 10))
    
    def load_config(self):
        """加载配置文件"""
        config_path = self.get_config_path()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        default_config = {
            'groups': [
                {'title': '启动套装 1', 'apps': []},
                {'title': '启动套装 2', 'apps': []},
                {'title': '启动套装 3', 'apps': []}
            ]
        }
        return default_config
    
    def get_config_path(self):
        """获取配置文件路径"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, self.CONFIG_FILE)
    
    def save_config(self):
        """保存配置文件"""
        config_path = self.get_config_path()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def create_ui(self):
        """创建主界面"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🚀 WinStart - 软件启动套装",
            font=('Microsoft YaHei', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        groups_frame = ttk.Frame(main_frame)
        groups_frame.pack(fill=tk.BOTH, expand=True)
        
        groups_frame.columnconfigure(0, weight=1)
        groups_frame.columnconfigure(1, weight=1)
        groups_frame.columnconfigure(2, weight=1)
        
        for i in range(self.GROUP_COUNT):
            group_data = self.config['groups'][i] if i < len(self.config['groups']) else {'title': f'启动套装 {i+1}', 'apps': []}
            
            group_frame = ttk.Frame(groups_frame)
            group_frame.grid(row=0, column=i, sticky='nsew', padx=5)
            
            launch_group = LaunchGroup(
                group_frame,
                group_data['title'],
                group_data['apps'],
                self.on_config_change,
                i
            )
            self.launch_groups.append(launch_group)
        
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(
            footer_frame,
            text="提示：点击右上角 ⋮ 按钮管理软件列表",
            font=('Microsoft YaHei', 9),
            foreground='gray'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            footer_frame,
            text="💾 保存配置",
            command=self.save_current_config
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            footer_frame,
            text="🔄 刷新界面",
            command=self.refresh_ui
        ).pack(side=tk.RIGHT, padx=5)
    
    def on_config_change(self):
        """配置变更回调"""
        self.config['groups'] = []
        for group in self.launch_groups:
            self.config['groups'].append({
                'title': group.title,
                'apps': group.app_list
            })
        self.save_config()
    
    def save_current_config(self):
        """手动保存配置"""
        self.on_config_change()
        messagebox.showinfo("保存成功", "配置已保存")
    
    def refresh_ui(self):
        """刷新界面"""
        self.config = self.load_config()
        for i, group in enumerate(self.launch_groups):
            if i < len(self.config['groups']):
                group_data = self.config['groups'][i]
                group.title = group_data['title']
                group.app_list = group_data['apps']
                group.refresh_list()
                group.frame.config(text=group.title)


def main():
    """主函数"""
    root = tk.Tk()
    
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = WinStartApp(root)
    
    root.mainloop()


if __name__ == '__main__':
    import sys
    main()
