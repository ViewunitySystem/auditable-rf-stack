# RF Transceiver System - Setup Guide

**Version:** 2.0.0  
**Date:** 2025-09-29  
**Author:** Raymond Demitrio Dr. Tel

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Platform-Specific Setup](#platform-specific-setup)
5. [Hardware Configuration](#hardware-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## System Requirements

### Minimum Requirements
- **Python:** 3.8 or later
- **Node.js:** 18.0 or later
- **RAM:** 4 GB minimum, 8 GB recommended
- **Storage:** 2 GB free space
- **OS:** Windows 10+, macOS 10.15+, Ubuntu 18.04+

### Supported Hardware
- **SDR Devices:** RTL2832U, HackRF One, LimeSDR
- **LTE/5G Modems:** Qualcomm X55, Sierra EM7565
- **Neuro Devices:** OpenBCI Cyton, Emotiv Insight
- **CAN Adapters:** USBtin, Peak-CAN
- **USB Serial:** FTDI, CP2102, CH340

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/tel1-nl/rf-transceiver-system.git
cd rf-transceiver-system
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### 3. Build Frontend
```bash
npm run build
```

### 4. Start Backend
```bash
# With hardware
python server_real_rf_system.py --port COM5  # Windows
python server_real_rf_system.py --port /dev/ttyUSB0  # Linux/macOS

# Mock mode (no hardware)
python server_real_rf_system.py --port /dev/null
```

### 5. Access Frontend
Open your browser and navigate to: `http://localhost:3000`

---

## Detailed Installation

### Python Backend Setup

#### 1. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### 2. Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy
```

#### 3. Verify Installation
```bash
# Test Python installation
python -c "import serial, websockets, asyncio; print('Python dependencies OK')"

# Run tests
pytest tests/ -v
```

### Node.js Frontend Setup

#### 1. Install Node.js
Download and install Node.js 18+ from: https://nodejs.org/

#### 2. Install Dependencies
```bash
# Install dependencies
npm install

# Install development dependencies
npm install --save-dev @types/react @types/react-dom typescript
```

#### 3. Build Frontend
```bash
# Development build
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

#### 4. Verify Installation
```bash
# Test Node.js installation
node --version
npm --version

# Run frontend tests
npm test
```

---

## Platform-Specific Setup

### Windows Setup

#### 1. Install Python
- Download Python 3.8+ from https://python.org
- Enable "Add Python to PATH" during installation
- Verify installation: `python --version`

#### 2. Install Node.js
- Download Node.js 18+ from https://nodejs.org
- Use the Windows Installer (.msi)
- Verify installation: `node --version`

#### 3. Install USB Drivers
- Install FTDI drivers for USB-to-Serial devices
- Install device-specific drivers (e.g., RTL-SDR drivers)

#### 4. Run Installation Script
```powershell
# Run as Administrator
.\installers\windows\install.ps1 -InstallPath "C:\RF Transceiver System"
```

#### 5. Start Service
```powershell
# Start Windows Service
Start-Service "RF Transceiver System"

# Or run manually
.\START_RF_BACKEND.bat
```

### Linux Setup

#### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nodejs npm build-essential

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm gcc gcc-c++

# Arch Linux
sudo pacman -S python python-pip nodejs npm base-devel
```

#### 2. Install USB Support
```bash
# Install udev rules
sudo cp installers/linux/udev/99-rf-transceiver.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# Add user to dialout group
sudo usermod -a -G dialout $USER
```

#### 3. Run Installation Script
```bash
# Make executable
chmod +x installers/linux/install.sh

# Run installation
sudo ./installers/linux/install.sh
```

#### 4. Start Service
```bash
# Start systemd service
sudo systemctl start rf-transceiver-system

# Check status
sudo systemctl status rf-transceiver-system
```

### macOS Setup

#### 1. Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Dependencies
```bash
# Install Python and Node.js
brew install python node

# Install USB support
brew install libusb
```

#### 3. Install Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Build and Run
```bash
# Build frontend
npm install
npm run build

# Start backend
python server_real_rf_system.py --port /dev/tty.usbserial-*
```

---

## Hardware Configuration

### SDR Device Setup

#### RTL2832U (RTL-SDR)
1. Install RTL-SDR drivers
2. Connect device via USB
3. Verify device detection:
   ```bash
   # Linux
   lsusb | grep RTL2838
   
   # Windows
   # Check Device Manager for RTL2838UHIDIR
   ```

4. Test with backend:
   ```bash
   python server_real_rf_system.py --port /dev/ttyUSB0  # Linux
   python server_real_rf_system.py --port COM3          # Windows
   ```

#### HackRF One
1. Install HackRF drivers and tools
2. Connect device via USB
3. Verify device detection:
   ```bash
   hackrf_info
   ```

4. Configure for use with backend

### LTE/5G Modem Setup

#### Qualcomm X55 Modem
1. Install QMI tools:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libqmi-utils
   
   # CentOS/RHEL
   sudo yum install libqmi
   ```

2. Configure modem:
   ```bash
   # Enable QMI mode
   sudo qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode=mode=online
   
   # Check signal strength
   sudo qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength
   ```

3. Connect to backend:
   ```bash
   python server_real_rf_system.py --port /dev/ttyUSB2
   ```

### CAN Bus Setup

#### USBtin CAN Adapter
1. Install CAN utilities:
   ```bash
   sudo apt-get install can-utils
   ```

2. Configure CAN interface:
   ```bash
   sudo ip link set can0 type can bitrate 500000
   sudo ip link set up can0
   ```

3. Test CAN communication:
   ```bash
   candump can0
   ```

---

## Troubleshooting

### Common Issues

#### 1. "Permission denied" for serial port
**Linux/macOS:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

**Windows:**
- Run as Administrator
- Check Device Manager for port permissions

#### 2. "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

#### 3. WebSocket connection failed
- Check if backend is running: `netstat -an | grep 8765`
- Verify firewall settings
- Check if port 8765 is available

#### 4. Frontend build fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 5. Hardware not detected
- Check USB connection
- Install device drivers
- Verify device is not in use by other applications

### Debug Mode

#### Enable Debug Logging
```bash
# Set environment variable
export RF_LOG_LEVEL=DEBUG

# Or use command line flag
python server_real_rf_system.py --debug
```

#### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# System logs (Linux)
journalctl -u rf-transceiver-system -f

# Windows Event Viewer
# Look for "RF Transceiver System" service logs
```

---

## Advanced Configuration

### Environment Variables

```bash
# Backend configuration
export RF_SERIAL_PORT=/dev/ttyUSB0
export RF_BAUD_RATE=115200
export RF_WEBSOCKET_HOST=0.0.0.0
export RF_WEBSOCKET_PORT=8765
export RF_LOG_LEVEL=INFO
export RF_AUDIT_ENABLED=true

# Frontend configuration
export VITE_API_URL=ws://localhost:8765
export VITE_BACKEND_URL=http://localhost:8000
```

### Configuration Files

#### Backend Config (`config.yaml`)
```yaml
server:
  host: "0.0.0.0"
  port: 8765
  debug: false

serial:
  port: "/dev/ttyUSB0"
  baudrate: 115200
  timeout: 1

logging:
  level: "INFO"
  file: "logs/backend.log"
  max_size: "10MB"
  backup_count: 5

audit:
  enabled: true
  file: "logs/audit.log"
  retention_days: 30
```

#### Frontend Config (`vite.config.ts`)
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8765',
        ws: true
      }
    }
  }
})
```

### Docker Deployment

#### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Custom Docker Build
```bash
# Build image
docker build -t rf-transceiver-system .

# Run container
docker run -d \
  --name rf-backend \
  -p 8765:8765 \
  -p 8000:8000 \
  -v /dev:/dev:ro \
  rf-transceiver-system
```

### Production Deployment

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### SSL/TLS Setup
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure Nginx for HTTPS
# Add SSL configuration to nginx.conf
```

---

## Support and Contact

### Documentation
- **GitHub Repository:** https://github.com/tel1-nl/rf-transceiver-system
- **Documentation:** https://rf-transceiver-system.readthedocs.io
- **Issue Tracker:** https://github.com/tel1-nl/rf-transceiver-system/issues

### Contact Information
- **Author:** Raymond Demitrio Dr. Tel
- **Email:** contact@tel1.nl
- **Website:** https://tel1.nl

### Community
- **Discussions:** GitHub Discussions
- **Wiki:** Project Wiki
- **Examples:** Examples repository

---

**Last Updated:** 2025-09-29  
**Version:** 2.0.0
