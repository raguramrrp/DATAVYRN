@echo off
echo ========================================================
echo   Launching DATAVYRN Data Intelligence ^& Training Workbench
echo ========================================================
echo.

if not exist ".venv\Scripts\streamlit.exe" (
    echo Virtual environment or Streamlit not detected. Running setup.bat first...
    call setup.bat
)

echo Starting DATAVYRN on http://localhost:8501 ...
.venv\Scripts\streamlit.exe run app.py --server.headless=false --server.port=8501 --theme.base="light"
