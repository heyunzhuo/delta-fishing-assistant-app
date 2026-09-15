@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================
echo   钓鱼经验机 - 单文件 exe 构建
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [错误] 找不到 Python 启动器 py。
  echo        请先安装 64 位 Python 3.11 或更高版本，安装时勾选 "Add python.exe to PATH"。
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] 创建构建用虚拟环境 .venv ...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [错误] 创建虚拟环境失败。请确认已安装 Python 3.11+ 且包含 Tcl/Tk 组件。
    pause
    exit /b 1
  )
) else (
  echo [1/4] 复用已有虚拟环境 .venv
)

set "PY=.venv\Scripts\python.exe"

echo [2/4] 安装依赖 ...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [错误] 依赖安装失败，请检查网络。
  pause
  exit /b 1
)

echo [3/4] 安装 PyInstaller ...
"%PY%" -m pip install "pyinstaller>=6.6"
if errorlevel 1 (
  echo [错误] PyInstaller 安装失败。
  pause
  exit /b 1
)

echo [4/4] 开始打包（首次约需 2~5 分钟）...
"%PY%" -m PyInstaller --noconfirm --clean "钓鱼经验机.spec"
if errorlevel 1 (
  echo [错误] 打包失败，请把上面的报错信息保存下来。
  pause
  exit /b 1
)

if not exist "dist\钓鱼经验机.exe" (
  echo [错误] 打包结束但没有生成 dist\钓鱼经验机.exe。
  pause
  exit /b 1
)

echo.
echo ============================================
echo   构建成功
echo ============================================
for %%F in ("dist\钓鱼经验机.exe") do echo   文件：%%~fF   大小：%%~zF 字节
echo.
echo   把这个 exe 拷到任意普通文件夹即可运行，不需要安装 Python。
echo   注意：双击后必须允许管理员权限，否则无法控制游戏。
echo.
pause
