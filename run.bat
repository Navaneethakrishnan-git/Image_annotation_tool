@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Create it with: python -m venv .venv
    pause
    exit /b 1
)
.venv\Scripts\python.exe main.py
echo.
echo Application closed. Exit code: %ERRORLEVEL%
pause
