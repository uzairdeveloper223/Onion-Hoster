"""
Onion Hoster - Update Manager
Author: Uzair Developer
GitHub: uzairdeveloper223

This module handles checking for updates, downloading new versions,
and managing the update process.
"""

import os
import json
import shutil
import subprocess
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from packaging import version


class UpdateManager:
    """Manages application updates from GitHub."""

    def __init__(self, config_manager):
        """
        Initialize the update manager.

        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)

        from .constants import (
            VERSION,
            GITHUB_USERNAME,
            GITHUB_REPO,
            UPDATE_CHECK_URL,
            APP_ROOT,
        )

        self.current_version = VERSION
        self.github_username = GITHUB_USERNAME
        self.github_repo = GITHUB_REPO
        self.update_check_url = UPDATE_CHECK_URL
        self.app_root = Path(APP_ROOT)

    def check_for_updates(
        self, timeout: int = 10
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Check if a new update is available.

        Args:
            timeout: Request timeout in seconds

        Returns:
            Tuple of (update_available: bool, latest_version: str, update_info: dict)
        """
        try:
            self.logger.info("Checking for updates...")

            # Fetch version information from GitHub
            response = requests.get(self.update_check_url, timeout=timeout)
            response.raise_for_status()

            update_info = response.json()
            latest_version = update_info.get("version")

            if not latest_version:
                self.logger.error("Could not parse version from update info")
                return False, None, None

            # Compare versions
            if version.parse(latest_version) > version.parse(self.current_version):
                self.logger.info(
                    f"Update available: {latest_version} (current: {self.current_version})"
                )

                # Save update status
                self.config.set_update_status(
                    needs_update=True,
                    latest_version=latest_version,
                    current_version=self.current_version,
                )

                return True, latest_version, update_info
            else:
                self.logger.info(f"Already on latest version: {self.current_version}")

                # Update status
                self.config.set_update_status(
                    needs_update=False,
                    latest_version=latest_version,
                    current_version=self.current_version,
                )

                return False, latest_version, update_info

        except requests.RequestException as e:
            self.logger.error(f"Failed to check for updates: {e}")
            return False, None, None
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return False, None, None

    def get_update_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed update information.

        Returns:
            Dictionary with update information or None
        """
        try:
            response = requests.get(self.update_check_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get update info: {e}")
            return None

    def download_update(self, destination: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Download the latest version from GitHub.

        Args:
            destination: Destination directory for download

        Returns:
            Tuple of (success: bool, message: str)
        """
        if destination is None:
            destination = self.app_root.parent / f"{self.github_repo}-update"

        destination = Path(destination)

        try:
            # Check if git is available
            if not shutil.which("git"):
                return False, "Git is not installed. Please install git to update."

            # Remove existing update directory if it exists
            if destination.exists():
                shutil.rmtree(destination)

            # Clone the repository
            repo_url = (
                f"https://github.com/{self.github_username}/{self.github_repo}.git"
            )
            self.logger.info(f"Cloning repository from {repo_url}")

            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(destination)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error occurred"
                self.logger.error(f"Failed to clone repository: {error_msg}")
                return False, f"Failed to download update: {error_msg}"

            self.logger.info(f"Update downloaded to {destination}")

            # Mark that update needs to be applied
            update_status = self.config.get_update_status()
            update_status["update_downloaded"] = True
            update_status["update_path"] = str(destination)

            with open(self.config.update_status_file, "w") as f:
                json.dump(update_status, f, indent=4)

            return True, f"Update downloaded to {destination}"

        except subprocess.TimeoutExpired:
            return False, "Download timed out. Please check your internet connection."
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return False, f"Error: {str(e)}"

    def apply_update(self, update_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Apply the downloaded update.

        Args:
            update_path: Path to the downloaded update

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get update path from status if not provided
            if update_path is None:
                update_status = self.config.get_update_status()
                update_path = update_status.get("update_path")

                if not update_path:
                    return (
                        False,
                        "No update path found. Please download the update first.",
                    )

            update_path = Path(update_path)

            if not update_path.exists():
                return False, f"Update path does not exist: {update_path}"

            self.logger.info(f"Applying update from {update_path}")

            # Backup current installation
            backup_dir = self.app_root.parent / f"{self.github_repo}-backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            self.logger.info(f"Creating backup at {backup_dir}")
            shutil.copytree(self.app_root, backup_dir)

            # Copy new files (excluding .git and config directories)
            src_dir = update_path / "src"
            assets_dir = update_path / "assets"
            config_version_file = update_path / "config" / "version.json"

            # Update source files
            if src_dir.exists():
                dest_src = self.app_root / "src"
                if dest_src.exists():
                    shutil.rmtree(dest_src)
                shutil.copytree(src_dir, dest_src)
                self.logger.info("Source files updated")

            # Update assets
            if assets_dir.exists():
                dest_assets = self.app_root / "assets"
                if dest_assets.exists():
                    shutil.rmtree(dest_assets)
                shutil.copytree(assets_dir, dest_assets)
                self.logger.info("Assets updated")

            # Update version.json
            if config_version_file.exists():
                dest_version = self.app_root / "config" / "version.json"
                shutil.copy2(config_version_file, dest_version)
                self.logger.info("Version file updated")

            # Copy main executables
            for script in ["onion-host", "onion-host.py"]:
                src_script = update_path / script
                if src_script.exists():
                    dest_script = self.app_root / script
                    shutil.copy2(src_script, dest_script)
                    # Make executable on Unix systems
                    if os.name != "nt":
                        os.chmod(dest_script, 0o755)
                    self.logger.info(f"Updated {script}")

            # Copy requirements.txt if exists
            requirements = update_path / "requirements.txt"
            if requirements.exists():
                dest_req = self.app_root / "requirements.txt"
                shutil.copy2(requirements, dest_req)
                self.logger.info("Requirements updated")

            # Update the config with new version
            with open(config_version_file, "r") as f:
                version_info = json.load(f)
                new_version = version_info.get("version")

            self.config.set("version", new_version, save=False)
            self.config.set("last_updated", version_info.get("release_date"))

            # Clear update status
            self.config.set_update_status(
                needs_update=False,
                latest_version=new_version,
                current_version=new_version,
            )

            # Clean up downloaded update
            if update_path.exists():
                shutil.rmtree(update_path)

            self.logger.info(f"Update applied successfully! New version: {new_version}")

            return (
                True,
                f"Update applied successfully! Please restart the application. New version: {new_version}",
            )

        except Exception as e:
            self.logger.error(f"Error applying update: {e}")

            # Try to restore backup
            backup_dir = self.app_root.parent / f"{self.github_repo}-backup"
            if backup_dir.exists():
                try:
                    self.logger.info("Restoring from backup...")
                    if self.app_root.exists():
                        shutil.rmtree(self.app_root)
                    shutil.copytree(backup_dir, self.app_root)
                    self.logger.info("Backup restored successfully")
                    return False, f"Update failed: {str(e)}. Restored from backup."
                except Exception as restore_error:
                    self.logger.error(f"Failed to restore backup: {restore_error}")
                    return (
                        False,
                        f"Update failed and backup restoration failed: {str(e)}",
                    )

            return False, f"Error applying update: {str(e)}"

    def rollback_update(self) -> Tuple[bool, str]:
        """
        Rollback to the backup version.

        Returns:
            Tuple of (success: bool, message: str)
        """
        backup_dir = self.app_root.parent / f"{self.github_repo}-backup"

        if not backup_dir.exists():
            return False, "No backup found to rollback to."

        try:
            self.logger.info("Rolling back to previous version...")

            # Remove current installation
            if self.app_root.exists():
                shutil.rmtree(self.app_root)

            # Restore from backup
            shutil.copytree(backup_dir, self.app_root)

            self.logger.info("Rollback completed successfully")
            return (
                True,
                "Rollback completed successfully! Please restart the application.",
            )

        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False, f"Error during rollback: {str(e)}"

    def cleanup_update_files(self) -> bool:
        """
        Clean up temporary update files and backups.

        Returns:
            bool: True if successful
        """
        try:
            # Remove backup directory
            backup_dir = self.app_root.parent / f"{self.github_repo}-backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                self.logger.info("Backup directory cleaned up")

            # Remove update directory
            update_status = self.config.get_update_status()
            update_path = update_status.get("update_path")
            if update_path and Path(update_path).exists():
                shutil.rmtree(update_path)
                self.logger.info("Update directory cleaned up")

            return True

        except Exception as e:
            self.logger.error(f"Error cleaning up update files: {e}")
            return False

    def get_changelog(self, version_info: Optional[Dict] = None) -> list:
        """
        Get the changelog for a version.

        Args:
            version_info: Version information dictionary

        Returns:
            List of changes
        """
        if version_info is None:
            version_info = self.get_update_info()

        if not version_info:
            return []

        changelog = version_info.get("changelog", [])
        if not changelog:
            return []

        # Return the latest changelog entry
        if isinstance(changelog, list) and len(changelog) > 0:
            return changelog[0].get("changes", [])

        return []

    def auto_update(self) -> Tuple[bool, str]:
        """
        Automatically check, download, and apply updates.

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check for updates
        update_available, latest_version, update_info = self.check_for_updates()

        if not update_available:
            return True, "Already on the latest version."

        self.logger.info(f"Auto-updating to version {latest_version}")

        # Download update
        success, message = self.download_update()
        if not success:
            return False, f"Failed to download update: {message}"

        # Apply update
        success, message = self.apply_update()
        if not success:
            return False, f"Failed to apply update: {message}"

        return (
            True,
            f"Successfully updated to version {latest_version}! Please restart the application.",
        )

    def get_update_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the update status.

        Returns:
            Dictionary with update status summary
        """
        update_status = self.config.get_update_status()

        return {
            "current_version": self.current_version,
            "latest_version": update_status.get("latest_version"),
            "needs_update": update_status.get("needs_update", False),
            "update_downloaded": update_status.get("update_downloaded", False),
            "checked_at": update_status.get("checked_at"),
            "update_path": update_status.get("update_path"),
        }


# Singleton instance
_update_manager_instance = None


def get_update_manager(config_manager) -> UpdateManager:
    """Get or create the UpdateManager singleton instance."""
    global _update_manager_instance
    if _update_manager_instance is None:
        _update_manager_instance = UpdateManager(config_manager)
    return _update_manager_instance
