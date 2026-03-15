"""
MCP Tool Pydantic Schemas
=========================

Typed input/output models for each MCP automation tool.
These schemas enable LLM agents to discover and validate tool parameters
programmatically without importing heavy optional dependencies.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Base classes
# ---------------------------------------------------------------------------


class ToolInput(BaseModel):
    """Base class for all tool input models."""

    model_config = {"extra": "forbid"}


class ToolOutput(BaseModel):
    """Base class for all tool output models."""

    success: bool
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Per-tool input schemas
# ---------------------------------------------------------------------------


class OpenAppInput(ToolInput):
    """Input schema for the open_app tool."""

    name: str = Field(..., description="Application name or path to executable")
    wait_time: int = Field(2, ge=0, description="Seconds to wait after launching")


class ClickUIInput(ToolInput):
    """Input schema for the click_ui tool."""

    label: str = Field(..., description="Text label or description of the UI element to click")
    confidence: float = Field(0.8, ge=0.0, le=1.0, description="Confidence threshold for vision-mode matching")
    template_path: Optional[str] = Field(None, description="Path to template image for vision-mode matching")


class TypeTextInput(ToolInput):
    """Input schema for the type_text tool."""

    text: str = Field(..., description="Text to type at the current cursor position")
    interval: float = Field(0.05, ge=0.0, description="Delay between keystrokes in seconds")


class ReadScreenInput(ToolInput):
    """Input schema for the read_screen tool."""

    region: Optional[Dict[str, int]] = Field(
        None,
        description="Optional screen region with keys 'x', 'y', 'width', 'height'",
    )


class RunCustomScriptInput(ToolInput):
    """Input schema for the run_custom_script tool."""

    file: str = Field(..., description="Path to the Python script file to execute")


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------

#: Mapping of tool name → its input Pydantic model class.
TOOL_SCHEMAS: Dict[str, type] = {
    "open_app": OpenAppInput,
    "click_ui": ClickUIInput,
    "type_text": TypeTextInput,
    "read_screen": ReadScreenInput,
    "run_custom_script": RunCustomScriptInput,
}
