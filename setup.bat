@echo off
echo ========================================================
echo   DATAVYRN - Windows Environment & Dependency Setup
echo ========================================================
echo.

set PYTHON_CMD=python
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py -3.12
)

echo [1/3] Creating virtual environment (.venv)...
%PYTHON_CMD% -m venv .venv
if %ERRORLEVEL% neq 0 (
    echo Error creating virtual environment. Attempting fallback with default python...
    python -m venv .venv
)

echo.
echo [2/3] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo.
echo [3/3] Installing dependencies from requirements.txt...
.venv\Scripts\pip.exe install -r requirements.txt

echo.
echo ========================================================
echo   DATAVYRN Setup Completed Successfully!
echo   To launch the application, run: run.bat
echo ========================================================
pause
