"""
Onion Hoster - CLI Interface
Author: Uzair Developer
GitHub: uzairdeveloper223

This module provides the command-line interface for Onion Hoster.
It supports both interactive and direct command modes.
"""

import os
import sys
import cmd
import time
import pyperclip
from pathlib import Path
from typing import Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.constants import (
    CLI_BANNER,
    VERSION,
    AUTHOR,
    GITHUB_USERNAME,
    HOSTING_METHOD_NGINX,
    HOSTING_METHOD_CUSTOM_PORT,
)
from core.system_detector import get_system_detector
from core.config_manager import get_config_manager
from core.onion_service import OnionServiceManager
from core.update_manager import get_update_manager


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    PURPLE = "\033[35m"


class OnionHosterCLI(cmd.Cmd):
    """Interactive CLI for Onion Hoster."""

    intro = (
        Colors.PURPLE
        + CLI_BANNER
        + Colors.ENDC
        + '\nType "help" or "?" to list commands.\n'
    )
    prompt = Colors.PURPLE + "onion-hoster> " + Colors.ENDC

    def __init__(self):
        """Initialize the CLI."""
        super().__init__()

        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.system = get_system_detector()
        self.config = get_config_manager()
        self.service = OnionServiceManager(self.config, self.system)
        self.updater = get_update_manager(self.config)

        # Check if CLI can run
        can_run, message = self.system.can_run_cli()
        if not can_run:
            self.print_error(message)
            sys.exit(1)

        # Show warning if desktop environment exists
        if self.system.has_gui and self.system.desktop_env:
            self.print_warning(message)
            response = input("Continue with CLI mode? (y/n): ").strip().lower()
            if response != "y":
                print("Exiting...")
                sys.exit(0)

        # Update platform info in config
        self.config.update_platform_info(self.system.get_platform_info())

    def print_success(self, message: str):
        """Print success message in green."""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message: str):
        """Print error message in red."""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

    def print_warning(self, message: str):
        """Print warning message in yellow."""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

    def print_info(self, message: str):
        """Print info message in cyan."""
        print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

    def print_header(self, message: str):
        """Print header message in purple."""
        print(f"\n{Colors.PURPLE}{Colors.BOLD}{message}{Colors.ENDC}")

    def do_status(self, arg):
        """Show system status and service information."""
        self.print_header("=== System Status ===")

        # System information
        info = self.system.get_platform_info()
        print(f"\n{Colors.BOLD}System Information:{Colors.ENDC}")
        print(f"  OS: {info['os_name']} ({info['os_type']})")
        if info["distro"]:
            print(f"  Distribution: {info['distro']}")
        if info["desktop_env"]:
            print(f"  Desktop Environment: {info['desktop_env']}")
        print(f"  Architecture: {info['architecture']}")
        print(f"  Python: {info['python_version']}")

        # Dependencies
        print(f"\n{Colors.BOLD}Dependencies:{Colors.ENDC}")
        if info["tor_installed"]:
            self.print_success("Tor is installed")
        else:
            self.print_error("Tor is not installed")

        if info["nginx_installed"]:
            self.print_success("Nginx is installed")
        else:
            self.print_error("Nginx is not installed")

        if info["tor_browser_installed"]:
            self.print_success("Tor Browser is installed")
        else:
            self.print_warning("Tor Browser is not installed")

        # Service status
        service_status = self.service.get_service_status()
        print(f"\n{Colors.BOLD}Service Status:{Colors.ENDC}")

        if service_status["service_running"]:
            self.print_success("Onion service is running")
            if service_status["onion_address"]:
                print(
                    f"  Onion Address: {Colors.OKGREEN}{service_status['onion_address']}{Colors.ENDC}"
                )
            if service_status["site_directory"]:
                print(f"  Site Directory: {service_status['site_directory']}")
            print(f"  Nginx Port: {service_status['nginx_port']}")
        else:
            self.print_info("Onion service is not running")

    def do_install(self, arg):
        """
        Install dependencies.
        Usage: install <tor|nginx|tor-browser|all>
        """
        if not arg:
            self.print_error(
                "Please specify what to install: tor, nginx, tor-browser, or all"
            )
            return

        arg = arg.lower().strip()

        if arg == "tor":
            self.print_info("Installing Tor...")
            success, message = self.service.install_tor()
            if success:
                self.print_success(message)
            else:
                self.print_error(message)

        elif arg == "nginx":
            self.print_info("Installing Nginx...")
            success, message = self.service.install_nginx()
            if success:
                self.print_success(message)
            else:
                self.print_error(message)

        elif arg == "tor-browser" or arg == "torbrowser":
            self.print_info("Installing Tor Browser...")
            success, message = self.service.install_tor_browser()
            if success:
                self.print_success(message)
            else:
                self.print_error(message)

        elif arg == "all":
            self.print_info("Installing all dependencies...")

            # Install Tor
            self.print_info("Installing Tor...")
            success, message = self.service.install_tor()
            if success:
                self.print_success(message)
            else:
                self.print_error(message)

            # Install Nginx
            self.print_info("Installing Nginx...")
            success, message = self.service.install_nginx()
            if success:
                self.print_success(message)
            else:
                self.print_error(message)

            # Install Tor Browser
            self.print_info("Installing Tor Browser...")
            success, message = self.service.install_tor_browser()
            if success:
                self.print_success(message)
            else:
                self.print_warning(message)

        else:
            self.print_error(f"Unknown package: {arg}")
            print("Available packages: tor, nginx, tor-browser, all")

    def do_start(self, arg):
        """
        Start the onion service.
        Usage: start <directory>  (for nginx method)
        Usage: start              (for custom port method, no directory needed)
        """
        hosting_method = self.config.get("hosting_method", HOSTING_METHOD_NGINX)

        if hosting_method == HOSTING_METHOD_NGINX:
            # Nginx method requires directory
            if not arg:
                site_dir = self.config.get("site_directory")
                if not site_dir:
                    self.print_error("Please specify the site directory")
                    print("Usage: start <directory>")
                    return
            else:
                site_dir = arg.strip()
        else:
            # Custom port method
            custom_port = self.config.get("custom_port")
            if not custom_port:
                self.print_error(
                    "Custom port not configured. Use: config set custom_port <port>"
                )
                return

            # Validate custom port
            valid, msg = self.service.validate_port(custom_port)
            if not valid:
                self.print_error(f"Invalid custom port: {msg}")
                return

            # For custom port method, directory can be empty or specified
            site_dir = arg.strip() if arg else self.config.get("site_directory", "")
            self.print_info(f"Using custom port method with port: {custom_port}")

        # Check dependencies
        deps = self.service.check_dependencies()
        if not deps["tor"]:
            self.print_error("Tor is not installed. Install it with: install tor")
            return

        # Only require nginx for nginx method
        if hosting_method == HOSTING_METHOD_NGINX and not deps["nginx"]:
            self.print_error("Nginx is not installed. Install it with: install nginx")
            return

        self.print_info(f"Starting onion service...")
        self.print_info("This may take a moment...")

        # Progress bar for bootstrap
        import sys

        last_progress = 0

        def bootstrap_progress_callback(progress, status):
            nonlocal last_progress
            if progress > last_progress:
                last_progress = progress
                # Create progress bar
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)

                # Color based on progress
                if progress < 30:
                    color = Colors.WARNING
                elif progress < 70:
                    color = Colors.OKCYAN
                else:
                    color = Colors.OKGREEN

                # Print progress bar
                sys.stdout.write(
                    f"\r{color}[{bar}] {progress}%{Colors.ENDC} - {status[:50]}"
                )
                sys.stdout.flush()

                if progress == 100:
                    print()  # New line after completion

        success, message, onion_address = self.service.start_service(
            site_dir, progress_callback=bootstrap_progress_callback
        )
        print()  # Ensure we're on a new line

        if success:
            self.print_success(message)
            if onion_address:
                print(
                    f"\n{Colors.BOLD}{Colors.OKGREEN}Your onion address:{Colors.ENDC}"
                )
                print(f"{Colors.OKGREEN}{Colors.BOLD}{onion_address}{Colors.ENDC}")

                # Try to copy to clipboard
                try:
                    pyperclip.copy(onion_address)
                    self.print_success("Onion address copied to clipboard!")
                except:
                    self.print_info("Tip: Copy the address above to share your site")
        else:
            self.print_error(message)

    def do_stop(self, arg):
        """Stop the onion service."""
        if not self.config.get("service_running", False):
            self.print_warning("Service is not running")
            return

        self.print_info("Stopping onion service...")
        success, message = self.service.stop_service()

        if success:
            self.print_success(message)
        else:
            self.print_error(message)

    def do_restart(self, arg):
        """Restart the onion service."""
        self.print_info("Restarting onion service...")

        # Stop first
        if self.config.get("service_running", False):
            success, message = self.service.stop_service()
            if not success:
                self.print_error(f"Failed to stop service: {message}")
                return
            time.sleep(2)

        # Start
        site_dir = self.config.get("site_directory")
        if not site_dir:
            self.print_error("No site directory configured. Use: start <directory>")
            return

        # Progress bar for bootstrap
        import sys

        last_progress = 0

        def bootstrap_progress_callback(progress, status):
            nonlocal last_progress
            if progress > last_progress:
                last_progress = progress
                # Create progress bar
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)

                # Color based on progress
                if progress < 30:
                    color = Colors.WARNING
                elif progress < 70:
                    color = Colors.OKCYAN
                else:
                    color = Colors.OKGREEN

                # Print progress bar
                sys.stdout.write(
                    f"\r{color}[{bar}] {progress}%{Colors.ENDC} - {status[:50]}"
                )
                sys.stdout.flush()

                if progress == 100:
                    print()  # New line after completion

        success, message, onion_address = self.service.start_service(
            site_dir, progress_callback=bootstrap_progress_callback
        )
        print()  # Ensure we're on a new line

        if success:
            self.print_success(message)
            if onion_address:
                print(f"\n{Colors.OKGREEN}Onion address: {onion_address}{Colors.ENDC}")

                # Try to copy to clipboard
                try:
                    pyperclip.copy(onion_address)
                    self.print_success("Onion address copied to clipboard!")
                except:
                    self.print_info("Tip: Copy the address above to share your site")
        else:
            self.print_error(message)

    def do_address(self, arg):
        """Show the current onion address."""
        onion_address = self.config.get("onion_address")

        if onion_address:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}Your onion address:{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}{onion_address}{Colors.ENDC}\n")

            # Try to copy to clipboard
            try:
                pyperclip.copy(onion_address)
                self.print_success("Copied to clipboard!")
            except:
                pass
        else:
            self.print_warning("No onion address available. Start the service first.")

    def do_open(self, arg):
        """Open the onion site in Tor Browser."""
        onion_address = self.config.get("onion_address")

        if not onion_address:
            self.print_error("No onion address available. Start the service first.")
            return

        if not self.system.is_tor_browser_installed():
            self.print_error("Tor Browser is not installed")
            self.print_info("Install it with: install tor-browser")
            return

        self.print_info("Opening in Tor Browser...")
        success, message = self.service.open_in_tor_browser(onion_address)

        if success:
            self.print_success(message)
        else:
            self.print_error(message)

    def do_validate(self, arg):
        """
        Validate a site directory.
        Usage: validate <directory>
        """
        if not arg:
            self.print_error("Please specify a directory to validate")
            print("Usage: validate <directory>")
            return

        directory = arg.strip()
        valid, message = self.service.validate_site_directory(directory)

        if valid:
            self.print_success(message)
            self.print_success(f"Directory is ready: {directory}")
        else:
            self.print_error(message)

    def do_config(self, arg):
        """
        View or modify configuration.
        Usage: config [get|set|show] [key] [value]
        """
        args = arg.split()

        if not args or args[0] == "show":
            # Show all configuration
            self.print_header("=== Configuration ===")
            config = self.config.get_all_config()

            print(f"\n{Colors.BOLD}General:{Colors.ENDC}")
            print(f"  Version: {config.get('version')}")
            print(f"  Theme: {config.get('theme')}")
            print(f"  Accent Color: {config.get('accent_color')}")

            print(f"\n{Colors.BOLD}Service:{Colors.ENDC}")
            print(f"  Site Directory: {config.get('site_directory')}")
            print(f"  Hosting Method: {config.get('hosting_method')}")
            print(f"  Nginx Port: {config.get('nginx_port')}")
            print(f"  Custom Port: {config.get('custom_port')}")
            print(f"  Onion Address: {config.get('onion_address')}")
            print(f"  Service Running: {config.get('service_running')}")

            print(f"\n{Colors.BOLD}Platform:{Colors.ENDC}")
            platform = config.get("platform", {})
            print(f"  OS Type: {platform.get('os_type')}")
            print(f"  Distribution: {platform.get('distro')}")
            print(f"  Desktop Environment: {platform.get('desktop_env')}")

        elif args[0] == "get":
            if len(args) < 2:
                self.print_error("Usage: config get <key>")
                return

            key = args[1]
            value = self.config.get(key)
            if value is not None:
                print(f"{key}: {value}")
            else:
                self.print_warning(f"Key not found: {key}")

        elif args[0] == "set":
            if len(args) < 3:
                self.print_error("Usage: config set <key> <value>")
                return

            key = args[1]
            value = " ".join(args[2:])

            # Special handling for hosting_method
            if key == "hosting_method":
                if value not in [HOSTING_METHOD_NGINX, HOSTING_METHOD_CUSTOM_PORT]:
                    self.print_error(
                        f"Invalid hosting method. Use '{HOSTING_METHOD_NGINX}' or '{HOSTING_METHOD_CUSTOM_PORT}'"
                    )
                    return
                success, msg = self.service.set_hosting_method(value)
                if success:
                    self.print_success(msg)
                    if value == HOSTING_METHOD_NGINX:
                        self.print_info(
                            "⚠️ Nginx method: Only static websites will work (no PHP, no server-side processing)"
                        )
                    else:
                        self.print_info(
                            "✓ Custom Port method: Full support for PHP, databases, and dynamic content"
                        )
                        self.print_info(
                            "Don't forget to set custom_port with: config set custom_port <port>"
                        )
                else:
                    self.print_error(msg)
                return

            # Special handling for custom_port
            if key == "custom_port":
                try:
                    port = int(value)
                    valid, msg = self.service.validate_port(port)
                    if not valid:
                        self.print_error(f"Invalid port: {msg}")
                        return
                    success, msg = self.service.set_custom_port(port)
                    if success:
                        self.print_success(msg)
                        self.print_info(
                            "⚠️ Remember to set hosting_method to 'custom_port' with: config set hosting_method custom_port"
                        )
                    else:
                        self.print_error(msg)
                except ValueError:
                    self.print_error("Port must be a number")
                return

            # Try to parse as int or bool
            if value.isdigit():
                value = int(value)
            elif value.lower() in ["true", "false"]:
                value = value.lower() == "true"

            success = self.config.set(key, value)
            if success:
                self.print_success(f"Set {key} = {value}")
            else:
                self.print_error(f"Failed to set {key}")

        else:
            self.print_error(f"Unknown config command: {args[0]}")
            print("Usage: config [get|set|show] [key] [value]")

    def do_method(self, arg):
        """
        Set or view hosting method.
        Usage: method [nginx|custom_port] [port]

        Examples:
          method              - Show current method
          method nginx        - Switch to Nginx method (static sites only)
          method custom_port 3000 - Switch to custom port method with port 3000
        """
        args = arg.split()

        if not args:
            # Show current method
            current_method = self.config.get("hosting_method", HOSTING_METHOD_NGINX)
            custom_port = self.config.get("custom_port")

            self.print_header("=== Hosting Method ===")
            print(f"\n{Colors.BOLD}Current Method:{Colors.ENDC} {current_method}")

            if current_method == HOSTING_METHOD_NGINX:
                print(f"\n{Colors.WARNING}Nginx Method:{Colors.ENDC}")
                print("  ⚠️ Only static websites will work")
                print("  • HTML, CSS, JavaScript, images")
                print("  • No PHP, no server-side processing, no databases")
                print(
                    f"\n{Colors.BOLD}Nginx Port:{Colors.ENDC} {self.config.get('nginx_port', 8080)}"
                )
            else:
                print(f"\n{Colors.OKGREEN}Custom Port Method:{Colors.ENDC}")
                print("  ✓ Full support for dynamic content")
                print("  • PHP, Python, Node.js, etc.")
                print("  • Databases and server-side processing")
                if custom_port:
                    print(f"\n{Colors.BOLD}Custom Port:{Colors.ENDC} {custom_port}")
                else:
                    self.print_warning(
                        "⚠️ Custom port not set! Use: method custom_port <port>"
                    )

            return

        method = args[0].lower()

        if method == "nginx":
            success, msg = self.service.set_hosting_method(HOSTING_METHOD_NGINX)
            if success:
                self.print_success(msg)
                self.print_info(
                    "⚠️ Only static websites will work (no PHP, no server-side processing)"
                )
            else:
                self.print_error(msg)

        elif method == "custom_port" or method == "custom":
            if len(args) < 2:
                self.print_error("Please specify the port number")
                print("Usage: method custom_port <port>")
                return

            try:
                port = int(args[1])
                valid, msg = self.service.validate_port(port)
                if not valid:
                    self.print_error(f"Invalid port: {msg}")
                    return

                # Set custom port
                success, msg = self.service.set_custom_port(port)
                if not success:
                    self.print_error(msg)
                    return

                # Set hosting method
                success, msg = self.service.set_hosting_method(
                    HOSTING_METHOD_CUSTOM_PORT
                )
                if success:
                    self.print_success(f"Hosting method set to custom port: {port}")
                    self.print_info(
                        "✓ Full support for PHP, databases, and dynamic content"
                    )
                    self.print_info(
                        f"Make sure your local website is running on port {port}"
                    )
                else:
                    self.print_error(msg)
            except ValueError:
                self.print_error("Port must be a number")

        else:
            self.print_error(f"Unknown method: {method}")
            print("Usage: method [nginx|custom_port] [port]")

    def do_update(self, arg):
        """
        Check for and apply updates.
        Usage: update [check|download|apply|auto]
        """
        args = arg.split()

        if not args or args[0] == "check":
            # Check for updates
            self.print_info("Checking for updates...")
            update_available, latest_version, update_info = (
                self.updater.check_for_updates()
            )

            if update_available:
                self.print_success(
                    f"Update available: v{latest_version} (current: v{VERSION})"
                )

                # Show changelog
                changelog = self.updater.get_changelog(update_info)
                if changelog:
                    print(f"\n{Colors.BOLD}Changelog:{Colors.ENDC}")
                    for change in changelog:
                        print(f"  • {change}")

                print(f"\nTo update, run: update auto")
            else:
                self.print_success(f"You are using the latest version (v{VERSION})")

        elif args[0] == "download":
            # Download update
            self.print_info("Downloading update...")
            success, message = self.updater.download_update()

            if success:
                self.print_success(message)
                self.print_info("To apply the update, run: update apply")
            else:
                self.print_error(message)

        elif args[0] == "apply":
            # Apply update
            self.print_info("Applying update...")
            success, message = self.updater.apply_update()

            if success:
                self.print_success(message)
                self.print_warning(
                    "Please restart the application to use the new version"
                )
            else:
                self.print_error(message)

        elif args[0] == "auto":
            # Automatic update
            self.print_info("Starting automatic update...")
            success, message = self.updater.auto_update()

            if success:
                self.print_success(message)
                self.print_warning(
                    "Please restart the application to use the new version"
                )
            else:
                self.print_error(message)

        else:
            self.print_error(f"Unknown update command: {args[0]}")
            print("Usage: update [check|download|apply|auto]")

    def do_history(self, arg):
        """Show service history."""
        history = self.config.get("history", [])

        if not history:
            self.print_info("No history available")
            return

        self.print_header("=== Service History ===")

        for i, entry in enumerate(reversed(history[-10:]), 1):
            action = entry.get("action", "unknown")
            timestamp = entry.get("timestamp", "unknown")

            print(f"\n{Colors.BOLD}{i}. {action}{Colors.ENDC}")
            print(f"   Time: {timestamp}")

            if "site_directory" in entry:
                print(f"   Directory: {entry['site_directory']}")
            if "onion_address" in entry:
                print(f"   Address: {entry['onion_address']}")

    def do_clear(self, arg):
        """Clear the screen."""
        os.system("clear" if os.name != "nt" else "cls")
        print(Colors.PURPLE + CLI_BANNER + Colors.ENDC)

    def do_version(self, arg):
        """Show version information."""
        self.print_header(f"Onion Hoster v{VERSION}")
        print(f"Author: {AUTHOR}")
        print(f"GitHub: github.com/{GITHUB_USERNAME}")
        print(f"\nRun 'update check' to check for updates")

    def do_exit(self, arg):
        """Exit the application."""
        self.print_info("Goodbye!")
        return True

    def do_quit(self, arg):
        """Exit the application."""
        return self.do_exit(arg)

    def do_EOF(self, arg):
        """Handle EOF (Ctrl+D)."""
        print()  # New line
        return self.do_exit(arg)

    def emptyline(self):
        """Do nothing on empty line."""
        pass

    def default(self, line):
        """Handle unknown commands."""
        self.print_error(f"Unknown command: {line}")
        print("Type 'help' to see available commands")


def main():
    """Main entry point for CLI."""
    try:
        # Check if running in GUI-only environment
        system = get_system_detector()

        if not system.has_gui and os.environ.get("DISPLAY") is None:
            # Pure CLI environment - proceed
            pass

        # Start CLI
        cli = OnionHosterCLI()
        cli.cmdloop()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        logging.exception("Fatal error in CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()
