#!/usr/bin/env python3
"""
Onion Hoster - Main Launcher Script
Author: Uzair Developer
GitHub: uzairdeveloper223

This is the main entry point for Onion Hoster.
It automatically detects the environment and launches the appropriate interface.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.system_detector import get_system_detector
from core.constants import VERSION, APP_NAME, CLI_BANNER


def print_banner():
    """Print application banner."""
    print(CLI_BANNER)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{VERSION} - Host static websites on Tor Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--cli", action="store_true", help="Force CLI mode")

    parser.add_argument("--gui", action="store_true", help="Force GUI mode")

    parser.add_argument("--version", action="version", version=f"{APP_NAME} v{VERSION}")

    parser.add_argument(
        "--check-system",
        action="store_true",
        help="Check system information and dependencies",
    )

    args = parser.parse_args()

    # Initialize system detector
    system = get_system_detector()

    # Check system information
    if args.check_system:
        print_banner()
        print("\n=== System Information ===\n")
        print(system)
        sys.exit(0)

    # Determine which mode to run
    if args.cli and args.gui:
        print("Error: Cannot specify both --cli and --gui")
        sys.exit(1)

    if args.cli:
        # Force CLI mode
        can_run, message = system.can_run_cli()
        if not can_run:
            print(f"Error: {message}")
            sys.exit(1)

        if system.has_gui and system.desktop_env:
            print(f"Warning: {message}")
            response = input("Continue with CLI mode? (y/n): ").strip().lower()
            if response != "y":
                print("Exiting...")
                sys.exit(0)

        # Launch CLI
        from cli.cli_interface import main as cli_main

        cli_main()

    elif args.gui:
        # Force GUI mode
        can_run, message = system.can_run_gui()
        if not can_run:
            print(f"Error: {message}")
            print("\nGUI mode requires a desktop environment.")
            print("Please use CLI mode instead: python onion-host.py --cli")
            sys.exit(1)

        # Launch GUI
        from gui.gui_app import main as gui_main

        gui_main()

    else:
        # Auto-detect mode
        if system.has_gui:
            # GUI available - use GUI mode
            try:
                from gui.gui_app import main as gui_main

                gui_main()
            except ImportError as e:
                print(f"Error: GUI dependencies not installed: {e}")
                print("\nPlease install GUI dependencies:")
                print("  pip install -r requirements.txt")
                print("\nOr use CLI mode:")
                print("  python onion-host.py --cli")
                sys.exit(1)
        else:
            # No GUI - use CLI mode
            print("No GUI detected. Starting in CLI mode...\n")
            from cli.cli_interface import main as cli_main

            cli_main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
