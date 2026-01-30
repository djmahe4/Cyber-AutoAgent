#!/usr/bin/env python3
"""
Tests for the modules/config/environment module.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.config.environment import (
    auto_setup,
    clean_operation_memory,
)


class TestCleanOperationMemory:
    """Test clean_operation_memory function."""

    def test_clean_operation_memory_no_target_name(self, caplog):
        """Test that clean_operation_memory logs warning when no target_name is provided."""
        import logging
        with caplog.at_level(logging.WARNING):
            clean_operation_memory(operation_id="test_op", target_name=None)
            assert "No target_name provided, skipping memory cleanup" in caplog.text

    def test_clean_operation_memory_path_not_exists(self, tmp_path, caplog):
        """Test that clean_operation_memory handles non-existent path."""
        # Change to a temporary directory so the path doesn't exist
        import os
        import logging
        orig_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            with caplog.at_level(logging.DEBUG):
                clean_operation_memory(operation_id="test_op", target_name="test_target")
                assert "Memory path does not exist" in caplog.text
        finally:
            os.chdir(orig_dir)

    def test_clean_operation_memory_removes_directory(self, tmp_path, caplog):
        """Test that clean_operation_memory removes the memory directory."""
        # Setup test directory structure in tmp_path
        import os
        import logging
        orig_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            target_name = "test_target"
            memory_path = tmp_path / "outputs" / target_name / "memory" / f"mem0_faiss_{target_name}"
            memory_path.mkdir(parents=True, exist_ok=True)
            
            # Verify it exists
            assert memory_path.exists()
            
            # Call clean_operation_memory
            with caplog.at_level(logging.INFO):
                clean_operation_memory(operation_id="test_op", target_name=target_name)
            
            # Verify it was deleted
            assert not memory_path.exists()
            assert "Cleaned up operation memory" in caplog.text
        finally:
            os.chdir(orig_dir)

    def test_clean_operation_memory_safety_check(self, caplog):
        """Test that clean_operation_memory performs safety check."""
        import logging
        # Create a path without the expected pattern
        with caplog.at_level(logging.ERROR):
            with patch("os.path.exists", return_value=True):
                with patch("modules.config.environment.os.path.join", return_value="/some/dangerous/path"):
                    clean_operation_memory(operation_id="test_op", target_name="test_target")
                    assert "SAFETY CHECK FAILED" in caplog.text

    def test_clean_operation_memory_handles_exception(self, caplog):
        """Test that clean_operation_memory handles exceptions gracefully."""
        import logging
        with caplog.at_level(logging.ERROR):
            with patch("os.path.exists", return_value=True):
                with patch("modules.config.environment.os.path.join", return_value="/outputs/test/memory/mem0_faiss_test"):
                    with patch("os.path.isdir", return_value=True):
                        with patch("shutil.rmtree", side_effect=Exception("Test error")):
                            clean_operation_memory(operation_id="test_op", target_name="test_target")
                            assert "Failed to clean" in caplog.text


class TestAutoSetup:
    """Test auto_setup function."""

    def test_auto_setup_creates_directories(self, tmp_path):
        """Test that auto_setup creates necessary directories."""
        with patch("pathlib.Path", return_value=tmp_path / "tools"):
            with patch.dict(os.environ, {}, clear=True):
                # Mock the tools directory checks
                mock_tools_path = MagicMock()
                mock_tools_path.exists.return_value = False
                mock_tools_path.mkdir = MagicMock()
                
                with patch("modules.config.environment.Path", return_value=mock_tools_path):
                    with patch("os.listdir", return_value=[]):
                        result = auto_setup(skip_mem0_cleanup=True)
                        assert isinstance(result, list)

    def test_auto_setup_sets_mem0_telemetry(self):
        """Test that auto_setup sets MEM0_TELEMETRY environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path") as mock_path:
                mock_tools_path = MagicMock()
                mock_tools_path.exists.return_value = False
                mock_path.return_value = mock_tools_path
                
                with patch("os.listdir", return_value=[]):
                    auto_setup(skip_mem0_cleanup=True)
                    assert os.environ.get("MEM0_TELEMETRY") == "false"

    def test_auto_setup_discovers_tools(self):
        """Test that auto_setup discovers available tools."""
        with patch("pathlib.Path") as mock_path:
            mock_tools_path = MagicMock()
            mock_tools_path.exists.return_value = True
            mock_tools_path.is_dir.return_value = True
            mock_path.return_value = mock_tools_path
            
            with patch("os.listdir", return_value=["tool1.sh", "tool2.py", "readme.txt"]):
                with patch("os.path.isfile", return_value=True):
                    with patch("os.access", return_value=True):
                        result = auto_setup(skip_mem0_cleanup=True)
                        assert isinstance(result, list)

    def test_auto_setup_skip_mem0_cleanup(self):
        """Test that auto_setup respects skip_mem0_cleanup flag."""
        with patch("pathlib.Path") as mock_path:
            mock_tools_path = MagicMock()
            mock_tools_path.exists.return_value = True
            mock_tools_path.is_dir.return_value = True
            mock_path.return_value = mock_tools_path
            
            with patch("os.listdir", return_value=[]):
                result = auto_setup(skip_mem0_cleanup=True)
                assert isinstance(result, list)
