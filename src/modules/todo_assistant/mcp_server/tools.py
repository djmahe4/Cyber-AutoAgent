"""
MCP Automation Tools
====================

Core automation tools for OS interaction with platform-aware automation.

Platform Support:
- Windows: pywinauto (primary), pyautogui + opencv (fallback)
- macOS: pyobjc/applescript (primary), pyautogui + opencv (fallback)  
- Linux: xdotool/atspi (primary), pyautogui + opencv (fallback)

Vision Mode: opencv + pyautogui for pixel-based matching (user-enabled)
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .platform_automation import PlatformAutomation, AUTOMATION_LIBS
from .action_logger import ActionLogger

logger = logging.getLogger(__name__)

# Global automation instance (can be set with vision mode)
_automation_instance = None
_action_logger = None


def set_vision_mode(enabled: bool):
    """
    Enable or disable vision mode.
    
    Args:
        enabled: If True, use opencv + pyautogui for pixel matching
    """
    global _automation_instance
    _automation_instance = PlatformAutomation(vision_mode=enabled)
    logger.info("Vision mode %s", "enabled" if enabled else "disabled")


def get_automation() -> PlatformAutomation:
    """Get or create automation instance."""
    global _automation_instance
    if _automation_instance is None:
        _automation_instance = PlatformAutomation(vision_mode=False)
    return _automation_instance


def get_logger() -> ActionLogger:
    """Get or create action logger."""
    global _action_logger
    if _action_logger is None:
        _action_logger = ActionLogger()
    return _action_logger


def open_app(name: str, wait_time: int = 2, log_action: bool = True) -> Dict[str, Any]:
    """
    Open an application by name using platform-aware automation.
    
    Args:
        name: Application name or path to executable
        wait_time: Seconds to wait after launching
        log_action: Whether to log this action
        
    Returns:
        Dict with success status and details
    """
    automation = get_automation()
    action_logger = get_logger() if log_action else None
    
    try:
        logger.info("Opening application: %s (method: %s)", name, automation.get_primary_method())
        
        # Use platform-specific method
        if sys.platform == "win32":
            result = automation.open_app_windows(name, wait_time)
        elif sys.platform == "darwin":
            result = automation.open_app_macos(name, wait_time)
        else:
            result = automation.open_app_linux(name, wait_time)
        
        # Log action
        if action_logger:
            action_logger.log_action(
                action_type="open_app",
                target=name,
                method=result.get("method", "unknown"),
                result=result,
                take_screenshots=True
            )
        
        return result
    
    except Exception as e:
        logger.error("Failed to open application: %s", str(e))
        result = {
            "success": False,
            "error": str(e),
            "app": name
        }
        
        if action_logger:
            action_logger.log_action(
                action_type="open_app",
                target=name,
                method="error",
                result=result,
                take_screenshots=False
            )
        
        return result


def click_ui(
    label: str,
    confidence: float = 0.8,
    template_path: Optional[str] = None,
    log_action: bool = True
) -> Dict[str, Any]:
    """
    Click a UI element by label using platform-aware automation.
    
    Args:
        label: Text label or description of UI element
        confidence: Confidence threshold for vision mode matching (0.0-1.0)
        template_path: Path to template image for vision mode
        log_action: Whether to log this action
        
    Returns:
        Dict with success status and details
    """
    automation = get_automation()
    action_logger = get_logger() if log_action else None
    
    try:
        logger.info("Clicking UI element: %s (method: %s)", label, automation.get_primary_method())
        
        # Use platform-specific or vision mode method
        if automation.vision_mode:
            result = automation.click_ui_vision(label, template_path, confidence)
        elif sys.platform == "win32":
            result = automation.click_ui_windows(label)
        elif sys.platform == "darwin":
            result = automation.click_ui_macos(label)
        else:
            result = automation.click_ui_linux(label)
        
        # Log action
        if action_logger:
            action_logger.log_action(
                action_type="click_ui",
                target=label,
                method=result.get("method", "unknown"),
                result=result,
                take_screenshots=True
            )
        
        return result
    
    except Exception as e:
        logger.error("Failed to click UI element: %s", str(e))
        result = {
            "success": False,
            "error": str(e),
            "label": label
        }
        
        if action_logger:
            action_logger.log_action(
                action_type="click_ui",
                target=label,
                method="error",
                result=result,
                take_screenshots=True
            )
        
        return result


def type_text(text: str, interval: float = 0.05, log_action: bool = True) -> Dict[str, Any]:
    """
    Type text at current cursor position.
    
    Args:
        text: Text to type
        interval: Delay between keystrokes in seconds
        log_action: Whether to log this action
        
    Returns:
        Dict with success status and details
    """
    action_logger = get_logger() if log_action else None
    
    try:
        logger.info("Typing text: %s", text[:50])
        
        # Use pyautogui for text typing (cross-platform)
        if not AUTOMATION_LIBS.get("pyautogui"):
            result = {
                "success": False,
                "error": "pyautogui not available",
                "note": "Install pyautogui to enable text typing"
            }
        else:
            import pyautogui
            pyautogui.write(text, interval=interval)
            result = {
                "success": True,
                "text_length": len(text),
                "interval": interval,
                "method": "pyautogui"
            }
        
        # Log action
        if action_logger:
            action_logger.log_action(
                action_type="type_text",
                target=f"text({len(text)} chars)",
                method=result.get("method", "unknown"),
                result=result,
                take_screenshots=False  # Don't screenshot for typing (security)
            )
        
        return result
    
    except Exception as e:
        logger.error("Failed to type text: %s", str(e))
        result = {
            "success": False,
            "error": str(e)
        }
        
        if action_logger:
            action_logger.log_action(
                action_type="type_text",
                target="text",
                method="error",
                result=result,
                take_screenshots=False
            )
        
        return result


def read_screen(region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    Read text from screen using OCR.
    
    Args:
        region: Optional region dict with 'x', 'y', 'width', 'height'
        
    Returns:
        Dict with success status and extracted text
    """
    try:
        logger.info("Reading screen text")
        
        # This is a placeholder implementation
        # Real implementation would use pytesseract or similar OCR
        try:
            import pytesseract
            from PIL import ImageGrab
            
            if region:
                screenshot = ImageGrab.grab(bbox=(
                    region['x'],
                    region['y'],
                    region['x'] + region['width'],
                    region['y'] + region['height']
                ))
            else:
                screenshot = ImageGrab.grab()
            
            text = pytesseract.image_to_string(screenshot)
            return {
                "success": True,
                "text": text,
                "method": "pytesseract",
                "region": region
            }
        except ImportError:
            return {
                "success": False,
                "error": "OCR library not available",
                "note": "Install pytesseract and pillow to enable screen reading"
            }
    
    except Exception as e:
        logger.error("Failed to read screen: %s", str(e))
        return {
            "success": False,
            "error": str(e)
        }


def run_custom_script(file: str, args: Optional[list] = None) -> Dict[str, Any]:
    """
    Execute a user-defined automation script.
    
    Args:
        file: Path to Python script file
        args: Optional command-line arguments
        
    Returns:
        Dict with success status and script output
    """
    try:
        logger.info("Running custom script: %s", file)
        
        script_path = Path(file)
        if not script_path.exists():
            return {
                "success": False,
                "error": "Script file not found",
                "file": file
            }
        
        if not script_path.suffix == ".py":
            return {
                "success": False,
                "error": "Only Python scripts are supported",
                "file": file
            }
        
        # Execute the script
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "file": file,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Script execution timeout (30s)",
            "file": file
        }
    except Exception as e:
        logger.error("Failed to run custom script: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "file": file
        }
