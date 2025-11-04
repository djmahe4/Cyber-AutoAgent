"""
MCP Automation Tools
====================

Core automation tools for OS interaction.
Primary: pywinauto
Fallback: pyautogui + OpenCV
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Try to import automation libraries
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui not available - UI automation will be limited")

try:
    from pywinauto import Application
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logger.warning("pywinauto not available - using fallback automation")


def open_app(name: str, wait_time: int = 2) -> Dict[str, Any]:
    """
    Open an application by name.
    
    Args:
        name: Application name or path to executable
        wait_time: Seconds to wait after launching
        
    Returns:
        Dict with success status and details
    """
    try:
        logger.info("Opening application: %s", name)
        
        # Try different methods based on platform
        if sys.platform == "win32":
            # Windows
            if PYWINAUTO_AVAILABLE:
                try:
                    app = Application(backend="uia").start(name)
                    import time
                    time.sleep(wait_time)
                    return {
                        "success": True,
                        "app": name,
                        "method": "pywinauto",
                        "pid": app.process if hasattr(app, 'process') else None
                    }
                except Exception as e:
                    logger.warning("pywinauto failed, trying subprocess: %s", str(e))
            
            # Fallback to subprocess
            subprocess.Popen(name, shell=True)
            import time
            time.sleep(wait_time)
            return {
                "success": True,
                "app": name,
                "method": "subprocess",
                "note": "Application launched, but process handle not available"
            }
        
        elif sys.platform == "darwin":
            # macOS
            subprocess.Popen(["open", "-a", name])
            import time
            time.sleep(wait_time)
            return {
                "success": True,
                "app": name,
                "method": "open",
                "platform": "macOS"
            }
        
        else:
            # Linux
            subprocess.Popen([name])
            import time
            time.sleep(wait_time)
            return {
                "success": True,
                "app": name,
                "method": "subprocess",
                "platform": "Linux"
            }
    
    except Exception as e:
        logger.error("Failed to open application: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "app": name
        }


def click_ui(label: str, confidence: float = 0.8) -> Dict[str, Any]:
    """
    Click a UI element by label or visual match.
    
    Args:
        label: Text label or description of UI element
        confidence: Confidence threshold for image matching (0.0-1.0)
        
    Returns:
        Dict with success status and details
    """
    try:
        logger.info("Clicking UI element: %s", label)
        
        if not PYAUTOGUI_AVAILABLE:
            return {
                "success": False,
                "error": "pyautogui not available",
                "label": label,
                "note": "Install pyautogui to enable UI clicking"
            }
        
        # Try to find and click the element
        # First attempt: locate by text/image
        try:
            # This is a placeholder - real implementation would need image templates
            # or OCR to find UI elements
            location = pyautogui.locateOnScreen(label, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                return {
                    "success": True,
                    "label": label,
                    "method": "image_match",
                    "position": {"x": center.x, "y": center.y}
                }
        except Exception:
            pass
        
        # Fallback: use center click as demonstration
        # In production, this would use OCR or template matching
        return {
            "success": False,
            "error": "Element not found",
            "label": label,
            "note": "Could not locate UI element. Ensure templates are configured."
        }
    
    except Exception as e:
        logger.error("Failed to click UI element: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "label": label
        }


def type_text(text: str, interval: float = 0.05) -> Dict[str, Any]:
    """
    Type text at current cursor position.
    
    Args:
        text: Text to type
        interval: Delay between keystrokes in seconds
        
    Returns:
        Dict with success status and details
    """
    try:
        logger.info("Typing text: %s", text[:50])
        
        if not PYAUTOGUI_AVAILABLE:
            return {
                "success": False,
                "error": "pyautogui not available",
                "note": "Install pyautogui to enable text typing"
            }
        
        pyautogui.write(text, interval=interval)
        return {
            "success": True,
            "text_length": len(text),
            "interval": interval,
            "method": "pyautogui"
        }
    
    except Exception as e:
        logger.error("Failed to type text: %s", str(e))
        return {
            "success": False,
            "error": str(e)
        }


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
