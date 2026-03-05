@echo off
chcp 65001 >nul
REM ============================================
REM WinStart - Windows 开机自启动脚本
REM 功能：开机登录后按顺序启动多个软件
REM ============================================

REM 等待系统完全启动（可选，单位：秒）
REM 如果开机后软件启动失败，可以适当增加等待时间
timeout /t 3 /nobreak >nul

REM ============================================
REM 启动项目列表（按顺序执行）
REM 格式：start "" "程序完整路径"
REM ============================================

REM 示例1：启动浏览器（请替换为你的实际路径）
REM start "" "C:\Program Files\Google\Chrome\Application\chrome.exe"

REM 示例2：启动微信
REM start "" "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"

REM 示例3：启动记事本（测试用）
REM start "" "C:\Windows\System32\notepad.exe"

REM ============================================
REM 在下方添加你的启动项
REM 复制上面的格式，修改路径即可
REM ============================================

REM 启动项 1
REM start "" "这里填写程序完整路径"

REM 启动项 2
REM start "" "这里填写程序完整路径"

REM 启动项 3
REM start "" "这里填写程序完整路径"

REM ============================================
REM 启动完成
REM ============================================
echo WinStart 启动完成
