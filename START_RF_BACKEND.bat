@echo off
echo Starting RF Backend Server...
echo.
echo Dependencies: pip install pyserial websockets
echo.
echo Usage: START_RF_BACKEND.bat COM5
echo        (or any other COM port)
echo.
if "%1"=="" (
    echo Error: Please specify COM port as parameter
    echo Example: START_RF_BACKEND.bat COM5
    pause
    exit /b 1
)

echo Starting server with port: %1
python server_real_rf_system.py --port %1 --host 127.0.0.1 --wsport 8765
pause
