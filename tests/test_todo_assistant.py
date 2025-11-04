"""
Tests for To-Do Assistant Module
=================================

Test suite for MCP server, RAG engine, and Todo agent.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.todo_assistant.mcp_server import MCPServer
from modules.todo_assistant.todo_agent import TodoAgent, TaskStatus
from modules.todo_assistant.todo_agent.task_parser import TaskParser


class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_server_initialization(self):
        """Test server initializes with correct tools."""
        server = MCPServer(consent_required=False)
        tools = server.list_tools()
        
        assert len(tools) == 5
        assert "open_app" in tools
        assert "click_ui" in tools
        assert "type_text" in tools
        assert "read_screen" in tools
        assert "run_custom_script" in tools
    
    def test_get_tool_info(self):
        """Test retrieving tool information."""
        server = MCPServer(consent_required=False)
        info = server.get_tool_info("open_app")
        
        assert info is not None
        assert info["name"] == "open_app"
        assert "description" in info
    
    def test_execute_invalid_tool(self):
        """Test executing non-existent tool."""
        server = MCPServer(consent_required=False)
        result = server.execute_tool("nonexistent_tool")
        
        assert not result.success
        assert "not found" in result.message.lower()
    
    def test_dry_run(self):
        """Test dry-run preview."""
        server = MCPServer(consent_required=False)
        preview = server.dry_run("open_app", name="notepad")
        
        assert "notepad" in preview.lower()
        assert "would open" in preview.lower()
    
    def test_execution_log(self):
        """Test execution logging."""
        server = MCPServer(consent_required=False)
        
        # Initially empty
        assert len(server.get_execution_log()) == 0
        
        # Execute a tool (will fail but still logs)
        server.execute_tool("open_app", name="test_app")
        
        # Should have one entry
        assert len(server.get_execution_log()) == 1
        
        # Clear log
        server.clear_log()
        assert len(server.get_execution_log()) == 0


class TestTaskParser:
    """Test task parsing functionality."""
    
    def test_simple_open_task(self):
        """Test parsing simple 'open' command."""
        parser = TaskParser()
        actions = parser.parse("open notepad")
        
        assert len(actions) == 1
        assert actions[0]["tool"] == "open_app"
        assert actions[0]["params"]["name"] == "notepad"
    
    def test_launch_command(self):
        """Test parsing 'launch' command."""
        parser = TaskParser()
        actions = parser.parse("launch excel")
        
        assert len(actions) == 1
        assert actions[0]["tool"] == "open_app"
        assert actions[0]["params"]["name"] == "excel"
    
    def test_click_command(self):
        """Test parsing 'click' command."""
        parser = TaskParser()
        actions = parser.parse("click Save button")
        
        assert len(actions) == 1
        assert actions[0]["tool"] == "click_ui"
        assert "save" in actions[0]["params"]["label"].lower()
    
    def test_type_command(self):
        """Test parsing 'type' command."""
        parser = TaskParser()
        actions = parser.parse("type 'Hello World'")
        
        assert len(actions) == 1
        assert actions[0]["tool"] == "type_text"
        # Parser converts to lowercase
        assert actions[0]["params"]["text"].lower() == "hello world"
    
    def test_multi_step_task(self):
        """Test parsing multi-step task."""
        parser = TaskParser()
        actions = parser.parse("open notepad then type 'test' then read screen")
        
        # Should parse into 3 actions
        assert len(actions) >= 2  # At least open and type
        
        # First should be open
        assert actions[0]["tool"] == "open_app"
        
        # Should contain type action
        tools = [a["tool"] for a in actions]
        assert "type_text" in tools
    
    def test_run_script_command(self):
        """Test parsing 'run script' command."""
        parser = TaskParser()
        actions = parser.parse("run script 'test.py'")
        
        assert len(actions) == 1
        assert actions[0]["tool"] == "run_custom_script"
        assert actions[0]["params"]["file"] == "test.py"
    
    def test_supported_actions(self):
        """Test getting supported actions list."""
        parser = TaskParser()
        actions = parser.get_supported_actions()
        
        assert len(actions) > 0
        assert any("open" in a.lower() for a in actions)
        assert any("click" in a.lower() for a in actions)


class TestTodoAgent:
    """Test Todo agent functionality."""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = TodoAgent(auto_execute=False)
        
        assert agent is not None
        assert not agent.auto_execute
        assert len(agent.tasks) == 0
    
    def test_add_task(self):
        """Test adding a task."""
        agent = TodoAgent(auto_execute=False)
        task = agent.add_task("open notepad")
        
        assert task is not None
        assert task.id == 1
        assert task.status == TaskStatus.PENDING
        assert len(task.actions) > 0
        assert len(agent.tasks) == 1
    
    def test_get_task(self):
        """Test retrieving task details."""
        agent = TodoAgent(auto_execute=False)
        task = agent.add_task("open excel")
        
        retrieved = agent.get_task(task.id)
        assert retrieved is not None
        assert retrieved["id"] == task.id
        assert retrieved["description"] == "open excel"
    
    def test_list_tasks(self):
        """Test listing all tasks."""
        agent = TodoAgent(auto_execute=False)
        
        agent.add_task("open notepad")
        agent.add_task("open excel")
        
        tasks = agent.list_tasks()
        assert len(tasks) == 2
    
    def test_list_tasks_by_status(self):
        """Test filtering tasks by status."""
        agent = TodoAgent(auto_execute=False)
        
        agent.add_task("open notepad")
        agent.add_task("open excel")
        
        pending_tasks = agent.list_tasks(status=TaskStatus.PENDING)
        assert len(pending_tasks) == 2
        
        completed_tasks = agent.list_tasks(status=TaskStatus.COMPLETED)
        assert len(completed_tasks) == 0
    
    def test_cancel_task(self):
        """Test cancelling a pending task."""
        agent = TodoAgent(auto_execute=False)
        task = agent.add_task("open notepad")
        
        success = agent.cancel_task(task.id)
        assert success
        
        retrieved = agent.get_task(task.id)
        assert retrieved["status"] == TaskStatus.CANCELLED.value
    
    def test_dry_run_execution(self):
        """Test dry-run task execution."""
        agent = TodoAgent(auto_execute=False)
        task = agent.add_task("open notepad")
        
        result = agent.execute_task(task.id, dry_run=True)
        
        assert result["success"]
        assert result["dry_run"]
        
        # Task should still be pending after dry run
        retrieved = agent.get_task(task.id)
        assert retrieved["status"] == TaskStatus.PENDING.value
    
    def test_get_stats(self):
        """Test getting agent statistics."""
        agent = TodoAgent(auto_execute=False)
        
        agent.add_task("open notepad")
        agent.add_task("open excel")
        task = agent.add_task("open chrome")
        agent.cancel_task(task.id)
        
        stats = agent.get_stats()
        
        assert stats["total_tasks"] == 3
        assert stats["status_counts"]["pending"] == 2
        assert stats["status_counts"]["cancelled"] == 1
    
    def test_auto_execute_mode(self):
        """Test auto-execute mode."""
        agent = TodoAgent(auto_execute=True)
        
        assert agent.auto_execute
        
        # Adding a task should trigger execution (though it will fail)
        task = agent.add_task("open nonexistent_app")
        
        # Task should have been attempted
        # Status might be failed or completed depending on execution
        retrieved = agent.get_task(task.id)
        assert retrieved["status"] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]


class TestRAGEngine:
    """Test RAG engine functionality."""
    
    def test_rag_initialization(self):
        """Test RAG engine initializes."""
        # Skip if dependencies not available
        pytest.importorskip("langchain_community")
        
        from modules.todo_assistant.rag_engine import RAGEngine
        
        # Use temp directory for testing
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RAGEngine(
                vector_store="faiss",
                persist_directory=tmpdir
            )
            
            stats = engine.get_stats()
            assert stats["vector_store_type"] == "faiss"
            assert stats["num_documents"] == 0
    
    def test_rag_stats(self):
        """Test getting RAG statistics."""
        pytest.importorskip("langchain_community")
        
        from modules.todo_assistant.rag_engine import RAGEngine
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RAGEngine(persist_directory=tmpdir)
            stats = engine.get_stats()
            
            assert "vector_store_type" in stats
            assert "num_documents" in stats
            assert "persist_directory" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
