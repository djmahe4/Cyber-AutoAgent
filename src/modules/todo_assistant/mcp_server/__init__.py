"""
MCP Server for OS Automation
============================

Model Context Protocol (MCP) server providing OS automation tools:
- open_app: Launch applications
- click_ui: Click UI elements  
- type_text: Type text input
- read_screen: Extract text from screen
- run_custom_script: Execute user-defined automation scripts

Uses pywinauto as primary library with fallback to pyautogui + OpenCV.
"""

from .server import MCPServer
from .tools import (
    open_app,
    click_ui,
    type_text,
    read_screen,
    run_custom_script
)

__all__ = [
    "MCPServer",
    "open_app",
    "click_ui", 
    "type_text",
    "read_screen",
    "run_custom_script"
]
