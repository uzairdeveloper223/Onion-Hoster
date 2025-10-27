"""
Onion Hoster - System Detection Utility
Author: Uzair Developer
GitHub: uzairdeveloper223

This module detects the operating system, distribution, desktop environment,
and checks for required software installations.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, List


class SystemDetector:
    """Detects system information and environment details."""

    def __init__(self):
        self.os_type = self._detect_os_type()
        self.is_termux = self._is_termux()
        self.distro = self._detect_linux_distro() if self.os_type == "linux" else None
        self.desktop_env = self._detect_desktop_environment()
        self.has_gui = self._has_gui_capability()

    def _detect_os_type(self) -> str:
        """Detect the operating system type."""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def _is_termux(self) -> bool:
        """Check if running in Termux environment."""
        return "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")

    def _detect_linux_distro(self) -> Optional[str]:
        """Detect Linux distribution type."""
        if self.is_termux:
            return "termux"

        try:
            # Try reading /etc/os-release
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()

                    # Debian-based
                    if any(
                        x in content
                        for x in [
                            "debian",
                            "ubuntu",
                            "mint",
                            "pop",
                            "elementary",
                            "zorin",
                        ]
                    ):
                        return "debian"

                    # Arch-based
                    elif any(
                        x in content for x in ["arch", "manjaro", "endeavour", "garuda"]
                    ):
                        return "arch"

                    # Red Hat-based
                    elif any(
                        x in content
                        for x in ["rhel", "fedora", "centos", "rocky", "alma"]
                    ):
                        return "redhat"

                    # SUSE-based
                    elif any(x in content for x in ["suse", "opensuse"]):
                        return "suse"

                    # Gentoo
                    elif "gentoo" in content:
                        return "gentoo"

            # Fallback: Check for package managers
            if shutil.which("apt"):
                return "debian"
            elif shutil.which("pacman"):
                return "arch"
            elif shutil.which("dnf") or shutil.which("yum"):
                return "redhat"
            elif shutil.which("zypper"):
                return "suse"
            elif shutil.which("emerge"):
                return "gentoo"

        except Exception as e:
            print(f"Error detecting Linux distro: {e}")

        return "unknown"

    def _detect_desktop_environment(self) -> Optional[str]:
        """Detect the desktop environment."""
        if self.os_type == "windows":
            return "Windows Desktop"

        if self.os_type == "darwin":
            return "macOS Aqua"

        if self.is_termux:
            return None

        # Check common environment variables
        desktop_env_vars = [
            "DESKTOP_SESSION",
            "XDG_CURRENT_DESKTOP",
            "XDG_SESSION_DESKTOP",
            "GDMSESSION",
        ]

        for var in desktop_env_vars:
            env_value = os.environ.get(var, "").lower()
            if env_value:
                if "gnome" in env_value:
                    return "GNOME"
                elif "kde" in env_value or "plasma" in env_value:
                    return "KDE Plasma"
                elif "xfce" in env_value:
                    return "XFCE"
                elif "lxde" in env_value:
                    return "LXDE"
                elif "lxqt" in env_value:
                    return "LXQt"
                elif "mate" in env_value:
                    return "MATE"
                elif "cinnamon" in env_value:
                    return "Cinnamon"
                elif "unity" in env_value:
                    return "Unity"
                elif "budgie" in env_value:
                    return "Budgie"
                elif "pantheon" in env_value:
                    return "Pantheon"
                elif "i3" in env_value:
                    return "i3"
                elif "awesome" in env_value:
                    return "Awesome"
                elif "dwm" in env_value:
                    return "dwm"
                elif "sway" in env_value:
                    return "Sway"
                elif "hyprland" in env_value:
                    return "Hyprland"

        # Check for window manager processes
        try:
            result = subprocess.run(
                ["ps", "-e"], capture_output=True, text=True, timeout=5
            )
            processes = result.stdout.lower()

            wm_list = [
                ("gnome-shell", "GNOME"),
                ("kwin", "KDE Plasma"),
                ("xfwm4", "XFCE"),
                ("openbox", "Openbox"),
                ("fluxbox", "Fluxbox"),
                ("i3", "i3"),
                ("awesome", "Awesome"),
                ("dwm", "dwm"),
                ("bspwm", "bspwm"),
                ("sway", "Sway"),
            ]

            for process, de_name in wm_list:
                if process in processes:
                    return de_name

        except Exception:
            pass

        return None

    def _has_gui_capability(self) -> bool:
        """Check if the system has GUI capability."""
        if self.os_type == "windows":
            return True

        if self.os_type == "darwin":
            return True

        if self.is_termux:
            # Check if Termux:X11 or VNC is running
            return "DISPLAY" in os.environ

        # Linux: Check for DISPLAY or WAYLAND_DISPLAY
        if "DISPLAY" in os.environ or "WAYLAND_DISPLAY" in os.environ:
            return True

        # Check if X11 or Wayland is available
        if os.path.exists("/tmp/.X11-unix") or os.path.exists("/run/user"):
            return True

        return False

    def is_tor_installed(self) -> bool:
        """Check if Tor is installed."""
        return shutil.which("tor") is not None

    def is_nginx_installed(self) -> bool:
        """Check if Nginx is installed."""
        return shutil.which("nginx") is not None

    def is_tor_browser_installed(self) -> bool:
        """Check if Tor Browser is installed."""
        if self.os_type == "windows":
            # Common Windows paths
            common_paths = [
                os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\firefox.exe"),
                os.path.expanduser(
                    "~\\AppData\\Local\\Tor Browser\\Browser\\firefox.exe"
                ),
                "C:\\Program Files\\Tor Browser\\Browser\\firefox.exe",
            ]
            return any(os.path.exists(path) for path in common_paths)

        elif self.os_type == "darwin":
            return os.path.exists("/Applications/Tor Browser.app")

        else:  # Linux/Termux
            # Check for torbrowser-launcher or direct installation
            if shutil.which("torbrowser-launcher"):
                return True

            # Check common Linux paths
            common_paths = [
                os.path.expanduser("~/.local/share/torbrowser"),
                "/usr/bin/torbrowser-launcher",
                "/opt/tor-browser",
            ]
            return any(os.path.exists(path) for path in common_paths)

    def is_xclip_installed(self) -> bool:
        """Check if xclip is installed."""
        return shutil.which("xclip") is not None

    def get_tor_browser_path(self) -> Optional[str]:
        """Get the path to Tor Browser executable."""
        if self.os_type == "windows":
            common_paths = [
                os.path.expanduser("~\\Desktop\\Tor Browser\\Start Tor Browser.exe"),
                os.path.expanduser(
                    "~\\AppData\\Local\\Tor Browser\\Start Tor Browser.exe"
                ),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path

        elif self.os_type == "darwin":
            path = "/Applications/Tor Browser.app/Contents/MacOS/firefox"
            if os.path.exists(path):
                return path

        else:  # Linux
            if shutil.which("torbrowser-launcher"):
                return "torbrowser-launcher"

            # Check for direct installation
            common_paths = [
                os.path.expanduser(
                    "~/.local/share/torbrowser/tbb/x86_64/tor-browser/Browser/start-tor-browser"
                ),
                "/opt/tor-browser/Browser/start-tor-browser",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path

        return None

    def can_run_gui(self) -> Tuple[bool, str]:
        """
        Check if GUI can run in current environment.
        Returns: (can_run: bool, message: str)
        """
        if not self.has_gui:
            return False, "No GUI capability detected. Please use CLI mode."

        return True, "GUI capability detected."

    def can_run_cli(self) -> Tuple[bool, str]:
        """
        Check if CLI can run in current environment.
        Returns: (can_run: bool, message: str, warning: bool)
        """
        # CLI can always run, but warn if desktop environment exists
        if self.has_gui and self.desktop_env:
            warning = (
                f"Desktop environment detected ({self.desktop_env}). "
                "Consider using GUI mode for better experience."
            )
            return True, warning

        return True, "CLI mode ready."

    def get_platform_info(self) -> Dict[str, any]:
        """Get comprehensive platform information."""
        return {
            "os_type": self.os_type,
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "distro": self.distro,
            "is_termux": self.is_termux,
            "desktop_env": self.desktop_env,
            "has_gui": self.has_gui,
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "tor_installed": self.is_tor_installed(),
            "nginx_installed": self.is_nginx_installed(),
            "tor_browser_installed": self.is_tor_browser_installed(),
        }

    def get_install_command(self, package: str) -> Optional[str]:
        """Get the installation command for a package based on the platform."""
        from .constants import INSTALL_COMMANDS

        if self.is_termux:
            platform_key = "termux"
        elif self.distro in ["debian", "arch", "redhat"]:
            platform_key = self.distro
        elif self.os_type == "darwin":
            platform_key = "darwin"
        else:
            return None

        commands = INSTALL_COMMANDS.get(platform_key, {})
        return commands.get(package)

    def get_service_command(self, service: str, action: str) -> Optional[str]:
        """Get the service management command based on the platform."""
        from .constants import SERVICE_COMMANDS

        if self.is_termux:
            platform_key = "termux"
        elif self.distro in ["debian", "arch", "redhat"]:
            platform_key = self.distro
        elif self.os_type == "darwin":
            platform_key = "darwin"
        else:
            return None

        commands = SERVICE_COMMANDS.get(platform_key, {})
        command_key = f"{service}_{action}"
        return commands.get(command_key)

    def get_platform_paths(self) -> Optional[Dict[str, str]]:
        """Get platform-specific paths."""
        from .constants import PLATFORM_PATHS

        if self.is_termux:
            return PLATFORM_PATHS.get("termux")
        elif self.distro in ["debian", "arch", "redhat"]:
            return PLATFORM_PATHS.get(self.distro)
        elif self.os_type == "windows":
            paths = PLATFORM_PATHS.get("windows", {}).copy()
            # Replace {user} with actual username
            username = os.environ.get("USERNAME", "")
            for key, value in paths.items():
                if "{user}" in value:
                    paths[key] = value.replace("{user}", username)
            return paths
        elif self.os_type == "darwin":
            return PLATFORM_PATHS.get("darwin")

        return None

    def check_permissions(self) -> bool:
        """Check if the user has necessary permissions (root/sudo)."""
        if self.os_type == "windows":
            try:
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            return os.geteuid() == 0 if hasattr(os, "geteuid") else False

    def __str__(self) -> str:
        """String representation of system information."""
        info = self.get_platform_info()
        return (
            f"OS: {info['os_name']} ({info['os_type']})\n"
            f"Distribution: {info['distro']}\n"
            f"Desktop Environment: {info['desktop_env']}\n"
            f"GUI Capability: {info['has_gui']}\n"
            f"Termux: {info['is_termux']}\n"
            f"Tor Installed: {info['tor_installed']}\n"
            f"Nginx Installed: {info['nginx_installed']}\n"
            f"Tor Browser Installed: {info['tor_browser_installed']}"
        )


# Singleton instance
_detector_instance = None


def get_system_detector() -> SystemDetector:
    """Get or create the SystemDetector singleton instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SystemDetector()
    return _detector_instance
