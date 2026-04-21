@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "HOST=127.0.0.1"
set "PORT=5000"
set "PY=.venv\\Scripts\\python.exe"

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Create venv...
  python -m venv .venv
  if errorlevel 1 (
    echo [error] 创建虚拟环境失败，请确认已安装 Python 且可在命令行运行 python。
    pause
    exit /b 1
  )
)

echo [2/3] Install dependencies...
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [error] 依赖安装失败（pip install -r requirements.txt）。
  pause
  exit /b 1
)

if not exist ".env" (
  echo [info] Create .env from .env.example
  copy /y .env.example .env >nul
)

echo [info] Quick mode: USE_SQLITE=1 (no MySQL needed)
set USE_SQLITE=1

if exist "ticketing.db" (
  del /f /q "ticketing.db" >nul 2>nul
  if exist "ticketing.db" (
    echo [warn] ticketing.db 正被占用，跳过删除，将继续使用现有数据库。
  )
)
if exist "instance\\ticketing.db" (
  del /f /q "instance\\ticketing.db" >nul 2>nul
)

echo.
set "PORT_INPUT="
set /p "PORT_INPUT=请输入要启动的端口(默认 5000，直接回车): "
if "%PORT_INPUT%"=="" (
  set "PORT=5000"
) else (
  echo %PORT_INPUT%| findstr /r "^[0-9][0-9]*$" >nul
  if errorlevel 1 (
    echo [warn] 端口必须是纯数字，你输入的是 "%PORT_INPUT%"，将使用默认端口 5000。
    set "PORT=5000"
  ) else (
    set "PORT=%PORT_INPUT%"
  )
)

echo.
echo 将启动接口服务器:
echo - Mode: SQLite (USE_SQLITE=1)
echo - URL : http://%HOST%:%PORT%
echo.

set "PORT_PID="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
  set "PORT_PID=%%p"
)
if not "%PORT_PID%"=="" (
  echo [warn] 端口 %PORT% 已被占用（PID=%PORT_PID%）。
  choice /c YN /m "是否自动结束该进程并继续启动？(Y=结束进程，N=退出)"
  if errorlevel 2 (
    echo 已取消。你可以换一个端口，或手动关闭占用端口的程序。
    pause
    exit /b 1
  )
  echo [info] 正在结束 PID=%PORT_PID% ...
  taskkill /PID %PORT_PID% /F >nul 2>nul
  if errorlevel 1 (
    echo [error] 无法结束 PID=%PORT_PID%（可能权限不足或进程已退出）。
    pause
    exit /b 1
  )
  timeout /t 1 /nobreak >nul
)

choice /c YN /m "按 Y 开始运行，按 N 退出"
if errorlevel 2 (
  echo 已取消。
  exit /b 0
)

echo.
echo [3/3] Init DB and start server...
"%PY%" -m flask --app app init-db
if errorlevel 1 (
  echo [error] init-db 失败。
  pause
  exit /b 1
)

echo [info] 正在打开浏览器首页...
start "" "http://%HOST%:%PORT%/"

"%PY%" -m flask --app app run --debug --host %HOST% --port %PORT%
if errorlevel 1 (
  echo [error] Flask 启动失败（可能端口被占用或配置错误）。
  pause
  exit /b 1
)

endlocal

