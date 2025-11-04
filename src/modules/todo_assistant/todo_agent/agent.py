"""
To-Do Agent Implementation
==========================

Main agent for managing and executing to-do tasks.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..mcp_server import MCPServer
from ..rag_engine import RAGEngine
from .task_parser import TaskParser

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a to-do task."""
    id: int
    description: str
    status: TaskStatus
    actions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TodoAgent:
    """
    To-Do Agent for task management and execution.
    
    Translates natural language tasks into MCP + UI automation actions
    and executes them with appropriate safety checks.
    """
    
    def __init__(
        self,
        mcp_server: Optional[MCPServer] = None,
        rag_engine: Optional[RAGEngine] = None,
        auto_execute: bool = False
    ):
        """
        Initialize To-Do Agent.
        
        Args:
            mcp_server: MCP server instance for automation
            rag_engine: RAG engine for manual lookups
            auto_execute: Whether to auto-execute tasks
        """
        self.mcp_server = mcp_server or MCPServer(consent_required=True)
        self.rag_engine = rag_engine
        self.task_parser = TaskParser()
        self.auto_execute = auto_execute
        
        self.tasks: List[Task] = []
        self.next_task_id = 1
        
        logger.info("TodoAgent initialized (auto_execute=%s)", auto_execute)
    
    def add_task(self, description: str) -> Task:
        """
        Add a new task.
        
        Args:
            description: Natural language task description
            
        Returns:
            Created Task object
        """
        try:
            logger.info("Adding task: %s", description)
            
            # Parse task into actions
            actions = self.task_parser.parse(description)
            
            # Check RAG for relevant context if available
            if self.rag_engine:
                rag_context = self.rag_engine.query(description, k=2)
                if rag_context.get("success"):
                    logger.info("Found RAG context for task")
                    # Could enhance actions with RAG context here
            
            # Create task
            task = Task(
                id=self.next_task_id,
                description=description,
                status=TaskStatus.PENDING,
                actions=actions,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.tasks.append(task)
            self.next_task_id += 1
            
            logger.info("Task %d created with %d actions", task.id, len(actions))
            
            # Auto-execute if enabled
            if self.auto_execute:
                self.execute_task(task.id)
            
            return task
            
        except Exception as e:
            logger.error("Failed to add task: %s", str(e))
            raise
    
    def execute_task(self, task_id: int, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task_id: ID of task to execute
            dry_run: If True, preview actions without executing
            
        Returns:
            Dict with execution results
        """
        try:
            task = self._get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
            
            logger.info("Executing task %d: %s", task_id, task.description)
            
            if not dry_run:
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = datetime.now()
            
            results = []
            
            for i, action in enumerate(task.actions):
                logger.info("Executing action %d/%d: %s", i + 1, len(task.actions), action)
                
                tool_name = action.get("tool")
                params = action.get("params", {})
                
                if dry_run:
                    result = self.mcp_server.dry_run(tool_name, **params)
                    results.append({
                        "action": action,
                        "preview": result
                    })
                else:
                    result = self.mcp_server.execute_tool(tool_name, **params)
                    results.append({
                        "action": action,
                        "result": result
                    })
                    
                    if not result.success:
                        # Action failed
                        task.status = TaskStatus.FAILED
                        task.error = result.error
                        task.updated_at = datetime.now()
                        
                        logger.error("Task %d failed at action %d", task_id, i + 1)
                        
                        return {
                            "success": False,
                            "task_id": task_id,
                            "error": result.error,
                            "completed_actions": i,
                            "total_actions": len(task.actions),
                            "results": results
                        }
            
            # All actions completed
            if not dry_run:
                task.status = TaskStatus.COMPLETED
                task.result = {"results": results}
                task.updated_at = datetime.now()
            
            logger.info("Task %d completed successfully", task_id)
            
            return {
                "success": True,
                "task_id": task_id,
                "dry_run": dry_run,
                "completed_actions": len(task.actions),
                "results": results
            }
            
        except Exception as e:
            logger.error("Task execution failed: %s", str(e))
            
            task = self._get_task(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.updated_at = datetime.now()
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get task details.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task details as dict
        """
        task = self._get_task(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "actions": task.actions,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "result": task.result,
            "error": task.error
        }
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """
        List all tasks.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of task details
        """
        tasks = self.tasks
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return [self.get_task(t.id) for t in tasks]
    
    def cancel_task(self, task_id: int) -> bool:
        """
        Cancel a pending task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if cancelled successfully
        """
        task = self._get_task(task_id)
        if not task:
            return False
        
        if task.status != TaskStatus.PENDING:
            logger.warning("Cannot cancel task %d with status %s", task_id, task.status)
            return False
        
        task.status = TaskStatus.CANCELLED
        task.updated_at = datetime.now()
        logger.info("Task %d cancelled", task_id)
        return True
    
    def _get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.
        
        Returns:
            Dict with stats
        """
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([t for t in self.tasks if t.status == status])
        
        return {
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "auto_execute": self.auto_execute
        }
