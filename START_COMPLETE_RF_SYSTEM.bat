@echo off
echo ========================================
echo   RF TRANSCEIVER CONTROL SUITE v1.0.0
echo   Complete System Startup
echo ========================================
echo.

echo [1/4] Checking dependencies...
python -c "import serial, websockets; print('✅ Python dependencies OK')" 2>nul || (
    echo ❌ Installing Python dependencies...
    pip install pyserial websockets
)

echo.
echo [2/4] Installing Node.js dependencies...
if not exist "node_modules" (
    echo 📦 Installing npm packages...
    npm install
) else (
    echo ✅ Node.js dependencies OK
)

echo.
echo [3/4] Starting Backend Server...
echo Starting RF Backend on COM5...
start "RF Backend" cmd /k "python server_real_rf_system.py --port COM5 --host 127.0.0.1 --wsport 8765"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo [4/4] Starting Frontend...
echo Starting React Frontend on http://localhost:3000...
start "RF Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   🎉 SYSTEM STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Backend:  http://localhost:8765 (WebSocket)
echo Frontend: http://localhost:3000 (React App)
echo.
echo Hardware: COM5 (115200 Baud)
echo.
echo Press any key to exit...
pause >nul
