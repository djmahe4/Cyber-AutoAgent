# To-Do List Desktop UI Assistant

A comprehensive desktop automation assistant featuring MCP (Model Context Protocol), LangChain RAG, and PyAutoGUI/pywinauto for intelligent task automation.

## Overview

The To-Do Desktop Assistant allows you to:
- **Add tasks in natural language** that are automatically translated into automation actions
- **Upload PDF manuals** for RAG-based contextual assistance
- **Create custom automation scripts** for complex workflows
- **Execute tasks safely** with dry-run preview and consent checks
- **Code creatively** with Gemini-style vibe coding interface
- **Debug and monitor** with comprehensive execution logs

## Architecture

```
todo_assistant/
├── mcp_server/          # MCP tools for OS automation
│   ├── server.py        # MCP server implementation
│   └── tools.py         # Core automation tools
├── rag_engine/          # LangChain RAG for PDF processing
│   ├── engine.py        # RAG engine with FAISS/Chroma
│   └── pdf_processor.py # PDF ingestion and chunking
├── todo_agent/          # Task management system
│   ├── agent.py         # Main TodoAgent class
│   └── task_parser.py   # Natural language task parser
├── ui_scripts/          # User-defined automation scripts
│   └── example_*.py     # Example scripts
└── frontend/            # Streamlit UI
    └── app.py           # Main UI application
```

## Features

### 1. MCP Server (OS Automation Tools)

Five core tools for desktop automation:

- **open_app(name)**: Launch applications by name
- **click_ui(label)**: Click UI elements by label or visual match
- **type_text(text)**: Type text at cursor position
- **read_screen(region)**: Extract text from screen using OCR
- **run_custom_script(file)**: Execute user-defined Python scripts

**Primary Library**: pywinauto (Windows-optimized)  
**Fallback**: pyautogui + OpenCV (cross-platform)

### 2. RAG Engine (PDF Knowledge Base)

- Upload PDF manuals and documentation
- Automatic text extraction and chunking
- Vector storage with FAISS or Chroma
- Similarity search for relevant context
- Integration with task execution for smarter automation

### 3. To-Do Agent (Task Management)

- Natural language task parsing
- Multi-step action planning
- Task status tracking (pending, in_progress, completed, failed)
- Auto-execution mode
- Dry-run preview
- Task history and logs

### 4. Custom Scripts

- User-defined Python automation scripts
- Full access to pyautogui, pywinauto, and other libraries
- Script editor in UI
- Version control ready
- Examples included

### 5. Streamlit UI

**Tabs:**
- **To-Do List**: Add, view, and manage tasks
- **PDF Upload**: Upload and index PDF manuals
- **Scripts**: Create and edit custom automation scripts
- **Vibe Coding**: Gemini-style conversational coding interface
- **Debug**: Execution logs and traces

**Features:**
- Auto-execute toggle
- Debug mode
- Real-time statistics
- Task filtering by status
- Dry-run preview

## Installation

### Prerequisites

```bash
# Python 3.10+
python --version

# Install the project
cd /path/to/Cyber-AutoAgent
pip install -e .
```

### Install To-Do Assistant Dependencies

```bash
# Core dependencies
pip install streamlit pyautogui pillow pytesseract

# Optional: For advanced features
pip install pywinauto opencv-python  # Windows users
pip install langchain-community pypdf chromadb  # For RAG
```

### System Requirements

**Linux/macOS:**
- Python 3.10+
- pyautogui dependencies: `python3-tk python3-dev`

**Windows:**
- Python 3.10+
- pywinauto for native Windows automation

**OCR (Optional):**
- Tesseract OCR for screen reading
  ```bash
  # Ubuntu/Debian
  sudo apt install tesseract-ocr
  
  # macOS
  brew install tesseract
  
  # Windows
  # Download installer from https://github.com/UB-Mannheim/tesseract/wiki
  ```

## Quick Start

### 1. Launch the UI

```bash
cd src/modules/todo_assistant/frontend
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

### 2. Add Your First Task

In the "To-Do List" tab:
```
open notepad then type 'Hello World' then read screen
```

Click "Add Task" → The system will parse it into:
1. `open_app(name='notepad')`
2. `type_text(text='Hello World')`
3. `read_screen()`

### 3. Execute the Task

- Enable "Auto-Execute" for immediate execution
- Or click "▶️ Execute" on individual tasks
- Use "Dry Run" to preview actions first

### 4. Upload a PDF Manual

In the "PDF Upload" tab:
1. Click "Browse files"
2. Select a PDF (e.g., software manual)
3. Click "Upload & Index"

The system will extract text and make it available for context.

## Usage Examples

### Natural Language Tasks

```
# Simple tasks
"open chrome"
"click Save button"
"type 'my document title'"
"read screen"

# Multi-step tasks
"open excel then click File then click Save"
"launch notepad and type 'Meeting notes' then read screen"

# Custom scripts
"run script 'example_screenshot.py'"
```

### Programmatic Usage

```python
from modules.todo_assistant import TodoAgent, MCPServer
from modules.todo_assistant.rag_engine import RAGEngine

# Initialize components
mcp_server = MCPServer(consent_required=True)
rag_engine = RAGEngine(vector_store="faiss")
agent = TodoAgent(mcp_server=mcp_server, rag_engine=rag_engine)

# Add and execute task
task = agent.add_task("open notepad then type 'Hello'")
result = agent.execute_task(task.id)

