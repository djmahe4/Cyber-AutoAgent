# To-Do Assistant - React CLI Integration

## Overview

The To-Do Desktop Assistant is now fully integrated with the React CLI, providing a seamless command-line interface for desktop automation tasks.

## Quick Start

```bash
# Launch React CLI
cd src/modules/interfaces/react
npm start

# Or with the built distribution
npm run build
node dist/index.js
```

## Available Commands

### Add a Task

```bash
> /todo <task description>

Examples:
> /todo open notepad
> /todo open chrome then click File then type 'example.com'
> /todo run script 'backup.py'
```

**Response:**
```
✅ Task #1 created with 2 actions

Parsed actions:
  1. open_app({"name": "chrome"})
  2. click_ui({"label": "file"})
  3. type_text({"text": "example.com"})
```

### List Tasks

```bash
> /todo-list [status]

Examples:
> /todo-list          # All tasks
> /todo-list pending  # Only pending
> /todo-list completed
> /todo-list failed
```

**Response:**
```
📝 To-Do Tasks (3):

⏳ #1 - open notepad
   Status: pending, Actions: 1

✅ #2 - open chrome then type 'hello'
   Status: completed, Actions: 2

❌ #3 - click nonexistent button
   Status: failed, Actions: 1
```

### Execute a Task

```bash
> /todo-run <task_id> [dry]

Examples:
> /todo-run 1      # Execute task
> /todo-run 1 dry  # Dry-run (preview only)
```

**Response (Dry-run):**
```
🔍 Dry-running task #1...
✅ Task #1 dry-run completed

Results:
  1. open_app: ✅ Would open application: notepad
```

**Response (Actual Execution):**
```
▶️ Executing task #1...
✅ Task #1 execution completed

Results:
  1. open_app: ✅ Application launched successfully
```

### Cancel a Task

```bash
> /todo-cancel <task_id>

Example:
> /todo-cancel 1
```

**Response:**
```
🚫 Task #1 cancelled
```

### Toggle Vision Mode

```bash
> /vision <on|off>

Examples:
> /vision on   # Enable pixel-based UI detection
> /vision off  # Use platform-specific tools
```

**Response:**
```
🔍 Vision mode enabled
Using OpenCV + PyAutoGUI for pixel-based UI element detection
```

## Event System

The React CLI integration uses an event-driven architecture. Events are emitted at key points:

### Task Events

- `task:created` - When a new task is added
- `task:executing` - When task execution starts
- `task:completed` - When task completes successfully
- `task:failed` - When task execution fails

### Action Events

- `action:log` - When an action is logged
- `vision:mode:changed` - When vision mode is toggled

### Event Flow Example

```
User Input: /todo open notepad
     ↓
[Command Handler] → Parse command
     ↓
[TodoService] → Call Python bridge
     ↓
[cli_bridge.py] → Execute Python command
     ↓
[TodoAgent] → Add task
     ↓
[Event: task:created] → Emit to React CLI
     ↓
[React CLI] → Display result to user
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              React CLI (TypeScript)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  useCommandHandler                                │  │
│  │  - Parses /todo commands                          │  │
│  │  - Routes to TodoService                          │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  TodoService                                      │  │
│  │  - Manages task operations                        │  │
│  │  - Spawns Python subprocess                       │  │
│  │  - Emits events                                   │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────┘
                 │ JSON via subprocess
                 ↓
┌─────────────────────────────────────────────────────────┐
│              Python Backend                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │  cli_bridge.py                                    │  │
│  │  - Receives commands via args                     │  │
│  │  - Returns JSON responses                         │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  TodoAgent                                        │  │
│  │  - Manages task lifecycle                         │  │
│  │  - Parses natural language                        │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  PlatformAutomation                               │  │
│  │  - Detects OS                                     │  │
│  │  - Selects automation method                      │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ActionLogger                                     │  │
│  │  - Logs to JSONL                                  │  │
│  │  - Captures screenshots                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## CLI Bridge Protocol

Communication between React and Python uses JSON over stdin/stdout:

### Request Format

```bash
python3 cli_bridge.py <command> <json_params>
```

### Response Format

```json
{
  "success": true,
  "task": {
    "id": 1,
    "description": "open notepad",
    "status": "pending",
    "actions": [
      {
        "tool": "open_app",
        "params": {"name": "notepad"},
        "description": "open notepad"
      }
    ],
    "created_at": "2025-11-04T02:55:40",
    "updated_at": "2025-11-04T02:55:40"
  }
}
```

### Error Format

```json
{
  "success": false,
  "error": "Description of error"
}
```

## Platform-Specific Behavior

### Windows
- **Primary**: pywinauto for native Windows automation
- **Fallback**: pyautogui + opencv if pywinauto unavailable
- **Vision Mode**: opencv template matching + pyautogui clicking

### macOS
- **Primary**: pyobjc with AppleScript for UI automation
- **Fallback**: pyautogui + opencv
- **Vision Mode**: opencv template matching + pyautogui clicking

### Linux
- **Primary**: xdotool for X11 window management
- **Fallback**: pyautogui + opencv
- **Vision Mode**: opencv template matching + pyautogui clicking

## Logging and Screenshots

All actions are logged to structured files:

```
logs/
├── session_20251104_025540_b7316383.jsonl
├── session_20251104_025540_b7316383_summary.json
└── screenshots/
    └── session_20251104_025540_b7316383/
        ├── 0001_after.png
        ├── 0002_after.png
        └── 0003_after.png
