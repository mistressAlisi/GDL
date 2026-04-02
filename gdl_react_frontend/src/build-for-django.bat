@echo off
REM BETANY LOTTO - Build and Deploy to Django Static Folder (Windows)
REM This script builds the React app and copies it to Django's static folder

echo ============================================
echo   BETANY LOTTO - Build and Deploy Script
echo ============================================

REM Configuration
REM Set your Django project path here or use environment variable
if not defined DJANGO_PROJECT_PATH (
    set DJANGO_PROJECT_PATH=..\django-betany-lotto
)

set DJANGO_STATIC_PATH=%DJANGO_PROJECT_PATH%\static

REM Check if Django path exists
if not exist "%DJANGO_PROJECT_PATH%" (
    echo [ERROR] Django project not found at: %DJANGO_PROJECT_PATH%
    echo.
    echo Set DJANGO_PROJECT_PATH environment variable:
    echo   set DJANGO_PROJECT_PATH=C:\path\to\your\django-project
    echo   Or edit this script to set the correct path
    pause
    exit /b 1
)

REM Step 1: Clean previous build
echo.
echo [1/5] Cleaning previous build...
if exist dist (
    rmdir /s /q dist
)

REM Step 2: Build React app
echo.
echo [2/5] Building React application...
call npm run build

if not exist dist (
    echo [ERROR] Build failed - dist folder not created
    pause
    exit /b 1
)

echo [SUCCESS] Build complete

REM Step 3: Clear Django static folder
echo.
echo [3/5] Clearing Django static folder...
if exist "%DJANGO_STATIC_PATH%" (
    REM Keep .gitkeep or .gitignore if they exist
    for /d %%i in ("%DJANGO_STATIC_PATH%\*") do (
        rmdir /s /q "%%i"
    )
    for %%i in ("%DJANGO_STATIC_PATH%\*") do (
        if not "%%~nxi"==".gitkeep" if not "%%~nxi"==".gitignore" (
            del /q "%%i"
        )
    )
) else (
    mkdir "%DJANGO_STATIC_PATH%"
)

REM Step 4: Copy build to Django
echo.
echo [4/5] Copying build to Django static folder...
xcopy /E /I /Y dist\* "%DJANGO_STATIC_PATH%\"

echo [SUCCESS] Files copied to: %DJANGO_STATIC_PATH%

REM Step 5: Collect static files (optional)
echo.
echo [5/5] Django collectstatic
set /p COLLECT="Run Django collectstatic? (y/n): "

if /i "%COLLECT%"=="y" (
    echo Running collectstatic...
    cd "%DJANGO_PROJECT_PATH%"
    python manage.py collectstatic --noinput
    echo [SUCCESS] Static files collected
    cd "%~dp0"
) else (
    echo [SKIPPED] collectstatic
)

REM Summary
echo.
echo ============================================
echo   Deployment Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Start Django server:
echo    cd %DJANGO_PROJECT_PATH% ^&^& python manage.py runserver
echo.
echo 2. Start Daphne for WebSockets:
echo    daphne -p 8000 your_project.asgi:application
echo.
echo 3. Visit: http://localhost:8000
echo.
pause
