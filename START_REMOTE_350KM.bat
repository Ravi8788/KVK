@echo off
REM ============================================================
REM KVK System - Auto-launcher with SSH Tunnel (Internet Remote)
REM For machines 350 KM away from host
REM ============================================================

REM CONFIGURATION - UPDATE THESE VALUES:
set HOST_PUBLIC_IP=47.11.41.71
set HOST_USERNAME=Administrator
set HOST_INTERNAL_IP=192.168.31.99

REM Don't change below values
set SSH_PORT=22
set DB_PORT=5432

echo.
echo ============================================================
echo        KVK System Remote Launcher (350 KM Internet)
echo ============================================================
echo.
echo Host Public IP: %HOST_PUBLIC_IP%
echo Connecting via SSH tunnel...
echo.

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
    echo Possible causes:
    echo   - Host is offline or unreachable
    echo   - SSH service not running on host
    echo   - Firewall blocking port 22
    echo   - Wrong public IP or credentials
    echo.
    echo Please check:
    echo   1. HOST_PUBLIC_IP is correct: %HOST_PUBLIC_IP%
    echo   2. SSH running on host: net start sshd
    echo   3. Firewall allows port 22
    echo.
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
    echo While using the app, keep this window open.
    echo SSH tunnel will stay active.
    echo.
    pause
) else (
    echo [ERROR] KVKSystem.exe not found in current directory!
    echo Please place this script in same folder as KVKSystem.exe
    pause
)

:end
echo Exiting...
timeout /t 2
