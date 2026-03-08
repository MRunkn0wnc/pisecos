#!/bin/bash
# PiSecOS Installer - ROBUST VERSION

echo "PiSecOS Installer"
echo "================="

# Get the directory where this script is located (YOUR VERSION - BEST!)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Go up one level to repo root
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "Script location: $SCRIPT_DIR"
echo "Repository root: $REPO_DIR"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo $SCRIPT_DIR/install.sh"
    exit 1
fi

# Get the actual user (not root)
REAL_USER=${SUDO_USER:-$USER}
echo "Setting up for user: $REAL_USER"

# Create directories
echo "Creating directories..."
mkdir -p /opt/pisecos/{tools,scans,reports}
mkdir -p /var/log/pisecos
mkdir -p /etc/pisecos
mkdir -p $REPO_DIR/tools
mkdir -p $REPO_DIR/scans
mkdir -p $REPO_DIR/reports

# Create AI directories
echo "Creating AI directories..."
mkdir -p $REPO_DIR/core/ai/{bin,models}
chown -R $REAL_USER:$REAL_USER $REPO_DIR/core/ai 2>/dev/null || true

# Install system dependencies
echo "Installing system packages..."
apt-get update
apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    nmap \
    nikto \
    gobuster \
    dirb \
    wordlists \
    python3-tk \
    python3-pyqt5 \
    build-essential \
    cmake \
    libopenblas-dev \
    sqlmap \
    hydra \
    john \
    aircrack-ng

# Install Python packages
echo "Installing Python dependencies..."
pip3 install requests psutil PyQt5

# Create symlinks
echo "Creating symlinks..."
ln -sf $REPO_DIR/configs /etc/pisecos/configs
ln -sf $REPO_DIR/tools /opt/pisecos/tools
ln -sf $REPO_DIR/scans /opt/pisecos/scans
ln -sf $REPO_DIR/reports /opt/pisecos/reports

# Create systemd service
echo "Creating boot service..."
cat > /etc/systemd/system/pisecos.service << EOF
[Unit]
Description=PiSecOS Pentesting Framework
After=network.target

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$REPO_DIR
Environment="PYTHONPATH=$REPO_DIR"
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 $REPO_DIR/core/launcher.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl daemon-reload
systemctl enable pisecos.service

# Make scripts executable
chmod +x $REPO_DIR/scripts/*.sh
find $REPO_DIR/core -name "*.py" -exec chmod +x {} \;
find $REPO_DIR/gui -name "*.py" -exec chmod +x {} \;

# Set permissions
chown -R $REAL_USER:$REAL_USER $REPO_DIR 2>/dev/null || true
chown -R $REAL_USER:$REAL_USER /opt/pisecos 2>/dev/null || true
chown -R $REAL_USER:$REAL_USER /var/log/pisecos 2>/dev/null || true

echo ""
echo "===================================="
echo "INSTALLATION COMPLETE!"
echo "===================================="
echo ""
echo "Your PiSecOS is at: $REPO_DIR"
echo ""
echo " AI Setup (Optional but Recommended):"
echo "  After reboot, place your AI files:"
echo "  - Binary: $REPO_DIR/core/ai/bin/main"
echo "  - Model:  $REPO_DIR/core/ai/models/model.gguf"
echo ""
echo "  Or use symlinks:"
echo "  ln -s ~/llama.cpp/build/bin/main $REPO_DIR/core/ai/bin/"
echo "  ln -s ~/llama.cpp/models/your-model.gguf $REPO_DIR/core/ai/models/model.gguf"
echo ""
echo " Commands:"
echo "  Start now    : sudo systemctl start pisecos"
echo "  Check status : sudo systemctl status pisecos"
echo "  View logs    : sudo journalctl -u pisecos -f"
echo "  Stop         : sudo systemctl stop pisecos"
echo "  Restart      : sudo systemctl restart pisecos"
echo ""
echo " After reboot, PiSecOS starts automatically!"
echo "===================================="