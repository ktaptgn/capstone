@echo off
REM C5.1 demo launcher (Windows). Double-click to run.
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo [!] Node.js is not installed. Install it from https://nodejs.org and try again.
  pause
  exit /b 1
)
echo Starting C5.1 demo server...
node server.mjs
pause
