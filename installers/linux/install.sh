#!/bin/bash

# RF Transceiver System - Linux Installer
# Bash script for Linux installation

set -e

# Configuration
INSTALL_PATH="/opt/rf-transceiver-system"
SERVICE_NAME="rf-transceiver-system"
SERVICE_USER="rfuser"
SERVICE_GROUP="rfuser"
CREATE_DESKTOP_SHORTCUT=true
INSTALL_SERVICE=true
FORCE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or later."
        exit 1
    fi
    
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Found Python: $python_version"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18 or later."
        exit 1
    fi
    
    local node_version=$(node --version)
    log_success "Found Node.js: $node_version"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed. Please install npm."
        exit 1
    fi
}

install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y \
            python3-dev \
            python3-pip \
            python3-venv \
            build-essential \
            libffi-dev \
            libssl-dev \
            usbutils \
            socat \
            curl \
            wget \
            unzip
    elif command -v yum &> /dev/null; then
        yum update -y
        yum install -y \
            python3-devel \
            python3-pip \
            gcc \
            gcc-c++ \
            libffi-devel \
            openssl-devel \
            usbutils \
            socat \
            curl \
            wget \
            unzip
    elif command -v pacman &> /dev/null; then
        pacman -Syu --noconfirm \
            python \
            python-pip \
            base-devel \
            libffi \
            openssl \
            usbutils \
            socat \
            curl \
            wget \
            unzip
    else
        log_warning "Unknown package manager. Please install dependencies manually."
    fi
}

create_user() {
    log_info "Creating service user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$INSTALL_PATH" "$SERVICE_USER"
        log_success "Created user: $SERVICE_USER"
    else
        log_info "User already exists: $SERVICE_USER"
    fi
}

install_application() {
    log_info "Installing application to $INSTALL_PATH..."
    
    # Create installation directory
    if [[ -d "$INSTALL_PATH" ]]; then
        if [[ "$FORCE" == "true" ]]; then
            rm -rf "$INSTALL_PATH"
        else
            log_error "Installation directory already exists: $INSTALL_PATH. Use --force to overwrite."
            exit 1
        fi
    fi
    
    mkdir -p "$INSTALL_PATH"
    
    # Copy application files
    cp -r . "$INSTALL_PATH/"
    cd "$INSTALL_PATH"
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_PATH"
    chmod +x *.py *.sh
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install Node.js dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Build frontend
    log_info "Building frontend..."
    npm run build
    
    # Deactivate virtual environment
    deactivate
}

create_systemd_service() {
    if [[ "$INSTALL_SERVICE" == "true" ]]; then
        log_info "Creating systemd service..."
        
        cat > /etc/systemd/system/"$SERVICE_NAME".service << EOF
[Unit]
Description=RF Transceiver System Backend Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_PATH
Environment=PYTHONPATH=$INSTALL_PATH
ExecStart=$INSTALL_PATH/venv/bin/python $INSTALL_PATH/server_real_rf_system.py --host 0.0.0.0 --wsport 8765
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        # Reload systemd and enable service
        systemctl daemon-reload
        systemctl enable "$SERVICE_NAME"
        
        log_success "Systemd service created and enabled"
    fi
}

create_udev_rules() {
    log_info "Creating udev rules for USB devices..."
    
    cat > /etc/udev/rules.d/99-rf-transceiver.rules << EOF
# RF Transceiver System USB Device Rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666", GROUP="rfuser"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="003f", MODE="0666", GROUP="rfuser"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", MODE="0666", GROUP="rfuser"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0666", GROUP="rfuser"
EOF
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    log_success "Udev rules created and loaded"
}

create_desktop_shortcut() {
    if [[ "$CREATE_DESKTOP_SHORTCUT" == "true" ]]; then
        log_info "Creating desktop shortcut..."
        
        # Create desktop file
        cat > /usr/share/applications/rf-transceiver-system.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=RF Transceiver System
Comment=RF Transceiver System Control Suite
Exec=$INSTALL_PATH/START_RF_BACKEND.sh
Icon=$INSTALL_PATH/assets/icon.png
Terminal=true
Categories=Network;HamRadio;
EOF
        
        log_success "Desktop shortcut created"
    fi
}

create_uninstaller() {
    log_info "Creating uninstaller..."
    
    cat > "$INSTALL_PATH/uninstall.sh" << EOF
#!/bin/bash

echo "Uninstalling RF Transceiver System..."

# Stop and disable service
if systemctl is-active --quiet "$SERVICE_NAME"; then
    systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME"; then
    systemctl disable "$SERVICE_NAME"
fi

# Remove service file
rm -f /etc/systemd/system/"$SERVICE_NAME".service
systemctl daemon-reload

# Remove udev rules
rm -f /etc/udev/rules.d/99-rf-transceiver.rules
udevadm control --reload-rules

# Remove desktop shortcut
rm -f /usr/share/applications/rf-transceiver-system.desktop

# Remove application files
rm -rf "$INSTALL_PATH"

# Remove user (optional)
read -p "Remove service user $SERVICE_USER? (y/N): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    userdel "$SERVICE_USER" 2>/dev/null || true
fi

echo "RF Transceiver System uninstalled successfully!"
EOF
    
    chmod +x "$INSTALL_PATH/uninstall.sh"
    chown "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_PATH/uninstall.sh"
}

# Main installation process
main() {
    echo -e "${GREEN}RF Transceiver System - Linux Installer${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    check_root
    check_dependencies
    install_system_dependencies
    create_user
    install_application
    create_systemd_service
    create_udev_rules
    create_desktop_shortcut
    create_uninstaller
    
    log_success "Installation completed successfully!"
    echo -e "${BLUE}Installation path:${NC} $INSTALL_PATH"
    echo -e "${BLUE}To start the service:${NC} systemctl start $SERVICE_NAME"
    echo -e "${BLUE}To check status:${NC} systemctl status $SERVICE_NAME"
    echo -e "${BLUE}To uninstall:${NC} Run $INSTALL_PATH/uninstall.sh"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --no-service)
            INSTALL_SERVICE=false
            shift
            ;;
        --no-desktop-shortcut)
            CREATE_DESKTOP_SHORTCUT=false
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --install-path PATH    Installation path (default: /opt/rf-transceiver-system)"
            echo "  --no-service          Don't install systemd service"
            echo "  --no-desktop-shortcut Don't create desktop shortcut"
            echo "  --force               Force overwrite existing installation"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main
