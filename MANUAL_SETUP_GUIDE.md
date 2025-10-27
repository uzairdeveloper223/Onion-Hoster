# 🧅 Onion Hoster - Manual Setup Guide

## Overview

This guide explains how Onion Hoster now works based on your manual Debian setup, and how it's been adapted to work universally across all platforms (CLI, GUI, Termux, Windows, etc.).

## 🎯 What Changed?

### Before (Systemctl Method)
- Used `systemctl start tor` to start Tor as a background service
- No visibility into bootstrap progress
- No guarantee when .onion address would be available
- Relied on systemd (not available everywhere)

### After (Manual Method)
- Starts Tor directly: `sudo -u debian-tor tor -f /etc/tor/torrc`
- Shows real-time bootstrap progress (0% → 100%)
- Waits for .onion address generation
- Works on all platforms (even without systemd)

---

## 🛠️ How It Works Now

### Step-by-Step Process

1. **Directory Validation**
   - Checks for `index.html` in your website directory
   - Validates all required files exist

2. **Nginx Configuration**
   - Creates nginx config at `/etc/nginx/sites-available/onion-site`
   - Points to your website directory
   - Listens on `127.0.0.1:8080`
   - Symlinks to `sites-enabled`

3. **Tor Hidden Service Setup**
   - Creates `/var/lib/tor/hidden_service/` (or platform equivalent)
   - Sets correct permissions: `chmod 700`
   - Sets correct ownership: `chown debian-tor:debian-tor` (on Debian)
   - Appends to `/etc/tor/torrc`:
     ```
     HiddenServiceDir /var/lib/tor/hidden_service/
     HiddenServicePort 80 127.0.0.1:8080
     ```

4. **Start Nginx**
   - Starts nginx: `sudo systemctl start nginx`
   - Serves your website locally on port 8080

5. **Start Tor Manually** ⭐ NEW!
   - Runs: `sudo -u debian-tor tor -f /etc/tor/torrc`
   - Monitors output in real-time
   - Extracts bootstrap progress: "Bootstrapped 25%", "Bootstrapped 50%", etc.
   - Shows progress bar in CLI/GUI
   - Waits for "Bootstrapped 100%"
   - Reads `.onion` address from `/var/lib/tor/hidden_service/hostname`
   - Returns your `.onion` address

6. **Service Live!**
   - Your website is now accessible via the `.onion` address
   - Tor circuit is established
   - Anyone with Tor Browser can access it

---

## 📦 Platform-Specific Details

### Debian/Ubuntu
```bash
# Tor user
debian-tor:debian-tor

# Tor command
sudo -u debian-tor tor -f /etc/tor/torrc

# Service name
tor@default

# Paths
/etc/tor/torrc
/var/lib/tor/hidden_service/
/etc/nginx/sites-available/
```

### Arch Linux
```bash
# Tor user
tor:tor

# Tor command
sudo -u tor tor -f /etc/tor/torrc

# Service name
tor

# Paths
/etc/tor/torrc
/var/lib/tor/hidden_service/
/etc/nginx/sites-available/
```

### Fedora/RHEL/CentOS
```bash
# Tor user
tor:tor

# Tor command
sudo -u tor tor -f /etc/tor/torrc

# Service name
tor

# Paths
/etc/tor/torrc
/var/lib/tor/hidden_service/
/etc/nginx/conf.d/
```

### macOS
```bash
# Tor user
<current_user> (no sudo -u needed)

# Tor command
tor -f /usr/local/etc/tor/torrc

# Service name (via Homebrew)
brew services start tor

# Paths
/usr/local/etc/tor/torrc
/usr/local/var/lib/tor/hidden_service/
/usr/local/etc/nginx/nginx.conf
```

### Termux (Android)
```bash
# No sudo needed
tor -f $PREFIX/etc/tor/torrc

# Paths
$PREFIX/etc/tor/torrc
$HOME/.tor/hidden_service/
$PREFIX/etc/nginx/nginx.conf
```

### Windows
```powershell
# Using Tor Expert Bundle
C:\Users\<user>\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe -f torrc

# Paths
C:\Users\<user>\Desktop\Tor Browser\Browser\TorBrowser\Data\Tor\torrc
C:\Users\<user>\AppData\Roaming\tor\hidden_service\
C:\nginx\conf\nginx.conf
```

---

## 🔧 Key Problems We Solved

### Problem 1: Nginx 404 Error
**Issue:** HTML file path didn't match nginx config

**Solution:**
- App now dynamically creates nginx config with correct paths
- Uses absolute path to your website directory
- Validates directory before configuration

