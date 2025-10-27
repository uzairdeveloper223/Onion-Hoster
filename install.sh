#!/bin/bash
#
# Onion Hoster - Installation Script
# Author: Uzair Developer
# GitHub: uzairdeveloper223
#
# This script helps install Onion Hoster and its dependencies
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ONION HOSTER INSTALLER                    ║"
    echo "║        Host your static websites on the Tor Network         ║"
    echo "║                                                              ║"
    echo "║              Author: Uzair Developer                         ║"
    echo "║              GitHub: github.com/uzairdeveloper223            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

# Print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS and distribution
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS_NAME=$ID
            OS_VERSION=$VERSION_ID
        else
            OS_NAME="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_NAME="macos"
    elif [[ -n "$TERMUX_VERSION" ]]; then
        OS_NAME="termux"
    else
        OS_NAME="unknown"
    fi
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."

    if command_exists python3; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, but found $PYTHON_VERSION"
            return 1
        fi
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)

        if [ "$PYTHON_MAJOR" -eq 3 ]; then
            PYTHON_CMD="python"
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required"
            return 1
        fi
    else
        print_error "Python is not installed"
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."

    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        print_error "pip is not installed"
        return 1
    fi

    $PIP_CMD install -r requirements.txt --user

    if [ $? -eq 0 ]; then
        print_success "Python dependencies installed"
        return 0
    else
        print_error "Failed to install Python dependencies"
        return 1
    fi
}

# Install system dependencies based on OS
install_system_deps() {
    print_info "Checking system dependencies..."

    case "$OS_NAME" in
        ubuntu|debian|linuxmint|pop)
            print_info "Detected Debian-based system"
            echo "Do you want to install Tor and Nginx? (y/n)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                sudo apt update
                sudo apt install -y tor nginx
                print_success "Tor and Nginx installed"
            fi
            ;;

        arch|manjaro|endeavouros)
            print_info "Detected Arch-based system"
            echo "Do you want to install Tor and Nginx? (y/n)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                sudo pacman -Sy --noconfirm tor nginx
                print_success "Tor and Nginx installed"
            fi
            ;;

        fedora|rhel|centos|rocky|alma)
            print_info "Detected RedHat-based system"
            echo "Do you want to install Tor and Nginx? (y/n)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                sudo dnf install -y tor nginx
                print_success "Tor and Nginx installed"
            fi
            ;;

        macos)
            print_info "Detected macOS"
            if ! command_exists brew; then
                print_warning "Homebrew not found"
                echo "Install Homebrew? (y/n)"
                read -r response
                if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                fi
            fi

            if command_exists brew; then
                echo "Do you want to install Tor and Nginx via Homebrew? (y/n)"
                read -r response
                if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                    brew install tor nginx
                    print_success "Tor and Nginx installed"
                fi
            fi
            ;;

        termux)
            print_info "Detected Termux"
            echo "Do you want to install Tor and Nginx? (y/n)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                pkg update
                pkg install -y tor nginx
                print_success "Tor and Nginx installed"
            fi
            ;;

        *)
            print_warning "Unknown OS. Please install Tor and Nginx manually."
            ;;
    esac
}

# Make launcher executable
setup_launcher() {
    print_info "Setting up launcher..."

    if [ -f "onion-host" ]; then
        chmod +x onion-host
        print_success "Launcher is now executable"
    else
        print_warning "Launcher script not found"
    fi
}

# Create desktop entry (Linux only)
create_desktop_entry() {
    if [[ "$OS_NAME" != "ubuntu" && "$OS_NAME" != "debian" && "$OS_NAME" != "arch" && "$OS_NAME" != "fedora" ]]; then
        return
    fi

    print_info "Create desktop entry? (y/n)"
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        INSTALL_DIR="$(pwd)"
        DESKTOP_FILE="$HOME/.local/share/applications/onion-hoster.desktop"

        mkdir -p "$HOME/.local/share/applications"

        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Onion Hoster
Comment=Host static websites on Tor Network
Icon=network-server
Exec=$INSTALL_DIR/onion-host --gui
Terminal=false
Categories=Network;Application;
Keywords=tor;onion;hosting;privacy;
EOF

        chmod +x "$DESKTOP_FILE"
        print_success "Desktop entry created"
    fi
}

# Test installation
test_installation() {
    print_info "Testing installation..."

    if [ -f "onion-host.py" ]; then
        $PYTHON_CMD onion-host.py --version >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_success "Installation test passed"
            return 0
        else
            print_warning "Installation test had issues"
            return 1
        fi
    else
        print_error "Main script not found"
        return 1
    fi
}

# Main installation process
main() {
    print_banner

    print_info "Starting Onion Hoster installation...\n"

    # Detect OS
    detect_os
    print_info "Operating System: $OS_NAME"

    # Check Python
    if ! check_python; then
        print_error "Please install Python 3.8 or higher and try again"
        exit 1
    fi

    # Install Python dependencies
    if ! install_python_deps; then
        print_error "Failed to install Python dependencies"
        exit 1
    fi

    # Install system dependencies
    install_system_deps

    # Setup launcher
    setup_launcher

    # Create desktop entry (Linux)
    create_desktop_entry

    # Test installation
    test_installation

    # Success message
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}To start Onion Hoster:${NC}"
    echo ""
    echo -e "  ${YELLOW}Auto-detect mode:${NC}  ./onion-host"
    echo -e "  ${YELLOW}GUI mode:${NC}         ./onion-host --gui"
    echo -e "  ${YELLOW}CLI mode:${NC}         ./onion-host --cli"
    echo -e "  ${YELLOW}Check system:${NC}     ./onion-host --check-system"
    echo ""
    echo -e "${GREEN}Quick start:${NC}"
    echo -e "  1. Run: ${YELLOW}./onion-host${NC}"
    echo -e "  2. Select your website directory"
    echo -e "  3. Click 'Start Service'"
    echo -e "  4. Share your .onion address!"
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    print_info "For help, visit: https://github.com/uzairdeveloper223/Onion-Hoster"
    echo ""
}

# Run main installation
main
