"""
MCP Server Implementation
=========================

Central server for managing MCP tools and handling automation requests.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .tools import open_app, click_ui, type_text, read_screen, run_custom_script

logger = logging.getLogger(__name__)


@dataclass
class MCPToolResult:
    """Result from an MCP tool execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPServer:
    """
    MCP Server for OS automation.
    
    Provides a centralized interface for executing OS automation tools.
    Supports tool registration, execution, and result handling.
    """
    
    def __init__(self, consent_required: bool = True):
        """
        Initialize MCP Server.
        
        Args:
            consent_required: Whether to require user consent before executing tools
        """
        self.consent_required = consent_required
        self.tools = {
            "open_app": open_app,
            "click_ui": click_ui,
            "type_text": type_text,
            "read_screen": read_screen,
            "run_custom_script": run_custom_script
        }
        self.execution_log: List[Dict[str, Any]] = []
        logger.info("MCP Server initialized with %d tools", len(self.tools))
    
    def list_tools(self) -> List[str]:
        """
        Get list of available tools.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool metadata including description and parameters
        """
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        return {
            "name": tool_name,
            "description": tool.__doc__,
            "parameters": getattr(tool, "__annotations__", {})
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> MCPToolResult:
        """
        Execute an MCP tool.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            MCPToolResult with execution status and data
        """
        if tool_name not in self.tools:
            return MCPToolResult(
                success=False,
                message=f"Tool '{tool_name}' not found",
                error=f"Available tools: {', '.join(self.list_tools())}"
            )
        
        try:
            logger.info("Executing tool: %s with args: %s", tool_name, kwargs)
            tool = self.tools[tool_name]
            result = tool(**kwargs)
            
            # Log execution
            self.execution_log.append({
                "tool": tool_name,
                "args": kwargs,
                "result": result,
                "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
            })
            
            return MCPToolResult(
                success=True,
                message=f"Tool '{tool_name}' executed successfully",
                data=result
            )
        except Exception as e:
            logger.error("Tool execution failed: %s", str(e), exc_info=True)
            return MCPToolResult(
                success=False,
                message=f"Tool '{tool_name}' execution failed",
                error=str(e)
            )
    
    def dry_run(self, tool_name: str, **kwargs) -> str:
        """
        Preview what a tool would do without executing it.
        
        Args:
            tool_name: Name of the tool
            **kwargs: Tool-specific parameters
            
        Returns:
            Description of the action that would be performed
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        descriptions = {
            "open_app": f"Would open application: {kwargs.get('name', 'unknown')}",
            "click_ui": f"Would click UI element: {kwargs.get('label', 'unknown')}",
            "type_text": f"Would type text: {kwargs.get('text', 'unknown')}",
            "read_screen": "Would read text from screen",
            "run_custom_script": f"Would run script: {kwargs.get('file', 'unknown')}"
        }
        
        return descriptions.get(tool_name, f"Would execute tool: {tool_name}")
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        Get the execution log.
        
        Returns:
            List of executed tool records
        """
        return self.execution_log.copy()
    
    def clear_log(self):
        """Clear the execution log."""
        self.execution_log.clear()
        logger.info("Execution log cleared")
