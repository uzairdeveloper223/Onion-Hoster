#!/data/data/com.termux/files/usr/bin/bash

################################################################################
# Onion Hoster - Termux Edition
# Author: Uzair Developer
# GitHub: uzairdeveloper223
#
# A complete bash implementation for Termux users to host websites on Tor
# without Python dependencies.
################################################################################

# Version
VERSION="1.0.0"
APP_NAME="Onion Hoster (Termux)"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration paths
CONFIG_DIR="$HOME/.onion-hoster-termux"
CONFIG_FILE="$CONFIG_DIR/config.conf"
LOG_FILE="$CONFIG_DIR/onion-hoster.log"
HIDDEN_SERVICE_DIR="$HOME/.tor/hidden_service"
TOR_CONFIG="$PREFIX/etc/tor/torrc"
NGINX_CONFIG="$PREFIX/etc/nginx/nginx.conf"
NGINX_SITE_CONFIG="$PREFIX/etc/nginx/sites-available/onion-site.conf"
PID_DIR="$CONFIG_DIR/pids"

# Restricted ports (Tor-related)
RESTRICTED_PORTS="9050 9051 9150 9151"

# Default values
DEFAULT_NGINX_PORT=8080
DEFAULT_HOSTING_METHOD="nginx"

################################################################################
# Utility Functions
################################################################################

# Print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_header() {
    echo -e "${PURPLE}${BOLD}$1${NC}"
}

# Log function
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Print banner
print_banner() {
    clear
    echo -e "${PURPLE}${BOLD}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    ONION HOSTER (TERMUX)                     ║
║        Host your websites on the Tor Network - Termux        ║
║                                                              ║
║              Author: Uzair Developer                         ║
║              GitHub: github.com/uzairdeveloper223            ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${CYAN}Version: $VERSION${NC}"
    echo ""
}

# Initialize configuration directory
init_config() {
    if [ ! -d "$CONFIG_DIR" ]; then
        mkdir -p "$CONFIG_DIR"
        mkdir -p "$PID_DIR"
        log_message "Configuration directory created"
    fi

    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOF
# Onion Hoster Configuration
SITE_DIRECTORY=""
HOSTING_METHOD="$DEFAULT_HOSTING_METHOD"
NGINX_PORT=$DEFAULT_NGINX_PORT
CUSTOM_PORT=""
ONION_ADDRESS=""
SERVICE_RUNNING=false
FIRST_RUN=true
EOF
        log_message "Configuration file created"
    fi
}

# Load configuration
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    fi
}

# Save configuration
save_config() {
    cat > "$CONFIG_FILE" << EOF
# Onion Hoster Configuration
SITE_DIRECTORY="$SITE_DIRECTORY"
HOSTING_METHOD="$HOSTING_METHOD"
NGINX_PORT=$NGINX_PORT
CUSTOM_PORT="$CUSTOM_PORT"
ONION_ADDRESS="$ONION_ADDRESS"
SERVICE_RUNNING=$SERVICE_RUNNING
FIRST_RUN=false
EOF
    log_message "Configuration saved"
}

################################################################################
# Validation Functions
################################################################################

