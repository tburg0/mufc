@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ========================================
echo   Publishing approved fighters not live...
echo ========================================
py scripts\publish_all_approved.py
if errorlevel 1 (
  echo.
  echo [ERROR] publish_all_approved.py failed.
  pause
  exit /b 1
)

echo.
echo Done. Missing approved fighters were published.
pause
exit /b 0
