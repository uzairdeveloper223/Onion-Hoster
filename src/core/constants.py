"""
Onion Hoster - Constants and Configuration
Author: Uzair Developer
GitHub: uzairdeveloper223
"""

import os
from pathlib import Path

# Version Information
VERSION = "1.0.0"
APP_NAME = "Onion Hoster"
AUTHOR = "Uzair Developer"
GITHUB_USERNAME = "uzairdeveloper223"
GITHUB_REPO = "Onion-Hoster"
GITHUB_URL = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"
UPDATE_CHECK_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/config/version.json"

# Application Paths
APP_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR_NAME = ".onion-hoster"

# Platform-specific config directories
if os.name == "nt":  # Windows
    CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / CONFIG_DIR_NAME
elif os.name == "posix":
    if "TERMUX_VERSION" in os.environ:  # Termux
        CONFIG_DIR = Path.home() / CONFIG_DIR_NAME
    else:  # Linux/Mac
        CONFIG_DIR = Path.home() / ".config" / CONFIG_DIR_NAME
else:
    CONFIG_DIR = Path.home() / CONFIG_DIR_NAME

# Configuration Files
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "onion-hoster.log"
UPDATE_STATUS_FILE = CONFIG_DIR / "update_status.json"

# Theme Colors (Material You - Tor Browser inspired)
THEME_COLORS = {
    "primary": "#7D4698",  # Purple (Tor purple)
    "primary_dark": "#5E2C7A",  # Darker purple
    "primary_light": "#9B6AB8",  # Lighter purple
    "secondary": "#9B6AB8",  # Light purple
    "accent": "#B794F4",  # Purple accent
    "background": "#1E1E1E",  # Dark background
    "surface": "#2D2D2D",  # Surface dark
    "surface_variant": "#3D3D3D",  # Surface variant
    "error": "#CF6679",  # Error red
    "success": "#81C784",  # Success green
    "warning": "#FFB74D",  # Warning orange
    "text_primary": "#FFFFFF",  # White text
    "text_secondary": "#B0B0B0",  # Gray text
    "text_disabled": "#666666",  # Disabled text
    "border": "#4D4D4D",  # Border color
    "hover": "#3D3D3D",  # Hover state
}

# Nginx Configuration
NGINX_DEFAULT_PORT = 8080
NGINX_CONFIG_TEMPLATE = """server {{
    listen 127.0.0.1:{port};
    server_name localhost;

    # Security headers - hide OS info
    server_tokens off;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer" always;

    root {root_dir};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}

    # Disable access logs for privacy
    access_log off;
    error_log {error_log};
}}
"""

# Tor Configuration
TOR_CONFIG_TEMPLATE = """# Onion Hoster Hidden Service Configuration
HiddenServiceDir {hidden_service_dir}
HiddenServicePort 80 127.0.0.1:{nginx_port}
"""

