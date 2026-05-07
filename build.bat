@echo off
setlocal EnableDelayedExpansion

REM Towards Victory - build and deploy to EU5 mod folder
REM Usage: build.bat

set "ROOT=%~dp0"
set "SRC=%ROOT%src"
set "MOD_DIR=C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game\mod"
set "DEST=%MOD_DIR%\tv"

echo === [1/2] Validating mod source ===
set "VALIDATE_OUT=%TEMP%\tv_validate_out.txt"
call conda run --no-capture-output -n eu5 python "%ROOT%scripts\validate.py" > "!VALIDATE_OUT!" 2>&1
set "VALIDATE_RC=!errorlevel!"
type "!VALIDATE_OUT!"
del "!VALIDATE_OUT!" 2>nul
if !VALIDATE_RC! neq 0 (
    echo.
    echo [ERROR] Validation failed. Deployment aborted.
    pause
    exit /b 1
)

echo.
echo === [2/2] Deploying src to !DEST! ===
if not exist "!MOD_DIR!" (
    echo [ERROR] EU5 mod directory not found: !MOD_DIR!
    pause
    exit /b 1
)

robocopy "!SRC!" "!DEST!" /MIR
set "RC=!errorlevel!"
if !RC! GEQ 8 (
    echo.
    echo [ERROR] robocopy failed with exit code !RC!.
    pause
    exit /b 1
)

echo.
echo [DONE] Deployed to !DEST!
endlocal
pause
