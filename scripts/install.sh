#!/bin/bash
# PiSecOS Installer
# Location: pisecos/scripts/install.sh

echo "PiSecOS Installer"
echo "================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Go up one level to repo root
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "Repository found at: $REPO_DIR"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo ./scripts/install.sh"
    exit 1
fi

# Verify Bullseye
if ! grep -q "bullseye" /etc/os-release; then
    echo "Warning: This doesn't appear to be Raspberry Pi OS Bullseye"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installing PiSecOS from $REPO_DIR..."

# Create system directories
mkdir -p /var/log/pisecos
mkdir -p /etc/pisecos

# Create symlinks
ln -sf $REPO_DIR/configs /etc/pisecos/configs
ln -sf $REPO_DIR/tools /opt/pisecos-tools 2>/dev/null
ln -sf $REPO_DIR/scans /opt/pisecos-scans 2>/dev/null

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-pip python3-dev git wget curl \
    nmap nikto gobuster dirb wordlists \
    python3-tk python3-pyqt5

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f "$REPO_DIR/requirements.txt" ]; then
    pip3 install -r $REPO_DIR/requirements.txt
else
    pip3 install requests psutil
fi

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/pisecos.service << EOF
[Unit]
Description=PiSecOS Pentesting Framework
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$REPO_DIR
Environment="PYTHONPATH=$REPO_DIR"
ExecStart=/usr/bin/python3 $REPO_DIR/core/launcher.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Make Python files executable
find $REPO_DIR/core -name "*.py" -exec chmod +x {} \;
find $REPO_DIR/gui -name "*.py" -exec chmod +x {} \;

# Enable service
systemctl daemon-reload
systemctl enable pisecos.service

echo ""
echo "===================================="
echo "Installation complete!"
echo "===================================="
echo ""
echo "Your repository is at: $REPO_DIR"
echo ""
echo "Commands:"
echo "  Start now    : sudo systemctl start pisecos"
echo "  Check status : sudo systemctl status pisecos"
echo "  View logs    : sudo journalctl -u pisecos -f"
echo "  Stop         : sudo systemctl stop pisecos"
echo "  Restart      : sudo systemctl restart pisecos"
echo ""
echo "Files location:"
echo "  Configs : $REPO_DIR/configs/"
echo "  Core    : $REPO_DIR/core/"
echo "  GUI     : $REPO_DIR/gui/"
echo "  Tools   : $REPO_DIR/tools/"
echo "  Scans   : $REPO_DIR/scans/"
echo "===================================="


# Install AI dependencies and offer to download model
echo "Installing AI dependencies..."
pip3 install llama-cpp-python || echo "AI dependencies optional, continuing..."

# Offer to download model
read -p "Download AEGIS AI model now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    bash /usr/local/pisecos/scripts/download_aegis_model.sh
fi