# Validate port
validate_port() {
    local port=$1

    # Check if port is a number
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        print_error "Port must be a number"
        return 1
    fi

    # Check port range
    if [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        print_error "Port must be between 1 and 65535"
        return 1
    fi

    # Check restricted ports
    for restricted in $RESTRICTED_PORTS; do
        if [ "$port" -eq "$restricted" ]; then
            print_error "Port $port is reserved for Tor services and cannot be used"
            return 1
        fi
    done

    # Warn about system reserved ports
    if [ "$port" -lt 1024 ]; then
        print_warning "Port $port is a system reserved port (1-1023). Consider using a port above 1024"
    fi

    return 0
}

# Validate directory
validate_directory() {
    local dir=$1

    if [ ! -d "$dir" ]; then
        print_error "Directory does not exist: $dir"
        return 1
    fi

    if [ ! -r "$dir" ]; then
        print_error "Directory is not readable: $dir"
        return 1
    fi

    # Check for index file (only for nginx method)
    if [ "$HOSTING_METHOD" = "nginx" ]; then
        if [ ! -f "$dir/index.html" ] && [ ! -f "$dir/index.htm" ]; then
            print_error "No index.html or index.htm found in directory"
            print_info "Your site directory must contain an index file"
            return 1
        fi
    fi

    return 0
}

################################################################################
# Dependency Management
################################################################################

# Check if a package is installed
check_package() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check all dependencies
check_dependencies() {
    print_header "=== Dependency Status ==="
    echo ""

    if check_package tor; then
        print_success "Tor: Installed"
        TOR_INSTALLED=true
    else
        print_error "Tor: Not Installed"
        TOR_INSTALLED=false
    fi

    if check_package nginx; then
        print_success "Nginx: Installed"
        NGINX_INSTALLED=true
    else
        print_error "Nginx: Not Installed"
        NGINX_INSTALLED=false
    fi

    if check_package termux-clipboard-set; then
        print_success "Termux-API: Installed"
        TERMUX_API_INSTALLED=true
    else
        print_warning "Termux-API: Not Installed (optional, for clipboard support)"
        TERMUX_API_INSTALLED=false
    fi

    echo ""
}

# Install Tor
install_tor() {
    print_info "Installing Tor..."
    if pkg update && pkg install -y tor; then
        print_success "Tor installed successfully!"
        log_message "Tor installed"
        return 0
    else
        print_error "Failed to install Tor"
        log_message "Tor installation failed"
        return 1
    fi
}

# Install Nginx
install_nginx() {
    print_info "Installing Nginx..."
    if pkg update && pkg install -y nginx; then
        print_success "Nginx installed successfully!"
        log_message "Nginx installed"
        return 0
    else
        print_error "Failed to install Nginx"
        log_message "Nginx installation failed"
        return 1
    fi
}

# Install Termux-API
install_termux_api() {
    print_info "Installing Termux-API..."
    if pkg update && pkg install -y termux-api; then
        print_success "Termux-API installed successfully!"
        print_info "Note: You also need to install 'Termux:API' app from F-Droid/Play Store"
        log_message "Termux-API installed"
        return 0
    else
        print_error "Failed to install Termux-API"
        log_message "Termux-API installation failed"
        return 1
    fi
}

# Install all dependencies
install_all_dependencies() {
    print_header "=== Installing All Dependencies ==="
    echo ""

    install_tor
    install_nginx
    install_termux_api

    echo ""
    print_success "All dependencies installed!"
}

################################################################################
# Tor Configuration
################################################################################

# Configure Tor hidden service
configure_tor() {
    local target_port=$1

    print_info "Configuring Tor hidden service..."

    # Create hidden service directory
    if [ ! -d "$HIDDEN_SERVICE_DIR" ]; then
        mkdir -p "$HIDDEN_SERVICE_DIR"
        chmod 700 "$HIDDEN_SERVICE_DIR"
        log_message "Hidden service directory created"
    fi

    # Backup original torrc if exists and not already backed up
    if [ -f "$TOR_CONFIG" ] && [ ! -f "$TOR_CONFIG.bak" ]; then
        cp "$TOR_CONFIG" "$TOR_CONFIG.bak"
        log_message "Tor config backed up"
    fi

    # Create a cleaned version without commented HiddenService examples
    if [ -f "$TOR_CONFIG" ]; then
        # Remove commented HiddenService examples that might cause conflicts
        grep -v "^#HiddenServiceDir" "$TOR_CONFIG" | grep -v "^#HiddenServicePort" > "$TOR_CONFIG.tmp"
        mv "$TOR_CONFIG.tmp" "$TOR_CONFIG"
    fi

    # Check if our hidden service is already configured (uncommented line)
    if grep -q "^HiddenServiceDir $HIDDEN_SERVICE_DIR" "$TOR_CONFIG" 2>/dev/null; then
        print_info "Hidden service already configured, updating port..."

        # Create temp file with updated configuration
        awk -v dir="$HIDDEN_SERVICE_DIR" -v port="$target_port" '
        /^HiddenServiceDir/ {
            if ($0 ~ dir) {
                print $0
                in_our_hs=1
                next
            }
        }
        /^HiddenServicePort/ {
            if (in_our_hs) {
                print "HiddenServicePort 80 127.0.0.1:" port
                in_our_hs=0
                next
            }
        }
        /^HiddenServiceDir/ {
            in_our_hs=0
        }
        { print }
        ' "$TOR_CONFIG" > "$TOR_CONFIG.tmp"

        mv "$TOR_CONFIG.tmp" "$TOR_CONFIG"
        print_success "Updated Tor configuration port"
    else
        print_info "Adding new hidden service configuration..."
        # Add new hidden service configuration at the end
        cat >> "$TOR_CONFIG" << EOF

# Onion Hoster Hidden Service Configuration
HiddenServiceDir $HIDDEN_SERVICE_DIR
HiddenServicePort 80 127.0.0.1:$target_port
EOF
        print_success "Tor hidden service configured"
    fi

    log_message "Tor configured with target port: $target_port"
    return 0
}

# Get onion address
get_onion_address() {
    local hostname_file="$HIDDEN_SERVICE_DIR/hostname"

    if [ -f "$hostname_file" ]; then
        ONION_ADDRESS=$(cat "$hostname_file")
        echo "$ONION_ADDRESS"
        return 0
    else
        return 1
    fi
}

################################################################################
# Nginx Configuration
################################################################################

# Create Nginx configuration
create_nginx_config() {
    local site_dir=$1
    local port=$2

    print_info "Creating Nginx configuration..."

    # Create sites-available directory if it doesn't exist
    local nginx_sites_dir="$PREFIX/etc/nginx/sites-available"
    mkdir -p "$nginx_sites_dir"
    mkdir -p "$PREFIX/etc/nginx/sites-enabled"

    # Create Nginx site configuration
    cat > "$NGINX_SITE_CONFIG" << EOF
server {
    listen 127.0.0.1:$port;
    server_name localhost;

    # Security headers
    server_tokens off;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer" always;

    root $site_dir;
    index index.html index.htm;

    # Static files
    location / {
        try_files \$uri \$uri/ =404;
    }

    # Disable access logs for privacy
    access_log off;
    error_log $LOG_FILE;
}
EOF

    # Enable the site (create symlink)
    local enabled_link="$PREFIX/etc/nginx/sites-enabled/onion-site.conf"
    if [ -L "$enabled_link" ]; then
        rm "$enabled_link"
    fi
    ln -s "$NGINX_SITE_CONFIG" "$enabled_link"

    # Update main nginx.conf to include sites-enabled
    if ! grep -q "include.*sites-enabled" "$NGINX_CONFIG"; then
        sed -i '/http {/a \    include sites-enabled/*.conf;' "$NGINX_CONFIG"
    fi

    print_success "Nginx configuration created"
    log_message "Nginx configured for $site_dir on port $port"
    return 0
}

################################################################################
# Service Management
################################################################################

# Kill existing Tor processes (SAFELY - only our processes)
kill_existing_tor() {
    print_info "Checking for existing Tor processes..."

    # First, kill our own PID if it exists
    if [ -f "$PID_DIR/tor.pid" ]; then
        local our_pid=$(cat "$PID_DIR/tor.pid")
        if kill -0 "$our_pid" 2>/dev/null; then
            print_info "Stopping our Tor process (PID: $our_pid)..."
            kill "$our_pid" 2>/dev/null
            sleep 2
            rm -f "$PID_DIR/tor.pid"
            print_success "Stopped our Tor process"
            log_message "Cleaned up our Tor process"
            return 0
        else
            rm -f "$PID_DIR/tor.pid"
        fi
    fi

    # Look for Tor processes using our specific config file
    local tor_pids=$(pgrep -f "tor -f $TOR_CONFIG" 2>/dev/null)

    if [ -n "$tor_pids" ]; then
        print_warning "Found Tor processes using our config, cleaning up..."

        for pid in $tor_pids; do
            if [ -n "$pid" ]; then
                print_info "Killing Tor PID: $pid"
                kill "$pid" 2>/dev/null
            fi
        done

        sleep 2
        print_success "Cleaned up Tor processes"
        log_message "Cleaned up Tor processes using our config"
        return 0
    else
        print_info "No Tor processes using our config found"
        return 0
    fi
}

# Start Tor
start_tor() {
    print_info "Starting Tor..."

    # Kill any existing Tor processes first
    kill_existing_tor

    # Start Tor in background
    tor -f "$TOR_CONFIG" > "$LOG_FILE" 2>&1 &
    local tor_pid=$!
    echo $tor_pid > "$PID_DIR/tor.pid"

    # Wait for Tor to bootstrap with progress bar
    print_info "Waiting for Tor to bootstrap..."
    local count=0
    local max_wait=60
    local last_progress=0

    while [ $count -lt $max_wait ]; do
        if grep -q "Bootstrapped 100%" "$LOG_FILE" 2>/dev/null; then
            echo -ne "\r${GREEN}[████████████████████████████████████████] 100%${NC} - Complete!      \n"
            print_success "Tor started successfully!"
            log_message "Tor started (PID: $tor_pid)"
            return 0
        fi

        # Show progress with bar
        if grep -q "Bootstrapped" "$LOG_FILE" 2>/dev/null; then
            local progress=$(grep "Bootstrapped" "$LOG_FILE" | tail -1 | grep -oP '\d+(?=%)' | tail -1)

            if [ -n "$progress" ] && [ "$progress" != "$last_progress" ]; then
                last_progress=$progress

                # Create progress bar (40 chars)
                local filled=$((progress * 40 / 100))
                local empty=$((40 - filled))
                local bar=$(printf '█%.0s' $(seq 1 $filled))$(printf '░%.0s' $(seq 1 $empty))

                # Color based on progress
                local color=$YELLOW
                if [ $progress -ge 70 ]; then
                    color=$GREEN
                elif [ $progress -ge 30 ]; then
                    color=$CYAN
                fi

                # Get status message
                local status=$(grep "Bootstrapped $progress%" "$LOG_FILE" | tail -1 | sed 's/.*Bootstrapped [0-9]*%[^:]*: //' | cut -c1-40)

                echo -ne "\r${color}[${bar}] ${progress}%${NC} - ${status}   "
            fi
        fi

        sleep 1
        ((count++))
    done

    echo ""
    print_error "Tor bootstrap timed out"
    log_message "Tor bootstrap timeout"
    return 1
}

# Stop Tor
stop_tor() {
    print_info "Stopping Tor..."

    if [ -f "$PID_DIR/tor.pid" ]; then
        local tor_pid=$(cat "$PID_DIR/tor.pid")
        if kill -0 $tor_pid 2>/dev/null; then
            kill $tor_pid
            rm "$PID_DIR/tor.pid"
            print_success "Tor stopped"
            log_message "Tor stopped"
            return 0
        fi
    fi

    # Fallback: kill all tor processes
    if pkill -f "tor"; then
        print_success "Tor stopped"
        log_message "Tor stopped (fallback)"
        return 0
    else
        print_warning "Tor was not running"
        return 1
    fi
}

# Start Nginx
start_nginx() {
    print_info "Starting Nginx..."

    # Check if Nginx is already running
    if pgrep -f "nginx" > /dev/null; then
        print_warning "Nginx is already running"
        return 0
    fi

    # Test Nginx configuration
    if ! nginx -t > /dev/null 2>&1; then
        print_error "Nginx configuration test failed"
        nginx -t
        return 1
    fi

    # Start Nginx
    if nginx; then
        print_success "Nginx started successfully!"
        log_message "Nginx started"
        return 0
    else
        print_error "Failed to start Nginx"
        log_message "Nginx start failed"
        return 1
    fi
}

# Stop Nginx
stop_nginx() {
    print_info "Stopping Nginx..."

    if pkill -f "nginx"; then
        print_success "Nginx stopped"
        log_message "Nginx stopped"
        return 0
    else
        print_warning "Nginx was not running"
        return 1
    fi
}

# Get service status
get_service_status() {
    print_header "=== Service Status ==="
    echo ""

    if pgrep -f "tor" > /dev/null; then
        print_success "Tor: Running"
        local tor_status=true
    else
        print_error "Tor: Stopped"
        local tor_status=false
    fi

    if pgrep -f "nginx" > /dev/null; then
        print_success "Nginx: Running"
        local nginx_status=true
    else
        print_error "Nginx: Stopped"
        local nginx_status=false
    fi

    echo ""
    echo -e "${BOLD}Configuration:${NC}"
    echo "  Hosting Method: $HOSTING_METHOD"
    echo "  Nginx Port: $NGINX_PORT"
    if [ -n "$CUSTOM_PORT" ]; then
        echo "  Custom Port: $CUSTOM_PORT"
    fi

    if [ -n "$ONION_ADDRESS" ]; then
        echo ""
        echo -e "${BOLD}Onion Address:${NC}"
        echo -e "${GREEN}$ONION_ADDRESS${NC}"
    fi

    echo ""
}

################################################################################
# Main Service Operations
################################################################################

# Start the complete service
start_service() {
    print_header "=== Starting Onion Service ==="
    echo ""

    # Check dependencies
    if ! check_package tor; then
        print_error "Tor is not installed. Install it with: install tor"
        return 1
    fi

    # Determine target port based on hosting method
    if [ "$HOSTING_METHOD" = "nginx" ]; then
        if ! check_package nginx; then
            print_error "Nginx is not installed. Install it with: install nginx"
            return 1
        fi

        # Validate site directory
        if [ -z "$SITE_DIRECTORY" ]; then
            print_error "Site directory not set. Use: config set site_directory <path>"
            return 1
        fi

        if ! validate_directory "$SITE_DIRECTORY"; then
            return 1
        fi

        local target_port=$NGINX_PORT

        # Create Nginx configuration
        if ! create_nginx_config "$SITE_DIRECTORY" "$target_port"; then
            return 1
        fi

        # Start Nginx
        if ! start_nginx; then
            return 1
        fi

    elif [ "$HOSTING_METHOD" = "custom_port" ]; then
        if [ -z "$CUSTOM_PORT" ]; then
            print_error "Custom port not set. Use: method custom_port <port>"
            return 1
        fi

        if ! validate_port "$CUSTOM_PORT"; then
            return 1
        fi

        local target_port=$CUSTOM_PORT
        print_info "Using custom port method with port: $target_port"
        print_warning "Make sure your local web server is running on port $target_port"
    else
        print_error "Invalid hosting method: $HOSTING_METHOD"
        return 1
    fi

    # Configure Tor
    if ! configure_tor "$target_port"; then
        return 1
    fi

    # Start Tor with progress
    echo ""
    if ! start_tor; then
        return 1
    fi

    # Wait for onion address
    echo ""
    print_info "Waiting for onion address..."
    sleep 2

    if get_onion_address > /dev/null; then
        ONION_ADDRESS=$(get_onion_address)
        SERVICE_RUNNING=true
        save_config

        echo ""
        print_success "Onion service started successfully!"
        echo ""
        print_header "Your Onion Address:"
        echo -e "${GREEN}${BOLD}$ONION_ADDRESS${NC}"
        echo ""

        # Copy to clipboard if termux-api is available
        if check_package termux-clipboard-set; then
            echo "$ONION_ADDRESS" | termux-clipboard-set
            print_success "Onion address copied to clipboard!"
        fi

        log_message "Service started: $ONION_ADDRESS"
        return 0
    else
        print_warning "Service started but onion address not available yet"
        print_info "Check back in a moment with: status"
        SERVICE_RUNNING=true
        save_config
        log_message "Service started (address pending)"
        return 0
    fi
}

# Stop the complete service
stop_service() {
    print_header "=== Stopping Onion Service ==="
    echo ""

    local errors=0

    # Stop Nginx if using nginx method
    if [ "$HOSTING_METHOD" = "nginx" ]; then
        if ! stop_nginx; then
            ((errors++))
        fi
    fi

    # Stop Tor
    if ! stop_tor; then
        ((errors++))
    fi

    SERVICE_RUNNING=false
    save_config

    echo ""
    if [ $errors -eq 0 ]; then
        print_success "Onion service stopped successfully!"
        log_message "Service stopped"
        return 0
    else
        print_warning "Service stopped with some errors"
        log_message "Service stopped with errors"
        return 1
    fi
}

# Restart the service
restart_service() {
    print_header "=== Restarting Onion Service ==="
    echo ""

    stop_service
    sleep 2
    start_service
}

################################################################################
# Configuration Management
################################################################################

# Show configuration
show_config() {
    print_header "=== Configuration ==="
    echo ""

    echo -e "${BOLD}General:${NC}"
    echo "  Version: $VERSION"
    echo "  Config Directory: $CONFIG_DIR"
    echo ""

    echo -e "${BOLD}Service:${NC}"
    echo "  Site Directory: ${SITE_DIRECTORY:-Not set}"
    echo "  Hosting Method: $HOSTING_METHOD"
    echo "  Nginx Port: $NGINX_PORT"
    echo "  Custom Port: ${CUSTOM_PORT:-Not set}"
    echo "  Onion Address: ${ONION_ADDRESS:-Not available}"
    echo "  Service Running: $SERVICE_RUNNING"
    echo ""

    echo -e "${BOLD}Paths:${NC}"
    echo "  Tor Config: $TOR_CONFIG"
    echo "  Nginx Config: $NGINX_CONFIG"
    echo "  Hidden Service Dir: $HIDDEN_SERVICE_DIR"
    echo "  Log File: $LOG_FILE"
    echo ""
}

# Set configuration value
set_config_value() {
    local key=$1
    local value=$2

    case "$key" in
        site_directory)
            if [ -d "$value" ]; then
                SITE_DIRECTORY="$value"
                save_config
                print_success "Site directory set to: $value"
            else
                print_error "Directory does not exist: $value"
                return 1
            fi
            ;;
        nginx_port)
            if validate_port "$value"; then
                NGINX_PORT=$value
                save_config
                print_success "Nginx port set to: $value"
            else
                return 1
            fi
            ;;
        custom_port)
            if validate_port "$value"; then
                CUSTOM_PORT=$value
                save_config
                print_success "Custom port set to: $value"
                print_info "Remember to set hosting method to 'custom_port'"
            else
                return 1
            fi
            ;;
        hosting_method)
            if [ "$value" = "nginx" ] || [ "$value" = "custom_port" ]; then
                HOSTING_METHOD=$value
                save_config
                print_success "Hosting method set to: $value"

                if [ "$value" = "nginx" ]; then
                    print_warning "Nginx method: Only static websites will work (no PHP, no server-side processing)"
                else
                    print_success "Custom Port method: Full support for PHP, databases, and dynamic content"
                fi
            else
                print_error "Invalid hosting method. Use 'nginx' or 'custom_port'"
                return 1
            fi
            ;;
        *)
            print_error "Unknown configuration key: $key"
            print_info "Available keys: site_directory, nginx_port, custom_port, hosting_method"
            return 1
            ;;
    esac

    return 0
}