# Check result
if result["success"]:
    print("Task completed!")
else:
    print(f"Task failed: {result['error']}")
```

### Custom Script Example

Create `my_automation.py`:
```python
#!/usr/bin/env python3
import pyautogui
import time

def main():
    print("Starting automation...")
    
    # Your automation logic
    pyautogui.click(100, 100)
    time.sleep(0.5)
    pyautogui.write("Automated text")
    
    print("✅ Complete")
    return 0

if __name__ == "__main__":
    exit(main())
```

Add to scripts directory and run:
```
run script 'my_automation.py'
```

## Safety Features

### 1. Consent Popup (Optional)

Enable consent requirement:
```python
mcp_server = MCPServer(consent_required=True)
```

### 2. Dry-Run Preview

Preview actions before execution:
```python
result = agent.execute_task(task_id, dry_run=True)
# Returns preview of what would happen
```

### 3. Execution Logs

All actions are logged:
```python
log = mcp_server.get_execution_log()
for entry in log:
    print(entry)
```

### 4. Task Status Tracking

Monitor task state:
- `pending`: Not yet executed
- `in_progress`: Currently executing
- `completed`: Successfully finished
- `failed`: Encountered error
- `cancelled`: Cancelled by user

## Configuration

### Vector Store Selection

```python
# Use FAISS (default)
rag_engine = RAGEngine(vector_store="faiss")

# Or use Chroma
rag_engine = RAGEngine(vector_store="chroma")
```

### Custom Paths

```python
# Custom script directory
mcp_server = MCPServer()
result = mcp_server.execute_tool(
    "run_custom_script",
    file="/custom/path/script.py"
)

# Custom RAG storage
rag_engine = RAGEngine(persist_directory="./my_rag_store")
```

### Embedding Model

Uses project default (mxbai-embed-large) via Ollama. Configure in RAG engine:
```python
from langchain_community.embeddings import OllamaEmbeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
```

## API Reference

### TodoAgent

**Methods:**
- `add_task(description: str) -> Task`: Add a new task
- `execute_task(task_id: int, dry_run: bool = False) -> Dict`: Execute a task
- `get_task(task_id: int) -> Dict`: Get task details
- `list_tasks(status: Optional[TaskStatus] = None) -> List[Dict]`: List tasks
- `cancel_task(task_id: int) -> bool`: Cancel a pending task
- `get_stats() -> Dict`: Get agent statistics

### MCPServer

**Methods:**
- `list_tools() -> List[str]`: Get available tools
- `get_tool_info(tool_name: str) -> Dict`: Get tool information
- `execute_tool(tool_name: str, **kwargs) -> MCPToolResult`: Execute a tool
- `dry_run(tool_name: str, **kwargs) -> str`: Preview tool action
- `get_execution_log() -> List[Dict]`: Get execution history
- `clear_log()`: Clear execution log

### RAGEngine

**Methods:**
- `ingest_pdf(pdf_path: str) -> Dict`: Add PDF to knowledge base
- `query(query: str, k: int = 4) -> Dict`: Search for relevant context
- `get_stats() -> Dict`: Get RAG statistics

## Troubleshooting

### Import Errors

```bash
# Missing streamlit
pip install streamlit

# Missing automation libraries
pip install pyautogui pillow

# Missing RAG dependencies
pip install langchain-community pypdf faiss-cpu
```

### Permission Issues

**macOS:**
- Go to System Preferences → Security & Privacy → Accessibility
- Grant permissions to Terminal or your Python executable

**Linux:**
- Install X11 dependencies: `sudo apt install python3-tk python3-xlib`

**Windows:**
- Run as administrator if needed for certain automation tasks

### OCR Not Working

```bash
# Install Tesseract
sudo apt install tesseract-ocr  # Linux
brew install tesseract          # macOS

# Verify installation
tesseract --version
```

### Vector Store Errors

```bash
# FAISS not found
pip install faiss-cpu

# Chroma not found
pip install chromadb
```

## Advanced Features

### Vibe Coding Mode

The Gemini-style vibe coding interface allows conversational code creation:

1. Describe your automation in natural language
2. System generates Python code
3. Preview and edit the code
4. Run in sandbox or save as script
5. Commit when approved

**Note**: LLM code generation requires additional setup (not included in basic version).

### RAG-Enhanced Automation

When PDFs are uploaded, the agent can query the knowledge base:

```python
# Agent automatically queries RAG for task context
task = agent.add_task("configure settings according to manual")

# The agent will search uploaded PDFs for relevant instructions
```

### Custom Tool Creation

Extend the MCP server with custom tools:

```python
def my_custom_tool(**kwargs):
    """My custom automation tool."""
    # Your logic here
    return {"success": True, "data": "result"}

# Register tool
mcp_server.tools["my_custom_tool"] = my_custom_tool
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional MCP tools
- Enhanced task parsing (ML-based)
- LLM integration for vibe coding
- More example scripts
- Cross-platform compatibility improvements
- UI enhancements

## License

This module is part of the Cyber-AutoAgent project and follows the MIT License.

## Acknowledgments

- **MCP (Model Context Protocol)**: Anthropic's protocol for AI-OS interaction
- **LangChain**: Framework for RAG pipelines
- **PyAutoGUI**: Cross-platform GUI automation
- **pywinauto**: Windows GUI automation
- **Streamlit**: Web UI framework

---

**Remember**: Always use automation responsibly and only on systems you own or have permission to automate!
