# To-Do Assistant - Quick Reference

## All Features at a Glance

### Core Capabilities
- ✅ Natural language task creation
- ✅ 5 MCP automation tools
- ✅ Platform-aware automation (Windows/macOS/Linux)
- ✅ Vision mode with OpenCV
- ✅ RAG with PDF manual ingestion
- ✅ Comprehensive logging with screenshots
- ✅ React CLI integration
- ✅ Streamlit UI dashboard
- ✅ **All 3 deployment modes supported**

### Quick Start by Mode

#### Local CLI (Development)
```bash
# Install
pip install -e .

# Run React CLI
cd src/modules/interfaces/react && npm start

# Use commands
> /todo open notepad
> /vision info
```

#### Single Container (Isolated)
```bash
# Start
docker-compose up -d cyber-autoagent

# Use
docker exec -it cyber-autoagent bash
node /app/src/modules/interfaces/react/dist/index.js
```

#### Full Stack (Production)
```bash
# Start all services
docker-compose up -d

# Use
docker exec -it cyber-autoagent bash
node /app/src/modules/interfaces/react/dist/index.js
```

## Command Reference

### React CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/todo <desc>` | Add automation task | `/todo open chrome` |
| `/todo-list [status]` | List tasks | `/todo-list pending` |
| `/todo-run <id> [dry]` | Execute task | `/todo-run 1 dry` |
| `/todo-cancel <id>` | Cancel task | `/todo-cancel 1` |
| `/vision <on\|off\|info>` | Vision mode control | `/vision info` |

### Python API

```python
from modules.todo_assistant import TodoAgent

# Create agent
agent = TodoAgent()

# Add task
task = agent.add_task("open notepad then type 'hello'")

# Execute with dry-run
result = agent.execute_task(task.id, dry_run=True)
result = agent.execute_task(task.id)

# List tasks
tasks = agent.list_tasks(status="pending")

# Check deployment
from modules.todo_assistant.deployment_adapter import get_config_adapter
info = get_config_adapter().get_deployment_info()
```

## Deployment Mode Detection

### Check Current Mode

**Via CLI Bridge:**
```bash
python3 src/modules/todo_assistant/cli_bridge.py get_deployment_info '{}'
```

**Via React CLI:**
```bash
> /vision info
```

**Via Python:**
```python
from modules.todo_assistant.deployment_adapter import DeploymentMode
print(DeploymentMode.detect())
```

### Expected Output

**Local CLI:**
```json
{
  "mode": "local-cli",
  "is_container": false,
  "is_local": true,
  "project_root": "/path/to/project"
}
```

**Single Container:**
```json
{
  "mode": "single-container",
  "is_container": true,
  "is_local": false,
  "project_root": "/app"
}
```

**Full Stack:**
```json
{
  "mode": "full-stack",
  "is_container": true,
  "is_local": false,
  "project_root": "/app",
  "features": {
    "observability": true
  }
}
```

## Feature Matrix

| Feature | Local CLI | Container | Full Stack |
|---------|-----------|-----------|------------|
| Task Management | ✅ | ✅ | ✅ |
| MCP Tools | ✅ | ✅ | ✅ |
| Platform Detection | ✅ | ✅ | ✅ |
| Vision Mode | ✅* | ✅* | ✅* |
| RAG Engine | ✅* | ✅* | ✅* |
| Action Logging | ✅ | ✅ | ✅ |
| Screenshots | ✅* | ✅* | ✅* |
| React CLI | ✅ | ✅ | ✅ |
| Streamlit UI | ✅ | ✅ | ✅ |
| Desktop Access | ✅ Full | ⚠️ Limited | ⚠️ Limited |
| Observability | ❌ | ❌ | ✅ |

*Requires optional dependencies

## Task Syntax

### Simple Tasks
```
open notepad
launch excel
start calculator
```

### Multi-Step Tasks
```
open chrome then type 'github.com'
launch word then click File then click New
```

### Custom Scripts
```
run script 'backup.py'
execute 'automation.py'
```

### All Supported Patterns

| Pattern | Tool | Example |
|---------|------|---------|
| `open/launch/start <app>` | open_app | `open notepad` |
| `click <element>` | click_ui | `click Save button` |
| `type '<text>'` | type_text | `type 'hello world'` |
| `read screen` | read_screen | `read screen` |
| `run script '<file>'` | run_custom_script | `run script 'test.py'` |

## Logging Structure

