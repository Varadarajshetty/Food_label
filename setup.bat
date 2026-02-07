@echo off
echo ================================================================================
echo AI FOOD LABEL DECODER - QUICK SETUP
echo ================================================================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo.

echo [2/3] Installing Python packages...
if exist "packages" (
    echo Found local packages folder. Installing offline...
    pip install --no-index --find-links=packages -r requirements.txt
) else (
    echo Downloading and installing packages from PyPI...
    pip install -r requirements.txt
)

if errorlevel 1 (
    echo ERROR: Package installation failed!
    pause
    exit /b 1
)
echo.

echo [3/3] Checking Tesseract OCR...
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo OK: Tesseract OCR found
    "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
) else (
    echo WARNING: Tesseract OCR not found!
    echo.
    echo Please install Tesseract OCR:
    echo   1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
    echo   2. Download and run the installer
    echo   3. Run this script again
    echo.
)

echo.
echo ================================================================================
echo SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo   1. Start backend: cd backend ^&^& python app.py
echo   2. Open frontend: frontend\index.html
echo.
echo For detailed instructions, see QUICKSTART.md
echo.
pause
