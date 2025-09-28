# RF Transceiver System - Windows Installer
# PowerShell script for Windows installation

param(
    [string]$InstallPath = "C:\Program Files\RF Transceiver System",
    [switch]$CreateDesktopShortcut,
    [switch]$InstallService,
    [switch]$Force
)

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires administrator privileges. Please run as administrator."
    exit 1
}

Write-Host "RF Transceiver System - Windows Installer" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or later."
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Error "Node.js is not installed or not in PATH. Please install Node.js 18 or later."
    exit 1
}

# Create installation directory
if (Test-Path $InstallPath) {
    if (-not $Force) {
        Write-Error "Installation directory already exists: $InstallPath. Use -Force to overwrite."
        exit 1
    }
    Remove-Item -Path $InstallPath -Recurse -Force
}

Write-Host "Creating installation directory: $InstallPath" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

# Copy application files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Path "*.py" -Destination $InstallPath -Force
Copy-Item -Path "*.json" -Destination $InstallPath -Force
Copy-Item -Path "*.toml" -Destination $InstallPath -Force
Copy-Item -Path "*.txt" -Destination $InstallPath -Force
Copy-Item -Path "*.md" -Destination $InstallPath -Force
Copy-Item -Path "18_Real_RF_Transceiver_System" -Destination $InstallPath -Recurse -Force
Copy-Item -Path "src" -Destination $InstallPath -Recurse -Force

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Set-Location $InstallPath
pip install -r requirements.txt

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

# Build frontend
Write-Host "Building frontend..." -ForegroundColor Yellow
npm run build

# Create Windows Service (default: true)
if ($InstallService -or (-not $PSBoundParameters.ContainsKey('InstallService'))) {
    Write-Host "Installing Windows Service..." -ForegroundColor Yellow
    
    # Install NSSM (Non-Sucking Service Manager) if not present
    $nssmPath = "$InstallPath\nssm.exe"
    if (-not (Test-Path $nssmPath)) {
        Write-Host "Downloading NSSM..." -ForegroundColor Yellow
        $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $nssmZip = "$InstallPath\nssm.zip"
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
        Expand-Archive -Path $nssmZip -DestinationPath $InstallPath -Force
        Copy-Item -Path "$InstallPath\nssm-2.24\win64\nssm.exe" -Destination $nssmPath
        Remove-Item -Path $nssmZip -Force
        Remove-Item -Path "$InstallPath\nssm-2.24" -Recurse -Force
    }
    
    # Create service
    & $nssmPath install "RF Transceiver System" python.exe "$InstallPath\server_real_rf_system.py"
    & $nssmPath set "RF Transceiver System" AppDirectory $InstallPath
    & $nssmPath set "RF Transceiver System" DisplayName "RF Transceiver System"
    & $nssmPath set "RF Transceiver System" Description "RF Transceiver System Backend Service"
    & $nssmPath set "RF Transceiver System" Start SERVICE_AUTO_START
    
    Write-Host "Windows Service installed successfully!" -ForegroundColor Green
}

# Create desktop shortcut (default: true)
if ($CreateDesktopShortcut -or (-not $PSBoundParameters.ContainsKey('CreateDesktopShortcut'))) {
    Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\RF Transceiver System.lnk")
    $Shortcut.TargetPath = "$InstallPath\START_RF_BACKEND.bat"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "RF Transceiver System"
    $Shortcut.Save()
}

# Create Start Menu shortcut
Write-Host "Creating Start Menu shortcut..." -ForegroundColor Yellow
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\RF Transceiver System"
New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$StartMenuPath\RF Transceiver System.lnk")
$Shortcut.TargetPath = "$InstallPath\START_RF_BACKEND.bat"
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.Description = "RF Transceiver System"
$Shortcut.Save()

# Create uninstaller
Write-Host "Creating uninstaller..." -ForegroundColor Yellow
$uninstallerContent = @"
# RF Transceiver System Uninstaller
Write-Host "Uninstalling RF Transceiver System..." -ForegroundColor Yellow

# Stop and remove service
if (Get-Service -Name "RF Transceiver System" -ErrorAction SilentlyContinue) {
    Stop-Service -Name "RF Transceiver System" -Force
    & "$InstallPath\nssm.exe" remove "RF Transceiver System" confirm
}

# Remove files
Remove-Item -Path "$InstallPath" -Recurse -Force

# Remove shortcuts
Remove-Item -Path "$env:USERPROFILE\Desktop\RF Transceiver System.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\RF Transceiver System" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "RF Transceiver System uninstalled successfully!" -ForegroundColor Green
"@

$uninstallerContent | Out-File -FilePath "$InstallPath\uninstall.ps1" -Encoding UTF8

Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "Installation path: $InstallPath" -ForegroundColor Cyan
Write-Host "To start the service: Start-Service 'RF Transceiver System'" -ForegroundColor Cyan
Write-Host "To uninstall: Run $InstallPath\uninstall.ps1" -ForegroundColor Cyan