# Platform-specific paths
PLATFORM_PATHS = {
    "debian": {
        "tor_config": "/etc/tor/torrc",
        "tor_service_dir": "/var/lib/tor",
        "nginx_sites_available": "/etc/nginx/sites-available",
        "nginx_sites_enabled": "/etc/nginx/sites-enabled",
        "nginx_config": "/etc/nginx/nginx.conf",
        "tor_browser_command": "torbrowser-launcher",
    },
    "arch": {
        "tor_config": "/etc/tor/torrc",
        "tor_service_dir": "/var/lib/tor",
        "nginx_sites_available": "/etc/nginx/sites-available",
        "nginx_sites_enabled": "/etc/nginx/sites-enabled",
        "nginx_config": "/etc/nginx/nginx.conf",
        "tor_browser_command": "torbrowser-launcher",
    },
    "redhat": {
        "tor_config": "/etc/tor/torrc",
        "tor_service_dir": "/var/lib/tor",
        "nginx_sites_available": "/etc/nginx/conf.d",
        "nginx_sites_enabled": "/etc/nginx/conf.d",
        "nginx_config": "/etc/nginx/nginx.conf",
        "tor_browser_command": "torbrowser-launcher",
    },
    "windows": {
        "tor_config": "C:\\Users\\{user}\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc",
        "tor_exe": "C:\\Users\\{user}\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
        "tor_browser_exe": "C:\\Users\\{user}\\Desktop\\Tor Browser\\Start Tor Browser.exe",
        "nginx_config": "C:\\nginx\\conf\\nginx.conf",
        "tor_service_dir": "C:\\Users\\{user}\\AppData\\Roaming\\tor",
    },
    "darwin": {  # macOS
        "tor_config": "/usr/local/etc/tor/torrc",
        "tor_service_dir": "/usr/local/var/lib/tor",
        "nginx_config": "/usr/local/etc/nginx/nginx.conf",
        "tor_browser_command": "/Applications/Tor Browser.app/Contents/MacOS/firefox",
    },
    "termux": {
        "tor_config": f"{os.environ.get('PREFIX', '/data/data/com.termux/files/usr')}/etc/tor/torrc",
        "tor_service_dir": f"{os.environ.get('HOME', '/data/data/com.termux/files/home')}/.tor",
        "nginx_config": f"{os.environ.get('PREFIX', '/data/data/com.termux/files/usr')}/etc/nginx/nginx.conf",
    },
}

# System Commands
INSTALL_COMMANDS = {
    "debian": {
        "tor": "sudo -S sh -c 'apt update && apt install -y tor'",
        "nginx": "sudo -S sh -c 'apt update && apt install -y nginx'",
        "tor_browser": "sudo -S sh -c 'apt update && apt install -y torbrowser-launcher'",
        "xclip": "sudo -S sh -c 'apt update && apt install -y xclip'",
    },
    "arch": {
        "tor": "sudo -S pacman -Sy --noconfirm tor",
        "nginx": "sudo -S pacman -Sy --noconfirm nginx",
        "tor_browser": "yay -S --noconfirm tor-browser",
        "xclip": "sudo -S pacman -Sy --noconfirm xclip",
    },
    "redhat": {
        "tor": "sudo -S dnf install -y tor",
        "nginx": "sudo -S dnf install -y nginx",
        "tor_browser": "flatpak install -y flathub com.github.micahflee.torbrowser-launcher",
        "xclip": "sudo -S dnf install -y xclip",
    },
    "termux": {
        "tor": "pkg update && pkg install -y tor",
        "nginx": "pkg update && pkg install -y nginx",
        "xclip": "pkg update && pkg install -y xclip",
    },
    "darwin": {
        "tor": "brew install tor",
        "nginx": "brew install nginx",
        "tor_browser": "brew install --cask tor-browser",
    },
}