All actions logged to structured files:

```
outputs/logs/
├── session_YYYYMMDD_HHMMSS_xxxxx.jsonl
├── session_YYYYMMDD_HHMMSS_xxxxx_summary.json
└── screenshots/
    └── session_YYYYMMDD_HHMMSS_xxxxx/
        ├── 0001_after.png
        ├── 0002_after.png
        └── ...
```

### JSONL Entry Format
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
    "data": {...}
  },
  "screenshots": {
    "after": "path/to/screenshot.png"
  }
}
```

## Platform Support

### Automatic Detection
```python
# System automatically selects best method
from modules.todo_assistant.mcp_server import get_automation

automation = get_automation()
print(automation.get_primary_method())
```

### By Platform

**Windows:**
- Primary: pywinauto
- Fallback: pyautogui + opencv

**macOS:**
- Primary: pyobjc/AppleScript
- Fallback: pyautogui + opencv

**Linux:**
- Primary: xdotool
- Fallback: pyautogui + opencv

**Vision Mode (All):**
- opencv + pyautogui
- User-enabled only

## Common Workflows

### Development Workflow
```bash
# 1. Local development
cd src/modules/todo_assistant
python3 cli_bridge.py add_task '{"description": "open notepad"}'

# 2. Test with React CLI
cd ../interfaces/react
npm start
> /todo open calculator
> /todo-run 1 dry

# 3. View logs
cat ../../outputs/logs/session_*.jsonl
```

### Container Workflow
```bash
# 1. Build and start
docker-compose up -d cyber-autoagent

# 2. Access CLI
docker exec -it cyber-autoagent bash
node /app/src/modules/interfaces/react/dist/index.js

# 3. Use commands
> /vision info
> /todo open notepad
> /todo-list
```

### Production Workflow
```bash
# 1. Start full stack
docker-compose up -d

# 2. Access observability
open http://localhost:3000  # Langfuse UI

# 3. Use agent
docker exec -it cyber-autoagent bash
node /app/src/modules/interfaces/react/dist/index.js

# 4. Monitor traces in Langfuse
```

## Troubleshooting

### Issue: Mode Not Detected
```bash
# Check environment
> /vision info

# Or via Python
python3 -c "from modules.todo_assistant.deployment_adapter import DeploymentMode; print(DeploymentMode.detect())"
```

### Issue: Features Not Available
```bash
# Check dependencies
> /vision info

# See missing packages
python3 -c "from modules.todo_assistant.deployment_adapter import get_dependency_adapter; print(get_dependency_adapter().get_missing_deps('automation'))"
```

### Issue: Paths Not Found
```bash
# Check path resolution
python3 -c "from modules.todo_assistant.deployment_adapter import get_path_adapter; pa = get_path_adapter(); print(f'Root: {pa.get_project_root()}'); print(f'Logs: {pa.get_logs_dir()}')"
```

### Issue: Desktop Automation Not Working in Container
**Expected behavior** - containers have limited desktop access.

**Solutions:**
1. Use local-CLI mode for desktop automation
2. Enable X11 forwarding (Linux)
3. Use VNC server in container
4. Use vision mode with templates

## Documentation Links

- **[Main Guide](todo-assistant.md)** - Complete feature documentation
- **[React CLI Integration](todo-assistant-react-cli.md)** - CLI commands and examples
- **[Deployment Modes](todo-assistant-deployment.md)** - Mode-specific setup and configuration
- **[Setup Instructions](todo-assistant-setup.md)** - Installation guide
- **[Module README](../src/modules/todo_assistant/README.md)** - Technical details

## Version Info

- **Version**: 0.1.0
- **Python**: 3.10+
- **Node**: 16+
- **Docker**: 20.10+
- **Status**: Production Ready ✅

## Quick Health Check

```bash
# Check all components
cd /path/to/Cyber-AutoAgent

# 1. Check Python backend
python3 scripts/test_todo_assistant.py

# 2. Check CLI bridge
python3 src/modules/todo_assistant/cli_bridge.py get_deployment_info '{}'

# 3. Check React integration (in separate terminal)
cd src/modules/interfaces/react && npm start

# 4. Test end-to-end
> /todo open notepad
> /todo-list
> /vision info
```

All checks passing? You're ready to use To-Do Assistant! 🎉

---

**Last Updated**: 2025-11-04  
**Deployment Modes**: local-cli ✅ | single-container ✅ | full-stack ✅
