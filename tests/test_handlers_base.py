#!/usr/bin/env python3
"""
Tests for the modules/handlers/base module.
"""

import os
from unittest.mock import patch

import pytest

from modules.handlers.base import (
    CONTENT_PREVIEW_LENGTH,
    DEFAULT_LANGFUSE_HOST,
    LANGFUSE_HOST,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    MAX_CONTENT_DISPLAY_LENGTH,
    HandlerError,
    HandlerState,
    StepLimitReached,
    is_docker,
)


class TestIsDocker:
    """Test is_docker function."""

    def test_is_docker_when_dockerenv_exists(self):
        """Test that is_docker returns True when /.dockerenv exists."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path == "/.dockerenv"
            assert is_docker() is True

    def test_is_docker_when_app_exists(self):
        """Test that is_docker returns True when /app exists."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path == "/app"
            assert is_docker() is True

    def test_is_docker_when_neither_exists(self):
        """Test that is_docker returns False when neither path exists."""
        with patch("os.path.exists", return_value=False):
            assert is_docker() is False


class TestConstants:
    """Test module constants."""

    def test_content_preview_length(self):
        """Test CONTENT_PREVIEW_LENGTH constant."""
        assert CONTENT_PREVIEW_LENGTH == 200

    def test_max_content_display_length(self):
        """Test MAX_CONTENT_DISPLAY_LENGTH constant."""
        assert MAX_CONTENT_DISPLAY_LENGTH == 500

    def test_langfuse_constants(self):
        """Test Langfuse-related constants."""
        assert isinstance(DEFAULT_LANGFUSE_HOST, str)
        assert isinstance(LANGFUSE_HOST, str)
        assert isinstance(LANGFUSE_PUBLIC_KEY, str)
        assert isinstance(LANGFUSE_SECRET_KEY, str)


class TestHandlerState:
    """Test HandlerState dataclass."""

    def test_handler_state_defaults(self):
        """Test that HandlerState initializes with correct defaults."""
        state = HandlerState()
        
        # Step tracking
        assert state.steps == 0
        assert state.max_steps == 100
        assert state.step_limit_reached is False
        
        # Tool tracking
        assert isinstance(state.shown_tools, set)
        assert len(state.shown_tools) == 0
        assert isinstance(state.tool_use_map, dict)
        assert isinstance(state.tool_results, dict)
        assert isinstance(state.tools_used, list)
        
        # Display state
        assert state.last_was_tool is False
        assert state.last_was_reasoning is False
        assert state.suppress_parent_handler is False
        assert state.suppress_parent_output is False
        
        # Operation tracking
        assert state.operation_id is None
        assert state.report_generated is False
        assert state.memory_operations == 0
        assert state.stop_tool_used is False
        assert isinstance(state.created_tools, list)
        assert state.start_time == 0.0
        assert state.evaluation_triggered is False
        assert state.evaluation_thread is None
        
        # Swarm operation tracking
        assert state.in_swarm_operation is False
        assert isinstance(state.swarm_agents, list)
        assert state.swarm_step_count == 0
        assert state.current_swarm_agent is None
        
        # Tool effectiveness tracking
        assert isinstance(state.tool_effectiveness, dict)

    def test_handler_state_custom_values(self):
        """Test that HandlerState accepts custom values."""
        state = HandlerState(
            steps=5,
            max_steps=50,
            operation_id="test_op_123",
            step_limit_reached=True,
        )
        
        assert state.steps == 5
        assert state.max_steps == 50
        assert state.operation_id == "test_op_123"
        assert state.step_limit_reached is True

    def test_handler_state_mutable_defaults(self):
        """Test that mutable default fields are independent between instances."""
        state1 = HandlerState()
        state2 = HandlerState()
        
        # Modify state1's sets and lists
        state1.shown_tools.add("tool1")
        state1.tools_used.append("tool2")
        state1.created_tools.append("tool3")
        
        # Verify state2 is unaffected
        assert "tool1" not in state2.shown_tools
        assert "tool2" not in state2.tools_used
        assert "tool3" not in state2.created_tools

    def test_handler_state_swarm_tracking(self):
        """Test swarm-related state tracking."""
        state = HandlerState(
            in_swarm_operation=True,
            swarm_agents=["agent1", "agent2"],
            swarm_step_count=3,
            current_swarm_agent="agent1"
        )
        
        assert state.in_swarm_operation is True
        assert len(state.swarm_agents) == 2
        assert state.swarm_step_count == 3
        assert state.current_swarm_agent == "agent1"


class TestHandlerError:
    """Test HandlerError exception."""

    def test_handler_error_is_exception(self):
        """Test that HandlerError is an Exception."""
        assert issubclass(HandlerError, Exception)

    def test_handler_error_can_be_raised(self):
        """Test that HandlerError can be raised and caught."""
        with pytest.raises(HandlerError):
            raise HandlerError("Test error")

    def test_handler_error_with_message(self):
        """Test that HandlerError preserves error message."""
        error_msg = "Test error message"
        try:
            raise HandlerError(error_msg)
        except HandlerError as e:
            assert str(e) == error_msg


class TestStepLimitReached:
    """Test StepLimitReached exception."""

    def test_step_limit_reached_is_handler_error(self):
        """Test that StepLimitReached is a HandlerError."""
        assert issubclass(StepLimitReached, HandlerError)

    def test_step_limit_reached_can_be_raised(self):
        """Test that StepLimitReached can be raised and caught."""
        with pytest.raises(StepLimitReached):
            raise StepLimitReached("Step limit exceeded")

    def test_step_limit_reached_with_message(self):
        """Test that StepLimitReached preserves error message."""
        error_msg = "Maximum steps reached"
        try:
            raise StepLimitReached(error_msg)
        except StepLimitReached as e:
            assert str(e) == error_msg

    def test_step_limit_reached_caught_as_handler_error(self):
        """Test that StepLimitReached can be caught as HandlerError."""
        with pytest.raises(HandlerError):
            raise StepLimitReached("Test")