```

### JSONL Log Entry

```json
{
  "session_id": "session_20251104_025540_b7316383",
  "action_id": 1,
  "timestamp": "2025-11-04T02:55:41.123456",
  "action_type": "open_app",
  "target": "notepad",
  "method": "pywinauto",
  "result": {
    "success": true,
    "error": null,
    "data": {
      "app": "notepad",
      "method": "pywinauto",
      "platform": "Windows",
      "pid": 12345
    }
  },
  "screenshots": {
    "before": null,
    "after": "logs/screenshots/session.../0001_after.png"
  },
  "metadata": {}
}
```

## Integration with Main Cyber-AutoAgent

The To-Do Assistant runs alongside the main security assessment functionality:

```bash
# Start React CLI (includes both security and to-do features)
npm start

# Use security assessment
> target https://example.com
> execute comprehensive scan

# Use to-do automation
> /todo open burp suite then configure proxy
> /todo-run 1
```

Both systems share:
- Configuration management
- Logging infrastructure
- Memory system (optional)
- Event emission protocol

## Best Practices

1. **Test with Dry-Run**: Always preview tasks before execution
   ```bash
   > /todo-run 1 dry
   ```

2. **Enable Vision Mode Selectively**: Only when platform tools fail
   ```bash
   > /vision on
   ```

3. **Monitor Logs**: Check debug dashboard in Streamlit UI for detailed traces

4. **Use Status Filters**: List only relevant tasks
   ```bash
   > /todo-list pending
   ```

5. **Cancel Stuck Tasks**: Cancel tasks that won't complete
   ```bash
   > /todo-cancel 3
   ```

## Troubleshooting

### Task Won't Execute

Check platform compatibility:
```bash
> /vision on  # Switch to vision mode
> /todo-run 1
```

### Commands Not Found

Ensure you're in the React CLI:
```bash
cd src/modules/interfaces/react
npm start
```

### Python Bridge Errors

Check Python path and dependencies:
```bash
cd /path/to/Cyber-AutoAgent
export PYTHONPATH=$PWD/src
python3 src/modules/todo_assistant/cli_bridge.py add_task '{"description": "test"}'
```

### Vision Mode Not Working

Install required dependencies:
```bash
pip install opencv-python pyautogui pillow
```

## Examples

### Example 1: Browser Automation

```bash
> /todo open chrome then type 'github.com' then press enter
> /todo-list
> /todo-run 1
```

### Example 2: Application Testing

```bash
> /todo open calculator then click button 5
> /todo-run 1 dry  # Preview first
> /todo-run 1      # Execute
```

### Example 3: Batch Operations

```bash
> /todo open notepad
> /todo type 'Line 1' then press enter
> /todo type 'Line 2' then press enter
> /todo-list pending
> /todo-run 1
> /todo-run 2
> /todo-run 3
```

## Security Considerations

⚠️ **Important**: Desktop automation has security implications:

1. **Consent**: Dry-run tasks before execution
2. **Scope**: Only automate systems you own
3. **Logs**: Review logs for unexpected behavior
4. **Vision Mode**: Requires template images - ensure they're from trusted sources
5. **Scripts**: Review custom scripts before execution

## Next Steps

- **Learn More**: See [todo-assistant.md](./todo-assistant.md) for full documentation
- **Setup Guide**: See [todo-assistant-setup.md](./todo-assistant-setup.md) for installation
- **UI Dashboard**: Launch Streamlit UI for visual interface
  ```bash
  cd src/modules/todo_assistant/frontend
  streamlit run app.py
  ```

---

**Version**: 0.1.0  
**Last Updated**: 2025-11-04  
**Status**: Production Ready with React CLI Integration ✅