# Get configuration value
get_config_value() {
    local key=$1

    case "$key" in
        site_directory)
            echo "${SITE_DIRECTORY:-Not set}"
            ;;
        nginx_port)
            echo "$NGINX_PORT"
            ;;
        custom_port)
            echo "${CUSTOM_PORT:-Not set}"
            ;;
        hosting_method)
            echo "$HOSTING_METHOD"
            ;;
        onion_address)
            echo "${ONION_ADDRESS:-Not available}"
            ;;
        *)
            print_error "Unknown configuration key: $key"
            return 1
            ;;
    esac
}

################################################################################
# Hosting Method Management
################################################################################

# Set hosting method (shortcut command)
set_hosting_method() {
    local method=$1
    local port=$2

    if [ "$method" = "nginx" ]; then
        HOSTING_METHOD="nginx"
        save_config
        print_success "Hosting method set to: Nginx"
        echo ""
        print_warning "Nginx Method:"
        echo "  ⚠  Only static websites will work"
        echo "  •  HTML, CSS, JavaScript, images"
        echo "  •  No PHP, no server-side processing, no databases"
        echo ""
        echo "Nginx Port: $NGINX_PORT"

    elif [ "$method" = "custom_port" ] || [ "$method" = "custom" ]; then
        if [ -z "$port" ]; then
            print_error "Please specify the port number"
            echo "Usage: method custom_port <port>"
            return 1
        fi

        if ! validate_port "$port"; then
            return 1
        fi

        CUSTOM_PORT=$port
        HOSTING_METHOD="custom_port"
        save_config

        print_success "Hosting method set to: Custom Port ($port)"
        echo ""
        print_success "Custom Port Method:"
        echo "  ✓  Full support for dynamic content"
        echo "  •  PHP, Python, Node.js, etc."
        echo "  •  Databases and server-side processing"
        echo ""
        print_warning "Make sure your local web server is running on port $port"

    else
        print_error "Invalid method. Use 'nginx' or 'custom_port'"
        echo ""
        echo "Examples:"
        echo "  method nginx              - Use Nginx for static sites"
        echo "  method custom_port 3000   - Use custom port 3000"
        return 1
    fi

    return 0
}

