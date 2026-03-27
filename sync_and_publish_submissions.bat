@echo off
setlocal EnableExtensions

REM Change this path if your project folder moves
cd /d "%~dp0"

echo ========================================
echo   Syncing Supabase submissions...
echo ========================================
py scripts\import_supabase_submissions.py
if errorlevel 1 (
  echo.
  echo [ERROR] import_supabase_submissions.py failed.
  pause
  exit /b 1
)

echo.
echo ========================================
echo   Backfilling approved fighters...
echo ========================================
py scripts\publish_all_approved.py
if errorlevel 1 (
  echo.
  echo [ERROR] publish_all_approved.py failed.
  pause
  exit /b 1
)

echo.
echo Done. Submissions synced and approved fighters published.
pause
exit /b 0
