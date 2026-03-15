"""
MCP Server for OS Automation
============================

Model Context Protocol (MCP) server providing OS automation tools:
- open_app: Launch applications
- click_ui: Click UI elements  
- type_text: Type text input
- read_screen: Extract text from screen
- run_custom_script: Execute user-defined automation scripts

Platform-aware automation:
- Windows: pywinauto
- macOS: pyobjc/applescript
- Linux: xdotool/atspi
- Vision Mode: opencv + pyautogui (user-enabled)
"""

from .server import MCPServer
from .tools import (
    open_app,
    click_ui,
    type_text,
    read_screen,
    run_custom_script,
    set_vision_mode,
    get_automation,
    get_logger
)
from .platform_automation import PlatformAutomation
from .action_logger import ActionLogger
from .manifest import get_capabilities, manifest_json
from .schemas import TOOL_SCHEMAS

__all__ = [
    "MCPServer",
    "open_app",
    "click_ui", 
    "type_text",
    "read_screen",
    "run_custom_script",
    "set_vision_mode",
    "get_automation",
    "get_logger",
    "PlatformAutomation",
    "ActionLogger",
    "get_capabilities",
    "manifest_json",
    "TOOL_SCHEMAS",
]