# Show current hosting method
show_hosting_method() {
    print_header "=== Hosting Method ==="
    echo ""

    echo -e "${BOLD}Current Method:${NC} $HOSTING_METHOD"
    echo ""

    if [ "$HOSTING_METHOD" = "nginx" ]; then
        echo -e "${YELLOW}Nginx Method:${NC}"
        echo "  ⚠  Only static websites will work"
        echo "  •  HTML, CSS, JavaScript, images"
        echo "  •  No PHP, no server-side processing, no databases"
        echo ""
        echo -e "${BOLD}Nginx Port:${NC} $NGINX_PORT"
    else
        echo -e "${GREEN}Custom Port Method:${NC}"
        echo "  ✓  Full support for dynamic content"
        echo "  •  PHP, Python, Node.js, etc."
        echo "  •  Databases and server-side processing"
        echo ""
        if [ -n "$CUSTOM_PORT" ]; then
            echo -e "${BOLD}Custom Port:${NC} $CUSTOM_PORT"
        else
            print_warning "Custom port not set! Use: method custom_port <port>"
        fi
    fi
    echo ""
}

################################################################################
# Interactive Menu
################################################################################

# Main menu
show_menu() {
    echo ""
    print_header "=== Main Menu ==="
    echo ""
    echo "  1. Start Service"
    echo "  2. Stop Service"
    echo "  3. Restart Service"
    echo "  4. Service Status"
    echo "  5. Show Onion Address"
    echo ""
    echo "  6. Set Hosting Method"
    echo "  7. Configure Settings"
    echo "  8. Validate Directory"
    echo ""
    echo "  9. Install Dependencies"
    echo " 10. Check Dependencies"
    echo ""
    echo " 11. View Logs"
    echo " 12. Help"
    echo "  0. Exit"
    echo ""
    echo -n "Select option: "
}

