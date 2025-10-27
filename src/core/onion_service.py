"""
Onion Hoster - Onion Service Manager
Author: Uzair Developer
GitHub: uzairdeveloper223

This module manages Tor hidden services and Nginx configuration.
It handles service setup, starting, stopping, and monitoring.
"""

import os
import subprocess
import time
import logging
import getpass
import signal
import re
import threading
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Callable
import shutil

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class SiteFileHandler(FileSystemEventHandler):
    """Handler for file system events to sync site files."""

    def __init__(self, service_manager):
        self.service = service_manager

    def on_any_event(self, event):
        """Sync files on any change."""
        if not event.is_directory:
            self.service._sync_site_files()


class OnionServiceManager:
    """Manages Tor hidden service and Nginx configuration."""

    def __init__(self, config_manager, system_detector):
        """
        Initialize the onion service manager.

        Args:
            config_manager: ConfigManager instance
            system_detector: SystemDetector instance
        """
        self.config = config_manager
        self.system = system_detector
        self.platform_paths = system_detector.get_platform_paths()
        self.logger = logging.getLogger(__name__)
        self._sudo_password = None
        self.is_gui = False
        self._tor_process = None
        self._nginx_process = None
        self._bootstrap_progress = 0
        self._onion_address = None
        self._file_observer = None
        self._site_directory = None

    def set_sudo_password(self, password: str):
        """Set the sudo password for privileged commands."""
        self._sudo_password = password

    def _sync_site_files(self):
        """Sync site files from user directory to nginx root."""
        if not self._site_directory:
            return

        nginx_root = "/var/www/html"
        try:
            # Copy files with sudo
            cmd = f"sudo -S cp -r {self._site_directory}/* {nginx_root}/"
            result = self._run_privileged_command(cmd)
            if result.returncode == 0:
                self.logger.info("Site files synced successfully")
            else:
                self.logger.error(f"Failed to sync site files: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Error syncing site files: {e}")

    def _start_file_watcher(self):
        """Start file watcher for site directory."""
        if not WATCHDOG_AVAILABLE or not self._site_directory:
            return

        try:
            event_handler = SiteFileHandler(self)
            observer = Observer()
            observer.schedule(event_handler, self._site_directory, recursive=True)
            observer.start()
            self._file_observer = observer
            self.logger.info("File watcher started")
        except Exception as e:
            self.logger.error(f"Failed to start file watcher: {e}")

    def _stop_file_watcher(self):
        """Stop file watcher."""
        if self._file_observer:
            self._file_observer.stop()
            self._file_observer.join()
            self._file_observer = None
            self.logger.info("File watcher stopped")

    def _run_privileged_command(
        self, cmd: str, timeout: int = 300
    ) -> subprocess.CompletedProcess:
        """
        Run a command that may require sudo privileges.

        Args:
            cmd: The command to run
            timeout: Timeout in seconds

        Returns:
            CompletedProcess instance
        """
        if "sudo -S" in cmd and not self.system.check_permissions():
            if self._sudo_password is None:
                if self.is_gui:
                    # GUI should have prompted already, but if not, this will fail
                    raise Exception("Sudo password not set for GUI mode")
                else:
                    self._sudo_password = getpass.getpass("Enter sudo password: ")
            return subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                input=self._sudo_password + "\n",
            )
        else:
            return subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )

    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if required dependencies are installed.

        Returns:
            Dictionary with dependency status
        """
        return {
            "tor": self.system.is_tor_installed(),
            "nginx": self.system.is_nginx_installed(),
            "tor_browser": self.system.is_tor_browser_installed(),
            "xclip": self.system.is_xclip_installed(),
        }

    def install_tor(self) -> Tuple[bool, str]:
        """
        Install Tor on the system.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.system.is_tor_installed():
            return True, "Tor is already installed."

        install_cmd = self.system.get_install_command("tor")
        if not install_cmd:
            return False, "Installation command not available for your platform."

        self.logger.info(f"Installing Tor: {install_cmd}")

        try:
            result = self._run_privileged_command(install_cmd, timeout=300)

            if result.returncode == 0:
                self.logger.info("Tor installed successfully")
                self.config.set_service_installed("tor", True)
                return True, "Tor installed successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to install Tor: {error_msg}")
                return False, f"Failed to install Tor: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Installation timed out. Please try manually."
        except Exception as e:
            self.logger.error(f"Error installing Tor: {e}")
            return False, f"Error: {str(e)}"

    def install_nginx(self) -> Tuple[bool, str]:
        """
        Install Nginx on the system.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.system.is_nginx_installed():
            return True, "Nginx is already installed."

        install_cmd = self.system.get_install_command("nginx")
        if not install_cmd:
            return False, "Installation command not available for your platform."

        self.logger.info(f"Installing Nginx: {install_cmd}")

        try:
            result = self._run_privileged_command(install_cmd, timeout=300)

            if result.returncode == 0:
                self.logger.info("Nginx installed successfully")
                self.config.set_service_installed("nginx", True)
                return True, "Nginx installed successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to install Nginx: {error_msg}")
                return False, f"Failed to install Nginx: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Installation timed out. Please try manually."
        except Exception as e:
            self.logger.error(f"Error installing Nginx: {e}")
            return False, f"Error: {str(e)}"

    def install_tor_browser(self) -> Tuple[bool, str]:
        """
        Install Tor Browser on the system.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.system.is_tor_browser_installed():
            return True, "Tor Browser is already installed."

        install_cmd = self.system.get_install_command("tor_browser")
        if not install_cmd:
            return (
                False,
                "Tor Browser installation not automated for your platform. Please install manually.",
            )

        self.logger.info(f"Installing Tor Browser: {install_cmd}")

        try:
            result = self._run_privileged_command(install_cmd, timeout=600)

            if result.returncode == 0:
                self.logger.info("Tor Browser installed successfully")
                self.config.set_service_installed("tor_browser", True)
                return True, "Tor Browser installed successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to install Tor Browser: {error_msg}")
                return False, f"Failed to install Tor Browser: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Installation timed out. Please try manually."
        except Exception as e:
            self.logger.error(f"Error installing Tor Browser: {e}")
            return False, f"Error: {str(e)}"

    def install_xclip(self) -> Tuple[bool, str]:
        """
        Install xclip on the system.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.system.is_xclip_installed():
            return True, "xclip is already installed."

        install_cmd = self.system.get_install_command("xclip")
        if not install_cmd:
            return (
                False,
                "xclip installation not automated for your platform. Please install manually.",
            )

        self.logger.info(f"Installing xclip: {install_cmd}")

        try:
            result = self._run_privileged_command(install_cmd, timeout=300)

            if result.returncode == 0:
                self.logger.info("xclip installed successfully")
                self.config.set_service_installed("xclip", True)
                return True, "xclip installed successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to install xclip: {error_msg}")
                return False, f"Failed to install xclip: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Installation timed out. Please try manually."
        except Exception as e:
            self.logger.error(f"Error installing xclip: {e}")
            return False, f"Error: {str(e)}"

    def validate_site_directory(self, directory: str) -> Tuple[bool, str]:
        """
        Validate the site directory.

        Args:
            directory: Path to the site directory

        Returns:
            Tuple of (valid: bool, message: str)
        """
        from .constants import VALID_INDEX_FILES

        dir_path = Path(directory)

        if not dir_path.exists():
            return False, "Directory does not exist."

        if not dir_path.is_dir():
            return False, "Path is not a directory."

        # Check for index file
        has_index = any(
            (dir_path / index_file).exists() for index_file in VALID_INDEX_FILES
        )

        if not has_index:
            return (
                False,
                f"No index file found. Please ensure one of these files exists: {', '.join(VALID_INDEX_FILES)}",
            )

        return True, "Directory is valid."

    def create_nginx_config(
        self, site_directory: str, port: int = None
    ) -> Tuple[bool, str]:
        """
        Create Nginx configuration for the onion site.

        Args:
            site_directory: Path to the site directory
            port: Nginx port (default from config)

        Returns:
            Tuple of (success: bool, message: str)
        """
        from .constants import NGINX_CONFIG_TEMPLATE

        if port is None:
            port = self.config.get("nginx_port", 8080)

        if not self.platform_paths:
            return False, "Platform paths not available."

        # Validate site directory
        valid, msg = self.validate_site_directory(site_directory)
        if not valid:
            return False, msg

        try:
            # Copy site files to nginx default directory
            nginx_root = "/var/www/html"

            # Create directory if not exists
            cmd = f"sudo -S mkdir -p {nginx_root}"
            result = self._run_privileged_command(cmd)
            if result.returncode != 0:
                return False, f"Failed to create nginx root directory: {result.stderr}"

            # Copy files
            cmd = f"sudo -S cp -r {site_directory}/* {nginx_root}/"
            result = self._run_privileged_command(cmd)
            if result.returncode != 0:
                return False, f"Failed to copy site files: {result.stderr}"

            # Set proper ownership (nginx user is www-data on debian/ubuntu)
            nginx_user = "www-data"
            cmd = f"sudo -S chown -R {nginx_user}:{nginx_user} {nginx_root}"
            result = self._run_privileged_command(cmd)
            if result.returncode != 0:
                self.logger.warning(f"Failed to set ownership: {result.stderr}")

            # Store site directory for file watching
            self._site_directory = site_directory

            # Start file watcher if available
            self._start_file_watcher()

            # Prepare nginx config
            error_log = self.config.log_file.parent / "nginx-error.log"
            nginx_config = NGINX_CONFIG_TEMPLATE.format(
                port=port, root_dir=nginx_root, error_log=error_log
            )

            config_name = self.config.get("nginx_config_name", "onion-site")

            # For Termux or non-systemd systems
            if self.system.is_termux:
                nginx_conf_dir = (
                    Path(self.platform_paths.get("nginx_config")).parent
                    / "sites-available"
                )
                nginx_conf_dir.mkdir(parents=True, exist_ok=True)
                config_path = nginx_conf_dir / config_name
            else:
                sites_available = self.platform_paths.get(
                    "nginx_sites_available", "/etc/nginx/sites-available"
                )
                config_path = Path(sites_available) / config_name

            # Write config file using privileged command
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".conf"
            ) as f:
                f.write(nginx_config)
                temp_file = f.name

            # Move temp file to config location with sudo
            cmd = f"mv {temp_file} {config_path}"
            result = self._run_privileged_command(f"sudo -S {cmd}")
            if result.returncode != 0:
                os.unlink(temp_file)
                return False, f"Failed to write nginx config: {result.stderr}"

            self.logger.info(f"Nginx config created at {config_path}")

            # Enable site (create symlink for Debian/Arch)
            if not self.system.is_termux and self.system.distro in ["debian", "arch"]:
                sites_enabled = self.platform_paths.get(
                    "nginx_sites_enabled", "/etc/nginx/sites-enabled"
                )
            enabled_path = Path(sites_enabled) / config_name

            # Remove existing symlink if it exists
            if enabled_path.exists():
                cmd = f"rm {enabled_path}"
            self._run_privileged_command(f"sudo -S {cmd}")

            # Create symlink
            cmd = f"ln -s {config_path} {enabled_path}"
            result = self._run_privileged_command(f"sudo -S {cmd}")
            if result.returncode != 0:
                return False, f"Failed to enable nginx site: {result.stderr}"
            self.logger.info(f"Nginx site enabled at {enabled_path}")

            # Disable default site if it exists
            default_enabled = Path(sites_enabled) / "default"
            if default_enabled.exists():
                cmd = f"rm {default_enabled}"
                self._run_privileged_command(f"sudo -S {cmd}")
                self.logger.info("Disabled default nginx site")

            # Test nginx config
            test_cmd = self.system.get_service_command("nginx", "test")
            if test_cmd:
                result = self._run_privileged_command(test_cmd)
                if result.returncode != 0:
                    return False, f"Nginx config test failed: {result.stderr}"

            self.config.update_site_directory(site_directory)
            self.config.set("nginx_port", port)

            return True, "Nginx configuration created successfully!"

        except PermissionError:
            return (
                False,
                "Permission denied. Please run with sudo/administrator privileges.",
            )
        except Exception as e:
            self.logger.error(f"Error creating nginx config: {e}")
            return False, f"Error: {str(e)}"

    def configure_tor_hidden_service(self, nginx_port: int = None) -> Tuple[bool, str]:
        """
        Configure Tor hidden service.

        Args:
            nginx_port: Nginx port to forward to

        Returns:
            Tuple of (success: bool, message: str)
        """
        from .constants import TOR_CONFIG_TEMPLATE

        if nginx_port is None:
            nginx_port = self.config.get("nginx_port", 8080)

        if not self.platform_paths:
            return False, "Platform paths not available."

        try:
            tor_config_path = Path(self.platform_paths.get("tor_config"))

            # Determine hidden service directory
            if self.system.is_termux:
                hidden_service_dir = Path.home() / ".tor" / "hidden_service"
            elif self.system.os_type == "windows":
                # Windows uses different path structure
                hidden_service_dir = (
                    Path(os.environ.get("APPDATA", "")) / "tor" / "hidden_service"
                )
            else:
                tor_service_dir = self.platform_paths.get(
                    "tor_service_dir", "/var/lib/tor"
                )
                hidden_service_dir = Path(tor_service_dir) / "hidden_service"

            self.config.set("hidden_service_dir", str(hidden_service_dir))

            # Create hidden service directory if it doesn't exist
            if self.system.os_type == "windows":
                hidden_service_dir.mkdir(parents=True, exist_ok=True)
            elif self.system.is_termux:
                # Termux doesn't need sudo
                os.makedirs(hidden_service_dir, mode=0o700, exist_ok=True)
            else:
                # Linux/macOS - need sudo
                cmd = f"mkdir -p {hidden_service_dir}"
                result = self._run_privileged_command(f"sudo -S {cmd}")
                if result.returncode != 0:
                    return (
                        False,
                        f"Failed to create hidden service directory: {result.stderr}",
                    )

                # Set ownership to tor user (varies by distro)
                tor_user = self._get_tor_user()
                tor_group = self._get_tor_group()

                cmd = f"chown -R {tor_user}:{tor_group} {hidden_service_dir}"
                result = self._run_privileged_command(f"sudo -S {cmd}")
                if result.returncode != 0:
                    self.logger.warning(f"Failed to set ownership: {result.stderr}")

                # Set permissions to 700 (required by Tor)
                cmd = f"chmod 700 {hidden_service_dir}"
                result = self._run_privileged_command(f"sudo -S {cmd}")
                if result.returncode != 0:
                    return (
                        False,
                        f"Failed to set permissions of hidden service directory: {result.stderr}",
                    )

            # Read existing tor config
            try:
                if tor_config_path.exists():
                    with open(tor_config_path, "r") as f:
                        existing_config = f.read()
                else:
                    existing_config = ""
            except PermissionError:
                # Try reading with sudo
                if self.system.os_type != "windows":
                    result = self._run_privileged_command(
                        f"sudo -S cat {tor_config_path}"
                    )
                    existing_config = result.stdout if result.returncode == 0 else ""
                else:
                    existing_config = ""

            # Check if hidden service already configured
            if (
                "HiddenServiceDir" in existing_config
                and str(hidden_service_dir) in existing_config
            ):
                self.logger.info("Hidden service already configured")
            else:
                # Add hidden service configuration
                hidden_service_config = TOR_CONFIG_TEMPLATE.format(
                    hidden_service_dir=hidden_service_dir, nginx_port=nginx_port
                )

                # Append to tor config using privileged command
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".tor"
                ) as f:
                    f.write(hidden_service_config)
                    temp_file = f.name

                # Append temp file to tor config
                if self.system.os_type == "windows" or self.system.is_termux:
                    # Direct write for Windows/Termux
                    with open(tor_config_path, "a") as f:
                        f.write(hidden_service_config)
                else:
                    cmd = f"cat {temp_file} >> {tor_config_path}"
                    result = self._run_privileged_command(f"sudo -S {cmd}")
                    if result.returncode != 0:
                        os.unlink(temp_file)
                        return False, f"Failed to update tor config: {result.stderr}"

                os.unlink(temp_file)
                self.logger.info(
                    f"Tor hidden service configured at {hidden_service_dir}"
                )

            return True, "Tor hidden service configured successfully!"

        except PermissionError:
            return (
                False,
                "Permission denied. Please run with sudo/administrator privileges.",
            )
        except Exception as e:
            self.logger.error(f"Error configuring Tor hidden service: {e}")
            return False, f"Error: {str(e)}"

    def _get_tor_user(self) -> str:
        """Get the appropriate tor user for the system."""
        if self.system.distro == "debian":
            return "debian-tor"
        elif self.system.os_type == "darwin":
            return os.environ.get("USER", "tor")
        else:
            return "tor"

    def _get_tor_group(self) -> str:
        """Get the appropriate tor group for the system."""
        if self.system.distro == "debian":
            return "debian-tor"
        elif self.system.os_type == "darwin":
            return "staff"
        else:
            return "tor"

    def start_nginx(self) -> Tuple[bool, str]:
        """
        Start Nginx service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        start_cmd = self.system.get_service_command("nginx", "start")
        if not start_cmd:
            return False, "Start command not available for your platform."

        try:
            result = self._run_privileged_command(start_cmd)

            if result.returncode == 0:
                self.logger.info("Nginx started successfully")
                return True, "Nginx started successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to start Nginx: {error_msg}")
                return False, f"Failed to start Nginx: {error_msg}"

        except Exception as e:
            self.logger.error(f"Error starting Nginx: {e}")
            return False, f"Error: {str(e)}"

    def stop_nginx(self) -> Tuple[bool, str]:
        """
        Stop Nginx service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        stop_cmd = self.system.get_service_command("nginx", "stop")
        if not stop_cmd:
            return False, "Stop command not available for your platform."

        try:
            result = self._run_privileged_command(stop_cmd)

            if result.returncode == 0:
                self.logger.info("Nginx stopped successfully")
                return True, "Nginx stopped successfully!"
            else:
                # Sometimes stopping already stopped service returns non-zero
                self.logger.info("Nginx stop command executed")
                return True, "Nginx stopped."

        except Exception as e:
            self.logger.error(f"Error stopping Nginx: {e}")
            return False, f"Error: {str(e)}"

    def restart_nginx(self) -> Tuple[bool, str]:
        """
        Restart Nginx service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        restart_cmd = self.system.get_service_command("nginx", "restart")
        if not restart_cmd:
            return False, "Restart command not available for your platform."

        try:
            result = self._run_privileged_command(restart_cmd)

            if result.returncode == 0:
                self.logger.info("Nginx restarted successfully")
                return True, "Nginx restarted successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to restart Nginx: {error_msg}")
                return False, f"Failed to restart Nginx: {error_msg}"

        except Exception as e:
            self.logger.error(f"Error restarting Nginx: {e}")
            return False, f"Error: {str(e)}"

    def start_tor_manual(
        self, progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Start Tor manually with bootstrap progress monitoring.
        This method runs Tor in the foreground and monitors its bootstrap progress.

        Args:
            progress_callback: Optional callback function(progress: int, message: str)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._tor_process and self._tor_process.poll() is None:
            return True, "Tor is already running."

        try:
            if not self.platform_paths:
                return False, "Platform paths not available."

            tor_config_path = self.platform_paths.get("tor_config")
            hidden_service_dir = self.config.get("hidden_service_dir")

            if not hidden_service_dir:
                return (
                    False,
                    "Hidden service directory not configured. Please configure first.",
                )

            # Build the Tor command based on platform
            if self.system.is_termux:
                tor_cmd = ["tor", "-f", tor_config_path]
            elif self.system.os_type == "windows":
                # Windows: Use Tor Expert Bundle
                tor_exe = self.platform_paths.get("tor_exe", "tor.exe")
                tor_cmd = [tor_exe, "-f", tor_config_path]
            elif self.system.os_type == "darwin":
                # macOS
                tor_cmd = ["tor", "-f", tor_config_path]
            else:
                # Linux: Run as tor user
                tor_user = self._get_tor_user()
                tor_cmd = ["sudo", "-u", tor_user, "tor", "-f", tor_config_path]

            self.logger.info(f"Starting Tor with command: {' '.join(tor_cmd)}")

            # Validate Tor config before starting
            if self.system.os_type == "linux" and not self.system.is_termux:
                tor_user = self._get_tor_user()
                verify_cmd = [
                    "sudo",
                    "-u",
                    tor_user,
                    "tor",
                    "--verify-config",
                    "-f",
                    tor_config_path,
                ]
                self.logger.info(f"Validating Tor config: {' '.join(verify_cmd)}")
                try:
                    verify_result = subprocess.run(
                        verify_cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        input=(
                            self._sudo_password + "\n" if self._sudo_password else None
                        ),
                    )
                    if verify_result.returncode != 0:
                        error_msg = verify_result.stderr or verify_result.stdout
                        self.logger.error(f"Tor config validation failed: {error_msg}")
                        return False, f"Tor configuration is invalid: {error_msg}"
                except subprocess.TimeoutExpired:
                    return False, "Tor config validation timed out."
                except Exception as e:
                    self.logger.warning(f"Could not validate Tor config: {e}")

            # Start Tor process
            if (
                self.system.os_type == "windows"
                or self.system.is_termux
                or self.system.os_type == "darwin"
            ):
                self._tor_process = subprocess.Popen(
                    tor_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
            else:
                # Linux with sudo
                self._tor_process = subprocess.Popen(
                    tor_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )
                # Send sudo password if needed
                if self._sudo_password:
                    try:
                        self._tor_process.stdin.write(self._sudo_password + "\n")
                        self._tor_process.stdin.flush()
                    except:
                        pass

            # Monitor bootstrap progress in a separate thread
            self._bootstrap_progress = 0
            bootstrap_complete = threading.Event()
            bootstrap_error = []

            def monitor_bootstrap():
                try:
                    for line in self._tor_process.stdout:
                        line = line.strip()
                        self.logger.debug(f"Tor output: {line}")

                        # Extract bootstrap percentage
                        bootstrap_match = re.search(r"Bootstrapped (\d+)%", line)
                        if bootstrap_match:
                            progress = int(bootstrap_match.group(1))
                            self._bootstrap_progress = progress

                            # Extract status message
                            status_match = re.search(
                                r"Bootstrapped \d+%.*?: (.+)$", line
                            )
                            status_msg = (
                                status_match.group(1)
                                if status_match
                                else "Connecting..."
                            )

                            if progress_callback:
                                progress_callback(progress, status_msg)

                            self.logger.info(
                                f"Bootstrap progress: {progress}% - {status_msg}"
                            )

                            if progress == 100:
                                bootstrap_complete.set()
                                break

                        # Check for errors
                        if "err" in line.lower() or "warn" in line.lower():
                            if "error" in line.lower():
                                bootstrap_error.append(line)

                except Exception as e:
                    self.logger.error(f"Error monitoring bootstrap: {e}")
                    bootstrap_error.append(str(e))

            monitor_thread = threading.Thread(target=monitor_bootstrap, daemon=True)
            monitor_thread.start()

            # Wait for bootstrap to complete (with timeout)
            if bootstrap_complete.wait(timeout=120):
                # Bootstrap complete, wait a moment for files to be written
                time.sleep(2)

                # Try to read the onion address
                self._onion_address = self._read_onion_address()

                if self._onion_address:
                    self.logger.info(
                        f"Tor service started! Address: {self._onion_address}"
                    )
                    return (
                        True,
                        f"Tor service started successfully! Your .onion address: {self._onion_address}",
                    )
                else:
                    return (
                        True,
                        "Tor service started! Address will be available shortly.",
                    )
            else:
                # Timeout
                if bootstrap_error:
                    error_msg = " | ".join(bootstrap_error[:3])
                    return False, f"Tor bootstrap timed out. Errors: {error_msg}"
                else:
                    return (
                        False,
                        f"Tor bootstrap timed out at {self._bootstrap_progress}%. Please check your network connection.",
                    )

        except FileNotFoundError as e:
            return False, f"Tor executable not found: {e}"
        except Exception as e:
            self.logger.error(f"Error starting Tor: {e}")
            return False, f"Error: {str(e)}"

    def _read_onion_address(self) -> Optional[str]:
        """Read the .onion address from the hidden service directory."""
        try:
            hidden_service_dir = self.config.get("hidden_service_dir")
            if not hidden_service_dir:
                return None

            hostname_file = Path(hidden_service_dir) / "hostname"

            if self.system.os_type == "linux" and not self.system.is_termux:
                # On Linux, always use sudo since file is owned by tor user
                result = self._run_privileged_command(f"sudo -S cat {hostname_file}")
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    self.logger.error(f"Failed to read hostname with sudo: {result.stderr}")
            else:
                # Try direct read for other systems
                if hostname_file.exists():
                    try:
                        with open(hostname_file, "r") as f:
                            return f.read().strip()
                    except Exception as e:
                        self.logger.error(f"Error reading hostname directly: {e}")

            return None
        except Exception as e:
            self.logger.error(f"Error reading onion address: {e}")
            return None

    def start_tor(self) -> Tuple[bool, str]:
        """
        Start Tor service using systemctl (legacy method).

        Returns:
            Tuple of (success: bool, message: str)
        """
        start_cmd = self.system.get_service_command("tor", "start")
        if not start_cmd:
            return False, "Start command not available for your platform."

        try:
            result = self._run_privileged_command(start_cmd)

            if result.returncode == 0:
                self.logger.info("Tor started successfully")
                return True, "Tor started successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to start Tor: {error_msg}")
                return False, f"Failed to start Tor: {error_msg}"

        except Exception as e:
            self.logger.error(f"Error starting Tor: {e}")
            return False, f"Error: {str(e)}"

    def stop_tor(self) -> Tuple[bool, str]:
        """
        Stop Tor service (both manual and systemctl).

        Returns:
            Tuple of (success: bool, message: str)
        """
        stopped = False

        # First, try to stop manual Tor process if running
        if self._tor_process and self._tor_process.poll() is None:
            try:
                self.logger.info("Stopping manual Tor process...")
                self._tor_process.terminate()
                self._tor_process.wait(timeout=10)
                stopped = True
                self.logger.info("Manual Tor process stopped")
            except subprocess.TimeoutExpired:
                self.logger.warning("Tor didn't stop gracefully, killing...")
                self._tor_process.kill()
                stopped = True
            except Exception as e:
                self.logger.error(f"Error stopping manual Tor: {e}")
            finally:
                self._tor_process = None
                self._bootstrap_progress = 0

        # Also try systemctl stop (in case it's running as service)
        stop_cmd = self.system.get_service_command("tor", "stop")
        if stop_cmd:
            try:
                result = self._run_privileged_command(stop_cmd)
                if result.returncode == 0:
                    stopped = True
                    self.logger.info("Tor service stopped via systemctl")
            except Exception as e:
                self.logger.debug(f"Systemctl stop failed (may not be running): {e}")

        if stopped:
            return True, "Tor stopped successfully!"
        else:
            return True, "Tor was not running or already stopped."

    def restart_tor(self) -> Tuple[bool, str]:
        """
        Restart Tor service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        restart_cmd = self.system.get_service_command("tor", "restart")
        if not restart_cmd:
            return False, "Restart command not available for your platform."

        try:
            result = self._run_privileged_command(restart_cmd)

            if result.returncode == 0:
                self.logger.info("Tor restarted successfully")
                return True, "Tor restarted successfully!"
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to restart Tor: {error_msg}")
                return False, f"Failed to restart Tor: {error_msg}"

        except Exception as e:
            self.logger.error(f"Error restarting Tor: {e}")
            return False, f"Error: {str(e)}"

    def get_onion_address(self, wait_time: int = 10) -> Optional[str]:
        """
        Get the .onion address for the hidden service.

        Args:
            wait_time: Time to wait for address generation (seconds)

        Returns:
            The .onion address or None if not found
        """
        # First check if we already have it from manual startup
        if self._onion_address:
            return self._onion_address

        # Try reading from file
        onion_address = self._read_onion_address()
        if onion_address:
            self._onion_address = onion_address
            self.config.update_onion_address(onion_address)
            return onion_address

        hidden_service_dir = self.config.get("hidden_service_dir")
        if not hidden_service_dir:
            self.logger.error("Hidden service directory not configured")
            return None

        hostname_file = Path(hidden_service_dir) / "hostname"

        # Wait for hostname file to be created
        for _ in range(wait_time):
            # Check if file exists using privileged command
            if self.system.os_type == "windows" or self.system.is_termux:
                if hostname_file.exists():
                    try:
                        with open(hostname_file, "r") as f:
                            onion_address = f.read().strip()
                            self.logger.info(f"Onion address: {onion_address}")
                            self._onion_address = onion_address
                            self.config.update_onion_address(onion_address)
                            return onion_address
                    except:
                        pass
            else:
                check_cmd = f"test -f {hostname_file}"
                result = self._run_privileged_command(f"sudo -S {check_cmd}")
                if result.returncode == 0:
                    # File exists, read it
                    read_cmd = f"cat {hostname_file}"
                    result = self._run_privileged_command(f"sudo -S {read_cmd}")
                    if result.returncode == 0:
                        onion_address = result.stdout.strip()
                        self.logger.info(f"Onion address: {onion_address}")
                        self._onion_address = onion_address
                        self.config.update_onion_address(onion_address)
                        return onion_address
                    else:
                        self.logger.error(
                            f"Error reading onion address: {result.stderr}"
                        )

            time.sleep(1)

        self.logger.warning("Onion address not generated yet")
        return None

    def start_service(
        self,
        site_directory: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Start the complete onion service with manual Tor startup and bootstrap monitoring.

        Args:
            site_directory: Path to the site directory
            progress_callback: Optional callback function(progress: int, message: str) for bootstrap updates

        Returns:
            Tuple of (success: bool, message: str, onion_address: Optional[str])
        """
        # Validate directory
        valid, msg = self.validate_site_directory(site_directory)
        if not valid:
            return False, msg, None

        # Create nginx config
        success, msg = self.create_nginx_config(site_directory)
        if not success:
            return False, msg, None

        # Configure tor hidden service
        success, msg = self.configure_tor_hidden_service()
        if not success:
            return False, msg, None

        # Start nginx
        success, msg = self.start_nginx()
        if not success:
            return False, f"Failed to start Nginx: {msg}", None

        # Start tor with manual startup and bootstrap monitoring
        self.logger.info("Starting Tor with bootstrap monitoring...")
        success, msg = self.start_tor_manual(progress_callback=progress_callback)
        if not success:
            return False, f"Failed to start Tor: {msg}", None

        # Get onion address (should be already read by start_tor_manual)
        onion_address = self._onion_address
        if not onion_address:
            # Fallback: try reading again
            onion_address = self._read_onion_address()

        if not onion_address:
            return (
                False,
                "Service started but onion address not available yet. Check back in a moment.",
                None,
            )

        self.config.set_service_running(True)
        self.config.update_onion_address(onion_address)
        self.config.add_to_history(
            {
                "action": "service_started",
                "site_directory": site_directory,
                "onion_address": onion_address,
            }
        )

        return True, "Onion service started successfully!", onion_address

    def stop_service(self) -> Tuple[bool, str]:
        """
        Stop the onion service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        errors = []

        # Stop nginx
        success, msg = self.stop_nginx()
        if not success:
            errors.append(f"Nginx: {msg}")

        # Stop tor
        success, msg = self.stop_tor()
        if not success:
            errors.append(f"Tor: {msg}")

        # Stop file watcher
        self._stop_file_watcher()

        self.config.set_service_running(False)
        self.config.add_to_history({"action": "service_stopped"})

        if errors:
            return False, "Errors occurred: " + "; ".join(errors)

        return True, "Onion service stopped successfully!"

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of services.

        Returns:
            Dictionary with service status information
        """
        # Check if manual Tor process is running
        tor_running = False
        if self._tor_process and self._tor_process.poll() is None:
            tor_running = True

        return {
            "service_running": self.config.get("service_running", False),
            "tor_running": tor_running,
            "bootstrap_progress": self._bootstrap_progress,
            "onion_address": self._onion_address or self.config.get("onion_address"),
            "site_directory": self.config.get("site_directory"),
            "nginx_port": self.config.get("nginx_port"),
            "tor_installed": self.system.is_tor_installed(),
            "nginx_installed": self.system.is_nginx_installed(),
            "tor_browser_installed": self.system.is_tor_browser_installed(),
        }

    def open_in_tor_browser(self, onion_address: str = None) -> Tuple[bool, str]:
        """
        Open the onion address in Tor Browser.

        Args:
            onion_address: The .onion address to open (uses saved if not provided)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not onion_address:
            onion_address = self.config.get("onion_address")

        if not onion_address:
            return False, "No onion address available."

        if not self.system.is_tor_browser_installed():
            return False, "Tor Browser is not installed."

        tor_browser_path = self.system.get_tor_browser_path()
        if not tor_browser_path:
            return False, "Could not find Tor Browser executable."

        try:
            url = f"http://{onion_address}"

            if self.system.os_type == "windows":
                subprocess.Popen([tor_browser_path, url])
            elif self.system.os_type == "darwin":
                subprocess.Popen(["open", "-a", tor_browser_path, url])
            else:  # Linux
                subprocess.Popen([tor_browser_path, url])

            self.logger.info(f"Opened {url} in Tor Browser")
            return True, "Opened in Tor Browser!"

        except Exception as e:
            self.logger.error(f"Error opening Tor Browser: {e}")
            return False, f"Error: {str(e)}"
