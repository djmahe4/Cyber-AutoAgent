"""
Action Logger for UI Automation
================================

Logs all automation actions with:
- Timestamps
- UI elements targeted
- Methods used
- Screenshots before & after
- Results and status
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

logger = logging.getLogger(__name__)

# Try to import screenshot libraries
try:
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    logger.warning("PIL not available - screenshots disabled")


class ActionLogger:
    """Logger for UI automation actions with screenshots and JSONL output."""
    
    def __init__(self, session_id: Optional[str] = None, log_dir: str = "./logs"):
        """
        Initialize action logger.
        
        Args:
            session_id: Unique session identifier (auto-generated if None)
            log_dir: Directory for log files
        """
        self.session_id = session_id or self._generate_session_id()
        self.log_dir = Path(log_dir)
        self.screenshot_dir = self.log_dir / "screenshots" / self.session_id
        
        # Create directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file path
        self.log_file = self.log_dir / f"{self.session_id}.jsonl"
        
        # Action counter
        self.action_count = 0
        
        logger.info("ActionLogger initialized: session=%s, log_file=%s", self.session_id, self.log_file)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def _take_screenshot(self, name: str) -> Optional[str]:
        """
        Take a screenshot and save it.
        
        Args:
            name: Screenshot name/identifier
            
        Returns:
            Path to screenshot file or None if failed
        """
        if not SCREENSHOT_AVAILABLE:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}_{name}.png"
            filepath = self.screenshot_dir / filename
            
            screenshot = ImageGrab.grab()
            screenshot.save(str(filepath))
            
            return str(filepath)
        except Exception as e:
            logger.error("Screenshot failed: %s", str(e))
            return None
    
    def log_action(
        self,
        action_type: str,
        target: str,
        method: str,
        result: Dict[str, Any],
        take_screenshots: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an automation action.
        
        Args:
            action_type: Type of action (e.g., 'click', 'type', 'open_app')
            target: Target element or application
            method: Method used (e.g., 'pywinauto', 'xdotool', 'vision')
            result: Result of the action
            take_screenshots: Whether to capture before/after screenshots
            metadata: Additional metadata
            
        Returns:
            Log entry dict
        """
        self.action_count += 1
        
        # Take screenshots
        screenshot_before = None
        screenshot_after = None
        
        if take_screenshots:
            # Note: In practice, "before" screenshot would be taken before action
            # This is a simplified version for logging purposes
            screenshot_after = self._take_screenshot(f"action_{self.action_count:04d}_after")
        
        # Build log entry
        log_entry = {
            "session_id": self.session_id,
            "action_id": self.action_count,
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "target": target,
            "method": method,
            "result": {
                "success": result.get("success", False),
                "error": result.get("error"),
                "data": {k: v for k, v in result.items() if k not in ["success", "error"]}
            },
            "screenshots": {
                "before": screenshot_before,
                "after": screenshot_after
            },
            "metadata": metadata or {}
        }
        
        # Write to JSONL file
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error("Failed to write log entry: %s", str(e))
        
        return log_entry
    
    def log_anomaly(
        self,
        anomaly_type: str,
        description: str,
        expected: Any,
        actual: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an anomaly or unexpected UI state.
        
        Args:
            anomaly_type: Type of anomaly (e.g., 'ui_mismatch', 'unexpected_state')
            description: Human-readable description
            expected: Expected state/result
            actual: Actual state/result
            metadata: Additional metadata
        """
        anomaly_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "type": "anomaly",
            "anomaly_type": anomaly_type,
            "description": description,
            "expected": expected,
            "actual": actual,
            "screenshot": self._take_screenshot(f"anomaly_{self.action_count:04d}"),
            "metadata": metadata or {}
        }
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(anomaly_entry) + "\n")
        except Exception as e:
            logger.error("Failed to write anomaly entry: %s", str(e))
    
    def get_session_log(self) -> list:
        """
        Read and return all log entries for this session.
        
        Returns:
            List of log entry dicts
        """
        entries = []
        
        if not self.log_file.exists():
            return entries
        
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            logger.error("Failed to read log file: %s", str(e))
        
        return entries
    
    def get_action_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for this session.
        
        Returns:
            Summary dict with statistics
        """
        entries = self.get_session_log()
        
        total_actions = len([e for e in entries if e.get("type") != "anomaly"])
        successful_actions = len([e for e in entries if e.get("result", {}).get("success")])
        failed_actions = total_actions - successful_actions
        anomalies = len([e for e in entries if e.get("type") == "anomaly"])
        
        # Count methods used
        methods = {}
        for entry in entries:
            if "method" in entry:
                method = entry["method"]
                methods[method] = methods.get(method, 0) + 1
        
        return {
            "session_id": self.session_id,
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "anomalies": anomalies,
            "methods_used": methods,
            "log_file": str(self.log_file),
            "screenshot_dir": str(self.screenshot_dir)
        }
    
    def close(self):
        """Close the logger and write summary."""
        summary = self.get_action_summary()
        
        # Write summary to separate file
        summary_file = self.log_dir / f"{self.session_id}_summary.json"
        try:
            with open(summary_file, "w") as f:
                json.dump(summary, f, indent=2)
            logger.info("Session summary written to %s", summary_file)
        except Exception as e:
            logger.error("Failed to write summary: %s", str(e))