# Interactive mode
interactive_mode() {
    while true; do
        show_menu
        read -r choice
        echo ""

        case $choice in
            1)
                start_service
                read -p "Press Enter to continue..."
                ;;
            2)
                stop_service
                read -p "Press Enter to continue..."
                ;;
            3)
                restart_service
                read -p "Press Enter to continue..."
                ;;
            4)
                get_service_status
                read -p "Press Enter to continue..."
                ;;
            5)
                if [ -n "$ONION_ADDRESS" ]; then
                    print_header "Your Onion Address:"
                    echo -e "${GREEN}${BOLD}$ONION_ADDRESS${NC}"
                    if check_package termux-clipboard-set; then
                        echo "$ONION_ADDRESS" | termux-clipboard-set
                        print_success "Copied to clipboard!"
                    fi
                else
                    print_warning "No onion address available yet"
                    print_info "Start the service first"
                fi
                read -p "Press Enter to continue..."
                ;;
            6)
                method_menu
                ;;
            7)
                config_menu
                ;;
            8)
                echo -n "Enter directory path: "
                read -r dir_path
                if validate_directory "$dir_path"; then
                    print_success "Directory is valid!"
                fi
                read -p "Press Enter to continue..."
                ;;
            9)
                install_all_dependencies
                read -p "Press Enter to continue..."
                ;;
            10)
                check_dependencies
                read -p "Press Enter to continue..."
                ;;
            11)
                if [ -f "$LOG_FILE" ]; then
                    tail -50 "$LOG_FILE"
                else
                    print_warning "No logs available"
                fi
                read -p "Press Enter to continue..."
                ;;
            12)
                show_help
                read -p "Press Enter to continue..."
                ;;
            0)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option"
                read -p "Press Enter to continue..."
                ;;
        esac

        print_banner
    done
}

