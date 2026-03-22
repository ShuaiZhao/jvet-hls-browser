@echo off
REM Interactive HLS Server Startup Script for Windows
REM This script starts the Flask proxy server with auto-restart capability

echo ========================================
echo Interactive HLS Server Manager
echo ========================================
echo.

REM Check if API key is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo WARNING: ANTHROPIC_API_KEY environment variable is not set
    echo    AI features will not work without an API key
    echo.
    echo    To set it, run:
    echo    set ANTHROPIC_API_KEY=sk-ant-...
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Menu to choose which server to run
echo.
echo Which server do you want to start?
echo 1^) Combined Server ^(port 8000^) - RECOMMENDED
echo    Serves static files + AI proxy in one server
echo.
echo 2^) Proxy Server ^(port 8001^) - Legacy
echo    For AI analysis features only
echo.
echo 3^) Backend API Server ^(port 5000^) - Advanced
echo    For real-time analysis and search
echo.
set /p choice="Enter choice [1-3]: "

if "%choice%"=="1" (
    goto start_combined
) else if "%choice%"=="2" (
    goto start_proxy
) else if "%choice%"=="3" (
    goto start_backend
) else (
    echo Invalid choice
    exit /b 1
)

:start_combined
echo.
echo Starting Combined Server...
echo Press CTRL+C to stop
echo ----------------------------------------
:combined_loop
python server\combined_server.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Server stopped cleanly
    goto end
) else (
    echo.
    echo WARNING: Server crashed with exit code %ERRORLEVEL%
    echo Restarting in 3 seconds...
    echo    ^(Press CTRL+C to abort^)
    timeout /t 3 /nobreak > nul
    goto combined_loop
)

:start_proxy
echo.
echo Starting Proxy Server...
echo Press CTRL+C to stop
echo ----------------------------------------
:proxy_loop
python server\proxy.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Server stopped cleanly
    goto end
) else (
    echo.
    echo WARNING: Server crashed with exit code %ERRORLEVEL%
    echo Restarting in 3 seconds...
    echo    ^(Press CTRL+C to abort^)
    timeout /t 3 /nobreak > nul
    goto proxy_loop
)

:start_backend
echo.
echo Starting Backend API Server...
echo Press CTRL+C to stop
echo ----------------------------------------
:backend_loop
python web\backend\api_server.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Server stopped cleanly
    goto end
) else (
    echo.
    echo WARNING: Server crashed with exit code %ERRORLEVEL%
    echo Restarting in 3 seconds...
    echo    ^(Press CTRL+C to abort^)
    timeout /t 3 /nobreak > nul
    goto backend_loop
)

:end
echo.
echo ========================================
echo Server stopped
echo ========================================
pause
