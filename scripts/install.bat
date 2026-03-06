@echo off
chcp 65001 >nul

echo ========================================
echo          WinStart 安装程序
echo ========================================
echo.

echo 正在准备安装 WinStart...
echo.

REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员权限运行此安装程序
    echo 右键点击 -> "以管理员身份运行"
    pause
    exit /b 1
)

REM 设置安装目录
set "INSTALL_DIR=%ProgramFiles%\WinStart"

REM 创建安装目录
echo 创建安装目录: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM 复制主程序
echo 复制主程序...
copy "%~dp0..\dist\WinStart.exe" "%INSTALL_DIR%\" >nul

REM 创建开始菜单快捷方式
echo 创建开始菜单快捷方式...
set "START_MENU_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\WinStart"
if not exist "%START_MENU_DIR%" mkdir "%START_MENU_DIR%"

echo [InternetShortcut] > "%START_MENU_DIR%\WinStart.url"
echo URL=file:///%INSTALL_DIR%/WinStart.exe >> "%START_MENU_DIR%\WinStart.url"
echo IconIndex=0 >> "%START_MENU_DIR%\WinStart.url"
echo IconFile=%INSTALL_DIR%\WinStart.exe >> "%START_MENU_DIR%\WinStart.url"

REM 创建桌面快捷方式（可选）
set /p "CREATE_DESKTOP=是否创建桌面快捷方式? (y/n): "
if /i "%CREATE_DESKTOP%"=="y" (
    echo 创建桌面快捷方式...
    echo [InternetShortcut] > "%USERPROFILE%\Desktop\WinStart.url"
    echo URL=file:///%INSTALL_DIR%/WinStart.exe >> "%USERPROFILE%\Desktop\WinStart.url"
    echo IconIndex=0 >> "%USERPROFILE%\Desktop\WinStart.url"
    echo IconFile=%INSTALL_DIR%\WinStart.exe >> "%USERPROFILE%\Desktop\WinStart.url"
)

REM 创建卸载脚本
echo 创建卸载程序...
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo chcp 65001 ^>nul >> "%INSTALL_DIR%\uninstall.bat"
echo echo 正在卸载 WinStart... >> "%INSTALL_DIR%\uninstall.bat"
echo echo. >> "%INSTALL_DIR%\uninstall.bat"
echo del "%START_MENU_DIR%\WinStart.url" >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%USERPROFILE%\Desktop\WinStart.url" del "%USERPROFILE%\Desktop\WinStart.url" >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir "%START_MENU_DIR%" 2^>nul >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir "%INSTALL_DIR%" /s /q >> "%INSTALL_DIR%\uninstall.bat"
echo echo 卸载完成! >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

echo.
echo ========================================
echo       安装完成!
echo ========================================
echo.
echo 程序已安装到: %INSTALL_DIR%
echo 开始菜单快捷方式已创建
echo.
echo 要卸载程序，请运行: %INSTALL_DIR%\uninstall.bat
echo.
echo 按任意键启动 WinStart...
pause >nul

REM 启动程序
start "" "%INSTALL_DIR%\WinStart.exe"

echo.
echo 谢谢使用 WinStart!
pause