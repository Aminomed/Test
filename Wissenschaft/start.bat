@echo off
echo ========================================================
echo  Zoom ins Unbestimmte - Wissenschaft & Wirklichkeit
echo ========================================================
echo Starte lokalen Webserver auf http://localhost:8000 ...
start http://localhost:8000
python -m http.server 8000
pause