### Problem 2: Tor Hidden Service Directory Not Created
**Issue:** `/var/lib/tor/hidden_service/` was empty, no .onion address generated

**Root Cause:** Wrong permissions (755 instead of 700)

**Solution:**
```python
# Create directory
os.makedirs(hidden_service_dir, mode=0o700, exist_ok=True)

# Set ownership
chown -R debian-tor:debian-tor /var/lib/tor/hidden_service

# Set permissions
chmod 700 /var/lib/tor/hidden_service
```

### Problem 3: Tor Service Not Actually Running
**Issue:** Starting `tor.service` (master service) which does nothing

**Root Cause:** Ubuntu uses multi-instance Tor (`tor@default`)

**Solution:**
- App now detects distro and uses correct service name
- Debian: `tor@default`
- Arch/Fedora: `tor`
- **NEW:** Manual startup bypasses systemctl entirely!

### Problem 4: "Permissions Too Permissive" Warnings
**Issue:** Tor refuses to load if directory isn't exactly `drwx------` (700)

**Solution:**
- Automatically sets 700 permissions
- Verifies ownership is correct for tor user
- Handles platform differences

---

## 📊 Bootstrap Progress Monitoring

### What You See

#### CLI Mode
```
Starting Tor with bootstrap monitoring...

[████████████████████░░░░░░░░░░░░░░░░░░░░] 50% - Loading relay descriptors
[████████████████████████████████████████] 100% - Done

✓ Tor service started successfully! Your .onion address: abc123xyz456.onion
```

#### GUI Mode
- Progress bar with percentage
- Real-time status messages
- "Connecting...", "Loading descriptors...", "Done"
- .onion address displayed when ready

### Bootstrap Stages
- **0-10%**: Starting Tor
- **10-25%**: Connecting to directory servers
- **25-50%**: Requesting relay information
- **50-75%**: Loading relay descriptors
- **75-90%**: Requesting network status
- **90-100%**: Establishing circuits
- **100%**: Done! Your .onion is live

---

## 🚀 Usage Examples

### Quick Start (CLI)

```bash
# Install dependencies
sudo apt install tor nginx  # Debian/Ubuntu
# or
sudo pacman -S tor nginx    # Arch
# or
pkg install tor nginx       # Termux

# Clone and setup
git clone https://github.com/uzairdeveloper223/Onion-Hoster.git
cd Onion-Hoster
pip install -r requirements.txt

# Run test script
python test_manual_tor.py /path/to/your/website
```

### Example Output
```
======================================================================
  ONION HOSTER v1.0.0 - Manual Tor Startup Test
======================================================================

✓ Website directory: /home/uzair/Tools/Onion-Hoster/example-site
✓ Index file found: /home/uzair/Tools/Onion-Hoster/example-site/index.html

Initializing system...
✓ Operating System: linux
✓ Distribution: debian
✓ Desktop Environment: GNOME
✓ Termux: False

Checking dependencies...
  Tor installed: ✓
  Nginx installed: ✓

Validating website directory...
✓ Directory is valid

Configuring Nginx...
✓ Nginx configuration created successfully!

Configuring Tor hidden service...
✓ Tor hidden service configured successfully!

Starting Nginx...
✓ Nginx started successfully!

Starting Tor with bootstrap monitoring...
This will show real-time progress as Tor connects to the network.

[████████████████████████████████████████] 100% - Done

✓ Tor service started successfully! Your .onion address: abc123xyz456.onion

======================================================================
  🎉 SUCCESS! Your website is now live on the Tor network!
======================================================================

  Your .onion address: abc123xyz456.onion

  Access your site at: http://abc123xyz456.onion

  You can open this address in Tor Browser.
======================================================================

Service is running. Press Ctrl+C to stop...
```

### Using Main CLI Interface

```bash
# Start CLI
./onion-host --cli

# In the CLI
onion-hoster> install all
onion-hoster> start /path/to/your/website
# Watch bootstrap progress...
# Get your .onion address

onion-hoster> status
onion-hoster> address
onion-hoster> open
onion-hoster> stop
```

### Using GUI

```bash
./onion-host --gui
```

1. Select your website directory
2. Click "Start Service"
3. Watch bootstrap progress bar
4. Copy your .onion address
5. Click "Open in Tor Browser"

---

## 🔍 Troubleshooting

### Issue: "Permission denied"
**Solution:**
```bash
# Make sure you run with sudo or provide password
./onion-host --cli

# Or set password in code
service.set_sudo_password("your_password")
```

