# To-Do Desktop Assistant

## Overview

The To-Do Desktop Assistant is a new module in Cyber-AutoAgent that provides intelligent desktop automation capabilities. It combines Model Context Protocol (MCP) for OS interaction, LangChain RAG for knowledge retrieval, and PyAutoGUI/pywinauto for UI automation.

## Key Features

### 🎯 Natural Language Task Processing
Add tasks in plain English and watch them execute:
- "open notepad then type 'Meeting notes'"
- "launch excel and click Save"
- "run script 'backup.py'"

### 🛠️ MCP Automation Server
Five core tools for desktop interaction:
1. **open_app(name)** - Launch applications
2. **click_ui(label)** - Click UI elements by label
3. **type_text(text)** - Type text at cursor position
4. **read_screen(region)** - Extract text using OCR
5. **run_custom_script(file)** - Execute Python automation scripts

### 📚 RAG Knowledge Base
- Upload PDF manuals and documentation
- Automatic text extraction and indexing
- Context-aware task suggestions
- FAISS or Chroma vector storage

### 💻 Streamlit UI
Interactive web interface with:
- Task list management
- PDF upload and indexing
- Custom script editor
- Debug mode with execution logs
- Vibe coding interface

### 🔒 Safety Features
- **Dry-run mode**: Preview actions before execution
- **Consent checks**: Optional user approval
- **Execution logs**: Full audit trail
- **Status tracking**: Monitor task progress

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Web UI                       │
│  ┌────────────┬────────────┬──────────┬──────────────┐ │
│  │  To-Do     │    PDF     │ Scripts  │ Vibe Coding  │ │
│  │   List     │   Upload   │  Editor  │   Panel      │ │
│  └────────────┴────────────┴──────────┴──────────────┘ │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│                  Todo Agent                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Task Parser (Natural Language → Actions)         │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────┬───────────────────────────────────┐  │
│  │  Task Queue   │  Status Tracking                  │  │
│  │  (pending,    │  (pending/in_progress/            │  │
│  │  completed)   │  completed/failed/cancelled)      │  │
│  └───────────────┴───────────────────────────────────┘  │
└───────────┬────────────────────┬────────────────────────┘
            │                    │
┌───────────▼──────────┐  ┌─────▼──────────────────────┐
│    MCP Server        │  │    RAG Engine              │
│                      │  │                            │
│  • open_app          │  │  • PDF Processing          │
│  • click_ui          │  │  • Vector Storage (FAISS)  │
│  • type_text         │  │  • Similarity Search       │
│  • read_screen       │  │  • Context Retrieval       │
│  • run_custom_script │  │                            │
└──────────┬───────────┘  └────────────────────────────┘
           │
┌──────────▼────────────────────────────────────────────┐
│           Desktop Automation Layer                     │
│  ┌──────────────┬──────────────┬──────────────────┐   │
│  │  pywinauto   │  pyautogui   │  Custom Scripts  │   │
│  │  (Windows)   │  (Cross-     │  (User-defined)  │   │
│  │              │  platform)   │                  │   │
│  └──────────────┴──────────────┴──────────────────┘   │
└────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Install with dependencies
pip install -e .

# Or install optional dependencies separately
pip install streamlit pyautogui pillow pytesseract
pip install langchain-community pypdf chromadb
```

### 2. Launch UI

```bash
cd src/modules/todo_assistant/frontend
streamlit run app.py
```

Opens at http://localhost:8501

### 3. Add Your First Task

In the "To-Do List" tab:
```
open notepad then type 'Hello World' then read screen
```

Click "Add Task" and then "Execute"

## Usage Examples

### Basic Tasks

```python
from modules.todo_assistant import TodoAgent

agent = TodoAgent(auto_execute=False)

# Simple task
task = agent.add_task("open calculator")

# Multi-step task
task = agent.add_task("open excel then click File then click Save")

# Execute with dry-run preview
result = agent.execute_task(task.id, dry_run=True)
print(result)

# Actually execute
result = agent.execute_task(task.id, dry_run=False)
```

### With RAG Context

```python
from modules.todo_assistant.rag_engine import RAGEngine

# Initialize RAG
rag = RAGEngine(vector_store="faiss")

# Upload a PDF manual
result = rag.ingest_pdf("./docs/excel_manual.pdf")
print(f"Indexed {result['num_documents']} chunks")

# Create agent with RAG
agent = TodoAgent(rag_engine=rag)

