@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

REM ---------------------------------------------------
REM Safe league loop with watchdog + blacklist support
REM ---------------------------------------------------
REM Assumes your existing scripts still create:
REM   current_match.txt
REM   current_stage.txt
REM   match_context.json
REM and that your normal launch args are stored below.
REM ---------------------------------------------------

set "MUGEN_EXE=./mugen.exe"
set "MATCH_TIMEOUT=90"
set "RETRY_DELAY=3"

:loop
cls
echo ========================================
echo MUFC SAFE LOOP
echo ========================================

REM Optional live sync steps
if exist "sync_live_roster.py" (
  py sync_live_roster.py
)
if exist "scripts\publish_all_approved.py" (
  py scripts\publish_all_approved.py
)

REM Your existing match generation step(s)
py matchmaker.py
if errorlevel 1 (
  echo Matchmaker failed. Retrying in %RETRY_DELAY%s...
  timeout /t %RETRY_DELAY% >nul
  goto loop
)

REM Example stage selection hook if you use one
if exist "pick_stage.py" (
  py pick_stage.py
)

REM Read generated stage if present
set "STAGEARG="
if exist "current_stage.txt" (
  for /f "usebackq delims=" %%S in ("current_stage.txt") do set "STAGE=%%S"
  set "STAGEARG=!STAGE:stages/=!"
)

REM Show prematch card if you use one
if exist "show_prematch.py" (
  py show_prematch.py
)

REM ---------------------------------------------------
REM Replace the command below with your exact existing
REM MUGEN launch command if it differs.
REM ---------------------------------------------------
py watch_mugen_match.py "%MUGEN_EXE%" --timeout %MATCH_TIMEOUT%
set "WATCHDOG_EXIT=%ERRORLEVEL%"

if "%WATCHDOG_EXIT%"=="124" (
  echo Watchdog timed out. Match was killed and blacklisted.
  if exist "watchdog_result.json" type watchdog_result.json
  timeout /t %RETRY_DELAY% >nul
  goto loop
)

if not "%WATCHDOG_EXIT%"=="0" (
  echo Match process exited with error %WATCHDOG_EXIT%.
  if exist "watchdog_result.json" type watchdog_result.json
  timeout /t %RETRY_DELAY% >nul
  goto loop
)

REM Normal post-match updates
if exist "update_records.py" (
  py update_records.py
)

REM Small pause and continue
timeout /t 2 >nul
goto loop
