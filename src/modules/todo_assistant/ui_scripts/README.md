# Custom UI Automation Scripts

This directory contains user-defined automation scripts that can be executed via the MCP server.

## Overview

Custom scripts allow you to create complex automation workflows that go beyond the built-in MCP tools. Scripts are Python files that can use any automation library (pyautogui, pywinauto, etc.) to interact with the desktop.

## Creating Scripts

### Basic Template

```python
#!/usr/bin/env python3
"""
My Custom Script
================

Description of what this script does.
"""

import pyautogui
import time


def main():
    """Main script logic."""
    try:
        # Your automation code here
        print("Automation starting...")
        
        # Example: Click and type
        pyautogui.click(100, 100)
        time.sleep(0.5)
        pyautogui.write("Hello World")
        
        print("✅ Success")
        return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
```

### Best Practices

1. **Use Try-Except**: Always wrap your code in try-except blocks
2. **Print Status**: Print progress messages for debugging
3. **Return Codes**: Return 0 for success, non-zero for failure
4. **Add Delays**: Use `time.sleep()` to let UI elements load
5. **Test First**: Test scripts manually before automation

## Available Libraries

- **pyautogui**: Cross-platform GUI automation
  - Click, type, screenshot, mouse control
  - Simple but powerful
  
- **pywinauto**: Windows GUI automation (Windows only)
  - More robust element identification
  - Native Windows control

- **opencv-python**: Computer vision
  - Template matching
  - Image recognition

## Example Scripts

### example_screenshot.py
Takes a screenshot and saves it to outputs directory.

```bash
python example_screenshot.py
```

### example_click_and_type.py
Demonstrates clicking and typing at screen center.

```bash
python example_click_and_type.py
```

## Running Scripts

### Via To-Do Agent

Add a task like:
```
run script 'example_screenshot.py'
```

### Via MCP Server

```python
from modules.todo_assistant.mcp_server import MCPServer

server = MCPServer()
result = server.execute_tool("run_custom_script", file="example_screenshot.py")
```

### Direct Execution

```bash
python src/modules/todo_assistant/ui_scripts/example_screenshot.py
```

## Safety Notes

⚠️ **Important Safety Guidelines**:

1. **Test in Safe Environment**: Always test scripts in a safe, sandboxed environment
2. **User Consent**: Scripts should only run with explicit user approval
3. **No Destructive Actions**: Avoid scripts that delete files or modify system settings
4. **Timeout**: Scripts should complete within reasonable time (< 30 seconds by default)
5. **Error Handling**: Always handle errors gracefully

## Troubleshooting

### Import Errors
```bash
# Install required packages
pip install pyautogui pillow pytesseract
```

### Permission Errors
- On macOS: Grant accessibility permissions in System Preferences
- On Linux: May need to run with appropriate permissions

### Script Not Found
- Use absolute paths or paths relative to project root
- Check file permissions (should be readable)

## Advanced Usage

### Passing Arguments

Scripts can accept command-line arguments:

```python
import sys

def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(f"Target: {target}")
    # ... rest of script
```

Run with:
```python
server.execute_tool("run_custom_script", file="script.py", args=["target_value"])
```

### Using Environment Variables

```python
import os

def main():
    api_key = os.getenv("MY_API_KEY")
    # Use api_key...
```

## Contributing Scripts

Feel free to add your own scripts to this directory! Useful scripts that could benefit others:

- Browser automation (opening sites, filling forms)
- File management (batch renaming, organizing)
- System monitoring (CPU, memory checks)
- Application launching and configuration
- Data extraction and processing

## License

Custom scripts in this directory are part of the Cyber-AutoAgent project and follow the same MIT license.
