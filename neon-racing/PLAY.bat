@echo off
title Neon Racing
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python play.py
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        py play.py
    ) else (
        echo Python was not found on this PC.
        echo Install it from https://python.org/downloads and try again.
        pause
        exit /b 1
    )
)

pause
