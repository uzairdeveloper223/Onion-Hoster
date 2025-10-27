"""
Onion Hoster - Core Package
Author: Uzair Developer
GitHub: uzairdeveloper223

This package contains the core functionality for Onion Hoster including
system detection, configuration management, service management, and updates.
"""

from .constants import (
    VERSION,
    APP_NAME,
    AUTHOR,
    GITHUB_USERNAME,
    GITHUB_REPO,
    THEME_COLORS,
)

from .system_detector import SystemDetector, get_system_detector
from .config_manager import ConfigManager, get_config_manager
from .onion_service import OnionServiceManager
from .update_manager import UpdateManager, get_update_manager

__all__ = [
    # Version and metadata
    "VERSION",
    "APP_NAME",
    "AUTHOR",
    "GITHUB_USERNAME",
    "GITHUB_REPO",
    "THEME_COLORS",
    # Core classes
    "SystemDetector",
    "ConfigManager",
    "OnionServiceManager",
    "UpdateManager",
    # Singleton getters
    "get_system_detector",
    "get_config_manager",
    "get_update_manager",
]
