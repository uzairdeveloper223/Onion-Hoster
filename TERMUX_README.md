# Onion Hoster - Termux Edition

![Version](https://img.shields.io/badge/version-1.0.0-purple)
![Platform](https://img.shields.io/badge/platform-Termux-green)
![License](https://img.shields.io/badge/license-MIT-blue)

**Host your websites on the Tor Network directly from your Android device using Termux!**

This is a standalone bash script version of Onion Hoster designed specifically for Termux users. It provides all the functionality of the main application without requiring Python dependencies.

---

## 📱 Features

- ✅ **Pure Bash** - No Python or complex dependencies required
- 🌐 **Two Hosting Methods**:
  - **Nginx Method** - Host static websites (HTML, CSS, JavaScript, images)
  - **Custom Port Method** - Full support for dynamic content (PHP, Node.js, Python, databases)
- 🔒 **Secure** - Automatic Tor configuration and port validation
- 🎨 **Interactive Menu** - User-friendly CLI interface
- 📋 **Clipboard Support** - Copy onion address with Termux-API
- 🚀 **Fast Setup** - Get your onion service running in minutes
- 📊 **Status Monitoring** - Real-time service status and logs
- ⚙️ **Easy Configuration** - Simple command-line interface

---

## 📋 Requirements

- **Android device** with Termux installed
- **Storage permission** for Termux
- **Internet connection**

---

## 🚀 Quick Start

### 1. Install Termux

Download and install Termux from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or Google Play Store.

### 2. Grant Storage Permission

```bash
termux-setup-storage
```

### 3. Download Onion Hoster

```bash
# Update packages
pkg update && pkg upgrade -y

# Install git
pkg install git -y

# Clone the repository
git clone https://github.com/uzairdeveloper223/Onion-Hoster.git
cd Onion-Hoster

# Make the script executable
chmod +x termux.sh
```

### 4. Install Dependencies

```bash
./termux.sh install all
```

This will install:
- **Tor** - The Onion Router
- **Nginx** - Web server (optional, for static sites)
- **Termux-API** - Clipboard support (optional)

> **Note**: You also need to install the [Termux:API](https://f-droid.org/packages/com.termux.api/) app from F-Droid for clipboard functionality.

---

## 💻 Usage

### Interactive Menu Mode

Simply run the script without arguments:

```bash
./termux.sh
```

This opens an interactive menu with all options.

### Command Line Mode

#### Start Service

For **static websites** (Nginx method):
```bash
# Set hosting method
./termux.sh method nginx

# Set your website directory
./termux.sh config set site_directory /path/to/website

# Start the service
./termux.sh start
```

For **dynamic websites** (Custom Port method):
```bash
# Set hosting method and port (e.g., your PHP server on port 3000)
./termux.sh method custom_port 3000

# Start the service
./termux.sh start
```

#### Check Status

```bash
./termux.sh status
```

#### Get Onion Address

```bash
./termux.sh address
```

#### Stop Service

```bash
./termux.sh stop
```

#### Restart Service

```bash
./termux.sh restart
```

---

## 🎯 Hosting Methods

### 📄 Nginx Method (Static Sites Only)

**Best for**: HTML, CSS, JavaScript, images, fonts

**Limitations**:
- ❌ No PHP
- ❌ No server-side processing
- ❌ No databases
- ❌ No backend languages

**Setup**:
```bash
./termux.sh method nginx
./termux.sh config set site_directory ~/my-website
./termux.sh start
```

Your website files should be in the directory with an `index.html` file.

---

### 🚀 Custom Port Method (Full Support)

**Best for**: PHP, Node.js, Python, databases, any web framework

**Supports**:
- ✅ PHP applications
- ✅ Node.js servers
- ✅ Python web apps (Flask, Django)
- ✅ Databases (MySQL, PostgreSQL, SQLite)
- ✅ Any web server running on a port

**Setup**:

1. **Start your local web server** (example with PHP):
```bash
# Install PHP
pkg install php -y

# Start PHP built-in server on port 3000
cd ~/my-php-app
php -S 127.0.0.1:3000
```

2. **Configure Onion Hoster**:
```bash
./termux.sh method custom_port 3000
./termux.sh start
```

Now your PHP application is accessible via Tor!

---

## ⚙️ Configuration

### View Configuration

```bash
./termux.sh config show
```

### Set Site Directory

```bash
./termux.sh config set site_directory /path/to/website
```

### Set Nginx Port

```bash
./termux.sh config set nginx_port 8080
```

### Set Custom Port

```bash
./termux.sh config set custom_port 3000
```

### Change Hosting Method

```bash
# Switch to Nginx method
./termux.sh method nginx

# Switch to Custom Port method with port 5000
./termux.sh method custom_port 5000
```

---

## 🔒 Port Restrictions

The following ports are **forbidden** as they're reserved for Tor:

- **9050** - Tor SOCKS proxy
- **9051** - Tor control port
- **9150** - Tor Browser SOCKS proxy
- **9151** - Tor Browser control port

**Recommended**: Use ports between **1024-65535** for your services.

---

## 📚 All Commands

### Service Management
```bash
./termux.sh start          # Start the onion service
./termux.sh stop           # Stop the onion service
./termux.sh restart        # Restart the onion service
./termux.sh status         # Show service status
./termux.sh address        # Display onion address
```

### Configuration
```bash
./termux.sh config show                          # Show all configuration
./termux.sh config get <key>                     # Get configuration value
./termux.sh config set <key> <value>             # Set configuration value
./termux.sh method [nginx|custom_port] [port]    # Set hosting method
```

### Dependencies
```bash
./termux.sh install all     # Install all dependencies
./termux.sh install tor     # Install Tor only
./termux.sh install nginx   # Install Nginx only
./termux.sh install api     # Install Termux-API only
./termux.sh check           # Check dependency status
```

### Utilities
```bash
./termux.sh validate <dir>  # Validate site directory
./termux.sh logs            # View log file (live tail)
./termux.sh help            # Show help message
./termux.sh menu            # Show interactive menu
./termux.sh version         # Show version information
```

---

## 📖 Examples

### Example 1: Host a Static HTML Website

```bash
# Create a simple website
mkdir -p ~/my-website
echo "<h1>Hello from Tor!</h1>" > ~/my-website/index.html

# Configure and start
./termux.sh method nginx
./termux.sh config set site_directory ~/my-website
./termux.sh start

# Get your onion address
./termux.sh address
```

### Example 2: Host a PHP Application

```bash
# Install PHP
pkg install php -y

# Create PHP app
mkdir -p ~/my-php-app
echo "<?php phpinfo(); ?>" > ~/my-php-app/index.php

# Start PHP server on port 8000
cd ~/my-php-app
php -S 127.0.0.1:8000 &

# Configure Onion Hoster for custom port
./termux.sh method custom_port 8000
./termux.sh start
```

### Example 3: Host a Node.js Application

```bash
# Install Node.js
pkg install nodejs -y

# Create simple Node.js server
mkdir -p ~/my-node-app
cat > ~/my-node-app/server.js << 'EOF'
const http = require('http');
const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('<h1>Hello from Node.js on Tor!</h1>');
});
server.listen(4000, '127.0.0.1', () => {
  console.log('Server running on port 4000');
});
EOF

# Start Node.js server
cd ~/my-node-app
node server.js &

# Configure Onion Hoster
./termux.sh method custom_port 4000
./termux.sh start
```

### Example 4: Host a Python Flask Application

```bash
# Install Python and Flask
pkg install python -y
pip install flask

# Create Flask app
mkdir -p ~/my-flask-app
cat > ~/my-flask-app/app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from Flask on Tor!</h1>'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
EOF

# Start Flask app
cd ~/my-flask-app
python app.py &

# Configure Onion Hoster
./termux.sh method custom_port 5000
./termux.sh start
```

---

## 🔧 Troubleshooting

### Service Won't Start

1. **Check dependencies**:
```bash
./termux.sh check
```

2. **View logs**:
```bash
./termux.sh logs
```

3. **Check if ports are in use**:
```bash
# Check if Tor is already running
pgrep tor

# Check if Nginx is already running
pgrep nginx
```

### Can't Access Onion Address

1. **Wait a moment** - It takes a few seconds for Tor to generate the address
2. **Check service status**:
```bash
./termux.sh status
```

3. **Try restarting**:
```bash
./termux.sh restart
```

### Port Already in Use

If you get a "port already in use" error:

1. **Choose a different port**:
```bash
./termux.sh config set nginx_port 8081
# or for custom port
./termux.sh method custom_port 3001
```

2. **Kill the process using the port**:
```bash
# Find the process
netstat -tulpn | grep :8080

# Kill it (replace PID with actual process ID)
kill <PID>
```

### Termux-API Clipboard Not Working

1. **Install Termux:API app** from F-Droid
2. **Grant permissions** to Termux:API
3. **Install termux-api package**:
```bash
pkg install termux-api -y
```

---

## 📁 File Locations

- **Configuration**: `~/.onion-hoster-termux/config.conf`
- **Logs**: `~/.onion-hoster-termux/onion-hoster.log`
- **Tor Config**: `$PREFIX/etc/tor/torrc`
- **Hidden Service**: `~/.tor/hidden_service/`
- **Nginx Config**: `$PREFIX/etc/nginx/`

---

## 🛡️ Security Considerations

1. **Keep Termux Updated**:
```bash
pkg update && pkg upgrade
```

2. **Don't expose sensitive data** - Only host content you want to be public

3. **Use HTTPS** (optional) - You can set up SSL certificates even on Tor

4. **Monitor logs regularly**:
```bash
./termux.sh logs
```

5. **Be cautious with Custom Port method** - Ensure your application is secure

---

## 🔄 Comparison with Main Application

| Feature | Main App (Python) | Termux Edition (Bash) |
|---------|-------------------|----------------------|
| Platform | Linux, macOS, Windows, Termux | Termux only |
| Dependencies | Python 3.6+, pip packages | Bash, Tor, Nginx |
| GUI | ✅ Yes (CustomTkinter) | ❌ No (CLI only) |
| CLI | ✅ Yes | ✅ Yes |
| Installation | pip install | pkg install |
| Hosting Methods | Nginx, Custom Port | Nginx, Custom Port |
| Size | ~10MB+ (with deps) | ~1MB (script only) |
| Performance | Excellent | Excellent |
| Auto-updates | ✅ Yes | Manual |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Uzair Developer**

- GitHub: [@uzairdeveloper223](https://github.com/uzairdeveloper223)
- Repository: [Onion-Hoster](https://github.com/uzairdeveloper223/Onion-Hoster)

---

## 🙏 Acknowledgments

- The Tor Project for making anonymous hosting possible
- Nginx for the powerful web server
- Termux community for the amazing Android terminal

---

## ⚠️ Disclaimer

This tool is for educational and legitimate purposes only. Users are responsible for complying with all applicable laws and regulations. The author is not responsible for any misuse of this software.

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. View logs: `./termux.sh logs`
3. Open an issue on [GitHub](https://github.com/uzairdeveloper223/Onion-Hoster/issues)

---

**Enjoy hosting on Tor from your Android device! 🎉**