#!/usr/bin/env python3
"""
Tests for the modules/evaluation/manager module.
"""

import threading
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.evaluation.manager import (
    EvaluationManager,
    TraceInfo,
    TraceType,
)


class TestTraceType:
    """Test TraceType enum."""

    def test_trace_type_values(self):
        """Test that TraceType enum has expected values."""
        assert TraceType.MAIN_AGENT.value == "main_agent"
        assert TraceType.REPORT_GENERATION.value == "report_generation"
        assert TraceType.SWARM_AGENT.value == "swarm_agent"

    def test_trace_type_members(self):
        """Test that all expected TraceType members exist."""
        expected_members = ["MAIN_AGENT", "REPORT_GENERATION", "SWARM_AGENT"]
        actual_members = [member.name for member in TraceType]
        assert set(expected_members) == set(actual_members)


class TestTraceInfo:
    """Test TraceInfo dataclass."""

    def test_trace_info_creation(self):
        """Test creating a TraceInfo object."""
        trace_info = TraceInfo(
            trace_id="test_trace_123",
            trace_type=TraceType.MAIN_AGENT,
            session_id="session_456",
            name="Test Trace",
        )

        assert trace_info.trace_id == "test_trace_123"
        assert trace_info.trace_type == TraceType.MAIN_AGENT
        assert trace_info.session_id == "session_456"
        assert trace_info.name == "Test Trace"
        assert isinstance(trace_info.metadata, dict)
        assert len(trace_info.metadata) == 0
        assert trace_info.evaluated is False
        assert trace_info.evaluation_scores is None

    def test_trace_info_with_metadata(self):
        """Test TraceInfo with custom metadata."""
        metadata = {"key": "value", "count": 42}
        trace_info = TraceInfo(
            trace_id="test_trace_123",
            trace_type=TraceType.REPORT_GENERATION,
            session_id="session_456",
            name="Test Trace",
            metadata=metadata,
        )

        assert trace_info.metadata == metadata
        assert trace_info.metadata["key"] == "value"
        assert trace_info.metadata["count"] == 42

    def test_trace_info_with_evaluation_scores(self):
        """Test TraceInfo with evaluation scores."""
        scores = {"accuracy": 0.95, "completeness": 0.88}
        trace_info = TraceInfo(
            trace_id="test_trace_123",
            trace_type=TraceType.MAIN_AGENT,
            session_id="session_456",
            name="Test Trace",
            evaluated=True,
            evaluation_scores=scores,
        )

        assert trace_info.evaluated is True
        assert trace_info.evaluation_scores == scores


class TestEvaluationManager:
    """Test EvaluationManager class."""

    def test_evaluation_manager_initialization(self):
        """Test EvaluationManager initialization."""
        manager = EvaluationManager(operation_id="op_123")

        assert manager.operation_id == "op_123"
        assert isinstance(manager.traces, dict)
        assert len(manager.traces) == 0
        assert manager.evaluator is None
        assert isinstance(manager._lock, type(threading.Lock()))
        assert manager._evaluation_thread is None

    def test_register_trace(self):
        """Test registering a trace for evaluation."""
        manager = EvaluationManager(operation_id="op_123")

        manager.register_trace(
            trace_id="trace_001",
            trace_type=TraceType.MAIN_AGENT,
            session_id="session_123",
            name="Main Agent Trace",
        )

        assert "trace_001" in manager.traces
        trace_info = manager.traces["trace_001"]
        assert trace_info.trace_id == "trace_001"
        assert trace_info.trace_type == TraceType.MAIN_AGENT
        assert trace_info.session_id == "session_123"
        assert trace_info.name == "Main Agent Trace"
        assert trace_info.evaluated is False

    def test_register_trace_with_metadata(self):
        """Test registering a trace with metadata."""
        manager = EvaluationManager(operation_id="op_123")
        metadata = {"target": "test.example.com", "tools_used": ["nmap", "nikto"]}

        manager.register_trace(
            trace_id="trace_001",
            trace_type=TraceType.MAIN_AGENT,
            session_id="session_123",
            name="Main Agent Trace",
            metadata=metadata,
        )

        trace_info = manager.traces["trace_001"]
        assert trace_info.metadata == metadata

    def test_register_multiple_traces(self):
        """Test registering multiple traces."""
        manager = EvaluationManager(operation_id="op_123")

        manager.register_trace(
            trace_id="trace_001",
            trace_type=TraceType.MAIN_AGENT,
            session_id="session_123",
            name="Main Agent Trace",
        )

        manager.register_trace(
            trace_id="trace_002",
            trace_type=TraceType.REPORT_GENERATION,
            session_id="session_124",
            name="Report Generation Trace",
        )

        assert len(manager.traces) == 2
        assert "trace_001" in manager.traces
        assert "trace_002" in manager.traces
        assert manager.traces["trace_001"].trace_type == TraceType.MAIN_AGENT
        assert manager.traces["trace_002"].trace_type == TraceType.REPORT_GENERATION

    def test_register_trace_thread_safety(self):
        """Test that register_trace is thread-safe."""
        manager = EvaluationManager(operation_id="op_123")
        errors = []

        def register_traces():
            try:
                for i in range(100):
                    manager.register_trace(
                        trace_id=f"trace_{threading.current_thread().name}_{i}",
                        trace_type=TraceType.MAIN_AGENT,
                        session_id=f"session_{i}",
                        name=f"Trace {i}",
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_traces, name=f"thread_{i}") for i in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 300 traces registered (3 threads * 100 each)
        assert len(manager.traces) == 300
        assert len(errors) == 0

    def test_evaluation_manager_with_different_trace_types(self):
        """Test EvaluationManager with different trace types."""
        manager = EvaluationManager(operation_id="op_123")

        # Register traces of different types
        trace_types = [
            (TraceType.MAIN_AGENT, "main_trace"),
            (TraceType.REPORT_GENERATION, "report_trace"),
            (TraceType.SWARM_AGENT, "swarm_trace"),
        ]

        for trace_type, trace_id in trace_types:
            manager.register_trace(
                trace_id=trace_id,
                trace_type=trace_type,
                session_id=f"session_{trace_id}",
                name=f"Trace for {trace_type.value}",
            )

        assert len(manager.traces) == 3
        assert manager.traces["main_trace"].trace_type == TraceType.MAIN_AGENT
        assert manager.traces["report_trace"].trace_type == TraceType.REPORT_GENERATION
        assert manager.traces["swarm_trace"].trace_type == TraceType.SWARM_AGENT

    def test_evaluation_manager_operation_id(self):
        """Test that operation_id is properly set and accessible."""
        operation_id = "test_operation_12345"
        manager = EvaluationManager(operation_id=operation_id)

        assert manager.operation_id == operation_id
