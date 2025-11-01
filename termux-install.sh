#!/data/data/com.termux/files/usr/bin/bash

################################################################################
# Onion Hoster - Termux Quick Install Script
# Author: Uzair Developer
# GitHub: uzairdeveloper223
#
# Quick installation script for Termux users
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Print functions
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${CYAN}ℹ${NC} $1"; }
print_header() { echo -e "${PURPLE}${BOLD}$1${NC}"; }

# Banner
clear
echo -e "${PURPLE}${BOLD}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║              ONION HOSTER - TERMUX INSTALLER                 ║
║        Quick Setup for Termux Android Users                  ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "This script must be run in Termux!"
    print_info "Download Termux from F-Droid: https://f-droid.org/packages/com.termux/"
    exit 1
fi

print_success "Running in Termux environment"
echo ""

# Check storage permission
print_header "=== Step 1: Storage Access ==="
echo ""
print_info "Checking storage access..."

if [ ! -d "$HOME/storage" ]; then
    print_warning "Storage access not granted"
    print_info "Granting storage access..."
    termux-setup-storage
    sleep 2

    if [ ! -d "$HOME/storage" ]; then
        print_error "Storage access denied"
        print_warning "Please manually run: termux-setup-storage"
        echo ""
        read -p "Press Enter to continue anyway..."
    else
        print_success "Storage access granted"
    fi
else
    print_success "Storage access already granted"
fi
echo ""

# Update packages
print_header "=== Step 2: Updating Packages ==="
echo ""
print_info "Updating package lists..."
if pkg update -y; then
    print_success "Package lists updated"
else
    print_error "Failed to update packages"
    exit 1
fi
echo ""

print_info "Upgrading installed packages..."
if pkg upgrade -y; then
    print_success "Packages upgraded"
else
    print_warning "Some packages may need manual upgrade"
fi
echo ""

# Install dependencies
print_header "=== Step 3: Installing Dependencies ==="
echo ""

# Install Tor
print_info "Installing Tor..."
if pkg install tor -y; then
    print_success "Tor installed successfully"
else
    print_error "Failed to install Tor"
    exit 1
fi

# Install Nginx
print_info "Installing Nginx..."
if pkg install nginx -y; then
    print_success "Nginx installed successfully"
else
    print_error "Failed to install Nginx"
    exit 1
fi

# Install Termux-API (optional)
print_info "Installing Termux-API (optional)..."
if pkg install termux-api -y; then
    print_success "Termux-API installed successfully"
    print_warning "Note: You also need to install 'Termux:API' app from F-Droid"
    print_info "Download from: https://f-droid.org/packages/com.termux.api/"
else
    print_warning "Termux-API installation failed (optional feature)"
fi

# Install Git (if not already installed)
if ! command -v git &> /dev/null; then
    print_info "Installing Git..."
    pkg install git -y
fi

echo ""

# Download Onion Hoster
print_header "=== Step 4: Downloading Onion Hoster ==="
echo ""

INSTALL_DIR="$HOME/onion-hoster"

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Onion Hoster directory already exists"
    echo -n "Do you want to remove it and reinstall? (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        print_success "Removed existing installation"
    else
        print_info "Using existing installation"
        cd "$INSTALL_DIR"
    fi
fi

if [ ! -d "$INSTALL_DIR" ]; then
    print_info "Cloning repository..."
    if git clone https://github.com/uzairdeveloper223/Onion-Hoster.git "$INSTALL_DIR"; then
        print_success "Repository cloned successfully"
        cd "$INSTALL_DIR"
    else
        print_error "Failed to clone repository"
        print_info "You can manually download from: https://github.com/uzairdeveloper223/Onion-Hoster"
        exit 1
    fi
fi

# Make script executable
chmod +x termux.sh
print_success "Script made executable"
echo ""

# Create alias
print_header "=== Step 5: Setting Up Command Alias ==="
echo ""

BASHRC="$HOME/.bashrc"
ALIAS_LINE="alias onion-host='$INSTALL_DIR/termux.sh'"

if grep -q "alias onion-host=" "$BASHRC" 2>/dev/null; then
    print_warning "Alias already exists in .bashrc"
else
    echo "" >> "$BASHRC"
    echo "# Onion Hoster alias" >> "$BASHRC"
    echo "$ALIAS_LINE" >> "$BASHRC"
    print_success "Alias added to .bashrc"
    print_info "You can now use 'onion-host' command from anywhere"
fi
echo ""

# Create desktop shortcut (if termux-widget is available)
if command -v termux-widget &> /dev/null; then
    print_info "Creating widget shortcut..."
    mkdir -p "$HOME/.shortcuts"
    cat > "$HOME/.shortcuts/onion-host.sh" << EOF
#!/data/data/com.termux/files/usr/bin/bash
$INSTALL_DIR/termux.sh menu
EOF
    chmod +x "$HOME/.shortcuts/onion-host.sh"
    print_success "Widget shortcut created"
    print_info "Add Termux:Widget to your home screen to use the shortcut"
fi
echo ""

# Installation complete
print_header "=== Installation Complete! ==="
echo ""
print_success "Onion Hoster has been installed successfully!"
echo ""
echo -e "${BOLD}Installation Directory:${NC} $INSTALL_DIR"
echo ""
echo -e "${BOLD}Quick Start:${NC}"
echo ""
echo "  1. Run the interactive menu:"
echo -e "     ${CYAN}cd $INSTALL_DIR && ./termux.sh${NC}"
echo ""
echo "  2. Or use the alias (restart Termux first):"
echo -e "     ${CYAN}onion-host${NC}"
echo ""
echo "  3. Or run specific commands:"
echo -e "     ${CYAN}cd $INSTALL_DIR && ./termux.sh help${NC}"
echo ""

echo -e "${BOLD}Next Steps:${NC}"
echo ""
echo "  • Choose hosting method:"
echo -e "    ${CYAN}./termux.sh method nginx${NC}              # For static sites"
echo -e "    ${CYAN}./termux.sh method custom_port 3000${NC}   # For dynamic sites"
echo ""
echo "  • Set site directory (for nginx method):"
echo -e "    ${CYAN}./termux.sh config set site_directory ~/mysite${NC}"
echo ""
echo "  • Start the service:"
echo -e "    ${CYAN}./termux.sh start${NC}"
echo ""
echo "  • Check status:"
echo -e "    ${CYAN}./termux.sh status${NC}"
echo ""

echo -e "${BOLD}Documentation:${NC}"
echo "  • Full Guide: $INSTALL_DIR/TERMUX_README.md"
echo "  • General Help: ./termux.sh help"
echo ""

echo -e "${BOLD}Support:${NC}"
echo "  • GitHub: https://github.com/uzairdeveloper223/Onion-Hoster"
echo "  • Issues: https://github.com/uzairdeveloper223/Onion-Hoster/issues"
echo ""

# Offer to run the script
echo -e "${YELLOW}${BOLD}Would you like to run Onion Hoster now? (y/n)${NC} "
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    print_success "Starting Onion Hoster..."
    sleep 1
    exec ./termux.sh
else
    echo ""
    print_info "You can start Onion Hoster anytime with:"
    echo -e "  ${CYAN}cd $INSTALL_DIR && ./termux.sh${NC}"
    echo ""
    print_success "Enjoy hosting on Tor! 🎉"
fi

exit 0
