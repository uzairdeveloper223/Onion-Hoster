# Changelog

All notable changes to Onion Hoster will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-11-1

### Added
- **Dual Hosting Methods**: Users can now choose between two hosting methods
  - **Nginx Method**: For static websites (HTML, CSS, JS, images) - existing behavior
  - **Custom Port Method**: For dynamic content (PHP, Node.js, Python, databases, etc.)
- **Port Validation System**: Automatic validation to prevent use of Tor-reserved ports
  - Port 9050 (Tor SOCKS) is now forbidden
  - Port 9051 (Tor control) is now forbidden
  - Port 9150 (Tor Browser SOCKS) is now forbidden
  - Port 9151 (Tor Browser control) is now forbidden
  - Ports 1-1023 are flagged as system reserved
- **Custom Port Configuration**: Users can specify their local web server port
  - Allows hosting of PHP, Python, Node.js, and other dynamic applications
  - Tor forwards traffic directly to user's specified port
- **Termux Edition**: Complete standalone bash implementation for Android/Termux users
  - Pure bash script requiring no Python dependencies
  - Full CLI interface with interactive menu
  - Supports both Nginx and Custom Port methods
  - Includes one-line installer script
  - Dedicated documentation (TERMUX_README.md)
- **Enhanced GUI Features**:
  - Radio buttons to select hosting method (Nginx vs Custom Port)
  - Custom port input field in Configuration tab
  - Warning messages about hosting method limitations
  - Start button now disables during service startup and re-enables on completion/failure
  - Real-time method validation and user feedback
- **Enhanced CLI Features**:
  - New `method` command for easy hosting method switching
  - Port configuration with automatic validation
  - Enhanced `config` command with hosting method support
  - Clear warnings about method consequences

### Changed
- **Tor Configuration**: Now updates torrc with user's desired port (nginx or custom)
- **Service Start Logic**: Modified to support both hosting methods
  - Nginx method: Validates directory and starts Nginx
  - Custom port method: Validates port and assumes user's server is running
- **GUI Configuration Tab**: Redesigned to include hosting method selection and custom port
- **CLI Commands**: Enhanced to support new hosting method configuration
- **Documentation**: Updated README.md with hosting method examples and port restrictions

### Fixed
- Port conflicts with Tor services
- Missing validation for custom ports
- Concurrent use of both hosting methods (now prevented)

### Security
- Added strict port validation to prevent Tor service conflicts
- Implemented port restriction system for security-critical ports
- Clear warnings about hosting method security implications

### Documentation
- Added TERMUX_README.md with complete Termux setup guide
- Added termux-install.sh quick installer for Android users
- Updated main README.md with Termux edition section
- Added hosting method comparison and examples
- Added port restriction documentation
- Added multiple language framework examples (PHP, Node.js, Python Flask, Django)
## [1.1.0] - 2025-09-XX - Manual Tor Startup Release

### 🎉 Major New Features

#### Manual Tor Startup with Bootstrap Monitoring
- **Real-time Progress Tracking**: Watch Tor bootstrap from 0% to 100%
- **Live Status Messages**: See exactly what Tor is doing at each stage
- **Cross-Platform Support**: Works on Linux, macOS, Windows, and Termux
- **Direct Tor Control**: Runs Tor directly instead of via systemctl
- **Immediate Address Generation**: Get your .onion address as soon as Tor reaches 100%

#### Bootstrap Progress Display
- CLI: Beautiful progress bar with percentage and status messages
- GUI: Real-time progress bar widget with live updates
- Status messages show connection stages:
  - "Connecting to directory servers"
  - "Loading relay descriptors"
  - "Requesting network status"
  - "Establishing circuits"
  - "Done!"

### ✨ Added

- `start_tor_manual()` method for direct Tor process control
- Bootstrap progress monitoring with regex parsing
- Progress callback system for GUI/CLI integration
- `test_manual_tor.py` - Standalone test script demonstrating new features
- `MANUAL_SETUP_GUIDE.md` - Comprehensive technical documentation
- Platform-specific Tor user detection (`_get_tor_user()`, `_get_tor_group()`)
- Automatic `.onion` address reading after bootstrap completion
- Threading for non-blocking bootstrap monitoring
- Enhanced error messages with bootstrap progress information

### 🔧 Changed

- `start_service()` now uses manual Tor startup instead of systemctl
- Modified to accept `progress_callback` parameter for real-time updates
- `stop_tor()` now handles both manual process and systemctl service
- `get_service_status()` includes `tor_running` and `bootstrap_progress` fields
- Improved permission handling for hidden service directories
- Better cross-platform path handling (Windows, Termux, macOS, Linux)

### 🐛 Fixed

- **Permission Issues**: Automatic `chmod 700` for hidden service directories
- **Ownership Problems**: Correct user/group assignment based on distribution
  - Debian/Ubuntu: `debian-tor:debian-tor`
  - Arch/Fedora: `tor:tor`
  - macOS: Current user
  - Termux: No ownership change needed
