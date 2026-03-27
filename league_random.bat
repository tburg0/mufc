@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:loop

REM Pick the next matchup (and write current_match.txt + mugen_args.txt + match_context.json)
python matchmaker.py
if errorlevel 1 goto fail
if not exist current_match.txt goto fail
if not exist mugen_args.txt goto fail

py scripts\import_supabase_submissions.py

set /p MUGENARGS=<mugen_args.txt
if "%MUGENARGS%"=="" goto fail

echo Using args: %MUGENARGS%

REM Show broadcast prematch card (also writes prematch.txt + is_title_match.txt)
python show_prematch.py
if errorlevel 1 goto fail
if exist prematch.txt type prematch.txt

timeout /t 1 >nul

for /f "tokens=1,2 delims=," %%A in (current_match.txt) do (
    set P1=%%A
    set P2=%%B
)

set ROUNDS=2
if exist is_title_match.txt (
    set /p ISTITLE=<is_title_match.txt
    if "!ISTITLE!"=="1" set ROUNDS=3
)

python pick_stage.py
if errorlevel 1 goto fail
for /f "usebackq delims=" %%S in ("current_stage.txt") do set "STAGE=%%S"

REM Strip leading "stages/" for command-line argument
set "STAGEARG=!STAGE:stages/=!"
echo Using stage: !STAGEARG!

echo Showing prematch card...
timeout /t 10 >nul

start "" /max /wait mugen.exe %MUGENARGS% -s "!STAGEARG!"

python update_records.py
if errorlevel 1 goto fail

timeout /t 2 >nul
goto loop

:fail
echo.
echo Loop stopped because a required file or script failed.
pause
