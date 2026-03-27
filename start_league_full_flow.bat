@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ========================================
echo   STEP 1: Sync new submissions
echo ========================================
py scripts\import_supabase_submissions.py
if errorlevel 1 (
  echo.
  echo [ERROR] Failed during submission sync.
  pause
  exit /b 1
)

echo.
echo ========================================
echo   STEP 2: Publish any approved fighters
echo ========================================
py scripts\publish_all_approved.py
if errorlevel 1 (
  echo.
  echo [ERROR] Failed during approved fighter publish.
  pause
  exit /b 1
)

echo.
echo ========================================
echo   STEP 3: Start league loop
echo ========================================
call league_random.bat
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" (
  echo League loop exited with errorlevel %ERR%.
) else (
  echo League loop exited normally.
)

pause
exit /b %ERR%
