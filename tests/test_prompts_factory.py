#!/usr/bin/env python3
"""
Tests for the modules/prompts/factory module.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.prompts.factory import (
    _lf_auth_header,
    _lf_cache_get,
    _lf_cache_set,
    _lf_ck,
    _lf_enabled,
    _lf_env_true,
    _lf_host,
    _lf_is_docker,
)


class TestLangfuseHelpers:
    """Test Langfuse helper functions."""

    def test_lf_env_true_returns_true_for_true(self):
        """Test _lf_env_true returns True for 'true' value."""
        with patch.dict(os.environ, {"TEST_VAR": "true"}):
            assert _lf_env_true("TEST_VAR") is True

    def test_lf_env_true_returns_false_for_false(self):
        """Test _lf_env_true returns False for 'false' value."""
        with patch.dict(os.environ, {"TEST_VAR": "false"}):
            assert _lf_env_true("TEST_VAR") is False

    def test_lf_env_true_returns_false_for_missing(self):
        """Test _lf_env_true returns False for missing variable."""
        with patch.dict(os.environ, {}, clear=True):
            assert _lf_env_true("MISSING_VAR") is False

    def test_lf_env_true_case_insensitive(self):
        """Test _lf_env_true is case-insensitive."""
        with patch.dict(os.environ, {"TEST_VAR": "TRUE"}):
            assert _lf_env_true("TEST_VAR") is True
        with patch.dict(os.environ, {"TEST_VAR": "False"}):
            assert _lf_env_true("TEST_VAR") is False

    def test_lf_is_docker_when_dockerenv_exists(self):
        """Test _lf_is_docker returns True when /.dockerenv exists."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path == "/.dockerenv"
            assert _lf_is_docker() is True

    def test_lf_is_docker_when_app_exists(self):
        """Test _lf_is_docker returns True when /app exists."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path == "/app"
            assert _lf_is_docker() is True

    def test_lf_is_docker_when_neither_exists(self):
        """Test _lf_is_docker returns False when neither path exists."""
        with patch("os.path.exists", return_value=False):
            assert _lf_is_docker() is False

    def test_lf_enabled_requires_both_flags(self):
        """Test _lf_enabled requires both ENABLE_OBSERVABILITY and ENABLE_LANGFUSE_PROMPTS."""
        with patch.dict(os.environ, {"ENABLE_OBSERVABILITY": "true", "ENABLE_LANGFUSE_PROMPTS": "true"}):
            assert _lf_enabled() is True

        with patch.dict(os.environ, {"ENABLE_OBSERVABILITY": "true", "ENABLE_LANGFUSE_PROMPTS": "false"}):
            assert _lf_enabled() is False

        with patch.dict(os.environ, {"ENABLE_OBSERVABILITY": "false", "ENABLE_LANGFUSE_PROMPTS": "true"}):
            assert _lf_enabled() is False

        with patch.dict(os.environ, {}, clear=True):
            assert _lf_enabled() is False

    def test_lf_host_uses_docker_host_in_docker(self):
        """Test _lf_host returns docker host when in Docker."""
        with patch("modules.prompts.factory._lf_is_docker", return_value=True):
            with patch.dict(os.environ, {}, clear=True):
                host = _lf_host()
                assert "langfuse-web:3000" in host

    def test_lf_host_uses_localhost_outside_docker(self):
        """Test _lf_host returns localhost when not in Docker."""
        with patch("modules.prompts.factory._lf_is_docker", return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                host = _lf_host()
                assert "localhost:3000" in host

    def test_lf_host_uses_env_override(self):
        """Test _lf_host uses LANGFUSE_HOST environment variable."""
        with patch.dict(os.environ, {"LANGFUSE_HOST": "http://custom-host:9000"}):
            host = _lf_host()
            assert host == "http://custom-host:9000"

    def test_lf_host_strips_trailing_slash(self):
        """Test _lf_host strips trailing slash."""
        with patch.dict(os.environ, {"LANGFUSE_HOST": "http://custom-host:9000/"}):
            host = _lf_host()
            assert host == "http://custom-host:9000"

    def test_lf_auth_header_uses_env_credentials(self):
        """Test _lf_auth_header uses environment variables for credentials."""
        with patch.dict(os.environ, {"LANGFUSE_PUBLIC_KEY": "test_pk", "LANGFUSE_SECRET_KEY": "test_sk"}):
            header = _lf_auth_header()
            assert header.startswith("Basic ")
            assert len(header) > 10

    def test_lf_auth_header_uses_defaults(self):
        """Test _lf_auth_header uses default credentials when not set."""
        with patch.dict(os.environ, {}, clear=True):
            header = _lf_auth_header()
            assert header.startswith("Basic ")

    def test_lf_ck_creates_cache_key(self):
        """Test _lf_ck creates cache key from name and label."""
        key = _lf_ck("test_name", "test_label")
        assert key == "test_name::test_label"


class TestLangfuseCache:
    """Test Langfuse cache functions."""

    def test_lf_cache_set_and_get(self):
        """Test setting and getting cache values."""
        test_value = {"prompt": "test prompt", "version": 1}
        _lf_cache_set("test_name", "test_label", test_value)
        
        cached = _lf_cache_get("test_name", "test_label")
        assert cached is not None
        assert cached["prompt"] == "test prompt"
        assert cached["version"] == 1

    def test_lf_cache_get_nonexistent(self):
        """Test getting non-existent cache value returns None."""
        cached = _lf_cache_get("nonexistent_name", "nonexistent_label")
        assert cached is None

    def test_lf_cache_get_expired(self):
        """Test getting expired cache value returns None."""
        test_value = {"prompt": "test prompt"}
        
        # Set cache with expired timestamp
        with patch("time.time", return_value=0):
            _lf_cache_set("test_name", "test_label", test_value)
        
        # Try to get with current time (should be expired)
        with patch("time.time", return_value=100000):
            cached = _lf_cache_get("test_name", "test_label")
            assert cached is None

    def test_lf_cache_thread_safe(self):
        """Test cache operations are thread-safe."""
        import threading
        
        test_value = {"prompt": "test prompt"}
        errors = []
        
        def set_cache():
            try:
                for i in range(100):
                    _lf_cache_set(f"name_{i}", "label", test_value)
            except Exception as e:
                errors.append(e)
        
        def get_cache():
            try:
                for i in range(100):
                    _lf_cache_get(f"name_{i}", "label")
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=set_cache),
            threading.Thread(target=get_cache),
            threading.Thread(target=set_cache),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
