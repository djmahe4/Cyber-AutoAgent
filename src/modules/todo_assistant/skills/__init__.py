"""
To-Do Assistant Skills Package
================================

High-level skills composed from MCP tools.
Import the default registry and register your own skills::

    from modules.todo_assistant.skills import default_registry

    result = default_registry.run_skill("open_and_type", name="notepad", text="hello")
"""

from .registry import SkillRegistry, default_registry

__all__ = ["SkillRegistry", "default_registry"]
