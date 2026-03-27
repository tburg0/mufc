@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
pushd "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  set "PY=python"
)

:loop

echo.
echo ================= LIVE ROSTER SYNC =================
%PY% sync_live_roster.py
if errorlevel 1 (
  echo WARNING: live roster sync reported an error. Continuing with existing live roster.
)

REM Pick the next matchup (and write current_match.txt + is_title_match.txt)
%PY% matchmaker.py
if errorlevel 1 (
  echo ERROR: matchmaker failed.
  timeout /t 3 >nul
  goto loop
)

if not exist mugen_args.txt (
  echo ERROR: mugen_args.txt not found after matchmaker run.
  timeout /t 3 >nul
  goto loop
)

set /p MUGENARGS=<mugen_args.txt

echo Using args: %MUGENARGS%

REM Show broadcast prematch card (also writes prematch.txt)
%PY% show_prematch.py
if exist prematch.txt type prematch.txt
timeout /t 1 >nul

REM Read fighters back from current_match.txt
for /f "tokens=1,2 delims=," %%A in (current_match.txt) do (
    set P1=%%A
    set P2=%%B
)

set ROUNDS=2
set /p ISTITLE=<is_title_match.txt
if "%ISTITLE%"=="1" set ROUNDS=3

%PY% pick_stage.py
for /f "usebackq delims=" %%S in ("current_stage.txt") do set "STAGE=%%S"

REM Strip leading "stages/" for command-line argument
set "STAGEARG=!STAGE:stages/=!"
echo Using stage: !STAGEARG!

echo Showing prematch card...
timeout /t 10 >nul

start "" /max /wait mugen.exe %MUGENARGS% -s "!STAGEARG!"

%PY% update_records.py

timeout /t 2 >nul
goto loop