# Add task - will query RAG for context
task = agent.add_task("configure Excel settings per manual")
```

### Custom Scripts

Create `my_automation.py`:
```python
#!/usr/bin/env python3
import pyautogui
import time

def main():
    # Wait for positioning
    time.sleep(3)
    
    # Click and type
    pyautogui.click(500, 300)
    time.sleep(0.5)
    pyautogui.write("Automated input")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

Execute via task:
```python
task = agent.add_task("run script 'my_automation.py'")
```

## Task Parsing

The system understands various natural language patterns:

| Pattern | Tool | Example |
|---------|------|---------|
| `open/launch/start <app>` | open_app | "open chrome" |
| `click <element>` | click_ui | "click Save button" |
| `type '<text>'` | type_text | "type 'hello'" |
| `read screen` | read_screen | "read screen" |
| `run script '<file>'` | run_custom_script | "run script 'test.py'" |

Multi-step tasks are split on:
- "then"
- "and then"
- ";"
- "after that"

Example:
```
"open notepad then type 'test' then read screen"
```
Becomes:
1. `open_app(name='notepad')`
2. `type_text(text='test')`
3. `read_screen()`

## Configuration

### Vector Store Selection

```python
# Use FAISS (default, local)
rag = RAGEngine(vector_store="faiss")

# Or Chroma
rag = RAGEngine(vector_store="chroma")
```

### Auto-Execute Mode

```python
# Auto-execute tasks immediately after adding
agent = TodoAgent(auto_execute=True)

# Manual execution (default)
agent = TodoAgent(auto_execute=False)
```

### Consent Requirement

```python
# Require user consent before execution
server = MCPServer(consent_required=True)

# Skip consent (testing only)
server = MCPServer(consent_required=False)
```

## Integration with Cyber-AutoAgent

The To-Do Assistant is designed as a standalone module but can integrate with the main Cyber-AutoAgent framework:

### Shared Memory
Both systems can use the same Mem0 memory backend:
```python
from modules.tools.memory import Mem0Tool

# Use in cyber agent
cyber_memory = Mem0Tool()

# Share with todo assistant
from modules.todo_assistant.rag_engine import RAGEngine
todo_rag = RAGEngine(persist_directory=cyber_memory.store_path)
```

### Tool Coordination
The MCP tools could be exposed to the main Strands agent:
```python
from modules.todo_assistant.mcp_server import MCPServer

mcp = MCPServer()

# Register as Strands tools
for tool_name in mcp.list_tools():
    # Register tool with Strands framework
    pass
```

## API Reference

### TodoAgent

```python
class TodoAgent:
    def __init__(
        self,
        mcp_server: Optional[MCPServer] = None,
        rag_engine: Optional[RAGEngine] = None,
        auto_execute: bool = False
    )
    
    def add_task(self, description: str) -> Task
    def execute_task(self, task_id: int, dry_run: bool = False) -> Dict
    def get_task(self, task_id: int) -> Optional[Dict]
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict]
    def cancel_task(self, task_id: int) -> bool
    def get_stats(self) -> Dict
```

### MCPServer

```python
class MCPServer:
    def __init__(self, consent_required: bool = True)
    
    def list_tools(self) -> List[str]
    def get_tool_info(self, tool_name: str) -> Optional[Dict]
    def execute_tool(self, tool_name: str, **kwargs) -> MCPToolResult
    def dry_run(self, tool_name: str, **kwargs) -> str
    def get_execution_log(self) -> List[Dict]
    def clear_log(self)
```

### RAGEngine

```python
class RAGEngine:
    def __init__(
        self,
        vector_store: str = "faiss",
        embedding_model: Optional[str] = None,
        persist_directory: Optional[str] = None
    )
    
    def ingest_pdf(self, pdf_path: str) -> Dict
    def query(self, query: str, k: int = 4) -> Dict
    def get_stats(self) -> Dict
```

## Testing

Run the test suite:
```bash
# All todo assistant tests
pytest tests/test_todo_assistant.py -v

# Quick demo
python scripts/test_todo_assistant.py
```

23 tests covering:
- MCP server initialization and tool execution
- Task parsing (single and multi-step)
- Todo agent task management
- RAG engine initialization
- Status tracking and cancellation

## Security Considerations

⚠️ **Important**: The To-Do Assistant executes automation on your desktop. Always:

