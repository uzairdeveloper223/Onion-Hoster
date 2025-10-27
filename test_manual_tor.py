#!/usr/bin/env python3
"""
Test script for manual Tor startup with bootstrap progress monitoring.
This demonstrates the new manual Tor startup feature.

Usage:
    python test_manual_tor.py /path/to/your/website
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.system_detector import get_system_detector
from core.config_manager import ConfigManager
from core.onion_service import OnionServiceManager
from core.constants import VERSION


def print_banner():
    """Print test banner."""
    print("\n" + "=" * 70)
    print(f"  ONION HOSTER v{VERSION} - Manual Tor Startup Test")
    print("=" * 70 + "\n")


def progress_callback(progress: int, message: str):
    """
    Callback function for bootstrap progress updates.

    Args:
        progress: Bootstrap percentage (0-100)
        message: Status message
    """
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\r[{bar}] {progress}% - {message}", end="", flush=True)

    if progress == 100:
        print()  # New line after completion


def main():
    """Main test function."""
    print_banner()

    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python test_manual_tor.py /path/to/your/website")
        print("\nExample:")
        print("  python test_manual_tor.py ./example-site")
        sys.exit(1)

    site_directory = sys.argv[1]

    # Check if directory exists and has index.html
    if not os.path.isdir(site_directory):
        print(f"❌ Error: Directory '{site_directory}' does not exist!")
        sys.exit(1)

    index_file = os.path.join(site_directory, "index.html")
    if not os.path.isfile(index_file):
        print(f"❌ Error: No index.html found in '{site_directory}'!")
        sys.exit(1)

    print(f"✓ Website directory: {os.path.abspath(site_directory)}")
    print(f"✓ Index file found: {index_file}\n")

    # Initialize components
    print("Initializing system...")
    system = get_system_detector()
    config = ConfigManager()
    service = OnionServiceManager(config, system)

    # Print system info
    print(f"✓ Operating System: {system.os_type}")
    print(f"✓ Distribution: {system.distro}")
    print(f"✓ Desktop Environment: {system.desktop_env or 'None (CLI)'}")
    print(f"✓ Termux: {system.is_termux}")
    print()

    # Check dependencies
    print("Checking dependencies...")
    deps = service.check_dependencies()
    print(f"  Tor installed: {'✓' if deps['tor'] else '✗'}")
    print(f"  Nginx installed: {'✓' if deps['nginx'] else '✗'}")
    print()

    if not deps["tor"] or not deps["nginx"]:
        print("❌ Error: Tor and Nginx must be installed!")
        print("\nTo install:")
        if system.distro == "debian":
            print("  sudo apt update && sudo apt install tor nginx")
        elif system.distro == "arch":
            print("  sudo pacman -Sy tor nginx")
        elif system.is_termux:
            print("  pkg install tor nginx")
        sys.exit(1)

    # Ask for sudo password if needed (Linux)
    if (
        system.os_type == "linux"
        and not system.is_termux
        and not system.check_permissions()
    ):
        import getpass

        print("⚠️  Root privileges required for configuration.")
        password = getpass.getpass("Enter sudo password: ")
        service.set_sudo_password(password)
        print()

    # Validate site directory
    print("Validating website directory...")
    valid, msg = service.validate_site_directory(site_directory)
    if not valid:
        print(f"❌ Validation failed: {msg}")
        sys.exit(1)
    print(f"✓ {msg}\n")

    # Create Nginx configuration
    print("Configuring Nginx...")
    success, msg = service.create_nginx_config(site_directory)
    if not success:
        print(f"❌ Failed: {msg}")
        sys.exit(1)
    print(f"✓ {msg}\n")

    # Configure Tor hidden service
    print("Configuring Tor hidden service...")
    success, msg = service.configure_tor_hidden_service()
    if not success:
        print(f"❌ Failed: {msg}")
        sys.exit(1)
    print(f"✓ {msg}\n")

    # Start Nginx
    print("Starting Nginx...")
    success, msg = service.start_nginx()
    if not success:
        print(f"❌ Failed: {msg}")
        sys.exit(1)
    print(f"✓ {msg}\n")

    # Start Tor with manual startup and bootstrap monitoring
    print("Starting Tor with bootstrap monitoring...")
    print("This will show real-time progress as Tor connects to the network.\n")

    success, msg = service.start_tor_manual(progress_callback=progress_callback)

    if success:
        print(f"\n✓ {msg}\n")

        # Get onion address
        onion_address = service._onion_address
        if onion_address:
            print("=" * 70)
            print("  🎉 SUCCESS! Your website is now live on the Tor network!")
            print("=" * 70)
            print(f"\n  Your .onion address: {onion_address}")
            print(f"\n  Access your site at: http://{onion_address}")
            print("\n  You can open this address in Tor Browser.")
            print("=" * 70 + "\n")
        else:
            print("⚠️  Service started but address not available yet.")
            print("   Check again in a few moments.\n")

        # Show how to stop
        print("To stop the service:")
        print("  - Press Ctrl+C to interrupt")
        print(
            "  - Or run: python -c 'from src.core.onion_service import OnionServiceManager; "
            "from src.core.config_manager import ConfigManager; "
            "from src.core.system_detector import get_system_detector; "
            "s = OnionServiceManager(ConfigManager(), get_system_detector()); "
            "s.stop_service()'\n"
        )

        # Keep running
        print("Service is running. Press Ctrl+C to stop...")
        try:
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping service...")
            success, msg = service.stop_service()
            if success:
                print(f"✓ {msg}")
            else:
                print(f"⚠️  {msg}")
            print("\nGoodbye!")
    else:
        print(f"\n❌ Failed to start Tor: {msg}")
        print("\nCleaning up Nginx...")
        service.stop_nginx()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
