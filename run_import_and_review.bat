@echo off
cd /d "%~dp0"

echo Importing new fighters from Supabase...
py scripts\import_supabase_submissions.py

echo.
echo Opening drafts folder...
explorer submissions\drafts

pause