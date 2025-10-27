"""
Onion Hoster - Configuration Manager
Author: Uzair Developer
GitHub: uzairdeveloper223

This module handles all configuration management including saving,
loading, and updating application settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class ConfigManager:
    """Manages application configuration and settings."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Custom configuration directory (optional)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            from .constants import CONFIG_DIR

            self.config_dir = Path(CONFIG_DIR)

        self.config_file = self.config_dir / "config.json"
        self.update_status_file = self.config_dir / "update_status.json"
        self.log_file = self.config_dir / "onion-hoster.log"

        self._ensure_config_dir()
        self._setup_logging()
        self.config = self._load_config()

    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Configuration directory: {self.config_dir}")
        except Exception as e:
            logging.error(f"Failed to create config directory: {e}")
            raise

    def _setup_logging(self):
        """Setup logging configuration."""
        from .constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL

        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        from .constants import VERSION, NGINX_DEFAULT_PORT

        return {
            "version": VERSION,
            "first_run": True,
            "last_updated": None,
            "site_directory": None,
            "nginx_port": NGINX_DEFAULT_PORT,
            "onion_address": None,
            "service_running": False,
            "auto_start": False,
            "theme": "dark",
            "accent_color": "#7D4698",
            "language": "en",
            "check_updates_on_start": True,
            "show_notifications": True,
            "log_level": "INFO",
            "hidden_service_dir": None,
            "nginx_config_name": "onion-site",
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "services": {
                "tor_enabled": False,
                "nginx_enabled": False,
                "tor_installed": False,
                "nginx_installed": False,
                "tor_browser_installed": False,
            },
            "platform": {"os_type": None, "distro": None, "desktop_env": None},
            "history": [],
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            logging.info("Config file not found, creating default configuration")
            return self._get_default_config()

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                logging.info("Configuration loaded successfully")
                return config
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse config file: {e}")
            logging.warning("Using default configuration")
            return self._get_default_config()
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return self._get_default_config()

    def save_config(self) -> bool:
        """
        Save current configuration to file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.config["last_modified"] = datetime.now().isoformat()

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)

            logging.info("Configuration saved successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
            save: Whether to save immediately

        Returns:
            bool: True if successful
        """
        keys = key.split(".")
        config = self.config

        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

        if save:
            return self.save_config()

        return True

    def delete(self, key: str, save: bool = True) -> bool:
        """
        Delete a configuration key.

        Args:
            key: Configuration key to delete
            save: Whether to save immediately

        Returns:
            bool: True if successful
        """
        keys = key.split(".")
        config = self.config

        try:
            for k in keys[:-1]:
                config = config[k]

            if keys[-1] in config:
                del config[keys[-1]]

                if save:
                    return self.save_config()
                return True

            return False
        except (KeyError, TypeError):
            return False

    def update_site_directory(self, directory: str) -> bool:
        """Update the site directory configuration."""
        return self.set("site_directory", directory)

    def update_onion_address(self, address: str) -> bool:
        """Update the onion address configuration."""
        return self.set("onion_address", address)

    def set_service_running(self, running: bool) -> bool:
        """Update the service running status."""
        return self.set("service_running", running)

    def set_service_installed(self, service: str, installed: bool) -> bool:
        """Update service installation status."""
        return self.set(f"services.{service}_installed", installed)

    def add_to_history(self, entry: Dict[str, Any]) -> bool:
        """
        Add an entry to the history.

        Args:
            entry: History entry dictionary

        Returns:
            bool: True if successful
        """
        history = self.get("history", [])
        entry["timestamp"] = datetime.now().isoformat()
        history.append(entry)

        # Keep only last 100 entries
        if len(history) > 100:
            history = history[-100:]

        return self.set("history", history)

    def clear_history(self) -> bool:
        """Clear the history."""
        return self.set("history", [])

    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return self.get("first_run", True)

    def set_first_run_complete(self) -> bool:
        """Mark first run as complete."""
        return self.set("first_run", False)

    def get_update_status(self) -> Dict[str, Any]:
        """
        Get update status from file.

        Returns:
            Dictionary with update status
        """
        if not self.update_status_file.exists():
            return {
                "needs_update": False,
                "latest_version": None,
                "current_version": None,
                "checked_at": None,
            }

        try:
            with open(self.update_status_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to read update status: {e}")
            return {
                "needs_update": False,
                "latest_version": None,
                "current_version": None,
                "checked_at": None,
            }

    def set_update_status(
        self,
        needs_update: bool,
        latest_version: str = None,
        current_version: str = None,
    ) -> bool:
        """
        Save update status to file.

        Args:
            needs_update: Whether an update is needed
            latest_version: Latest available version
            current_version: Current installed version

        Returns:
            bool: True if successful
        """
        try:
            status = {
                "needs_update": needs_update,
                "latest_version": latest_version,
                "current_version": current_version,
                "checked_at": datetime.now().isoformat(),
            }

            with open(self.update_status_file, "w") as f:
                json.dump(status, f, indent=4)

            logging.info(f"Update status saved: needs_update={needs_update}")
            return True
        except Exception as e:
            logging.error(f"Failed to save update status: {e}")
            return False

    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to a file.

        Args:
            export_path: Path to export the configuration

        Returns:
            bool: True if successful
        """
        try:
            with open(export_path, "w") as f:
                json.dump(self.config, f, indent=4)

            logging.info(f"Configuration exported to {export_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to export config: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a file.

        Args:
            import_path: Path to import the configuration from

        Returns:
            bool: True if successful
        """
        try:
            with open(import_path, "r") as f:
                imported_config = json.load(f)

            # Merge with default config to ensure all keys exist
            default_config = self._get_default_config()
            self.config = {**default_config, **imported_config}

            self.save_config()
            logging.info(f"Configuration imported from {import_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to import config: {e}")
            return False

    def reset_config(self) -> bool:
        """
        Reset configuration to defaults.

        Returns:
            bool: True if successful
        """
        try:
            self.config = self._get_default_config()
            self.save_config()
            logging.info("Configuration reset to defaults")
            return True
        except Exception as e:
            logging.error(f"Failed to reset config: {e}")
            return False

    def get_all_config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self.config.copy()

    def validate_config(self) -> bool:
        """
        Validate the configuration.

        Returns:
            bool: True if configuration is valid
        """
        required_keys = ["version", "nginx_port", "services", "platform"]

        for key in required_keys:
            if key not in self.config:
                logging.error(f"Missing required config key: {key}")
                return False

        # Validate nginx port
        nginx_port = self.get("nginx_port")
        if not isinstance(nginx_port, int) or nginx_port < 1024 or nginx_port > 65535:
            logging.error(f"Invalid nginx port: {nginx_port}")
            return False

        return True

    def update_platform_info(self, platform_info: Dict[str, Any]) -> bool:
        """
        Update platform information in config.

        Args:
            platform_info: Platform information dictionary

        Returns:
            bool: True if successful
        """
        self.set("platform.os_type", platform_info.get("os_type"), save=False)
        self.set("platform.distro", platform_info.get("distro"), save=False)
        self.set("platform.desktop_env", platform_info.get("desktop_env"), save=False)

        self.set(
            "services.tor_installed", platform_info.get("tor_installed"), save=False
        )
        self.set(
            "services.nginx_installed", platform_info.get("nginx_installed"), save=False
        )
        self.set(
            "services.tor_browser_installed",
            platform_info.get("tor_browser_installed"),
            save=False,
        )

        return self.save_config()

    def __repr__(self) -> str:
        """String representation of the config manager."""
        return f"ConfigManager(config_dir='{self.config_dir}')"


# Singleton instance
_config_manager_instance = None


def get_config_manager(config_dir: Optional[Path] = None) -> ConfigManager:
    """Get or create the ConfigManager singleton instance."""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager(config_dir)
    return _config_manager_instance
