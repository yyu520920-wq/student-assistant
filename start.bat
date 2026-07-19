@echo off
chcp 65001 >nul
title 大学日程计划 v1.3
cd /d "%~dp0"
echo.
echo  📚 大学日程计划 v1.3 启动中...
echo.
python start.py %1
pause
