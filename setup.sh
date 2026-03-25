#!/bin/bash
# ============================================
# SMART STUDY DESK - AUTOMATIC SETUP SCRIPT
# ============================================
# Cài đặt tất cả dependencies + project setup
# Usage: bash setup.sh

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
        MODEL=$(cat /proc/device-tree/model)
        print_success "Detected: $MODEL"
        return 0
    else
        print_warning "Not running on Raspberry Pi (simulation mode enabled)"
        return 1
    fi
}

# Update system
update_system() {
    print_header "STEP 1: Updating System"
    
    sudo apt update
    sudo apt upgrade -y
    
    print_success "System updated"
}

# Install system dependencies
install_system_deps() {
    print_header "STEP 2: Installing System Dependencies"
    
    PACKAGES=(
        "python3-pip"
        "python3-dev"
        "git"
        "python3-opencv"
        "libatlas-base-dev"
        "libjasper-dev"
        "libtiff-dev"
        "libjasper1"
        "libharfbuzz0b"
        "libwebp6"
        "libtiff5"
        "libjasper1"
        "libharfbuzz0b"
        "libwebp6"
    )
    
    for package in "${PACKAGES[@]}"; do
        if dpkg -l | grep -q "^ii.*$package"; then
            print_success "$package already installed"
        else
            print_warning "Installing $package..."
            sudo apt install -y "$package"
        fi
    done
}

# Install Python dependencies
install_python_deps() {
    print_header "STEP 3: Installing Python Dependencies"
    
    # Upgrade pip
    pip3 install --upgrade pip
    
    # Install requirements
    pip3 install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Setup GPIO
setup_gpio() {
    print_header "STEP 4: Setting up GPIO"
    
    # Add user to gpio group
    if ! groups pi | grep -q gpio; then
        sudo usermod -a -G gpio pi
        print_success "Added 'pi' user to gpio group"
    else
        print_success "User 'pi' already in gpio group"
    fi
}

# Create .env file for configuration
create_env_file() {
    print_header "STEP 5: Creating Configuration File"
    
    ENV_FILE=".env"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Creating $ENV_FILE template..."
        
        cat > "$ENV_FILE" << 'EOF'
# Telegram Configuration
TELEGRAM_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE

# GPIO Configuration
RELAY_PIN=17

# Camera Configuration
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30

# Web Configuration
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_DEBUG=False

# Debug
DEBUG_MODE=False
SIMULATE_HARDWARE=False
EOF
        
        print_success "Created $ENV_FILE"
        print_warning "Please edit $ENV_FILE and add your Telegram credentials!"
        print_warning "nano .env"
    else
        print_success ".env already exists"
    fi
}

# Create systemd service for auto-start
create_systemd_service() {
    print_header "STEP 6: Creating Systemd Service"
    
    SERVICE_FILE="/etc/systemd/system/smart-study-desk.service"
    
    print_warning "Creating systemd service file..."
    
    sudo tee "$SERVICE_FILE" > /dev/null << 'EOF'
[Unit]
Description=Smart Study Desk System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/smart-study-desk
Environment="PATH=/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/bin/python3 /home/pi/smart-study-desk/main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Systemd service created"
    print_warning "To enable auto-start: sudo systemctl enable smart-study-desk"
}

# Test installations
test_installations() {
    print_header "STEP 7: Testing Installations"
    
    # Test Python
    if python3 --version | grep -q "Python 3"; then
        print_success "Python 3: $(python3 --version)"
    else
        print_error "Python 3 not found!"
        return 1
    fi
    
    # Test OpenCV
    if python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>/dev/null; then
        print_success "OpenCV installed"
    else
        print_error "OpenCV import failed!"
    fi
    
    # Test Flask
    if python3 -c "import flask; print(f'Flask: {flask.__version__}')" 2>/dev/null; then
        print_success "Flask installed"
    else
        print_error "Flask import failed!"
    fi
    
    # Test RPi.GPIO (only if on real Raspberry)
    if check_raspberry_pi; then
        if python3 -c "import RPi.GPIO" 2>/dev/null; then
            print_success "RPi.GPIO installed"
        else
            print_warning "RPi.GPIO not available (will use simulation)"
        fi
    fi
}

# Final checklist
final_checklist() {
    print_header "SETUP COMPLETE! ✅"
    
    echo -e "\n${BLUE}📋 Checklist:${NC}"
    echo "  ✅ System updated"
    echo "  ✅ System dependencies installed"
    echo "  ✅ Python dependencies installed"
    echo "  ✅ GPIO configured"
    echo "  ✅ Configuration files created"
    echo "  ✅ Systemd service created"
    
    echo -e "\n${BLUE}📝 Next steps:${NC}"
    echo "  1. Edit .env file with your Telegram credentials:"
    echo "     nano .env"
    echo ""
    echo "  2. Test camera:"
    echo "     python3 vision/camera.py"
    echo ""
    echo "  3. Test motion detector:"
    echo "     python3 vision/motion_detector.py"
    echo ""
    echo "  4. Test relay:"
    echo "     python3 hardware/relay.py"
    echo ""
    echo "  5. Run main system:"
    echo "     python3 main.py"
    echo ""
    echo "  6. Or enable auto-start:"
    echo "     sudo systemctl enable smart-study-desk"
    echo "     sudo systemctl start smart-study-desk"
    
    echo -e "\n${BLUE}📊 Current Status:${NC}"
    echo "  Raspberry Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
    echo "  Python: $(python3 --version)"
    echo "  IP Address: $(hostname -I)"
    
    echo -e "\n${GREEN}🎉 Ready to go!${NC}\n"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║  SMART STUDY DESK - SETUP SCRIPT       ║"
    echo "║  IoT Learning Environment System       ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Check if running as root for some operations
    if [ "$EUID" -ne 0 ] && [ "$EUID" != "" ]; then
        # Some operations need sudo, which will be called when needed
        print_warning "Some operations require sudo and will prompt for password"
    fi
    
    # Execute setup steps
    check_raspberry_pi
    update_system
    install_system_deps
    install_python_deps
    setup_gpio
    create_env_file
    create_systemd_service
    test_installations
    final_checklist
}

# Run main function
main
