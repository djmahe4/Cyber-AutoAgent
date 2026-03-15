"""
Skill Registry
==============

A lightweight registry for composing high-level *skills* from MCP tool calls.

A skill is a callable that accepts ``**kwargs`` and returns a result dict.
Skills are registered by name with a short description so that agents can
discover them alongside the capability manifest.

Example usage::

    from modules.todo_assistant.skills.registry import SkillRegistry

    registry = SkillRegistry()

    @registry.register("greet", description="Print a greeting")
    def greet(name: str = "world") -> dict:
        return {"message": f"Hello, {name}!"}

    result = registry.run_skill("greet", name="Alice")
    # {"message": "Hello, Alice!"}
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry that maps skill names to callables."""

    def __init__(self) -> None:
        self._skills: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def register_skill(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
    ) -> None:
        """Register a skill callable under *name*.

        Args:
            name: Unique skill identifier.
            func: Callable that implements the skill; must accept ``**kwargs``.
            description: Short human-readable description for discovery.
        """
        if name in self._skills:
            logger.warning("Overwriting existing skill '%s'", name)
        self._skills[name] = {"func": func, "description": description}
        logger.debug("Registered skill '%s'", name)

    def register(
        self,
        name: str,
        description: str = "",
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator form of :meth:`register_skill`.

        Example::

            @registry.register("my_skill", description="does something")
            def my_skill(**kwargs):
                ...
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register_skill(name, func, description)
            return func

        return decorator

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_skill(self, skill_name: str, **kwargs: Any) -> Any:
        """Execute a registered skill by name.

        Args:
            skill_name: Registered skill name.
            **kwargs: Arguments forwarded to the skill callable.

        Returns:
            Whatever the skill callable returns.

        Raises:
            KeyError: If *skill_name* is not registered.
        """
        if skill_name not in self._skills:
            raise KeyError(f"Skill '{skill_name}' is not registered. Available: {list(self._skills)}")
        logger.info("Running skill '%s' with kwargs=%s", skill_name, list(kwargs.keys()))
        return self._skills[skill_name]["func"](**kwargs)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_skills(self) -> Dict[str, str]:
        """Return a mapping of skill name → description."""
        return {name: entry["description"] for name, entry in self._skills.items()}

    def get_skill_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Return registration metadata for *name*, or ``None`` if not found."""
        entry = self._skills.get(name)
        if entry is None:
            return None
        return {"name": name, "description": entry["description"]}


# ---------------------------------------------------------------------------
# Built-in example skill: open_and_type
# ---------------------------------------------------------------------------


def _open_and_type(name: str, text: str, wait_time: int = 2, interval: float = 0.05) -> Dict[str, Any]:
    """Open an application and type text into it.

    This skill composes :func:`~modules.todo_assistant.mcp_server.tools.open_app`
    and :func:`~modules.todo_assistant.mcp_server.tools.type_text`.

    Args:
        name: Application name to open.
        text: Text to type after the application is open.
        wait_time: Seconds to wait after opening the application.
        interval: Delay between keystrokes in seconds.

    Returns:
        Dict with ``open_result`` and ``type_result`` keys.
    """
    # Import lazily to avoid circular imports at module load time and keep
    # the skills package dependency-light.
    from modules.todo_assistant.mcp_server.tools import open_app, type_text  # noqa: PLC0415

    open_result = open_app(name=name, wait_time=wait_time)
    type_result = type_text(text=text, interval=interval)
    return {
        "skill": "open_and_type",
        "open_result": open_result,
        "type_result": type_result,
        "success": open_result.get("success", False) and type_result.get("success", False),
    }


# ---------------------------------------------------------------------------
# Default registry (pre-populated with built-in skills)
# ---------------------------------------------------------------------------

#: Module-level registry pre-populated with built-in skills.
default_registry = SkillRegistry()
default_registry.register_skill(
    "open_and_type",
    _open_and_type,
    description="Open an application by name and type text into it.",
)