### Issue: "Tor bootstrap stuck at X%"
**Possible Causes:**
- No internet connection
- Firewall blocking Tor
- ISP blocking Tor

**Solution:**
```bash
# Check if Tor can connect
tor --verify-config

# Check firewall
sudo ufw status

# Try with bridges (add to torrc)
UseBridges 1
Bridge obfs4 ...
```

### Issue: "Hidden service directory permissions too permissive"
**Solution:**
```bash
# Fix manually
sudo chmod 700 /var/lib/tor/hidden_service
sudo chown -R debian-tor:debian-tor /var/lib/tor/hidden_service

# App should do this automatically, but if not:
# Report as bug!
```

### Issue: ".onion address not generated"
**Solution:**
```bash
# Wait for bootstrap 100%
# Check if hostname file exists
sudo cat /var/lib/tor/hidden_service/hostname

# If empty, restart tor
sudo systemctl restart tor@default
# or
service.stop_tor()
service.start_tor_manual()
```

### Issue: "Nginx 404 error"
**Solution:**
```bash
# Check nginx config
sudo nginx -t

# Check your website directory
ls -la /path/to/your/website
# Must have index.html

# Check nginx is serving on 8080
curl http://127.0.0.1:8080
```

---

## 📁 Important File Locations

### Your Website Files
```
/home/uzair/Tools/Onion-Hoster/example-site/
├── index.html  (required)
├── style.css
├── script.js
└── ...
```

### Tor Configuration
```
/etc/tor/torrc
# Contains:
HiddenServiceDir /var/lib/tor/hidden_service/
HiddenServicePort 80 127.0.0.1:8080
```

### Hidden Service Files
```
/var/lib/tor/hidden_service/
├── hostname                    (your .onion address)
├── hs_ed25519_public_key      (public key)
└── hs_ed25519_secret_key      (KEEP SECRET!)
```

### Nginx Configuration
```
/etc/nginx/sites-available/onion-site
/etc/nginx/sites-enabled/onion-site -> ../sites-available/onion-site
```

### App Configuration
```
~/.config/.onion-hoster/config.json      (Linux)
%APPDATA%\.onion-hoster\config.json      (Windows)
~/.onion-hoster/config.json              (Termux)
```

---

## 🎨 Code Integration Example

### Custom Progress Callback

```python
from src.core.system_detector import get_system_detector
from src.core.config_manager import ConfigManager
from src.core.onion_service import OnionServiceManager

# Initialize
system = get_system_detector()
config = ConfigManager()
service = OnionServiceManager(config, system)

# Define custom progress callback
def my_progress_handler(progress: int, message: str):
    print(f"Bootstrap: {progress}% - {message}")
    # Update your GUI, send to websocket, etc.

# Set sudo password (if needed)
service.set_sudo_password("your_password")

# Start service with progress monitoring
success, msg, onion_address = service.start_service(
    site_directory="/path/to/website",
    progress_callback=my_progress_handler
)

if success:
    print(f"Success! Address: {onion_address}")
else:
    print(f"Failed: {msg}")
```

### Check Service Status

```python
status = service.get_service_status()
print(f"Service running: {status['service_running']}")
print(f"Tor running: {status['tor_running']}")
print(f"Bootstrap progress: {status['bootstrap_progress']}%")
print(f"Onion address: {status['onion_address']}")
```

---

## 🔐 Security Notes

1. **Keep your private key safe!**
   - Location: `/var/lib/tor/hidden_service/hs_ed25519_secret_key`
   - Don't share or commit to git
   - Backup securely

2. **Permissions matter**
   - Hidden service dir MUST be 700
   - Tor will refuse to run otherwise

3. **HTTPS not needed**
   - .onion sites are end-to-end encrypted by Tor
   - No need for SSL certificates

4. **No logs**
   - Nginx configured with `access_log off`
   - For privacy

---

## 🤝 Contributing

Found a bug? Have an improvement?

1. Fork the repo
2. Create a feature branch
3. Test on your platform
4. Submit a pull request

---

## 📚 Additional Resources

- [Tor Project Documentation](https://www.torproject.org/docs/)
- [Tor Hidden Services Guide](https://community.torproject.org/onion-services/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [GitHub Repository](https://github.com/uzairdeveloper223/Onion-Hoster)

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/uzairdeveloper223/Onion-Hoster/issues)
- **Discussions:** [GitHub Discussions](https://github.com/uzairdeveloper223/Onion-Hoster/discussions)

---

**Made with ❤️ and 🧅 by Uzair Developer**

*Host your content. Stay anonymous. Embrace freedom.*