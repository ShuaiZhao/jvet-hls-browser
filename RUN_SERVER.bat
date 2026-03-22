@echo off
REM Simple script to start the Interactive HLS server
REM Just double-click this file or run: RUN_SERVER.bat

cd /d "%~dp0"

echo ==========================================
echo Interactive HLS Specification Browser
echo ==========================================
echo.

REM Check for API key
if "%ANTHROPIC_API_KEY%"=="" (
    echo WARNING: ANTHROPIC_API_KEY not set
    echo.
    echo AI features will be limited without an API key.
    echo To set it, run:
    echo   set ANTHROPIC_API_KEY=sk-ant-...
    echo.
)

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Starting server...
echo.

REM Start the combined server
python server\combined_server.py

echo.
echo Server stopped.
pause
