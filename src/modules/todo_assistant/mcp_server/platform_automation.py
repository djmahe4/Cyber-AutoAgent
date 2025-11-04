"""
Platform-Aware UI Automation
============================

Automatically selects the best UI automation library based on the platform:
- Windows: pywinauto (primary), pyautogui + opencv (fallback)
- macOS: pyobjc/applescript (primary), pyautogui + opencv (fallback)
- Linux: xdotool/atspi (primary), pyautogui + opencv (fallback)

Vision Mode uses opencv + pyautogui for pixel-based matching.
"""

import logging
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Detect platform
PLATFORM = sys.platform
IS_WINDOWS = PLATFORM == "win32"
IS_MACOS = PLATFORM == "darwin"
IS_LINUX = PLATFORM.startswith("linux")

# Try to import platform-specific libraries
AUTOMATION_LIBS = {}

# Windows - pywinauto
if IS_WINDOWS:
    try:
        from pywinauto import Application
        AUTOMATION_LIBS["pywinauto"] = True
        logger.info("pywinauto available for Windows")
    except ImportError:
        AUTOMATION_LIBS["pywinauto"] = False
        logger.warning("pywinauto not available")

# macOS - pyobjc (for AppleScript)
if IS_MACOS:
    try:
        import AppKit
        AUTOMATION_LIBS["pyobjc"] = True
        logger.info("pyobjc available for macOS")
    except ImportError:
        AUTOMATION_LIBS["pyobjc"] = False
        logger.warning("pyobjc not available")

# Linux - xdotool check
if IS_LINUX:
    try:
        result = subprocess.run(["which", "xdotool"], capture_output=True)
        AUTOMATION_LIBS["xdotool"] = result.returncode == 0
        if AUTOMATION_LIBS["xdotool"]:
            logger.info("xdotool available for Linux")
        else:
            logger.warning("xdotool not available")
    except Exception:
        AUTOMATION_LIBS["xdotool"] = False
        logger.warning("xdotool check failed")

# Vision mode libraries (cross-platform)
try:
    import pyautogui
    AUTOMATION_LIBS["pyautogui"] = True
    logger.info("pyautogui available for vision mode")
except ImportError:
    AUTOMATION_LIBS["pyautogui"] = False
    logger.warning("pyautogui not available")

try:
    import cv2
    import numpy as np
    AUTOMATION_LIBS["opencv"] = True
    logger.info("opencv available for vision mode")
except ImportError:
    AUTOMATION_LIBS["opencv"] = False
    logger.warning("opencv not available")


