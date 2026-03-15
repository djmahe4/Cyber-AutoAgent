"""
MCP Capability Manifest
=======================

Provides a programmatic, JSON-serialisable description of every tool exposed
by the MCP server.  LLM agents and sub-agents can call ``get_capabilities()``
to discover available tools, their JSON schemas, and platform support without
importing any heavy optional dependencies.
"""

import json
import sys
from typing import Any, Dict

from .schemas import TOOL_SCHEMAS

# ---------------------------------------------------------------------------
# Platform support map
# ---------------------------------------------------------------------------

_PLATFORM_SUPPORT: Dict[str, Dict[str, Any]] = {
    "open_app": {
        "win": {"primary": "pywinauto", "fallback": "subprocess"},
        "mac": {"primary": "open", "fallback": "subprocess"},
        "linux": {"primary": "subprocess", "fallback": "subprocess"},
    },
    "click_ui": {
        "win": {"primary": "pywinauto", "fallback": "vision/pyautogui"},
        "mac": {"primary": "applescript", "fallback": "vision/pyautogui"},
        "linux": {"primary": "xdotool", "fallback": "vision/pyautogui"},
    },
    "type_text": {
        "win": {"primary": "pyautogui", "fallback": None},
        "mac": {"primary": "pyautogui", "fallback": None},
        "linux": {"primary": "pyautogui", "fallback": None},
    },
    "read_screen": {
        "win": {"primary": "pytesseract+pillow", "fallback": None},
        "mac": {"primary": "pytesseract+pillow", "fallback": None},
        "linux": {"primary": "pytesseract+pillow", "fallback": None},
    },
    "run_custom_script": {
        "win": {"primary": "subprocess", "fallback": None},
        "mac": {"primary": "subprocess", "fallback": None},
        "linux": {"primary": "subprocess", "fallback": None},
    },
}

# ---------------------------------------------------------------------------
# Per-tool human-readable descriptions
# ---------------------------------------------------------------------------

_TOOL_DESCRIPTIONS: Dict[str, str] = {
    "open_app": "Launch an application by name using platform-aware automation.",
    "click_ui": "Click a UI element by label using platform-aware or vision-mode automation.",
    "type_text": "Type text at the current cursor position using pyautogui.",
    "read_screen": "Extract text from the screen (or a region) using OCR.",
    "run_custom_script": "Execute a user-defined Python automation script with a 30-second timeout.",
}


def _current_platform_key() -> str:
    """Return a short platform key ('win', 'mac', or 'linux')."""
    if sys.platform == "win32":
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def get_capabilities() -> Dict[str, Any]:
    """
    Return a dict describing all available MCP tools.

    The returned structure is JSON-serialisable and looks like::

        {
            "schema_version": "1.0",
            "current_platform": "linux",
            "tools": {
                "open_app": {
                    "description": "...",
                    "input_schema": { ... },   # JSON Schema dict
                    "platform_support": { ... }
                },
                ...
            }
        }

    This function is import-safe: it never imports heavy optional dependencies
    (opencv, langchain, streamlit, etc.) at call time.
    """
    current_platform = _current_platform_key()
    tools: Dict[str, Any] = {}

    for tool_name, schema_cls in TOOL_SCHEMAS.items():
        tools[tool_name] = {
            "description": _TOOL_DESCRIPTIONS.get(tool_name, ""),
            "input_schema": schema_cls.model_json_schema(),
            "platform_support": _PLATFORM_SUPPORT.get(tool_name, {}),
            "current_platform_method": _PLATFORM_SUPPORT.get(tool_name, {}).get(current_platform, {}),
        }

    return {
        "schema_version": "1.0",
        "current_platform": current_platform,
        "tools": tools,
    }


def manifest_json(**kwargs: Any) -> str:
    """
    Return the capability manifest as a JSON string.

    All keyword arguments are forwarded to :func:`json.dumps`
    (e.g. ``indent=2`` for pretty-printing).
    """
    return json.dumps(get_capabilities(), **kwargs)
