@echo off
setlocal EnableDelayedExpansion

REM Towards Victory - build and deploy to EU5 mod folder
REM Usage: build.bat

set "ROOT=%~dp0"
set "SRC=%ROOT%src"
set "ED_SRC=%ROOT%src_engineering_department"
set "MNT_COMPAT=%ROOT%submods\tv_meiou_and_taxes_compat"
set "MOD_DIR=C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game\mod"
set "DEST=%MOD_DIR%\tv"
set "ED_DEST=%MOD_DIR%\tv_engineering_department"
set "MNT_COMPAT_DEST=%MOD_DIR%\tv_meiou_and_taxes_compat"

echo === [1/4] Validating mod source ===
set "VALIDATE_OUT=%TEMP%\tv_validate_out.txt"
if not defined EU5_PYTHON set "EU5_PYTHON=C:\Users\Hades\anaconda3\envs\eu5\python.exe"
if not exist "!EU5_PYTHON!" (
    echo [ERROR] eu5 Python interpreter not found: !EU5_PYTHON!
    echo Set EU5_PYTHON to the python.exe inside the eu5 environment, then retry.
    pause
    exit /b 1
)
call "!EU5_PYTHON!" "%ROOT%scripts\validate.py" > "!VALIDATE_OUT!" 2>&1
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
echo === [2/4] Deploying src to !DEST! ===
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
echo === [3/4] Deploying Engineering Department src to !ED_DEST! ===
if not exist "!ED_SRC!" (
    echo [ERROR] Engineering Department source not found: !ED_SRC!
    pause
    exit /b 1
)

robocopy "!ED_SRC!" "!ED_DEST!" /MIR
set "RC=!errorlevel!"
if !RC! GEQ 8 (
    echo.
    echo [ERROR] robocopy failed with exit code !RC!.
    pause
    exit /b 1
)

echo.
echo === [4/4] Deploying M^&T compatibility submod to !MNT_COMPAT_DEST! ===
if not exist "!MNT_COMPAT!" (
    echo [ERROR] Compatibility submod source not found: !MNT_COMPAT!
    pause
    exit /b 1
)

robocopy "!MNT_COMPAT!" "!MNT_COMPAT_DEST!" /MIR
set "RC=!errorlevel!"
if !RC! GEQ 8 (
    echo.
    echo [ERROR] robocopy failed with exit code !RC!.
    pause
    exit /b 1
)

echo.
echo [DONE] Deployed to !DEST!, !ED_DEST!, and !MNT_COMPAT_DEST!
endlocal
pause
