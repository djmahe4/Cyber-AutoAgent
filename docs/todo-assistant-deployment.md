# To-Do Assistant - Deployment Modes

## Overview

The To-Do Desktop Assistant supports all three deployment modes of Cyber-AutoAgent:
1. **local-cli**: Direct Python execution on the host
2. **single-container**: Docker container with the core agent
3. **full-stack**: Full stack with observability services

## Deployment Modes

### 1. Local CLI Mode

**Description**: Direct Python execution without containers

**When to use**:
- Development and testing
- Quick experimentation
- Systems without Docker
- Full access to host desktop automation

**Setup**:
```bash
# Install dependencies
pip install -e .

# Optional: Install UI automation libraries
pip install pyautogui pillow opencv-python

# Run React CLI
cd src/modules/interfaces/react
npm start

# Or run Streamlit UI
cd src/modules/todo_assistant/frontend
streamlit run app.py
```

**Characteristics**:
- ✅ Direct host system access
- ✅ Native desktop automation
- ✅ Full file system access
- ✅ No Docker overhead
- ⚠️ Requires manual dependency installation
- ⚠️ No observability stack

**File Paths**:
- Project root: `$(pwd)`
- Outputs: `./outputs`
- Logs: `./outputs/logs`
- Screenshots: `./outputs/logs/screenshots`

### 2. Single Container Mode

**Description**: Core agent running in Docker container

**When to use**:
- Isolated execution environment
- Consistent runtime across systems
- Simpler dependency management
- Want containerization without full stack

**Setup**:
```bash
# Build and start container
docker-compose up -d cyber-autoagent

# Access shell
docker exec -it cyber-autoagent bash

# Inside container
cd /app
node src/modules/interfaces/react/dist/index.js
```

**Characteristics**:
- ✅ Isolated environment
- ✅ Pre-installed dependencies
- ✅ Consistent runtime
- ✅ Mounted volumes for persistence
- ⚠️ Limited host desktop access
- ⚠️ No observability stack

**File Paths**:
- Project root: `/app`
- Outputs: `/app/outputs` (mounted to `../outputs`)
- Logs: `/app/outputs/logs`
- Screenshots: `/app/outputs/logs/screenshots`

### 3. Full Stack Mode

**Description**: All services including Langfuse observability

**When to use**:
- Production deployments
- Need observability and tracing
- Performance monitoring
- Team environments

**Setup**:
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Access agent shell
docker exec -it cyber-autoagent bash
```

**Characteristics**:
- ✅ Full observability stack
- ✅ Langfuse tracing
- ✅ PostgreSQL for persistence
- ✅ Performance monitoring
- ✅ Team collaboration ready
- ⚠️ Higher resource usage
- ⚠️ More complex setup

**Services**:
- `cyber-autoagent`: Main agent container
- `langfuse-web`: Observability web UI
- `langfuse-worker`: Background processing
- `postgres`: Data persistence

**File Paths**: Same as single-container mode

## Deployment Adapter

The To-Do Assistant automatically adapts to the deployment mode using the `deployment_adapter.py` module.

### Automatic Detection

```python
from modules.todo_assistant.deployment_adapter import DeploymentMode

# Detects mode automatically
mode = DeploymentMode.detect()
print(f"Running in: {mode}")

# Checks
is_container = DeploymentMode.is_container()
is_local = DeploymentMode.is_local()
```

### Path Resolution

```python
from modules.todo_assistant.deployment_adapter import get_path_adapter

path_adapter = get_path_adapter()

# Automatically resolves paths for current mode
project_root = path_adapter.get_project_root()
outputs_dir = path_adapter.get_outputs_dir()
logs_dir = path_adapter.get_logs_dir()
scripts_dir = path_adapter.get_scripts_dir()
```

### Dependency Checking

```python
from modules.todo_assistant.deployment_adapter import get_dependency_adapter

dep_adapter = get_dependency_adapter()

# Check available features
if dep_adapter.has_vision_mode():
    print("Vision mode available")

if dep_adapter.has_rag():
    print("RAG engine available")

# Get missing dependencies
missing = dep_adapter.get_missing_deps("automation")
if missing:
    print(f"Install: pip install {' '.join(missing)}")
```

### Configuration

```python
from modules.todo_assistant.deployment_adapter import get_config_adapter

config_adapter = get_config_adapter()

# Get deployment-specific config
mcp_config = config_adapter.get_mcp_config()
rag_config = config_adapter.get_rag_config()
logging_config = config_adapter.get_logging_config()

# Get full deployment info
info = config_adapter.get_deployment_info()
```

## Feature Availability by Mode

| Feature | Local CLI | Single Container | Full Stack |
|---------|-----------|------------------|------------|
| Task Management | ✅ | ✅ | ✅ |
| MCP Tools | ✅ | ✅ | ✅ |
| Host Desktop Access | ✅ | ⚠️ Limited | ⚠️ Limited |
| Vision Mode | ✅* | ✅* | ✅* |
| RAG Engine | ✅* | ✅* | ✅* |
| Screenshots | ✅* | ✅* | ✅* |
| Action Logging | ✅ | ✅ | ✅ |
| Observability | ❌ | ❌ | ✅ |
| Langfuse Tracing | ❌ | ❌ | ✅ |

*Depends on installed dependencies

## Desktop Automation in Containers

### Limitations

Desktop automation from containers has limitations:

1. **No Direct Display Access**: Containers don't have access to host display
2. **Limited UI Interaction**: Cannot directly interact with host GUI apps
3. **Vision Mode Only**: Use vision mode for containerized automation

### Workarounds

**Option 1: Use Local CLI Mode**
```bash
# Run without containers for full desktop access
cd src/modules/interfaces/react
npm start
```

**Option 2: X11 Forwarding (Linux)**
```bash
# Mount X11 socket
docker run -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  cyber-autoagent
```

**Option 3: VNC in Container**
```dockerfile
# Install VNC server in container
RUN apt-get install -y x11vnc xvfb

