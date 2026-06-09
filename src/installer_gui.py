import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import win32com.client
import pythoncom
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.startup_manager import ensure_startup_option_in_task_manager

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def copy_application_files(source_dir, fallback_exe, install_dir):
    if os.path.isdir(source_dir):
        for name in os.listdir(install_dir):
            path = os.path.join(install_dir, name)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except OSError:
                pass
        shutil.copytree(source_dir, install_dir, dirs_exist_ok=True)
        return os.path.join(install_dir, "WinStart.exe")

    target_exe = os.path.join(install_dir, "WinStart.exe")
    if not os.path.exists(fallback_exe):
        raise FileNotFoundError("Source file not found: WinStart.exe")
    if os.path.exists(target_exe):
        try:
            os.remove(target_exe)
        except OSError:
            pass
    shutil.copy2(fallback_exe, target_exe)
    return target_exe

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinStart Setup / 安装向导")
        # Increased height to ensure button is visible
        self.root.geometry("500x380")
        self.root.resizable(False, False)
        
        # Center the window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 380) // 2
        root.geometry(f"500x380+{x}+{y}")

        # Styles
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        
        # Header
        header_frame = tk.Frame(root, bg="#f0f0f0", height=80)
        header_frame.pack(fill=tk.X)
        
        # Bilingual Title
        title_label = tk.Label(header_frame, text="WinStart Setup\nWinStart 安装向导", 
                             font=("Microsoft YaHei", 14, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)
        
        # Main Content
        content_frame = tk.Frame(root, padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(content_frame, text="Ready to install / 准备安装")
        self.status_label.pack(pady=(0, 10), anchor="w")
        
        self.progress = ttk.Progressbar(content_frame, mode='determinate', length=440)
        self.progress.pack(pady=(0, 20))
        
        # Bilingual Options
        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        self.desktop_check = ttk.Checkbutton(content_frame, 
                                           text="Create desktop shortcut / 创建桌面快捷方式", 
                                           variable=self.desktop_shortcut_var)
        self.desktop_check.pack(anchor="w", pady=8)
        
        self.startmenu_shortcut_var = tk.BooleanVar(value=True)
        self.startmenu_check = ttk.Checkbutton(content_frame, 
                                             text="Create start menu shortcut / 创建开始菜单快捷方式", 
                                             variable=self.startmenu_shortcut_var)
        self.startmenu_check.pack(anchor="w", pady=8)
        
        # Install Button
        # Pack at the bottom with enough padding
        self.install_btn = ttk.Button(root, text="Install / 开始安装", command=self.start_install)
        self.install_btn.pack(side=tk.BOTTOM, pady=30)

    def create_shortcut(self, target_path, shortcut_path, description="WinStart"):
        try:
            os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.Description = description
            shortcut.IconLocation = target_path
            shortcut.Save()
            return True
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            raise

    def get_desktop_dir(self):
        shell = win32com.client.Dispatch("WScript.Shell")
        return shell.SpecialFolders("Desktop")

    def start_install(self):
        self.install_btn.config(state="disabled")
        self.desktop_check.config(state="disabled")
        self.startmenu_check.config(state="disabled")
        threading.Thread(target=self.install_process, daemon=True).start()

    def install_process(self):
        pythoncom.CoInitialize()
        try:
            # 1. Prepare Paths (User level installation)
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
            install_dir = os.path.join(local_appdata, "WinStart")
            exe_name = "WinStart.exe"
            
            self.update_status("Creating installation directory... / 正在创建安装目录...", 10)
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
            
            # 2. Extract Files
            self.update_status("Copying files... / 正在复制文件...", 30)
            source_dir = get_resource_path("WinStart_app")
            source_exe = get_resource_path(exe_name)
            if not os.path.exists(source_exe):
                source_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", exe_name)
            target_exe = copy_application_files(source_dir, source_exe, install_dir)
            self.update_status("Files copied / 文件复制完成", 60)

            # Register startup entry immediately so Task Manager can enable/disable it
            self.update_status("Registering startup option... / 正在注册启动项...", 68)
            ensure_startup_option_in_task_manager(target_exe, "WinStart")
            
            # 3. Create Shortcuts
            self.update_status("Creating shortcuts... / 正在创建快捷方式...", 70)
            desktop = self.get_desktop_dir()
            
            if self.startmenu_shortcut_var.get():
                start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "WinStart")
                self.create_shortcut(target_exe, os.path.join(start_menu, "WinStart.lnk"))
            
            if self.desktop_shortcut_var.get():
                self.create_shortcut(target_exe, os.path.join(desktop, "WinStart.lnk"))
            
            self.update_status("Finishing up... / 即将完成...", 90)
            
            # 4. Create Uninstaller (Simple batch script)
            uninstall_script = os.path.join(install_dir, "uninstall.bat")
            with open(uninstall_script, "w", encoding="utf-8") as f:
                f.write('@echo off\n')
                f.write('chcp 65001 >nul\n')  # Ensure UTF-8 for Chinese characters
                f.write('echo Uninstalling WinStart... / 正在卸载 WinStart...\n')
                f.write('taskkill /F /IM WinStart.exe >nul 2>&1\n')
                f.write('reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WinStart" /f >nul 2>&1\n')
                f.write('reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run" /v "WinStart" /f >nul 2>&1\n')
                f.write(f'del "{os.path.join(desktop, "WinStart.lnk")}"\n')
                f.write(f'rmdir /s /q "{os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "WinStart")}"\n')
                # Self-delete logic
                f.write('echo Uninstallation complete, cleaning up... / 卸载完成，正在清理...\n')
                f.write('timeout /t 2 /nobreak >nul\n')
                f.write(f'rmdir /s /q "{install_dir}"\n')
            
            self.update_status("Installation complete! / 安装完成!", 100)
            messagebox.showinfo("Success / 成功", f"WinStart has been successfully installed!\n\nInstall path:\n{target_exe}")
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Error / 错误", f"Installation failed / 安装失败:\n{str(e)}")
            self.root.quit()
        finally:
            pythoncom.CoUninitialize()

    def update_status(self, text, value):
        self.status_label.config(text=text)
        self.progress['value'] = value
        self.root.update_idletasks()
        time.sleep(0.5) # Simulate work for better UX

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
