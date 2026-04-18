@echo off
REM ============================================================
REM KVK System - Auto-launcher with SSH Tunnel
REM Remote Machine Setup (350 KM, Public IP: 47.11.41.71)
REM ============================================================
REM
REM HOW TO USE:
REM 1. Place this file in same folder as KVKSystem.exe
REM 2. Place .env file in same folder
REM 3. Double-click this file to auto-launch
REM
REM ============================================================

REM CONFIGURATION - ALREADY SET FOR YOUR SETUP:
set HOST_PUBLIC_IP=47.11.41.71
set HOST_USERNAME=Administrator
set HOST_INTERNAL_IP=192.168.31.99
set SSH_PORT=22
set DB_PORT=5432

echo.
echo ============================================================
echo        KVK System - Remote Launcher (350 KM Internet)
echo        Host IP: %HOST_PUBLIC_IP%
echo ============================================================
echo.

if not exist ".env" (
    echo [ERROR] .env not found in this folder.
    echo Copy .env.remote_template as .env and update DB_PASSWORD and ADMIN_PASSWORD.
    pause
    goto end
)

REM Check if SSH tunnel already running
netstat -an | find ":5432" >nul
if %errorlevel% equ 0 (
    echo [OK] SSH tunnel already running
    goto launch_app
) else (
    echo [STARTING] SSH tunnel to %HOST_PUBLIC_IP%...
)

REM Start SSH tunnel in background window
REM This creates encrypted connection: localhost:5432 -> host:5432
start "PostgreSQL SSH Tunnel" /min powershell -NoExit -Command ^
    "ssh -L %DB_PORT%:%HOST_INTERNAL_IP%:%DB_PORT% %HOST_USERNAME%@%HOST_PUBLIC_IP% -N"

REM Wait for tunnel to establish (3 seconds should be enough)
echo.
echo [WAITING] 3 seconds for tunnel to establish...
timeout /t 3 /nobreak

:launch_app

REM Verify tunnel is running
netstat -an | find ":5432" >nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] SSH tunnel failed to start!
    echo.
    echo Possible causes:
    echo   1. Host is offline (192.168.31.99 or 47.11.41.71 not reachable)
    echo   2. SSH service not running on host machine
    echo   3. Windows Firewall blocking port 22
    echo   4. Router not configured for port forwarding
    echo   5. Incorrect credentials
    echo.
    echo TO TROUBLESHOOT:
    echo   A. Test manually in PowerShell:
    echo      ssh -v Administrator@47.11.41.71
    echo.
    echo   B. Check if SSH tunnel can be created:
    echo      ssh -L 5432:192.168.31.99:5432 Administrator@47.11.41.71 -N
    echo.
    echo   C. Check from host machine:
    echo      - Is PostgreSQL running?
    echo      - Is SSH service running? (Get-Service sshd)
    echo      - Do port forwards exist in router? (5432 and 22)
    echo.
    echo Keeping window open for debugging...
    pause
    goto end
)

echo [OK] SSH tunnel established successfully!
echo.
echo [LAUNCHING] KVKSystem.exe in 2 seconds...
timeout /t 2 /nobreak

REM Launch the application
if exist "KVKSystem.exe" (
    start KVKSystem.exe
    echo [OK] KVKSystem launched!
    echo.
    echo IMPORTANT: Keep this window open while using the app!
    echo When you close this window, SSH tunnel will stop.
    echo.
    pause
) else (
    echo.
    echo [ERROR] KVKSystem.exe not found!
    echo.
    echo File structure should be:
    echo    C:\KVK\
    echo    ├── KVKSystem.exe
    echo    ├── .env
    echo    └── launcher.bat (this file)
    echo.
    pause
)

:end
echo.
echo Closing launcher...
timeout /t 1
