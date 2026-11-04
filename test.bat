@echo off
echo ========================================================
echo   DATAVYRN - Automated Test Suite Runner (PyTest)
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Python virtual environment not found! Please run setup.bat first.
    pause
    exit /b 1
)

echo Executing all 21 unit, integration, and ML pipeline tests...
.venv\Scripts\python.exe -m pytest tests/ -v
if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   All tests PASSED successfully!
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   Tests FAILED! Check error output above.
    echo ========================================================
)
pause