# Start virtual display
ENV DISPLAY=:99
CMD ["x11vnc", "-forever", "-usepw", "-create"]
```

**Option 4: Vision Mode with Templates**
```python
# Use template-based automation in container
automation = PlatformAutomation(vision_mode=True)
result = automation.click_ui_vision(
    label="button",
    template_path="/app/templates/button.png"
)
```

## React CLI Integration

The React CLI automatically detects and adapts to the deployment mode:

```bash
# Local CLI
npm start

# Container (from within)
docker exec -it cyber-autoagent bash
node /app/src/modules/interfaces/react/dist/index.js

# Check deployment info
> /todo-run 1
> cat /app/outputs/logs/session_*/deployment_info.json
```

## Switching Modes

### From Local to Container

```bash
# 1. Build container
docker-compose build

# 2. Start container
docker-compose up -d cyber-autoagent

# 3. Access shell
docker exec -it cyber-autoagent bash

# 4. Run CLI
cd /app
node src/modules/interfaces/react/dist/index.js
```

### From Container to Local

```bash
# 1. Stop containers
docker-compose down

# 2. Run locally
cd src/modules/interfaces/react
npm start
```

### From Single to Full Stack

```bash
# Start all services
docker-compose up -d
```

## Environment Variables

Configure behavior via environment variables:

```bash
# Deployment mode (auto-detected)
export CONTAINER=docker          # Mark as container environment

# Paths (local CLI mode)
export CYBER_PROJECT_ROOT=/path/to/project

# Features
export TODO_ENABLE_RAG=true
export TODO_ENABLE_SCREENSHOTS=true
export TODO_VISION_MODE=false

# Logging
export TODO_LOG_LEVEL=INFO
export TODO_LOG_DIR=./custom_logs

# Observability (full-stack mode)
export ENABLE_OBSERVABILITY=true
export LANGFUSE_HOST=http://langfuse-web:3000
```

## Testing Each Mode

### Test Local CLI

```bash
cd src/modules/todo_assistant
python3 cli_bridge.py get_deployment_info '{}'
```

Expected output:
```json
{
  "success": true,
  "deployment": {
    "mode": "local-cli",
    "is_container": false,
    "is_local": true
  }
}
```

### Test Single Container

```bash
docker-compose up -d cyber-autoagent
docker exec cyber-autoagent python3 /app/src/modules/todo_assistant/cli_bridge.py get_deployment_info '{}'
```

Expected output:
```json
{
  "success": true,
  "deployment": {
    "mode": "single-container",
    "is_container": true,
    "is_local": false
  }
}
```

### Test Full Stack

```bash
docker-compose up -d
docker exec cyber-autoagent python3 /app/src/modules/todo_assistant/cli_bridge.py get_deployment_info '{}'
```

Expected output:
```json
{
  "success": true,
  "deployment": {
    "mode": "full-stack",
    "is_container": true,
    "is_local": false,
    "features": {
      "observability": true
    }
  }
}
```

## Best Practices

### Development
- Use **local-cli** mode for active development
- Direct desktop access for testing automation
- Fast iteration without container rebuilds

### Testing
- Use **single-container** mode for integration testing
- Consistent environment across team
- Easier CI/CD integration

### Production
- Use **full-stack** mode for deployments
- Full observability and monitoring
- Better resource management

### Desktop Automation
- Always use **local-cli** mode for desktop automation
- Containers have limited desktop access
- Use vision mode in containers if needed

## Troubleshooting

### Mode Not Detected

```python
# Check deployment info
from modules.todo_assistant.deployment_adapter import get_config_adapter
info = get_config_adapter().get_deployment_info()
print(info)
```

### Paths Not Resolving

```python
# Check path adapter
from modules.todo_assistant.deployment_adapter import get_path_adapter
adapter = get_path_adapter()
print(f"Project root: {adapter.get_project_root()}")
print(f"Outputs: {adapter.get_outputs_dir()}")
```

### Dependencies Missing

```python
# Check available dependencies
from modules.todo_assistant.deployment_adapter import get_dependency_adapter
adapter = get_dependency_adapter()
print(f"Available: {adapter.available_deps}")
print(f"Missing for automation: {adapter.get_missing_deps('automation')}")
```

### Container Can't Access Desktop

This is expected behavior. Solutions:
1. Use local-CLI mode for desktop automation
2. Set up X11 forwarding (Linux)
3. Use VNC server in container
4. Use vision mode with templates

## Migration Guide

### Upgrading from Pre-Deployment-Adapter Version

The deployment adapter is backward compatible. No changes required for existing code.

**Optional**: Update to use adapter explicitly:

```python
# Before
logs_dir = "./logs"

# After
from modules.todo_assistant.deployment_adapter import get_path_adapter
logs_dir = get_path_adapter().get_logs_dir()
```

---

**Version**: 0.1.0  
**Last Updated**: 2025-11-04  
**Status**: Production Ready - All Modes Supported ✅
