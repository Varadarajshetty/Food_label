@echo off
echo ================================================================================
echo STARTING AI FOOD LABEL DECODER
echo ================================================================================

echo Starting Backend Server (Port 5000)...
start "AI Food Label Backend" cmd /k "cd backend && python app.py"

echo Starting Frontend Server (Port 8000)...
start "AI Food Label Frontend" cmd /k "cd frontend && python -m http.server 8000 --bind 127.0.0.1"

echo.
echo ================================================================================
echo SERVERS STARTED!
echo ================================================================================
echo.
echo Backend running in new window...
echo Frontend running in new window...
echo.
echo Waiting 5 seconds for servers to initialize...
timeout /t 5 >nul
echo.
echo Opening application in browser...
start http://127.0.0.1:8000
echo.
echo Close the terminal windows to stop the servers.
pause
