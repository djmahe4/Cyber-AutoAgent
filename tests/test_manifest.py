"""
Tests for MCP Capability Manifest
====================================

Validates that get_capabilities() returns a well-formed structure and that
the pydantic schemas accept and reject sample inputs correctly.
"""

import json

import pytest

from modules.todo_assistant.mcp_server.manifest import get_capabilities, manifest_json
from modules.todo_assistant.mcp_server.schemas import (
    ClickUIInput,
    OpenAppInput,
    ReadScreenInput,
    RunCustomScriptInput,
    TOOL_SCHEMAS,
    TypeTextInput,
)


class TestGetCapabilities:
    """Tests for the get_capabilities() manifest function."""

    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)

    def test_schema_version_present(self):
        caps = get_capabilities()
        assert "schema_version" in caps
        assert caps["schema_version"] == "1.0"

    def test_current_platform_present(self):
        caps = get_capabilities()
        assert "current_platform" in caps
        assert caps["current_platform"] in ("win", "mac", "linux")

    def test_tools_key_present(self):
        caps = get_capabilities()
        assert "tools" in caps
        assert isinstance(caps["tools"], dict)

    def test_all_five_tools_present(self):
        caps = get_capabilities()
        tools = caps["tools"]
        expected = {"open_app", "click_ui", "type_text", "read_screen", "run_custom_script"}
        assert expected == set(tools.keys())

    def test_each_tool_has_required_keys(self):
        caps = get_capabilities()
        for tool_name, tool_info in caps["tools"].items():
            assert "description" in tool_info, f"{tool_name} missing 'description'"
            assert "input_schema" in tool_info, f"{tool_name} missing 'input_schema'"
            assert "platform_support" in tool_info, f"{tool_name} missing 'platform_support'"

    def test_input_schema_is_json_schema_dict(self):
        caps = get_capabilities()
        for tool_name, tool_info in caps["tools"].items():
            schema = tool_info["input_schema"]
            assert isinstance(schema, dict), f"{tool_name}: input_schema should be a dict"
            assert "type" in schema or "properties" in schema, (
                f"{tool_name}: input_schema looks malformed"
            )

    def test_manifest_json_returns_string(self):
        result = manifest_json()
        assert isinstance(result, str)
        assert "open_app" in result

    def test_manifest_json_with_indent(self):
        result = manifest_json(indent=2)
        parsed = json.loads(result)
        assert "tools" in parsed


class TestToolSchemas:
    """Tests for individual pydantic input schemas."""

    def test_open_app_valid(self):
        obj = OpenAppInput(name="notepad")
        assert obj.name == "notepad"
        assert obj.wait_time == 2  # default

    def test_open_app_custom_wait(self):
        obj = OpenAppInput(name="chrome", wait_time=5)
        assert obj.wait_time == 5

    def test_open_app_rejects_extra_fields(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OpenAppInput(name="notepad", unknown_field="bad")

    def test_click_ui_valid(self):
        obj = ClickUIInput(label="Save")
        assert obj.label == "Save"
        assert obj.confidence == 0.8
        assert obj.template_path is None

    def test_click_ui_with_template(self):
        obj = ClickUIInput(label="OK", confidence=0.9, template_path="/tmp/ok.png")
        assert obj.template_path == "/tmp/ok.png"

    def test_click_ui_confidence_bounds(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ClickUIInput(label="X", confidence=1.5)

        with pytest.raises(ValidationError):
            ClickUIInput(label="X", confidence=-0.1)

    def test_type_text_valid(self):
        obj = TypeTextInput(text="hello world")
        assert obj.text == "hello world"
        assert obj.interval == 0.05

    def test_read_screen_no_region(self):
        obj = ReadScreenInput()
        assert obj.region is None

    def test_read_screen_with_region(self):
        obj = ReadScreenInput(region={"x": 0, "y": 0, "width": 800, "height": 600})
        assert obj.region["width"] == 800

    def test_run_custom_script_valid(self):
        obj = RunCustomScriptInput(file="backup.py")
        assert obj.file == "backup.py"

    def test_tool_schemas_registry_completeness(self):
        expected = {"open_app", "click_ui", "type_text", "read_screen", "run_custom_script"}
        assert set(TOOL_SCHEMAS.keys()) == expected

    def test_tool_schemas_are_pydantic_models(self):
        from pydantic import BaseModel

        for name, cls in TOOL_SCHEMAS.items():
            assert issubclass(cls, BaseModel), f"{name} schema is not a pydantic BaseModel"
