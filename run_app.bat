@echo off

chcp 65001 >nul

setlocal EnableExtensions

title 工业互联网可视化平台 - 一键启动

color 0A

set "PROJECT_DIR=E:\industrial_platform_demo"

set "BACKEND_URL=http://localhost:8000"

set "FRONTEND_URL=http://localhost:8080"

echo ============================================================

echo   基于 Python 生态的工业互联网可视化平台

echo   One-Click Launcher

echo ============================================================

echo.

echo [1/5] 进入项目目录: %PROJECT_DIR%

cd /d "%PROJECT_DIR%"

if errorlevel 1 (

    color 0C

    echo [ERROR] 找不到项目目录: %PROJECT_DIR%

    echo 请检查路径是否正确。

    echo.

    pause

    exit /b 1

)

echo [2/5] 检查 Python 和 Uvicorn 命令...

where python >nul 2>nul

if errorlevel 1 (

    color 0C

    echo [ERROR] 未找到 python 命令，请先安装 Python 或配置 PATH。

    echo.

    pause

    exit /b 1

)

where uvicorn >nul 2>nul

if errorlevel 1 (

    color 0C

    echo [ERROR] 未找到 uvicorn 命令。

    echo 请在项目环境中执行: pip install fastapi uvicorn nicegui

    echo.

    pause

    exit /b 1

)

echo [3/5] 启动后端服务 FastAPI，端口 8000...

start "Industrial Platform Backend - FastAPI" cmd /k "chcp 65001 >nul && cd /d %PROJECT_DIR% && uvicorn src.backend.main:app --reload --port 8000"

echo      等待后端初始化 5 秒...

timeout /t 5 /nobreak >nul

echo [4/5] 启动前端服务 NiceGUI，端口 8080...

start "Industrial Platform Frontend - NiceGUI" cmd /k "chcp 65001 >nul && cd /d %PROJECT_DIR% && python src/frontend/main.py"

echo      等待前端初始化 3 秒...

timeout /t 3 /nobreak >nul

echo [5/5] 打开浏览器: %FRONTEND_URL%

start "" "%FRONTEND_URL%"

echo.

echo ============================================================

echo   启动命令已执行完成

echo   后端地址: %BACKEND_URL%

echo   API 文档: %BACKEND_URL%/docs

echo   前端看板: %FRONTEND_URL%

echo ============================================================

echo.

echo 提示: 请保持弹出的后端和前端窗口运行。

echo 如需停止平台，请关闭那两个服务窗口。

echo.

pause

endlocal