# Service Management Commands
SERVICE_COMMANDS = {
    "debian": {
        "tor_start": "sudo -S systemctl start tor@default",
        "tor_stop": "sudo -S systemctl stop tor@default",
        "tor_restart": "sudo -S systemctl restart tor@default",
        "tor_enable": "sudo -S systemctl enable tor@default",
        "tor_status": "sudo -S systemctl status tor@default",
        "nginx_start": "sudo -S systemctl start nginx",
        "nginx_stop": "sudo -S systemctl stop nginx",
        "nginx_restart": "sudo -S systemctl restart nginx",
        "nginx_enable": "sudo -S systemctl enable nginx",
        "nginx_status": "sudo -S systemctl status nginx",
        "nginx_test": "sudo -S nginx -t",
    },
    "arch": {
        "tor_start": "sudo -S systemctl start tor",
        "tor_stop": "sudo -S systemctl stop tor",
        "tor_restart": "sudo -S systemctl restart tor",
        "tor_enable": "sudo -S systemctl enable tor",
        "tor_status": "sudo -S systemctl status tor",
        "nginx_start": "sudo -S systemctl start nginx",
        "nginx_stop": "sudo -S systemctl stop nginx",
        "nginx_restart": "sudo -S systemctl restart nginx",
        "nginx_enable": "sudo -S systemctl enable nginx",
        "nginx_status": "sudo -S systemctl status nginx",
        "nginx_test": "sudo -S nginx -t",
    },
    "redhat": {
        "tor_start": "sudo -S systemctl start tor",
        "tor_stop": "sudo -S systemctl stop tor",
        "tor_restart": "sudo -S systemctl restart tor",
        "tor_enable": "sudo -S systemctl enable tor",
        "tor_status": "sudo -S systemctl status tor",
        "nginx_start": "sudo -S systemctl start nginx",
        "nginx_stop": "sudo -S systemctl stop nginx",
        "nginx_restart": "sudo -S systemctl restart nginx",
        "nginx_enable": "sudo -S systemctl enable nginx",
        "nginx_status": "sudo -S systemctl status nginx",
        "nginx_test": "sudo -S nginx -t",
    },
    "termux": {
        "tor_start": "tor &",
        "tor_stop": "killall tor",
        "tor_restart": "killall tor && tor &",
        "nginx_start": "nginx",
        "nginx_stop": "killall nginx",
        "nginx_restart": "killall nginx && nginx",
        "nginx_test": "nginx -t",
    },
    "darwin": {
        "tor_start": "brew services start tor",
        "tor_stop": "brew services stop tor",
        "tor_restart": "brew services restart tor",
        "tor_status": "brew services list | grep tor",
        "nginx_start": "brew services start nginx",
        "nginx_stop": "brew services stop nginx",
        "nginx_restart": "brew services restart nginx",
        "nginx_status": "brew services list | grep nginx",
        "nginx_test": "nginx -t",
    },
}

# Requirements for index file detection
VALID_INDEX_FILES = ["index.html", "index.htm", "index.php"]

# GUI Configuration
GUI_WINDOW_SIZE = "900x700"
GUI_MIN_WINDOW_SIZE = (800, 600)
GUI_FONT_FAMILY = (
    "Segoe UI"
    if os.name == "nt"
    else "Ubuntu"
    if os.name == "posix"
    else "San Francisco"
)
GUI_FONT_SIZES = {
    "title": 24,
    "heading": 18,
    "subheading": 14,
    "body": 12,
    "small": 10,
}

# CLI Configuration
CLI_PROMPT = "onion-hoster> "
CLI_BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║                       ONION HOSTER v{VERSION}                      ║
║        Host your static websites on the Tor Network         ║
║                                                              ║
║              Author: {AUTHOR}                    ║
║              GitHub: github.com/{GITHUB_USERNAME}            ║
╚══════════════════════════════════════════════════════════════╝
"""

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"

# Error Messages
ERROR_MESSAGES = {
    "no_desktop": "No desktop environment detected. GUI mode cannot run in CLI-only environment.",
    "no_index": "No index file (index.html, index.htm) found in the selected directory.",
    "tor_not_installed": "Tor is not installed on your system.",
    "nginx_not_installed": "Nginx is not installed on your system.",
    "permission_denied": "Permission denied. Try running with sudo/administrator privileges.",
    "invalid_directory": "Invalid directory selected. Please choose a valid directory.",
    "update_failed": "Failed to check for updates. Please check your internet connection.",
    "config_error": "Configuration error. Please check your settings.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "tor_installed": "Tor has been successfully installed!",
    "nginx_installed": "Nginx has been successfully installed!",
    "service_started": "Onion service has been started successfully!",
    "service_stopped": "Onion service has been stopped successfully!",
    "config_saved": "Configuration saved successfully!",
    "update_available": "A new update is available!",
    "up_to_date": "You are using the latest version!",
}

# Desktop Environment Detection
DESKTOP_ENVIRONMENTS = [
    "GNOME",
    "KDE",
    "XFCE",
    "LXDE",
    "MATE",
    "Cinnamon",
    "Unity",
    "Budgie",
    "Pantheon",
    "i3",
    "awesome",
    "dwm",
]
