@echo off
title NETSCOUT Africa - Sales Dashboard

:: Set API key
set ANTHROPIC_API_KEY=ANTHROPIC_API_KEY
:: Go to the folder where this .bat file lives
cd /d "%~dp0"

:: Kill anything on port 8080
echo Clearing port 8080...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║  NETSCOUT Africa · Sales Intelligence App   ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Starting server...
echo  Open your browser at: http://localhost:8080
echo.

:: Open browser after 2 seconds
start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:8080"

:: Start Python server
python server.py

pause
