@echo off
setlocal EnableDelayedExpansion

REM Towards Victory - build and deploy to EU5 mod folder
REM Usage:
REM   build.bat
REM   build.bat --skip-validation

set "ROOT=%~dp0"
set "SRC=%ROOT%src"
set "ED_SRC=%ROOT%src_engineering_department"
set "COURT_SRC=%ROOT%src_court_positions"
set "MNT_COMPAT=%ROOT%submods\tv_meiou_and_taxes_compat"
set "SOL_COMPAT=%ROOT%submods\tv_standard_of_living_compat"
set "PP_COMPAT=%ROOT%submods\tv_prosper_or_perish_compat"
set "MOD_DIR=C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game\mod"
set "DEST=%MOD_DIR%\tv"
set "ED_DEST=%MOD_DIR%\tv_engineering_department"
set "COURT_DEST=%MOD_DIR%\tv_court_positions"
set "MNT_COMPAT_DEST=%MOD_DIR%\tv_meiou_and_taxes_compat"
set "SOL_COMPAT_DEST=%MOD_DIR%\tv_standard_of_living_compat"
set "PP_COMPAT_DEST=%MOD_DIR%\tv_prosper_or_perish_compat"
set "SKIP_VALIDATION=0"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--skip-validation" (
    set "SKIP_VALIDATION=1"
    shift
    goto parse_args
)
if /I "%~1"=="--help" (
    echo Usage: build.bat [--skip-validation]
    exit /b 0
)
echo [ERROR] Unknown argument: %~1
echo Usage: build.bat [--skip-validation]
pause
exit /b 1

:args_done

if not defined EU5_PYTHON set "EU5_PYTHON=C:\Users\Hades\anaconda3\envs\eu5\python.exe"
if not exist "!EU5_PYTHON!" (
    echo [ERROR] eu5 Python interpreter not found: !EU5_PYTHON!
    echo Set EU5_PYTHON to the python.exe inside the eu5 environment, then retry.
    pause
    exit /b 1
)

echo === [1/9] Regenerating generated submod outputs ===
call "!EU5_PYTHON!" "%ROOT%scripts\regenerate_submods.py"
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Submod regeneration failed. Deployment aborted.
    pause
    exit /b 1
)

echo.
echo === [2/9] Updating mod version ===
call "!EU5_PYTHON!" "%ROOT%scripts\update_mod_version.py"
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Mod version update failed. Deployment aborted.
    pause
    exit /b 1
)

echo.
if "!SKIP_VALIDATION!"=="1" (
    echo === [3/9] Skipping validation ===
    echo [WARN] Validation bypassed because --skip-validation was supplied.
) else (
    echo === [3/9] Validating mod source ===
    set "VALIDATE_OUT=%TEMP%\tv_validate_out.txt"
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
)

echo.
echo === [4/9] Deploying src to !DEST! ===
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
echo === [5/9] Deploying Engineering Department src to !ED_DEST! ===
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
echo === [6/9] Deploying Court Positions src to !COURT_DEST! ===
if not exist "!COURT_SRC!" (
    echo [ERROR] Court Positions source not found: !COURT_SRC!
    pause
    exit /b 1
)

robocopy "!COURT_SRC!" "!COURT_DEST!" /MIR
set "RC=!errorlevel!"
if !RC! GEQ 8 (
    echo.
    echo [ERROR] robocopy failed with exit code !RC!.
    pause
    exit /b 1
)

echo.
echo === [7/9] Deploying M^&T compatibility submod to !MNT_COMPAT_DEST! ===
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
echo === [8/9] Deploying Standard of Living compatibility submod to !SOL_COMPAT_DEST! ===
if not exist "!SOL_COMPAT!" (
    echo [ERROR] Compatibility submod source not found: !SOL_COMPAT!
    pause
    exit /b 1
)

robocopy "!SOL_COMPAT!" "!SOL_COMPAT_DEST!" /MIR
set "RC=!errorlevel!"
if !RC! GEQ 8 (
    echo.
    echo [ERROR] robocopy failed with exit code !RC!.
    pause
    exit /b 1
)

echo.
echo === [9/9] Deploying Prosper or Perish compatibility submod to !PP_COMPAT_DEST! ===
if not exist "!PP_COMPAT!" (
    echo [ERROR] Compatibility submod source not found: !PP_COMPAT!
    pause
    exit /b 1
)

robocopy "!PP_COMPAT!" "!PP_COMPAT_DEST!" /MIR
set "RC=!errorlevel!"
if !RC! GEQ 8 (
    echo.
    echo [ERROR] robocopy failed with exit code !RC!.
    pause
    exit /b 1
)

echo.
echo [DONE] Deployed to !DEST!, !ED_DEST!, !COURT_DEST!, !MNT_COMPAT_DEST!, !SOL_COMPAT_DEST!, and !PP_COMPAT_DEST!
endlocal
pause
