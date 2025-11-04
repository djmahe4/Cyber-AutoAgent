#!/usr/bin/env python3
"""
Deployment Adapter for To-Do Assistant
======================================

Ensures proper functioning across all deployment modes:
- local-cli: Direct Python execution
- single-container: Docker container with mounted volumes
- full-stack: Full stack with observability

Handles:
- Path resolution (host vs container)
- File system access (local vs mounted volumes)
- Dependency availability
- Environment detection
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DeploymentMode:
    """Deployment mode detection and configuration."""
    
    LOCAL_CLI = "local-cli"
    SINGLE_CONTAINER = "single-container"
    FULL_STACK = "full-stack"
    
    @staticmethod
    def detect() -> str:
        """
        Detect current deployment mode.
        
        Returns:
            Deployment mode string
        """
        # Check for container environment
        if os.path.exists("/.dockerenv") or os.environ.get("CONTAINER"):
            # In container - check if full stack
            if os.environ.get("LANGFUSE_HOST") and "langfuse" in os.environ.get("LANGFUSE_HOST", ""):
                return DeploymentMode.FULL_STACK
            return DeploymentMode.SINGLE_CONTAINER
        
        # Local CLI mode
        return DeploymentMode.LOCAL_CLI
    
    @staticmethod
    def is_container() -> bool:
        """Check if running in container."""
        mode = DeploymentMode.detect()
        return mode in [DeploymentMode.SINGLE_CONTAINER, DeploymentMode.FULL_STACK]
    
    @staticmethod
    def is_local() -> bool:
        """Check if running in local CLI mode."""
        return DeploymentMode.detect() == DeploymentMode.LOCAL_CLI


class PathAdapter:
    """Adapts file paths for different deployment modes."""
    
    def __init__(self):
        self.mode = DeploymentMode.detect()
        self.is_container = DeploymentMode.is_container()
        
        # Base paths
        if self.is_container:
            self.project_root = Path("/app")
            self.outputs_dir = Path("/app/outputs")
            self.logs_dir = Path("/app/outputs/logs")
        else:
            # Local CLI - use project root from environment or cwd
            self.project_root = Path(os.environ.get("CYBER_PROJECT_ROOT", os.getcwd()))
            self.outputs_dir = self.project_root / "outputs"
            self.logs_dir = self.outputs_dir / "logs"
        
        logger.info(
            "PathAdapter initialized: mode=%s, root=%s",
            self.mode,
            self.project_root
        )
    
    def get_project_root(self) -> Path:
        """Get project root path."""
        return self.project_root
    
    def get_outputs_dir(self) -> Path:
        """Get outputs directory."""
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        return self.outputs_dir
    
    def get_logs_dir(self) -> Path:
        """Get logs directory."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        return self.logs_dir
    
    def get_scripts_dir(self) -> Path:
        """Get user scripts directory."""
        scripts_dir = self.project_root / "src" / "modules" / "todo_assistant" / "ui_scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        return scripts_dir
    
    def get_rag_store_dir(self) -> Path:
        """Get RAG vector store directory."""
        rag_dir = self.outputs_dir / "rag_store"
        rag_dir.mkdir(parents=True, exist_ok=True)
        return rag_dir
    
    def resolve_script_path(self, script_path: str) -> Path:
        """
        Resolve script path - handles relative and absolute paths.
        
        Args:
            script_path: Script path (relative or absolute)
            
        Returns:
            Resolved absolute path
        """
        path = Path(script_path)
        
        if path.is_absolute():
            return path
        
        # Try relative to scripts directory first
        scripts_dir = self.get_scripts_dir()
        candidate = scripts_dir / path
        if candidate.exists():
            return candidate
        
        # Try relative to project root
        candidate = self.project_root / path
        if candidate.exists():
            return candidate
        
        # Try relative to current working directory
        candidate = Path.cwd() / path
        if candidate.exists():
            return candidate
        
        # Return original path (will fail if doesn't exist)
        return path


