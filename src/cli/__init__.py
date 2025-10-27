"""
Onion Hoster - CLI Package
Author: Uzair Developer
GitHub: uzairdeveloper223

This package contains the command-line interface for Onion Hoster
with interactive terminal support and full feature parity with the GUI.
"""

from .cli_interface import OnionHosterCLI, main

__all__ = [
    "OnionHosterCLI",
    "main",
]