- **Service Detection**: Proper detection of Debian's `tor@default` vs regular `tor` service
- **Bootstrap Timeout**: Service now waits for actual 100% instead of guessing
- **Address Generation**: Guaranteed .onion address availability after bootstrap
- **Multi-Instance Tor**: Correctly handles Ubuntu's multi-instance Tor setup

### 📝 Improved

- More detailed logging throughout Tor startup process
- Better error messages with specific troubleshooting steps
- Enhanced status reporting with bootstrap information
- Clearer user feedback during service startup
- Platform-specific command generation

### 🛠️ Technical Details

#### Platform-Specific Tor Commands

**Debian/Ubuntu:**
```bash
sudo -u debian-tor tor -f /etc/tor/torrc
```

**Arch Linux:**
```bash
sudo -u tor tor -f /etc/tor/torrc
```

**macOS:**
```bash
tor -f /usr/local/etc/tor/torrc
```

**Termux:**
```bash
tor -f $PREFIX/etc/tor/torrc
```

**Windows:**
```powershell
tor.exe -f torrc
```

#### Bootstrap Stages Tracked
- 0-10%: Starting Tor
- 10-25%: Connecting to directory servers
- 25-50%: Requesting relay information
- 50-75%: Loading relay descriptors
- 75-90%: Requesting network status
- 90-100%: Establishing circuits
- 100%: Service live!

### 📚 Documentation

- Added comprehensive `MANUAL_SETUP_GUIDE.md`
- Updated README with new features and troubleshooting
- Added code examples for custom progress callbacks
- Documented platform-specific behavior
- Included troubleshooting section for common issues

### 🧪 Testing

- New test script: `test_manual_tor.py`
- Demonstrates real-time bootstrap monitoring
- Works on all supported platforms
- Includes detailed output and error handling

---

## [1.0.0] - 2025-10-24 - Initial Release

### Features

- Cross-platform support (Linux, macOS, Windows, Termux)
- Dual interface (GUI and CLI)
- Automatic dependency detection and installation
- Nginx configuration generation
- Tor hidden service setup
- One-click Tor Browser integration
- Configuration management
- Update checker
- Material You dark theme (GUI)

### Platforms Supported

- **Linux**: Debian, Ubuntu, Arch, Manjaro, Fedora, RHEL, CentOS
- **macOS**: via Homebrew
- **Windows**: via Tor Expert Bundle
- **Termux**: Android terminal environment

### Components

- System detection utility
- Configuration manager
- Onion service manager
- GUI application (CustomTkinter)
- CLI interface (interactive terminal)
- Update manager
- Installation scripts

---

## Future Roadmap

### [1.2.0] - Planned
- Multiple site management (host multiple .onion sites)
- Traffic statistics (privacy-preserving analytics)
- Built-in website templates
- Configuration backup/restore

### [2.0.0] - Future
- Dynamic content support (PHP, Node.js, Python)
- Custom vanity .onion addresses
- Docker container support
- Mobile app (React Native)
- WebSocket support for real-time updates

---

## Migration Guide

### Upgrading from 1.0.0 to 1.1.0

The upgrade is backward compatible. Your existing configurations will work with the new version.

**Changes in behavior:**
- Services now start with manual Tor instead of systemctl
- You'll see bootstrap progress when starting services
- .onion addresses are guaranteed to be available after startup
- Stopping services now handles both manual and systemctl methods

**New features you can use:**
```python
# Use progress callback for custom UI
def my_progress(progress, message):
    print(f"{progress}% - {message}")

success, msg, address = service.start_service(
    "/path/to/site",
    progress_callback=my_progress
)
```

**Config file changes:**
- No changes to config.json format
- Additional status fields available in `get_service_status()`

---

## Known Issues

### Current Limitations

1. **Bootstrap Timeout**: Currently set to 120 seconds. May need adjustment for slow connections.
2. **Windows**: Requires manual Tor Expert Bundle installation
3. **Termux**: X11 support needed for GUI mode
4. **macOS**: May require Homebrew for easiest installation

### Reporting Issues

Found a bug? Please report it:
- GitHub Issues: https://github.com/uzairdeveloper223/Onion-Hoster/issues
- Include: OS, distribution, error message, and log file

---

## Credits

**Author:** Uzair Developer
**GitHub:** [@uzairdeveloper223](https://github.com/uzairdeveloper223)

**Special Thanks:**
- The Tor Project for making anonymous hosting possible
- The open-source community for continuous inspiration
- All contributors and testers

**Inspired by:** Real-world manual Debian setup experience that showed the value of visibility into Tor's bootstrap process.

---

**License:** MIT
**Repository:** https://github.com/uzairdeveloper223/Onion-Hoster

---

*Made with ❤️ and 🧅 for the privacy community*