class PlatformAutomation:
    """Platform-aware UI automation handler."""
    
    def __init__(self, vision_mode: bool = False):
        """
        Initialize platform automation.
        
        Args:
            vision_mode: If True, use opencv + pyautogui for pixel matching
        """
        self.vision_mode = vision_mode
        self.platform = PLATFORM
        self.available_methods = self._detect_available_methods()
        logger.info(
            "PlatformAutomation initialized: platform=%s, vision_mode=%s, methods=%s",
            self.platform,
            vision_mode,
            self.available_methods
        )
    
    def _detect_available_methods(self) -> list:
        """Detect available automation methods."""
        methods = []
        
        if self.vision_mode:
            if AUTOMATION_LIBS.get("pyautogui") and AUTOMATION_LIBS.get("opencv"):
                methods.append("vision")
            return methods
        
        # Platform-specific methods
        if IS_WINDOWS and AUTOMATION_LIBS.get("pywinauto"):
            methods.append("pywinauto")
        
        if IS_MACOS and AUTOMATION_LIBS.get("pyobjc"):
            methods.append("pyobjc")
        
        if IS_LINUX and AUTOMATION_LIBS.get("xdotool"):
            methods.append("xdotool")
        
        # Fallback
        if AUTOMATION_LIBS.get("pyautogui"):
            methods.append("pyautogui")
        
        if not methods:
            methods.append("subprocess")
        
        return methods
    
    def get_primary_method(self) -> str:
        """Get the primary automation method."""
        return self.available_methods[0] if self.available_methods else "none"
    
    def open_app_windows(self, name: str, wait_time: int = 2) -> Dict[str, Any]:
        """Open application on Windows using pywinauto."""
        try:
            from pywinauto import Application
            
            app = Application(backend="uia").start(name)
            time.sleep(wait_time)
            
            return {
                "success": True,
                "app": name,
                "method": "pywinauto",
                "platform": "Windows",
                "pid": app.process if hasattr(app, 'process') else None
            }
        except Exception as e:
            logger.error("pywinauto open_app failed: %s", str(e))
            raise
    
    def open_app_macos(self, name: str, wait_time: int = 2) -> Dict[str, Any]:
        """Open application on macOS using open command."""
        try:
            subprocess.Popen(["open", "-a", name])
            time.sleep(wait_time)
            
            return {
                "success": True,
                "app": name,
                "method": "open",
                "platform": "macOS"
            }
        except Exception as e:
            logger.error("macOS open_app failed: %s", str(e))
            raise
    
    def open_app_linux(self, name: str, wait_time: int = 2) -> Dict[str, Any]:
        """Open application on Linux."""
        try:
            subprocess.Popen([name])
            time.sleep(wait_time)
            
            return {
                "success": True,
                "app": name,
                "method": "subprocess",
                "platform": "Linux"
            }
        except Exception as e:
            logger.error("Linux open_app failed: %s", str(e))
            raise
    
    def click_ui_windows(self, label: str) -> Dict[str, Any]:
        """Click UI element on Windows using pywinauto."""
        # This is a placeholder - full implementation would require window/control detection
        return {
            "success": False,
            "error": "pywinauto click not fully implemented",
            "label": label,
            "method": "pywinauto",
            "note": "Requires window and control identification"
        }
    
    def click_ui_macos(self, label: str) -> Dict[str, Any]:
        """Click UI element on macOS using AppleScript."""
        try:
            # Use AppleScript to click UI elements
            script = f'''
            tell application "System Events"
                click button "{label}" of front window of (first process whose frontmost is true)
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "label": label,
                "method": "applescript",
                "platform": "macOS",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            logger.error("AppleScript click failed: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "label": label,
                "method": "applescript"
            }
    
    def click_ui_linux(self, label: str) -> Dict[str, Any]:
        """Click UI element on Linux using xdotool."""
        try:
            # Search for window with label and click
            result = subprocess.run(
                ["xdotool", "search", "--name", label, "click", "1"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "label": label,
                "method": "xdotool",
                "platform": "Linux",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            logger.error("xdotool click failed: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "label": label,
                "method": "xdotool"
            }
    
    def click_ui_vision(
        self,
        label: str,
        template_path: Optional[str] = None,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Click UI element using computer vision (opencv + pyautogui).
        
        Args:
            label: Element label/description
            template_path: Path to template image for matching
            confidence: Matching confidence threshold (0.0-1.0)
            region: Screen region to search (x, y, width, height)
        """
        try:
            import pyautogui
            import cv2
            import numpy as np
            from PIL import ImageGrab
            
            # Take screenshot
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert to opencv format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # If template provided, try to match
            if template_path and Path(template_path).exists():
                template = cv2.imread(template_path)
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= confidence:
                    # Calculate click position
                    template_h, template_w = template.shape[:2]
                    center_x = max_loc[0] + template_w // 2
                    center_y = max_loc[1] + template_h // 2
                    
                    if region:
                        center_x += region[0]
                        center_y += region[1]
                    
                    # Click
                    pyautogui.click(center_x, center_y)
                    
                    return {
                        "success": True,
                        "label": label,
                        "method": "vision",
                        "confidence": float(max_val),
                        "position": {"x": center_x, "y": center_y}
                    }
                else:
                    return {
                        "success": False,
                        "error": "Template match confidence too low",
                        "label": label,
                        "method": "vision",
                        "confidence": float(max_val),
                        "threshold": confidence
                    }
            else:
                return {
                    "success": False,
                    "error": "Template path not provided or does not exist",
                    "label": label,
                    "method": "vision",
                    "note": "Vision mode requires template image"
                }
        
        except Exception as e:
            logger.error("Vision mode click failed: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "label": label,
                "method": "vision"
            }
    
    def get_automation_info(self) -> Dict[str, Any]:
        """Get information about available automation methods."""
        return {
            "platform": self.platform,
            "vision_mode": self.vision_mode,
            "available_methods": self.available_methods,
            "primary_method": self.get_primary_method(),
            "libraries": AUTOMATION_LIBS
        }