# Method configuration menu
method_menu() {
    while true; do
        echo ""
        print_header "=== Hosting Method ==="
        echo ""
        echo "Current: $HOSTING_METHOD"
        echo ""
        echo "  1. Use Nginx (static sites only)"
        echo "  2. Use Custom Port (full support)"
        echo "  3. View Current Method"
        echo "  0. Back to Main Menu"
        echo ""
        echo -n "Select option: "
        read -r choice
        echo ""

        case $choice in
            1)
                set_hosting_method "nginx"
                read -p "Press Enter to continue..."
                ;;
            2)
                echo -n "Enter your local website port: "
                read -r port
                set_hosting_method "custom_port" "$port"
                read -p "Press Enter to continue..."
                ;;
            3)
                show_hosting_method
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                print_error "Invalid option"
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Configuration menu
config_menu() {
    while true; do
        echo ""
        print_header "=== Configuration ==="
        echo ""
        echo "  1. Set Site Directory"
        echo "  2. Set Nginx Port"
        echo "  3. Set Custom Port"
        echo "  4. View Configuration"
        echo "  0. Back to Main Menu"
        echo ""
        echo -n "Select option: "
        read -r choice
        echo ""

        case $choice in
            1)
                echo -n "Enter site directory path: "
                read -r dir_path
                set_config_value "site_directory" "$dir_path"
                read -p "Press Enter to continue..."
                ;;
            2)
                echo -n "Enter Nginx port (default 8080): "
                read -r port
                set_config_value "nginx_port" "$port"
                read -p "Press Enter to continue..."
                ;;
            3)
                echo -n "Enter custom port: "
                read -r port
                set_config_value "custom_port" "$port"
                read -p "Press Enter to continue..."
                ;;
            4)
                show_config
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                print_error "Invalid option"
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

