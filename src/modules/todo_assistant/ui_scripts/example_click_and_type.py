#!/usr/bin/env python3
"""
Example UI Automation Script: Click and Type
============================================

Demonstrates clicking a UI element and typing text.

Usage:
    python example_click_and_type.py
"""

import pyautogui
import time


def main():
    """Click and type demonstration."""
    print("Starting click and type automation...")
    
    try:
        # Wait for user to position window
        print("Position your target window. Automation starts in 3 seconds...")
        time.sleep(3)
        
        # Example: Click at center of screen
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        print(f"Clicking at ({center_x}, {center_y})...")
        pyautogui.click(center_x, center_y)
        
        # Wait a moment
        time.sleep(0.5)
        
        # Type some text
        text = "Hello from automation!"
        print(f"Typing: {text}")
        pyautogui.write(text, interval=0.1)
        
        print("✅ Automation completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
