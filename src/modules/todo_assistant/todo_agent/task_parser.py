"""
Task Parser
===========

Parse natural language task descriptions into MCP tool actions.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskParser:
    """
    Parse natural language tasks into MCP actions.
    
    Uses pattern matching and keyword extraction to translate
    user tasks into executable tool calls.
    """
    
    def __init__(self):
        """Initialize task parser."""
        self.patterns = self._init_patterns()
        logger.info("TaskParser initialized")
    
    def _init_patterns(self) -> List[Dict[str, Any]]:
        """
        Initialize parsing patterns.
        
        Returns:
            List of pattern dicts with regex and tool mappings
        """
        return [
            {
                "pattern": r"open\s+([a-zA-Z0-9_\-\.]+)",
                "tool": "open_app",
                "extract": lambda m: {"name": m.group(1)}
            },
            {
                "pattern": r"launch\s+([a-zA-Z0-9_\-\.]+)",
                "tool": "open_app",
                "extract": lambda m: {"name": m.group(1)}
            },
            {
                "pattern": r"start\s+([a-zA-Z0-9_\-\.]+)",
                "tool": "open_app",
                "extract": lambda m: {"name": m.group(1)}
            },
            {
                "pattern": r"click\s+(?:on\s+)?['\"]?([^'\"]+)['\"]?",
                "tool": "click_ui",
                "extract": lambda m: {"label": m.group(1).strip()}
            },
            {
                "pattern": r"type\s+['\"]([^'\"]+)['\"]",
                "tool": "type_text",
                "extract": lambda m: {"text": m.group(1)}
            },
            {
                "pattern": r"enter\s+['\"]([^'\"]+)['\"]",
                "tool": "type_text",
                "extract": lambda m: {"text": m.group(1)}
            },
            {
                "pattern": r"read\s+screen",
                "tool": "read_screen",
                "extract": lambda m: {}
            },
            {
                "pattern": r"run\s+script\s+['\"]?([^'\"]+)['\"]?",
                "tool": "run_custom_script",
                "extract": lambda m: {"file": m.group(1)}
            },
            {
                "pattern": r"execute\s+['\"]?([^'\"]+\.py)['\"]?",
                "tool": "run_custom_script",
                "extract": lambda m: {"file": m.group(1)}
            }
        ]
    
    def parse(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Parse a task description into actions.
        
        Args:
            task_description: Natural language task description
            
        Returns:
            List of action dicts with tool name and parameters
        """
        try:
            logger.info("Parsing task: %s", task_description)
            
            actions = []
            text = task_description.lower()
            
            # Split into steps if multiple actions
            steps = self._split_steps(text)
            
            for step in steps:
                action = self._parse_step(step)
                if action:
                    actions.append(action)
            
            if not actions:
                # Fallback: create a generic action
                logger.warning("No patterns matched, creating generic action")
                actions = [{
                    "tool": "read_screen",
                    "params": {},
                    "description": task_description,
                    "note": "No specific pattern matched - defaulting to screen read"
                }]
            
            logger.info("Parsed %d actions from task", len(actions))
            return actions
            
        except Exception as e:
            logger.error("Failed to parse task: %s", str(e))
            return []
    
    def _split_steps(self, text: str) -> List[str]:
        """
        Split task into multiple steps.
        
        Args:
            text: Task text
            
        Returns:
            List of step strings
        """
        # Split on common separators
        separators = [
            r"\s+then\s+",
            r"\s+and\s+then\s+",
            r"\s*;\s*",
            r"\s*\.\s+(?=[a-z])",
            r"\s+after\s+that\s+"
        ]
        
        steps = [text]
        for sep in separators:
            new_steps = []
            for step in steps:
                new_steps.extend(re.split(sep, step))
            steps = new_steps
        
        # Clean and filter
        steps = [s.strip() for s in steps if s.strip()]
        return steps
    
    def _parse_step(self, step: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single step.
        
        Args:
            step: Step text
            
        Returns:
            Action dict or None
        """
        for pattern_dict in self.patterns:
            pattern = pattern_dict["pattern"]
            match = re.search(pattern, step, re.IGNORECASE)
            
            if match:
                tool = pattern_dict["tool"]
                params = pattern_dict["extract"](match)
                
                return {
                    "tool": tool,
                    "params": params,
                    "description": step
                }
        
        return None
    
    def get_supported_actions(self) -> List[str]:
        """
        Get list of supported action types.
        
        Returns:
            List of action descriptions
        """
        return [
            "open/launch/start <app_name> - Open an application",
            "click <element> - Click a UI element",
            "type/enter '<text>' - Type text",
            "read screen - Read text from screen",
            "run script '<file>' - Execute a custom script"
        ]