1. **Test in Safe Environment**: Use a sandboxed or test system first
2. **Review Tasks**: Check parsed actions before execution
3. **Use Dry-Run**: Preview actions with `dry_run=True`
4. **Enable Consent**: Keep `consent_required=True` in production
5. **Audit Logs**: Monitor execution logs for unexpected behavior
6. **Limit Scope**: Only run on systems you own or have permission to automate

## Troubleshooting

### UI Won't Start
```bash
# Install streamlit
pip install streamlit

# Check for conflicts
streamlit --version
```

### Automation Not Working
```bash
# Install automation libraries
pip install pyautogui pillow

# For OCR
sudo apt install tesseract-ocr  # Linux
brew install tesseract          # macOS
```

### macOS Permissions
Go to System Preferences → Security & Privacy → Accessibility and grant permissions to Terminal or your Python executable.

### RAG Errors
```bash
# Install dependencies
pip install langchain-community pypdf faiss-cpu

# Or use Chroma
pip install chromadb
```

## Programmatic Capability Manifest

The MCP runtime exposes a **capability manifest** that LLM agents and sub-agents can
query programmatically to discover available tools, their JSON schemas, and platform
support — without needing to import any heavy optional dependencies.

### Importing the manifest

```python
from modules.todo_assistant.mcp_server import get_capabilities, manifest_json

# As a Python dict
caps = get_capabilities()
print(caps["schema_version"])   # "1.0"
print(caps["current_platform"]) # "win" | "mac" | "linux"
print(list(caps["tools"]))      # ['open_app', 'click_ui', 'type_text', 'read_screen', 'run_custom_script']

# As a JSON string (e.g. to send over HTTP or to an agent)
payload = manifest_json(indent=2)
print(payload)
```

### Tool entry structure

Each entry in `caps["tools"]` looks like:

```json
{
  "open_app": {
    "description": "Launch an application by name using platform-aware automation.",
    "input_schema": { "type": "object", "properties": { ... } },
    "platform_support": {
      "win": { "primary": "pywinauto", "fallback": "subprocess" },
      "mac": { "primary": "open",      "fallback": "subprocess" },
      "linux": { "primary": "subprocess", "fallback": "subprocess" }
    },
    "current_platform_method": { "primary": "subprocess", "fallback": "subprocess" }
  }
}
```

### Pydantic tool schemas

Each tool has a corresponding Pydantic model under
`modules.todo_assistant.mcp_server.schemas` for validated, type-safe invocation:

```python
from modules.todo_assistant.mcp_server.schemas import OpenAppInput, ClickUIInput

params = OpenAppInput(name="notepad", wait_time=3)
# Raises ValidationError for bad inputs automatically
```

---

## Skill Registry

High-level **skills** compose one or more MCP tool calls into reusable,
named workflows.  The module-level `default_registry` ships with one
built-in example skill (`open_and_type`).

### Using the built-in skill

```python
from modules.todo_assistant.skills import default_registry

result = default_registry.run_skill("open_and_type", name="notepad", text="Hello!")
print(result["success"])    # True / False
print(result["open_result"])
print(result["type_result"])
```

### Registering a custom skill

```python
from modules.todo_assistant.skills import SkillRegistry

registry = SkillRegistry()

@registry.register("save_and_close", description="Save a document and close the app")
def save_and_close(app: str = "notepad") -> dict:
    from modules.todo_assistant.mcp_server import click_ui
    click_ui(label="Save")
    click_ui(label="Close")
    return {"done": True}

result = registry.run_skill("save_and_close", app="notepad")
```

### Listing available skills

```python
for name, description in default_registry.list_skills().items():
    print(f"{name}: {description}")
```

---



Future enhancements:
- [ ] LLM-powered task parsing (beyond regex)
- [ ] Web browser automation (Selenium/Playwright)
- [ ] Mobile device automation
- [ ] Workflow recording and playback
- [ ] Cloud sync for tasks and scripts
- [ ] Multi-user collaboration
- [ ] Template library for common tasks
- [ ] Scheduled task execution
- [ ] Error recovery and retry logic

## Resources

- **Main Documentation**: [README.md](../src/modules/todo_assistant/README.md)
- **Setup Guide**: [todo-assistant-setup.md](todo-assistant-setup.md)
- **Example Scripts**: [ui_scripts/](../src/modules/todo_assistant/ui_scripts/)
- **Tests**: [test_todo_assistant.py](../tests/test_todo_assistant.py)

## License

Part of Cyber-AutoAgent project - MIT License

---

**Remember**: With automation comes responsibility. Always use this tool ethically and legally!
