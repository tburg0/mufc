@echo off
setlocal EnableDelayedExpansion
pushd "%~dp0"

REM ===== CONFIG =====
set "PORT=8000"
set "LOOP_BAT=league_random.bat"
set "WATCHER_BAT=start_watcher.bat"
REM ==================

echo ============================================
echo MUFC Stream Starter
echo ============================================

chcp 65001 >nul

REM Use py if available, else python
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  set "PY=python"
)

REM 1) Start local web server for overlay
echo Starting overlay server...
start "MUFC_HTTP" /min cmd /c "%PY% -m http.server %PORT%"

REM 2) Start your existing watcher
if exist "%WATCHER_BAT%" (
  echo Starting watcher...
  start "MUFC_WATCHER" cmd /c "%WATCHER_BAT%"
) else (
  echo WARNING: Could not find %WATCHER_BAT%
)

REM 3) Start fight loop
if exist "%LOOP_BAT%" (
  echo Starting match loop...
  start "MUFC_LOOP" cmd /c "%LOOP_BAT%"
) else (
  echo ERROR: Could not find %LOOP_BAT%
  pause
  exit /b 1
)

echo.
echo Overlay URL:
echo http://127.0.0.1:%PORT%/overlay/ufc.html
echo.
pause
popd