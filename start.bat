@echo off
chcp 65001 >nul
title 大学日程计划 v3.0
cd /d "%~dp0"
echo.
echo  📚 大学日程计划 v3.0 启动中...
echo.
python start.py %1
pause
