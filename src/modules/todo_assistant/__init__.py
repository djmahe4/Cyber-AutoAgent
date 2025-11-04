"""
To-Do List Desktop UI Assistant Module
======================================

A comprehensive desktop automation assistant featuring:
- MCP-based OS automation tools
- LangChain RAG with PDF manual ingestion
- UI automation via PyAutoGUI/pywinauto
- Task-driven automation system
- Gemini-style vibe coding interface

Author: Cyber-AutoAgent Team
License: MIT
"""

__version__ = "0.1.0"

from .todo_agent import TodoAgent
from .mcp_server import MCPServer

__all__ = ["TodoAgent", "MCPServer"]
