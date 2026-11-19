@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
python scripts\run_local_review.py %*
exit /b %ERRORLEVEL%
