@echo off
setlocal
echo Stopping MUFC processes...

REM Kills the named cmd windows we started
taskkill /fi "WINDOWTITLE eq MUFC_HTTP*" /t /f >nul 2>nul
taskkill /fi "WINDOWTITLE eq MUFC_WATCHER*" /t /f >nul 2>nul
taskkill /fi "WINDOWTITLE eq MUFC_LOOP*" /t /f >nul 2>nul

echo Done.
pause