################################################################################
# Help and Documentation
################################################################################

# Show help
show_help() {
    print_header "=== Onion Hoster Help ==="
    echo ""

    echo -e "${BOLD}COMMANDS:${NC}"
    echo ""

    echo -e "${CYAN}Service Management:${NC}"
    echo "  start             - Start the onion service"
    echo "  stop              - Stop the onion service"
    echo "  restart           - Restart the onion service"
    echo "  status            - Show service status"
    echo "  address           - Display onion address"
    echo ""

    echo -e "${CYAN}Configuration:${NC}"
    echo "  config show                           - Show all configuration"
    echo "  config get <key>                      - Get configuration value"
    echo "  config set <key> <value>              - Set configuration value"
    echo "  method [nginx|custom_port] [port]     - Set hosting method"
    echo ""

    echo -e "${CYAN}Dependencies:${NC}"
    echo "  install all       - Install all dependencies"
    echo "  install tor       - Install Tor"
    echo "  install nginx     - Install Nginx"
    echo "  install api       - Install Termux-API"
    echo "  check             - Check dependency status"
    echo ""

    echo -e "${CYAN}Utilities:${NC}"
    echo "  validate <dir>    - Validate site directory"
    echo "  logs              - View log file"
    echo "  help              - Show this help message"
    echo "  menu              - Show interactive menu"
    echo "  version           - Show version information"
    echo ""

    echo -e "${BOLD}EXAMPLES:${NC}"
    echo ""
    echo "  # Install dependencies"
    echo "  ./termux.sh install all"
    echo ""
    echo "  # Set up for static website (Nginx method)"
    echo "  ./termux.sh method nginx"
    echo "  ./termux.sh config set site_directory /path/to/website"
    echo "  ./termux.sh start"
    echo ""
    echo "  # Set up for dynamic website (Custom Port method)"
    echo "  ./termux.sh method custom_port 3000"
    echo "  ./termux.sh start"
    echo ""
    echo "  # Check status and get address"
    echo "  ./termux.sh status"
    echo "  ./termux.sh address"
    echo ""

    echo -e "${BOLD}HOSTING METHODS:${NC}"
    echo ""
    echo -e "${YELLOW}Nginx Method:${NC}"
    echo "  • Only static websites (HTML, CSS, JS, images)"
    echo "  • No PHP, no server-side processing"
    echo "  • Files are served from specified directory"
    echo ""
    echo -e "${GREEN}Custom Port Method:${NC}"
    echo "  • Full support for dynamic content"
    echo "  • PHP, Python, Node.js, databases, etc."
    echo "  • Your web server must be running on the specified port"
    echo ""

    echo -e "${BOLD}PORT RESTRICTIONS:${NC}"
    echo "  • Port 9050-9151: Reserved for Tor (forbidden)"
    echo "  • Port 1-1023: System reserved (not recommended)"
    echo "  • Port 1024-65535: Available for use"
    echo ""
}

