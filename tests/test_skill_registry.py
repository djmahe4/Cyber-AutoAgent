"""
Tests for the Skill Registry
==============================

Validates SkillRegistry registration, execution, discovery, and
error-handling behaviour without requiring any OS-specific libraries.
"""

import logging

import pytest

from modules.todo_assistant.skills.registry import SkillRegistry, default_registry


class TestSkillRegistry:
    """Unit tests for SkillRegistry."""

    def _make_registry(self) -> SkillRegistry:
        return SkillRegistry()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def test_register_and_list(self):
        reg = self._make_registry()
        reg.register_skill("greet", lambda name="world": f"Hello, {name}!", description="Greets someone")
        skills = reg.list_skills()
        assert "greet" in skills
        assert skills["greet"] == "Greets someone"

    def test_register_decorator(self):
        reg = self._make_registry()

        @reg.register("add", description="Adds two numbers")
        def add(a: int = 0, b: int = 0) -> int:
            return a + b

        assert "add" in reg.list_skills()

    def test_overwrite_warns(self, caplog):
        reg = self._make_registry()
        reg.register_skill("dup", lambda: 1, description="first")
        with caplog.at_level(logging.WARNING):
            reg.register_skill("dup", lambda: 2, description="second")
        assert any("Overwriting" in r.message for r in caplog.records)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def test_run_skill_basic(self):
        reg = self._make_registry()
        reg.register_skill("echo", lambda msg="hi": {"echoed": msg})
        result = reg.run_skill("echo", msg="ping")
        assert result == {"echoed": "ping"}

    def test_run_skill_default_kwargs(self):
        reg = self._make_registry()
        reg.register_skill("const", lambda: 42)
        assert reg.run_skill("const") == 42

    def test_run_skill_unknown_raises(self):
        reg = self._make_registry()
        with pytest.raises(KeyError, match="not registered"):
            reg.run_skill("nonexistent")

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def test_list_skills_empty(self):
        reg = self._make_registry()
        assert reg.list_skills() == {}

    def test_get_skill_info_existing(self):
        reg = self._make_registry()
        reg.register_skill("info_test", lambda: None, description="test desc")
        info = reg.get_skill_info("info_test")
        assert info is not None
        assert info["name"] == "info_test"
        assert info["description"] == "test desc"

    def test_get_skill_info_missing_returns_none(self):
        reg = self._make_registry()
        assert reg.get_skill_info("does_not_exist") is None

    # ------------------------------------------------------------------
    # Multiple skills coexist
    # ------------------------------------------------------------------

    def test_multiple_skills(self):
        reg = self._make_registry()
        reg.register_skill("a", lambda: "A")
        reg.register_skill("b", lambda: "B")
        reg.register_skill("c", lambda: "C")
        assert set(reg.list_skills().keys()) == {"a", "b", "c"}
        assert reg.run_skill("b") == "B"


class TestDefaultRegistry:
    """Tests for the pre-populated module-level default_registry."""

    def test_open_and_type_skill_registered(self):
        skills = default_registry.list_skills()
        assert "open_and_type" in skills

    def test_open_and_type_has_description(self):
        skills = default_registry.list_skills()
        assert skills["open_and_type"]  # non-empty description

    def test_open_and_type_skill_info(self):
        info = default_registry.get_skill_info("open_and_type")
        assert info is not None
        assert info["name"] == "open_and_type"

    def test_open_and_type_callable(self, mocker):
        """Verify open_and_type calls open_app and type_text and returns a result dict."""
        mock_open = mocker.patch(
            "modules.todo_assistant.mcp_server.tools.open_app",
            return_value={"success": True, "app": "notepad"},
        )
        mock_type = mocker.patch(
            "modules.todo_assistant.mcp_server.tools.type_text",
            return_value={"success": True, "text_length": 5},
        )

        result = default_registry.run_skill("open_and_type", name="notepad", text="hello")

        assert result["skill"] == "open_and_type"
        assert result["success"] is True
        assert "open_result" in result
        assert "type_result" in result
        mock_open.assert_called_once_with(name="notepad", wait_time=2)
        mock_type.assert_called_once_with(text="hello", interval=0.05)

    def test_open_and_type_propagates_failure(self, mocker):
        """If open_app fails, overall success should be False."""
        mocker.patch(
            "modules.todo_assistant.mcp_server.tools.open_app",
            return_value={"success": False, "error": "app not found"},
        )
        mocker.patch(
            "modules.todo_assistant.mcp_server.tools.type_text",
            return_value={"success": True, "text_length": 5},
        )

        result = default_registry.run_skill("open_and_type", name="badapp", text="hi")
        assert result["success"] is False
