# To-Do Desktop Assistant - Setup Guide

Complete setup instructions for the To-Do List Desktop UI Assistant.

## Overview

The To-Do Desktop Assistant is a new feature of Cyber-AutoAgent that provides:
- Natural language task automation
- PDF manual ingestion with RAG
- Custom UI automation scripts
- Streamlit-based UI
- Gemini-style vibe coding interface

## Quick Start

### 1. Install Dependencies

The core project dependencies are already specified in `pyproject.toml`. Install them:

```bash
cd /path/to/Cyber-AutoAgent
pip install -e .
```

### 2. Optional: Install Advanced Features

For full functionality, install these optional dependencies:

```bash
# OCR support (for read_screen tool)
pip install pytesseract

# Windows-specific automation (Windows only)
pip install pywinauto

# Computer vision (for advanced UI element detection)
pip install opencv-python

# Chroma vector store (alternative to FAISS)
pip install chromadb
```

### 3. Install System Dependencies

**Tesseract OCR (for screen reading):**

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Display server (Linux):**

```bash
sudo apt install python3-tk python3-xlib
```

### 4. Launch the Application

```bash
cd src/modules/todo_assistant/frontend
streamlit run app.py
```

The UI will open at `http://localhost:8501`

## Configuration

### Ollama Setup (Required for RAG)

The RAG engine uses Ollama for embeddings. Ensure Ollama is installed and running:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull embedding model
ollama pull mxbai-embed-large
```

### Environment Variables

Optional environment variables:

```bash
# Custom RAG storage location
export TODO_ASSISTANT_RAG_DIR="./outputs/todo_rag"

# Custom scripts directory
export TODO_ASSISTANT_SCRIPTS_DIR="./custom_scripts"

# Ollama host (if not localhost)
export OLLAMA_HOST="http://localhost:11434"
```

## Platform-Specific Setup

### macOS

Grant accessibility permissions:
1. Go to System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from the list
3. Add Terminal (or your Python executable)
4. Check the box to enable access

### Linux

Install X11 dependencies:
```bash
sudo apt install python3-tk python3-xlib scrot
```

### Windows

For best results, install pywinauto:
```bash
pip install pywinauto
```

Run scripts with appropriate permissions (may need administrator access for some automation).

## Verification

### Test Installation

```python
# Test MCP server
from modules.todo_assistant.mcp_server import MCPServer

server = MCPServer()
print(f"Available tools: {server.list_tools()}")

# Test RAG engine
from modules.todo_assistant.rag_engine import RAGEngine

rag = RAGEngine()
print(f"RAG initialized: {rag.get_stats()}")

# Test Todo agent
from modules.todo_assistant.todo_agent import TodoAgent

agent = TodoAgent()
print(f"Agent ready: {agent.get_stats()}")
```

### Run Example Script

```bash
cd src/modules/todo_assistant/ui_scripts
python example_screenshot.py
```

Should create a screenshot in `./outputs/screenshots/`

## Troubleshooting

### Import Errors

If you see import errors:

```bash
# Reinstall project
pip install -e . --force-reinstall

# Or install missing packages individually
pip install streamlit pyautogui pillow langchain-community pypdf
```

### Ollama Connection Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama
killall ollama
ollama serve
```

### Permission Denied (macOS/Linux)

```bash
# Check script permissions
chmod +x src/modules/todo_assistant/ui_scripts/*.py

# For macOS, grant accessibility permissions (see above)
```

### Streamlit Won't Start

```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit

# Run with verbose output
streamlit run app.py --logger.level=debug
```

### FAISS Errors

```bash
# Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu

# Or try GPU version if you have CUDA
pip install faiss-gpu
```

## Usage Examples

### Example 1: Simple Task

```
Task: "open notepad"
```

This will:
1. Parse task into `open_app(name='notepad')`
2. Execute the MCP tool
3. Launch Notepad

### Example 2: Multi-Step Task

```
Task: "open excel then click File then click Save"
```

This will:
1. Open Excel
2. Click the "File" menu
3. Click "Save" button

### Example 3: Custom Script

```
Task: "run script 'example_screenshot.py'"
```

This will execute the custom script which takes a screenshot.

### Example 4: With RAG Context

1. First, upload a PDF manual (e.g., Excel manual)
2. Then add task: "configure settings as per manual"
3. The agent will query the RAG engine for relevant instructions

## Advanced Configuration

### Custom Vector Store

Use Chroma instead of FAISS:

```python
from modules.todo_assistant.rag_engine import RAGEngine

rag = RAGEngine(
    vector_store="chroma",
    persist_directory="./my_chroma_db"
)
```

### Custom Embedding Model

```python
# Edit rag_engine/engine.py to change model:
# embeddings = OllamaEmbeddings(model="your-model-name")
```

### Disable Consent Popup

For testing, disable consent requirement:

```python
from modules.todo_assistant.mcp_server import MCPServer

server = MCPServer(consent_required=False)
```

**Warning**: Only disable consent in safe, controlled environments!

## Integration with Cyber-AutoAgent

The To-Do Assistant is designed as a standalone module but can integrate with the main Cyber-AutoAgent:

```python
# In future versions, could integrate with cyber agent tools
from modules.todo_assistant import TodoAgent
from modules.agents.cyber_autoagent import create_agent

# Share memory, tools, etc.
```

## Development

### Adding Custom Tools

Add new MCP tools in `mcp_server/tools.py`:

```python
def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Description of the tool."""
    try:
        # Your implementation
        return {"success": True, "result": "data"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

Register in `mcp_server/server.py`:

```python
self.tools["my_new_tool"] = my_new_tool
```

### Adding Task Patterns

Add new patterns in `todo_agent/task_parser.py`:

```python
{
    "pattern": r"your regex pattern",
    "tool": "tool_name",
    "extract": lambda m: {"param": m.group(1)}
}
```

### Testing

```bash
# Run tests (when implemented)
pytest tests/test_todo_assistant.py

# Or test manually
python -m modules.todo_assistant.mcp_server.tools
```

## Security Considerations

⚠️ **Important**: The To-Do Assistant executes automation on your desktop. Always:

1. **Review tasks** before execution
2. **Use dry-run** for new tasks
3. **Test scripts** in safe environment first
4. **Limit permissions** to necessary only
5. **Monitor logs** for unexpected behavior
6. **Use consent popup** in production

## Support

For issues or questions:
1. Check the main README: `src/modules/todo_assistant/README.md`
2. Review example scripts in `ui_scripts/`
3. Check troubleshooting section above
4. Open an issue on GitHub

## Roadmap

Future enhancements:
- [ ] LLM-powered task parsing (beyond regex)
- [ ] Gemini API integration for vibe coding
- [ ] More pre-built automation templates
- [ ] Browser automation (Selenium/Playwright)
- [ ] Mobile device automation
- [ ] Workflow recording and playback
- [ ] Multi-user collaboration
- [ ] Cloud sync for tasks and scripts

## License

Part of Cyber-AutoAgent project - MIT License

---

**Version**: 0.1.0  
**Last Updated**: 2024  
**Status**: Beta - Use in controlled environments only
