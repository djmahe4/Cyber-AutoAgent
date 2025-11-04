#!/usr/bin/env python3
"""
Example UI Automation Script: Take Screenshot
==============================================

This script demonstrates how to create custom automation scripts
that can be executed via the MCP server.

Usage:
    python example_screenshot.py
"""

import pyautogui
from datetime import datetime
from pathlib import Path


def main():
    """Take a screenshot and save it."""
    print("Taking screenshot...")
    
    # Create output directory
    output_dir = Path("./outputs/screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Take screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"screenshot_{timestamp}.png"
    
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filename))
        print(f"✅ Screenshot saved: {filename}")
        return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
