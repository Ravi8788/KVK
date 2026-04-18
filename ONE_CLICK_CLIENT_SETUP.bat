@echo off
setlocal enabledelayedexpansion

REM One-click client setup for remote laptops.
REM Place this file in the same folder as KVKSystem.exe.

cd /d "%~dp0"

echo.
echo ============================================================
echo                 KVK Client One-Click Setup
echo ============================================================
echo.

if not exist "KVKSystem.exe" (
    echo [ERROR] KVKSystem.exe not found in this folder.
    echo Copy KVKSystem.exe and this setup file into the same folder.
    pause
    exit /b 1
)

echo This setup will create a .env file for this laptop.
echo.

set /p DB_HOST=Enter DB host IP or name (example: 192.168.1.50): 
if "%DB_HOST%"=="" set DB_HOST=localhost

set /p DB_PORT=Enter DB port [5432]: 
if "%DB_PORT%"=="" set DB_PORT=5432

set /p DB_NAME=Enter database name [kvk]: 
if "%DB_NAME%"=="" set DB_NAME=kvk

set /p DB_USER=Enter database user [postgres]: 
if "%DB_USER%"=="" set DB_USER=postgres

set /p DB_PASSWORD=Enter database password: 
if "%DB_PASSWORD%"=="" (
    echo [ERROR] DB password cannot be empty.
    pause
    exit /b 1
)

set /p ADMIN_USERNAME=Enter admin username [admin]: 
if "%ADMIN_USERNAME%"=="" set ADMIN_USERNAME=admin

set /p ADMIN_PASSWORD=Enter admin password (strong): 
if "%ADMIN_PASSWORD%"=="" (
    echo [ERROR] Admin password cannot be empty.
    pause
    exit /b 1
)

set DB_SSLMODE=prefer
if /I "%DB_HOST%"=="localhost" set DB_SSLMODE=disable
if /I "%DB_HOST%"=="127.0.0.1" set DB_SSLMODE=disable

(
    echo DB_HOST=%DB_HOST%
    echo DB_PORT=%DB_PORT%
    echo DB_NAME=%DB_NAME%
    echo DB_USER=%DB_USER%
    echo DB_PASSWORD=%DB_PASSWORD%
    echo DB_SSLMODE=%DB_SSLMODE%
    echo APP_ENV=production
    echo PG_BIN_DIR=
    echo ADMIN_USERNAME=%ADMIN_USERNAME%
    echo ADMIN_PASSWORD=%ADMIN_PASSWORD%
) > ".env"

echo.
echo [OK] .env created successfully.
echo [INFO] SSL mode set to: %DB_SSLMODE%
echo.

set /p RUN_NOW=Launch KVKSystem.exe now? (Y/N): 
if /I "%RUN_NOW%"=="Y" (
    start "" "KVKSystem.exe"
    echo [OK] KVKSystem launched.
)

echo.
echo Setup complete.
pause
exit /b 0
