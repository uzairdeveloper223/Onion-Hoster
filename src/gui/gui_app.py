"""
Onion Hoster - GUI Application
Author: Uzair Developer
GitHub: uzairdeveloper223

This module provides the graphical user interface for Onion Hoster
using CustomTkinter with Material You design and Tor Browser-inspired theme.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import customtkinter as ctk
from customtkinter import CTkInputDialog
import pyperclip
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.constants import (
    VERSION,
    APP_NAME,
    AUTHOR,
    GITHUB_USERNAME,
    THEME_COLORS,
    GUI_WINDOW_SIZE,
    GUI_MIN_WINDOW_SIZE,
)
from core.system_detector import get_system_detector
from core.config_manager import get_config_manager
from core.onion_service import OnionServiceManager
from core.update_manager import get_update_manager


class OnionHosterGUI:
    """Main GUI application for Onion Hoster."""

    def __init__(self):
        """Initialize the GUI application."""

        # Initialize core components
        self.system = get_system_detector()
        self.config = get_config_manager()
        self.service = OnionServiceManager(self.config, self.system)
        self.service.is_gui = True
        self.updater = get_update_manager(self.config)
        self.logger = logging.getLogger(__name__)

        # Check if GUI can run
        can_run, message = self.system.can_run_gui()
        if not can_run:
            print(f"Error: {message}")
            print("Please use CLI mode instead.")
            sys.exit(1)

        # Update platform info
        self.config.update_platform_info(self.system.get_platform_info())

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")  # Will customize with purple

        # Create main window
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry(GUI_WINDOW_SIZE)
        self.root.minsize(*GUI_MIN_WINDOW_SIZE)

        # Configure grid weight
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Variables
        self.site_directory_var = tk.StringVar(
            value=self.config.get("site_directory", "")
        )
        self.onion_address_var = tk.StringVar(
            value=self.config.get("onion_address", "")
        )
        self.service_status_var = tk.StringVar(value="Stopped")
        self.status_message_var = tk.StringVar(value="Ready")

        # Create UI
        self.create_widgets()

        # Check dependencies on startup
        self.root.after(500, self.check_dependencies_startup)

        # Check for updates if enabled
        if self.config.get("check_updates_on_start", True):
            self.root.after(1000, self.check_updates_silent)

    def create_widgets(self):
        """Create all GUI widgets."""

        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.create_header(main_frame)

        # Content area with tabs
        self.create_tabview(main_frame)

        # Status bar
        self.create_status_bar(main_frame)

    def create_header(self, parent):
        """Create the header section."""
        header_frame = ctk.CTkFrame(parent, height=80, fg_color=THEME_COLORS["surface"])
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Logo/Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🧅 Onion Hoster",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=THEME_COLORS["primary"],
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Host your static websites on the Tor Network",
            font=ctk.CTkFont(size=12),
            text_color=THEME_COLORS["text_secondary"],
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Service status indicator
        self.status_indicator = ctk.CTkLabel(
            header_frame,
            textvariable=self.service_status_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME_COLORS["error"],
        )
        self.status_indicator.grid(
            row=0, column=1, rowspan=2, padx=20, pady=10, sticky="e"
        )

    def create_tabview(self, parent):
        """Create the main tabview."""
        self.tabview = ctk.CTkTabview(parent, fg_color=THEME_COLORS["surface"])
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Add tabs
        self.tab_main = self.tabview.add("Main")
        self.tab_config = self.tabview.add("Configuration")
        self.tab_dependencies = self.tabview.add("Dependencies")
        self.tab_about = self.tabview.add("About")

        # Configure tabs
        self.create_main_tab()
        self.create_config_tab()
        self.create_dependencies_tab()
        self.create_about_tab()

    def create_main_tab(self):
        """Create the main control tab."""
        tab = self.tab_main
        tab.grid_columnconfigure(0, weight=1)

        # Site directory section
        dir_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        dir_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        dir_frame.grid_columnconfigure(1, weight=1)

        dir_label = ctk.CTkLabel(
            dir_frame, text="Site Directory:", font=ctk.CTkFont(size=14, weight="bold")
        )
        dir_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            textvariable=self.site_directory_var,
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.dir_entry.grid(
            row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew"
        )

        browse_btn = ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self.browse_directory,
            width=120,
            height=35,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        browse_btn.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

        validate_btn = ctk.CTkButton(
            dir_frame,
            text="Validate",
            command=self.validate_directory,
            width=120,
            height=35,
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        validate_btn.grid(row=2, column=1, padx=15, pady=(0, 15), sticky="e")

        # Control buttons
        control_frame = ctk.CTkFrame(tab, fg_color="transparent")
        control_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        control_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_btn = ctk.CTkButton(
            control_frame,
            text="🚀 Start Service",
            command=self.start_service,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=THEME_COLORS["success"],
            hover_color="#66BB6A",
        )
        self.start_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="🛑 Stop Service",
            command=self.stop_service,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=THEME_COLORS["error"],
            hover_color="#E57373",
            state="disabled",
        )
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.restart_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Restart Service",
            command=self.restart_service,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=THEME_COLORS["warning"],
            hover_color="#FFB74D",
            state="disabled",
        )
        self.restart_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Onion address section
        address_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        address_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        address_frame.grid_columnconfigure(0, weight=1)

        address_label = ctk.CTkLabel(
            address_frame,
            text="Your Onion Address:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        address_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.address_entry = ctk.CTkEntry(
            address_frame,
            textvariable=self.onion_address_var,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="readonly",
            text_color=THEME_COLORS["success"],
        )
        self.address_entry.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")

        button_frame = ctk.CTkFrame(address_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.copy_btn = ctk.CTkButton(
            button_frame,
            text="📋 Copy Address",
            command=self.copy_address,
            height=40,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
            state="disabled",
        )
        self.copy_btn.grid(row=0, column=0, padx=5, pady=0, sticky="ew")

        self.open_browser_btn = ctk.CTkButton(
            button_frame,
            text="🌐 Open in Tor Browser",
            command=self.open_in_browser,
            height=40,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
            state="disabled",
        )
        self.open_browser_btn.grid(row=0, column=1, padx=5, pady=0, sticky="ew")

        # Log/Info area
        log_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 20))
        tab.grid_rowconfigure(3, weight=1)

        log_label = ctk.CTkLabel(
            log_frame, text="Activity Log:", font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.log_text = ctk.CTkTextbox(
            log_frame, height=150, font=ctk.CTkFont(size=11), wrap="word"
        )
        self.log_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log("Application started. Ready to host your site on Tor network.")

    def create_config_tab(self):
        """Create the configuration tab."""
        tab = self.tab_config
        tab.grid_columnconfigure(0, weight=1)

        # Nginx port setting
        port_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        port_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        port_frame.grid_columnconfigure(1, weight=1)

        port_label = ctk.CTkLabel(
            port_frame, text="Nginx Port:", font=ctk.CTkFont(size=14, weight="bold")
        )
        port_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.port_var = tk.StringVar(value=str(self.config.get("nginx_port", 8080)))
        port_entry = ctk.CTkEntry(
            port_frame, textvariable=self.port_var, width=150, height=35
        )
        port_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        port_save_btn = ctk.CTkButton(
            port_frame,
            text="Save",
            command=self.save_port_config,
            width=100,
            height=35,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        port_save_btn.grid(row=0, column=2, padx=15, pady=15, sticky="e")

        # Auto-start setting
        autostart_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        autostart_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.autostart_var = tk.BooleanVar(value=self.config.get("auto_start", False))
        autostart_check = ctk.CTkCheckBox(
            autostart_frame,
            text="Auto-start service on application launch",
            variable=self.autostart_var,
            command=self.toggle_autostart,
            font=ctk.CTkFont(size=13),
        )
        autostart_check.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Update settings
        update_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        update_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.check_updates_var = tk.BooleanVar(
            value=self.config.get("check_updates_on_start", True)
        )
        update_check = ctk.CTkCheckBox(
            update_frame,
            text="Check for updates on startup",
            variable=self.check_updates_var,
            command=self.toggle_update_check,
            font=ctk.CTkFont(size=13),
        )
        update_check.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Config actions
        actions_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        actions_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Configuration Actions:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        actions_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        button_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        button_container.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        button_container.grid_columnconfigure((0, 1, 2), weight=1)

        export_btn = ctk.CTkButton(
            button_container,
            text="Export Config",
            command=self.export_config,
            height=35,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        export_btn.grid(row=0, column=0, padx=5, pady=0, sticky="ew")

        import_btn = ctk.CTkButton(
            button_container,
            text="Import Config",
            command=self.import_config,
            height=35,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        import_btn.grid(row=0, column=1, padx=5, pady=0, sticky="ew")

        reset_btn = ctk.CTkButton(
            button_container,
            text="Reset to Defaults",
            command=self.reset_config,
            height=35,
            fg_color=THEME_COLORS["error"],
            hover_color="#E57373",
        )
        reset_btn.grid(row=0, column=2, padx=5, pady=0, sticky="ew")

    def create_dependencies_tab(self):
        """Create the dependencies tab."""
        tab = self.tab_dependencies
        tab.grid_columnconfigure(0, weight=1)

        # System info
        info_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        info_label = ctk.CTkLabel(
            info_frame,
            text="System Information:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        info_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        platform_info = self.system.get_platform_info()
        info_text = f"OS: {platform_info['os_name']}\n"
        if platform_info["distro"]:
            info_text += f"Distribution: {platform_info['distro']}\n"
        if platform_info["desktop_env"]:
            info_text += f"Desktop: {platform_info['desktop_env']}\n"
        info_text += f"Architecture: {platform_info['architecture']}"

        info_display = ctk.CTkLabel(
            info_frame, text=info_text, font=ctk.CTkFont(size=12), justify="left"
        )
        info_display.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        # Dependencies status
        deps_frame = ctk.CTkFrame(tab, fg_color=THEME_COLORS["surface_variant"])
        deps_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        deps_frame.grid_columnconfigure((0, 1), weight=1)

        deps_label = ctk.CTkLabel(
            deps_frame, text="Dependencies:", font=ctk.CTkFont(size=14, weight="bold")
        )
        deps_label.grid(
            row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w"
        )

        # Tor
        self.tor_status_label = ctk.CTkLabel(
            deps_frame, text="Tor: Checking...", font=ctk.CTkFont(size=12)
        )
        self.tor_status_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")

        self.tor_install_btn = ctk.CTkButton(
            deps_frame,
            text="Install Tor",
            command=lambda: self.install_dependency("tor"),
            width=120,
            height=30,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        self.tor_install_btn.grid(row=1, column=1, padx=15, pady=5, sticky="e")

        # Nginx
        self.nginx_status_label = ctk.CTkLabel(
            deps_frame, text="Nginx: Checking...", font=ctk.CTkFont(size=12)
        )
        self.nginx_status_label.grid(row=2, column=0, padx=15, pady=5, sticky="w")

        self.nginx_install_btn = ctk.CTkButton(
            deps_frame,
            text="Install Nginx",
            command=lambda: self.install_dependency("nginx"),
            width=120,
            height=30,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        self.nginx_install_btn.grid(row=2, column=1, padx=15, pady=5, sticky="e")

        # Tor Browser
        self.browser_status_label = ctk.CTkLabel(
            deps_frame, text="Tor Browser: Checking...", font=ctk.CTkFont(size=12)
        )
        self.browser_status_label.grid(row=3, column=0, padx=15, pady=5, sticky="w")

        self.browser_install_btn = ctk.CTkButton(
            deps_frame,
            text="Install Tor Browser",
            command=lambda: self.install_dependency("tor_browser"),
            width=120,
            height=30,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        self.browser_install_btn.grid(
        row=3, column=1, padx=15, pady=5, sticky="e"
        )

        # xclip
        self.xclip_status_label = ctk.CTkLabel(
            deps_frame, text="xclip: Checking...", font=ctk.CTkFont(size=12)
        )
        self.xclip_status_label.grid(row=4, column=0, padx=15, pady=5, sticky="w")

        self.xclip_install_btn = ctk.CTkButton(
            deps_frame,
            text="Install xclip",
            command=lambda: self.install_dependency("xclip"),
            width=120,
            height=30,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        self.xclip_install_btn.grid(
            row=4, column=1, padx=15, pady=(5, 15), sticky="e"
        )

        # Refresh button
        refresh_btn = ctk.CTkButton(
            tab,
            text="🔄 Refresh Status",
            command=self.check_dependencies_startup,
            height=40,
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["primary_dark"],
        )
        refresh_btn.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

    def create_about_tab(self):
        """Create the about tab."""
        tab = self.tab_about
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Center frame
        center_frame = ctk.CTkFrame(tab, fg_color="transparent")
        center_frame.grid(row=0, column=0, sticky="nsew")
        center_frame.grid_columnconfigure(0, weight=1)

        # Logo/Title
        title_label = ctk.CTkLabel(
            center_frame,
            text="🧅 Onion Hoster",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=THEME_COLORS["primary"],
        )
        title_label.grid(row=0, column=0, pady=(50, 10))

        # Version
        version_label = ctk.CTkLabel(
            center_frame,
            text=f"Version {VERSION}",
            font=ctk.CTkFont(size=16),
            text_color=THEME_COLORS["text_secondary"],
        )
        version_label.grid(row=1, column=0, pady=(0, 30))

        # Description
        desc_label = ctk.CTkLabel(
            center_frame,
            text="A cross-platform utility tool to host static websites\non the Tor network with ease.",
            font=ctk.CTkFont(size=14),
            justify="center",
        )
        desc_label.grid(row=2, column=0, pady=(0, 30))

        # Author info
        author_frame = ctk.CTkFrame(
            center_frame, fg_color=THEME_COLORS["surface_variant"]
        )
        author_frame.grid(row=3, column=0, pady=(0, 20), padx=50, sticky="ew")

        author_label = ctk.CTkLabel(
            author_frame, text=f"Created by: {AUTHOR}", font=ctk.CTkFont(size=13)
        )
        author_label.grid(row=0, column=0, padx=20, pady=(15, 5))

        github_label = ctk.CTkLabel(
            author_frame,
            text=f"GitHub: @{GITHUB_USERNAME}",
            font=ctk.CTkFont(size=13),
            text_color=THEME_COLORS["primary"],
            cursor="hand2",
        )
        github_label.grid(row=1, column=0, padx=20, pady=(5, 15))
        github_label.bind("<Button-1>", lambda e: self.open_github())

        # Update button
        update_btn = ctk.CTkButton(
            center_frame,
            text="🔄 Check for Updates",
            command=self.check_for_updates,
            height=45,
            width=200,
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        update_btn.grid(row=4, column=0, pady=(20, 0))

    def create_status_bar(self, parent):
        """Create the status bar."""
        status_frame = ctk.CTkFrame(parent, height=30, fg_color=THEME_COLORS["surface"])
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(10, 0))
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_message_var,
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    # Helper methods

    def log(self, message: str):
        """Add a message to the log."""
        self.log_text.insert("end", f"• {message}\n")
        self.log_text.see("end")

    def set_status(self, message: str):
        """Set the status bar message."""
        self.status_message_var.set(message)

    def update_service_status(self, running: bool):
        """Update the service status indicator."""
        if running:
            self.service_status_var.set("● Running")
            self.status_indicator.configure(text_color=THEME_COLORS["success"])
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.restart_btn.configure(state="normal")
            if self.onion_address_var.get():
                self.copy_btn.configure(state="normal")
                self.open_browser_btn.configure(state="normal")
        else:
            self.service_status_var.set("● Stopped")
            self.status_indicator.configure(text_color=THEME_COLORS["error"])
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.restart_btn.configure(state="disabled")
            self.copy_btn.configure(state="disabled")
            self.open_browser_btn.configure(state="disabled")

    def _ensure_sudo_password(self):
        """Ensure sudo password is set if needed."""
        if not self.system.check_permissions() and self.service._sudo_password is None:
            dialog = CTkInputDialog(title="Sudo Password", text="Enter your sudo password:")
            password = dialog.get_input()
            if password:
                self.service.set_sudo_password(password)
            else:
                raise Exception("Sudo password is required for this operation.")

    def check_dependencies_startup(self):
        """Check dependencies on startup."""
        deps = self.service.check_dependencies()

        # Update Tor status
        if deps["tor"]:
            self.tor_status_label.configure(
                text="Tor: ✓ Installed", text_color=THEME_COLORS["success"]
            )
            self.tor_install_btn.configure(state="disabled")
        else:
            self.tor_status_label.configure(
                text="Tor: ✗ Not Installed", text_color=THEME_COLORS["error"]
            )
            self.tor_install_btn.configure(state="normal")

        # Update Nginx status
        if deps["nginx"]:
            self.nginx_status_label.configure(
                text="Nginx: ✓ Installed", text_color=THEME_COLORS["success"]
            )
            self.nginx_install_btn.configure(state="disabled")
        else:
            self.nginx_status_label.configure(
                text="Nginx: ✗ Not Installed", text_color=THEME_COLORS["error"]
            )
            self.nginx_install_btn.configure(state="normal")

        # Update Tor Browser status
        if deps["tor_browser"]:
            self.browser_status_label.configure(
            text="Tor Browser: ✓ Installed", text_color=THEME_COLORS["success"]
            )
            self.browser_install_btn.configure(state="disabled")
        else:
            self.browser_status_label.configure(
            text="Tor Browser: ✗ Not Installed", text_color=THEME_COLORS["warning"]
            )
            self.browser_install_btn.configure(state="normal")

        # Update xclip status
        if deps["xclip"]:
            self.xclip_status_label.configure(
                text="xclip: ✓ Installed", text_color=THEME_COLORS["success"]
            )
            self.xclip_install_btn.configure(state="disabled")
        else:
            self.xclip_status_label.configure(
                text="xclip: ✗ Not Installed", text_color=THEME_COLORS["warning"]
            )
            self.xclip_install_btn.configure(state="normal")

        # Update service status
        running = self.config.get("service_running", False)
        self.update_service_status(running)

    # Command methods

    def browse_directory(self):
        """Open directory browser."""
        directory = filedialog.askdirectory(
            title="Select Site Directory",
            initialdir=self.site_directory_var.get() or os.path.expanduser("~"),
        )
        if directory:
            self.site_directory_var.set(directory)
            self.log(f"Selected directory: {directory}")

    def validate_directory(self):
        """Validate the selected directory."""
        directory = self.site_directory_var.get()
        if not directory:
            messagebox.showwarning("No Directory", "Please select a directory first.")
            return

        valid, message = self.service.validate_site_directory(directory)

        if valid:
            messagebox.showinfo("Valid Directory", f"✓ {message}")
            self.log(f"Directory validated: {directory}")
        else:
            messagebox.showerror("Invalid Directory", f"✗ {message}")
            self.log(f"Directory validation failed: {message}")

    def start_service(self):
        """Start the onion service."""
        directory = self.site_directory_var.get()
        if not directory:
            messagebox.showwarning(
                "No Directory", "Please select a site directory first."
            )
            return

        # Check dependencies
        deps = self.service.check_dependencies()
        if not deps["tor"] or not deps["nginx"]:
            messagebox.showerror(
                "Missing Dependencies",
                "Tor and Nginx must be installed. Please install them from the Dependencies tab.",
            )
            return

        # Ensure sudo password is set if needed
        try:
            self._ensure_sudo_password()
        except Exception as e:
            messagebox.showerror("Password Required", str(e))
            return

        self.log("Starting onion service...")
        self.set_status("Starting service...")

        def start_thread():
            success, message, onion_address = self.service.start_service(directory)

            self.root.after(
                0, lambda: self._start_service_callback(success, message, onion_address)
            )

        threading.Thread(target=start_thread, daemon=True).start()

    def _start_service_callback(self, success, message, onion_address):
        """Callback after service start."""
        if success:
            self.log(f"✓ {message}")
            if onion_address:
                self.onion_address_var.set(onion_address)
                self.log(f"Onion address: {onion_address}")
                messagebox.showinfo(
                    "Service Started",
                    f"Service started successfully!\n\nYour onion address:\n{onion_address}",
                )
            self.update_service_status(True)
            self.set_status("Service running")
        else:
            self.log(f"✗ {message}")
            messagebox.showerror("Error", f"Failed to start service:\n{message}")
            self.set_status("Failed to start service")

    def stop_service(self):
        """Stop the onion service."""
        if not messagebox.askyesno(
            "Stop Service", "Are you sure you want to stop the service?"
        ):
            return

        # Ensure sudo password is set if needed
        try:
            self._ensure_sudo_password()
        except Exception as e:
            messagebox.showerror("Password Required", str(e))
            return

        self.log("Stopping onion service...")
        self.set_status("Stopping service...")

        def stop_thread():
            success, message = self.service.stop_service()
            self.root.after(0, lambda: self._stop_service_callback(success, message))

        threading.Thread(target=stop_thread, daemon=True).start()

    def _stop_service_callback(self, success, message):
        """Callback after service stop."""
        if success:
            self.log(f"✓ {message}")
            self.update_service_status(False)
            self.set_status("Service stopped")
        else:
            self.log(f"✗ {message}")
            messagebox.showwarning(
                "Warning", f"Service stop completed with errors:\n{message}"
            )
            self.update_service_status(False)
            self.set_status("Service stopped")

    def restart_service(self):
        """Restart the onion service."""
        # Ensure sudo password is set if needed
        try:
            self._ensure_sudo_password()
        except Exception as e:
            messagebox.showerror("Password Required", str(e))
            return

        self.log("Restarting onion service...")
        self.set_status("Restarting service...")
        def restart_thread():
            # Stop
            success, message = self.service.stop_service()
            if success:
                self.root.after(0, lambda: self.log(f"✓ Service stopped"))

            import time

            time.sleep(2)

            # Start
            directory = self.config.get("site_directory")
            success, message, onion_address = self.service.start_service(directory)

            self.root.after(
                0, lambda: self._start_service_callback(success, message, onion_address)
            )

        threading.Thread(target=restart_thread, daemon=True).start()

    def copy_address(self):
        """Copy onion address to clipboard."""
        address = self.onion_address_var.get()
        if address:
            try:
                pyperclip.copy(address)
                self.log("✓ Onion address copied to clipboard")
                self.set_status("Address copied to clipboard")
                messagebox.showinfo("Copied", "Onion address copied to clipboard!")
            except Exception as e:
                self.log(f"✗ Failed to copy: {e}")
                messagebox.showerror("Error", f"Failed to copy to clipboard:\n{e}")

    def open_in_browser(self):
        """Open onion address in Tor Browser."""
        address = self.onion_address_var.get()
        if not address:
            messagebox.showwarning("No Address", "No onion address available.")
            return

        if not self.system.is_tor_browser_installed():
            messagebox.showerror(
                "Tor Browser Not Found",
                "Tor Browser is not installed. Please install it from the Dependencies tab.",
            )
            return

        self.log("Opening in Tor Browser...")
        success, message = self.service.open_in_tor_browser(address)

        if success:
            self.log(f"✓ {message}")
            self.set_status("Opened in Tor Browser")
        else:
            self.log(f"✗ {message}")
            messagebox.showerror("Error", f"Failed to open Tor Browser:\n{message}")

    def install_dependency(self, package):
        """Install a dependency."""
        try:
            self._ensure_sudo_password()
        except Exception as e:
            messagebox.showerror("Password Required", str(e))
            return

        self.log(f"Installing {package}...")
        self.set_status(f"Installing {package}...")

        def install_thread():
            if package == "tor":
                success, message = self.service.install_tor()
            elif package == "nginx":
                success, message = self.service.install_nginx()
            elif package == "tor_browser":
                success, message = self.service.install_tor_browser()
            elif package == "xclip":
                success, message = self.service.install_xclip()
            else:
                success, message = False, "Unknown package"
            self.root.after(
                0, lambda: self._install_callback(package, success, message)
            )

        threading.Thread(target=install_thread, daemon=True).start()

    def _install_callback(self, package, success, message):
        """Callback after installation."""
        if success:
            self.log(f"✓ {message}")
            messagebox.showinfo("Success", message)
            self.set_status(f"{package} installed successfully")
            self.check_dependencies_startup()
        else:
            self.log(f"✗ {message}")
            messagebox.showerror("Installation Failed", message)
            self.set_status(f"Failed to install {package}")

    def save_port_config(self):
        """Save nginx port configuration."""
        try:
            port = int(self.port_var.get())
            if port < 1024 or port > 65535:
                raise ValueError("Port must be between 1024 and 65535")

            self.config.set("nginx_port", port)
            self.log(f"✓ Nginx port set to {port}")
            self.set_status(f"Port configuration saved: {port}")
            messagebox.showinfo("Success", f"Nginx port set to {port}")
        except ValueError as e:
            messagebox.showerror("Invalid Port", str(e))

    def toggle_autostart(self):
        """Toggle autostart setting."""
        value = self.autostart_var.get()
        self.config.set("auto_start", value)
        self.log(f"Auto-start: {'enabled' if value else 'disabled'}")

    def toggle_update_check(self):
        """Toggle update check setting."""
        value = self.check_updates_var.get()
        self.config.set("check_updates_on_start", value)
        self.log(f"Update check on startup: {'enabled' if value else 'disabled'}")

    def export_config(self):
        """Export configuration."""
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if file_path:
            success = self.config.export_config(file_path)
            if success:
                self.log(f"✓ Configuration exported to {file_path}")
                messagebox.showinfo("Success", "Configuration exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export configuration.")

    def import_config(self):
        """Import configuration."""
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if file_path:
            success = self.config.import_config(file_path)
            if success:
                self.log(f"✓ Configuration imported from {file_path}")
                messagebox.showinfo("Success", "Configuration imported successfully!")
                # Refresh UI
                self.site_directory_var.set(self.config.get("site_directory", ""))
                self.onion_address_var.set(self.config.get("onion_address", ""))
                self.port_var.set(str(self.config.get("nginx_port", 8080)))
            else:
                messagebox.showerror("Error", "Failed to import configuration.")

    def reset_config(self):
        """Reset configuration to defaults."""
        if not messagebox.askyesno(
            "Reset Configuration",
            "Are you sure you want to reset all settings to defaults?",
        ):
            return

        success = self.config.reset_config()
        if success:
            self.log("✓ Configuration reset to defaults")
            messagebox.showinfo("Success", "Configuration reset successfully!")
            # Refresh UI
            self.site_directory_var.set("")
            self.onion_address_var.set("")
            self.port_var.set("8080")
            self.autostart_var.set(False)
            self.check_updates_var.set(True)
        else:
            messagebox.showerror("Error", "Failed to reset configuration.")

    def check_for_updates(self):
        """Check for updates."""
        self.log("Checking for updates...")
        self.set_status("Checking for updates...")

        def check_thread():
            update_available, latest_version, update_info = (
                self.updater.check_for_updates()
            )
            self.root.after(
                0,
                lambda: self._check_updates_callback(
                    update_available, latest_version, update_info
                ),
            )

        threading.Thread(target=check_thread, daemon=True).start()

    def _check_updates_callback(self, update_available, latest_version, update_info):
        """Callback after update check."""
        if update_available:
            self.log(f"✓ Update available: v{latest_version}")

            changelog = self.updater.get_changelog(update_info)
            changelog_text = (
                "\n".join([f"• {change}" for change in changelog])
                if changelog
                else "No changelog available."
            )

            message = f"A new version is available!\n\nCurrent: v{VERSION}\nLatest: v{latest_version}\n\nChanges:\n{changelog_text}\n\nWould you like to update now?"

            if messagebox.askyesno("Update Available", message):
                self.perform_update()
            else:
                self.set_status(f"Update available: v{latest_version}")
        else:
            self.log(f"✓ Already on latest version (v{VERSION})")
            messagebox.showinfo(
                "Up to Date", f"You are using the latest version (v{VERSION})"
            )
            self.set_status("Up to date")

    def check_updates_silent(self):
        """Check for updates silently on startup."""

        def check_thread():
            update_available, latest_version, update_info = (
                self.updater.check_for_updates()
            )
            if update_available:
                self.root.after(
                    0,
                    lambda: self.log(
                        f"ℹ Update available: v{latest_version}. Check the About tab."
                    ),
                )

        threading.Thread(target=check_thread, daemon=True).start()

    def perform_update(self):
        """Perform the update."""
        self.log("Downloading and applying update...")
        self.set_status("Updating...")

        def update_thread():
            success, message = self.updater.auto_update()
            self.root.after(0, lambda: self._update_callback(success, message))

        threading.Thread(target=update_thread, daemon=True).start()

    def _update_callback(self, success, message):
        """Callback after update."""
        if success:
            self.log(f"✓ {message}")
            messagebox.showinfo(
                "Update Successful",
                f"{message}\n\nThe application will now close. Please restart it to use the new version.",
            )
            self.root.quit()
        else:
            self.log(f"✗ {message}")
            messagebox.showerror("Update Failed", message)
            self.set_status("Update failed")

    def open_github(self):
        """Open GitHub repository."""
        import webbrowser

        webbrowser.open(f"https://github.com/{GITHUB_USERNAME}/Onion-Hoster")

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point for GUI."""
    try:
        # Check if running in CLI-only environment
        system = get_system_detector()
        can_run, message = system.can_run_gui()

        if not can_run:
            print(f"Error: {message}")
            print("\nGUI mode requires a desktop environment.")
            print("Please use CLI mode instead: python onion-host --cli")
            sys.exit(1)

        # Create and run GUI
        app = OnionHosterGUI()
        app.run()

    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.exception("Fatal error in GUI")
        sys.exit(1)


if __name__ == "__main__":
    main()
