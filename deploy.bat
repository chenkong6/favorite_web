@echo off
echo [INFO] Starting auto-update for Favorites Dashboard...

cd /d "%~dp0"

echo [INFO] Generating static site...

if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment...
    ".venv\Scripts\python.exe" generate_site.py
) else (
    echo [INFO] Using system python...
    python generate_site.py
)

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python script failed! Please check if python and beautifulsoup4 are installed.
    pause
    exit /b %ERRORLEVEL%
)

echo [INFO] Site generated successfully.
echo [INFO] Pushing to Git...

git add .
git commit -m "Auto-update favorites: %date% %time%"
git push

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git push failed!
    pause
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] Deployment trigger sent to Zeabur (via Git push).
pause
