@echo off
title SENTIMENTAL - Hidden Emotion & Intent Detection System
echo ======================================================================
echo  Starting SENTIMENTAL Application Server...
echo  Access web UI at: http://localhost:8000
echo ======================================================================
cd /d "%~dp0"
python run.py
pause