class DependencyAdapter:
    """Adapts functionality based on available dependencies."""
    
    def __init__(self):
        self.available_deps = self._check_dependencies()
        logger.info("Available dependencies: %s", self.available_deps)
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check which optional dependencies are available."""
        deps = {}
        
        # UI Automation
        try:
            import pyautogui
            deps["pyautogui"] = True
        except ImportError:
            deps["pyautogui"] = False
        
        try:
            from pywinauto import Application
            deps["pywinauto"] = True
        except ImportError:
            deps["pywinauto"] = False
        
        # Computer Vision
        try:
            import cv2
            deps["opencv"] = True
        except ImportError:
            deps["opencv"] = False
        
        # OCR
        try:
            import pytesseract
            from PIL import Image
            deps["ocr"] = True
        except ImportError:
            deps["ocr"] = False
        
        # RAG
        try:
            from langchain_community.vectorstores import FAISS
            deps["rag"] = True
        except ImportError:
            deps["rag"] = False
        
        # Screenshots
        try:
            from PIL import ImageGrab
            deps["screenshots"] = True
        except ImportError:
            deps["screenshots"] = False
        
        return deps
    
    def has_automation(self) -> bool:
        """Check if any UI automation library is available."""
        return any([
            self.available_deps.get("pyautogui"),
            self.available_deps.get("pywinauto")
        ])
    
    def has_vision_mode(self) -> bool:
        """Check if vision mode dependencies are available."""
        return (
            self.available_deps.get("pyautogui", False) and
            self.available_deps.get("opencv", False)
        )
    
    def has_rag(self) -> bool:
        """Check if RAG dependencies are available."""
        return self.available_deps.get("rag", False)
    
    def has_screenshots(self) -> bool:
        """Check if screenshot capability is available."""
        return self.available_deps.get("screenshots", False)
    
    def get_missing_deps(self, feature: str) -> list:
        """
        Get list of missing dependencies for a feature.
        
        Args:
            feature: Feature name (automation, vision, rag, screenshots, ocr)
            
        Returns:
            List of missing package names
        """
        if feature == "automation":
            missing = []
            if not self.available_deps.get("pyautogui"):
                missing.append("pyautogui")
            if not self.available_deps.get("pywinauto") and sys.platform == "win32":
                missing.append("pywinauto")
            return missing
        
        elif feature == "vision":
            missing = []
            if not self.available_deps.get("pyautogui"):
                missing.append("pyautogui")
            if not self.available_deps.get("opencv"):
                missing.append("opencv-python")
            return missing
        
        elif feature == "rag":
            if not self.available_deps.get("rag"):
                return ["langchain-community", "faiss-cpu", "pypdf"]
            return []
        
        elif feature == "screenshots":
            if not self.available_deps.get("screenshots"):
                return ["pillow"]
            return []
        
        elif feature == "ocr":
            if not self.available_deps.get("ocr"):
                return ["pytesseract", "pillow"]
            return []
        
        return []


class ConfigAdapter:
    """Adapts configuration for different deployment modes."""
    
    def __init__(self):
        self.mode = DeploymentMode.detect()
        self.path_adapter = PathAdapter()
        self.dep_adapter = DependencyAdapter()
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP server configuration."""
        return {
            "consent_required": self.mode == DeploymentMode.LOCAL_CLI,
            "log_actions": True,
            "screenshot_enabled": self.dep_adapter.has_screenshots()
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG engine configuration."""
        return {
            "vector_store": "faiss" if self.dep_adapter.has_rag() else None,
            "persist_directory": str(self.path_adapter.get_rag_store_dir()),
            "enabled": self.dep_adapter.has_rag()
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            "log_dir": str(self.path_adapter.get_logs_dir()),
            "screenshot_dir": str(self.path_adapter.get_logs_dir() / "screenshots"),
            "json_logs": True,
            "console_output": self.mode == DeploymentMode.LOCAL_CLI
        }
    
    def get_automation_config(self) -> Dict[str, Any]:
        """Get automation configuration."""
        return {
            "vision_mode_available": self.dep_adapter.has_vision_mode(),
            "platform_automation_available": self.dep_adapter.has_automation(),
            "screenshot_enabled": self.dep_adapter.has_screenshots()
        }
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information."""
        return {
            "mode": self.mode,
            "is_container": DeploymentMode.is_container(),
            "is_local": DeploymentMode.is_local(),
            "project_root": str(self.path_adapter.get_project_root()),
            "outputs_dir": str(self.path_adapter.get_outputs_dir()),
            "logs_dir": str(self.path_adapter.get_logs_dir()),
            "dependencies": self.dep_adapter.available_deps,
            "features": {
                "automation": self.dep_adapter.has_automation(),
                "vision_mode": self.dep_adapter.has_vision_mode(),
                "rag": self.dep_adapter.has_rag(),
                "screenshots": self.dep_adapter.has_screenshots()
            }
        }


# Singleton instances
_path_adapter = None
_dep_adapter = None
_config_adapter = None


def get_path_adapter() -> PathAdapter:
    """Get global PathAdapter instance."""
    global _path_adapter
    if _path_adapter is None:
        _path_adapter = PathAdapter()
    return _path_adapter


def get_dependency_adapter() -> DependencyAdapter:
    """Get global DependencyAdapter instance."""
    global _dep_adapter
    if _dep_adapter is None:
        _dep_adapter = DependencyAdapter()
    return _dep_adapter


def get_config_adapter() -> ConfigAdapter:
    """Get global ConfigAdapter instance."""
    global _config_adapter
    if _config_adapter is None:
        _config_adapter = ConfigAdapter()
    return _config_adapter
