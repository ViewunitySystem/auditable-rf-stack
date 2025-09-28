#!/bin/bash

echo "Starting RF Backend Server..."
echo ""
echo "Dependencies: pip install pyserial websockets"
echo ""
echo "Usage: ./start_rf_backend.sh /dev/ttyUSB0"
echo "       (or any other serial device)"
echo ""

if [ -z "$1" ]; then
    echo "Error: Please specify serial port as parameter"
    echo "Example: ./start_rf_backend.sh /dev/ttyUSB0"
    exit 1
fi

echo "Starting server with port: $1"
python3 server_real_rf_system.py --port "$1" --host 127.0.0.1 --wsport 8765