# Show version
show_version() {
    print_banner
    echo "Platform: Termux (Android)"
    echo "Author: Uzair Developer"
    echo "GitHub: https://github.com/uzairdeveloper223/Onion-Hoster"
    echo ""
}

################################################################################
# Command Line Interface
################################################################################

# Process command line arguments
process_command() {
    local cmd=$1
    shift

    case "$cmd" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            get_service_status
            ;;
        address)
            if [ -n "$ONION_ADDRESS" ]; then
                echo "$ONION_ADDRESS"
                if check_package termux-clipboard-set; then
                    echo "$ONION_ADDRESS" | termux-clipboard-set
                    print_success "Copied to clipboard!"
                fi
            else
                print_warning "No onion address available"
                print_info "Start the service first with: $0 start"
            fi
            ;;
        config)
            local subcmd=$1
            shift
            case "$subcmd" in
                show)
                    show_config
                    ;;
                get)
                    if [ -z "$1" ]; then
                        print_error "Usage: config get <key>"
                        exit 1
                    fi
                    get_config_value "$1"
                    ;;
                set)
                    if [ -z "$1" ] || [ -z "$2" ]; then
                        print_error "Usage: config set <key> <value>"
                        exit 1
                    fi
                    set_config_value "$1" "$2"
                    ;;
                *)
                    print_error "Unknown config command: $subcmd"
                    echo "Usage: config [show|get|set]"
                    exit 1
                    ;;
            esac
            ;;
        method)
            if [ -z "$1" ]; then
                show_hosting_method
            else
                set_hosting_method "$1" "$2"
            fi
            ;;
        validate)
            if [ -z "$1" ]; then
                print_error "Usage: validate <directory>"
                exit 1
            fi
            if validate_directory "$1"; then
                print_success "Directory is valid: $1"
            fi
            ;;
        install)
            local package=$1
            case "$package" in
                all)
                    install_all_dependencies
                    ;;
                tor)
                    install_tor
                    ;;
                nginx)
                    install_nginx
                    ;;
                api)
                    install_termux_api
                    ;;
                *)
                    print_error "Unknown package: $package"
                    echo "Usage: install [all|tor|nginx|api]"
                    exit 1
                    ;;
            esac
            ;;
        check)
            check_dependencies
            ;;
        logs)
            if [ -f "$LOG_FILE" ]; then
                tail -f "$LOG_FILE"
            else
                print_warning "No logs available"
            fi
            ;;
        menu)
            interactive_mode
            ;;
        help|--help|-h)
            show_help
            ;;
        version|--version|-v)
            show_version
            ;;
        *)
            print_error "Unknown command: $cmd"
            echo ""
            echo "Usage: $0 [command] [options]"
            echo "Try '$0 help' for more information."
            exit 1
            ;;
    esac
}

################################################################################
# Main Entry Point
################################################################################

# Initialize
init_config
load_config

# If no arguments, show interactive menu
if [ $# -eq 0 ]; then
    print_banner

    # First run setup
    if [ "$FIRST_RUN" = "true" ]; then
        echo -e "${YELLOW}${BOLD}Welcome to Onion Hoster!${NC}"
        echo ""
        print_info "This is your first time running Onion Hoster."
        echo ""
        echo "Would you like to install dependencies now? (y/n)"
        read -r response

        if [[ "$response" =~ ^[Yy]$ ]]; then
            install_all_dependencies
            echo ""
            read -p "Press Enter to continue..."
        fi

        FIRST_RUN=false
        save_config
        print_banner
    fi

    interactive_mode
else
    # Process command line arguments
    process_command "$@"
fi

exit 0
