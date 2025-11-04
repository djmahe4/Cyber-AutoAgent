#!/usr/bin/env python3
"""
CLI Bridge for To-Do Assistant
===============================

Bridge between React CLI and Python To-Do Assistant.
Receives commands via command-line arguments and returns JSON responses.

Usage:
    python cli_bridge.py <command> <json_params>

Commands:
    add_task        - Add a new task
    execute_task    - Execute a task
    list_tasks      - List all tasks
    get_task        - Get task details
    cancel_task     - Cancel a task
    set_vision_mode - Enable/disable vision mode
    get_action_logs - Get action logs
    get_automation_info - Get automation info
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.todo_assistant.mcp_server import MCPServer, set_vision_mode, get_automation, get_logger
from modules.todo_assistant.rag_engine import RAGEngine
from modules.todo_assistant.todo_agent import TodoAgent, TaskStatus


# Global agent instance
_agent = None


def get_agent():
    """Get or create agent instance."""
    global _agent
    if _agent is None:
        # Use deployment adapter for configuration
        try:
            from modules.todo_assistant.deployment_adapter import get_config_adapter
            config_adapter = get_config_adapter()
            
            mcp_config = config_adapter.get_mcp_config()
            rag_config = config_adapter.get_rag_config()
            
            # Create MCP server with deployment-aware config
            mcp_server = MCPServer(consent_required=mcp_config["consent_required"])
            
            # Initialize RAG engine if available
            rag_engine = None
            if rag_config["enabled"]:
                try:
                    rag_engine = RAGEngine(
                        vector_store=rag_config["vector_store"],
                        persist_directory=rag_config["persist_directory"]
                    )
                except Exception as e:
                    logger.warning("RAG engine initialization failed: %s", str(e))
            
        except ImportError:
            # Fallback if deployment adapter not available
            mcp_server = MCPServer(consent_required=False)
            rag_engine = None
            try:
                rag_engine = RAGEngine(vector_store="faiss")
            except Exception:
                pass
        
        _agent = TodoAgent(
            mcp_server=mcp_server,
            rag_engine=rag_engine,
            auto_execute=False
        )
    return _agent


def add_task(params):
    """Add a new task."""
    try:
        agent = get_agent()
        description = params.get('description')
        
        if not description:
            return {'success': False, 'error': 'Description required'}
        
        task = agent.add_task(description)
        
        # Convert task to dict
        task_dict = {
            'id': task.id,
            'description': task.description,
            'status': task.status.value,
            'actions': task.actions,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'result': task.result,
            'error': task.error
        }
        
        return {
            'success': True,
            'task': task_dict
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def execute_task(params):
    """Execute a task."""
    try:
        agent = get_agent()
        task_id = params.get('task_id')
        dry_run = params.get('dry_run', False)
        
        if task_id is None:
            return {'success': False, 'error': 'task_id required'}
        
        result = agent.execute_task(task_id, dry_run=dry_run)
        
        return {
            'success': result['success'],
            'task_id': result.get('task_id'),
            'dry_run': result.get('dry_run', False),
            'completed_actions': result.get('completed_actions'),
            'results': result.get('results', []),
            'error': result.get('error')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def list_tasks(params):
    """List all tasks."""
    try:
        agent = get_agent()
        status_str = params.get('status')
        
        # Convert status string to enum if provided
        status = None
        if status_str:
            try:
                status = TaskStatus(status_str)
            except ValueError:
                return {'success': False, 'error': f'Invalid status: {status_str}'}
        
        tasks = agent.list_tasks(status=status)
        
        return {
            'success': True,
            'tasks': tasks
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_task(params):
    """Get task details."""
    try:
        agent = get_agent()
        task_id = params.get('task_id')
        
        if task_id is None:
            return {'success': False, 'error': 'task_id required'}
        
        task = agent.get_task(task_id)
        
        return {
            'success': True,
            'task': task
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def cancel_task(params):
    """Cancel a task."""
    try:
        agent = get_agent()
        task_id = params.get('task_id')
        
        if task_id is None:
            return {'success': False, 'error': 'task_id required'}
        
        success = agent.cancel_task(task_id)
        
        return {
            'success': success,
            'cancelled': success
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def set_vision_mode_cmd(params):
    """Enable/disable vision mode."""
    try:
        enabled = params.get('enabled', False)
        set_vision_mode(enabled)
        
        return {
            'success': True,
            'vision_mode': enabled
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_action_logs_cmd(params):
    """Get action logs."""
    try:
        logger = get_logger()
        logs = logger.get_session_log()
        
        return {
            'success': True,
            'logs': logs
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'logs': []
        }


def get_automation_info_cmd(params):
    """Get automation info."""
    try:
        automation = get_automation()
        info = automation.get_automation_info()
        
        return {
            'success': True,
            'info': info
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_deployment_info_cmd(params):
    """Get deployment information."""
    try:
        from modules.todo_assistant.deployment_adapter import get_config_adapter
        config_adapter = get_config_adapter()
        info = config_adapter.get_deployment_info()
        
        return {
            'success': True,
            'deployment': info
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'deployment': {
                'mode': 'unknown',
                'error': str(e)
            }
        }


# Command map
COMMANDS = {
    'add_task': add_task,
    'execute_task': execute_task,
    'list_tasks': list_tasks,
    'get_task': get_task,
    'cancel_task': cancel_task,
    'set_vision_mode': set_vision_mode_cmd,
    'get_action_logs': get_action_logs_cmd,
    'get_automation_info': get_automation_info_cmd,
    'get_deployment_info': get_deployment_info_cmd
}


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: cli_bridge.py <command> <json_params>'
        }))
        sys.exit(1)
    
    command = sys.argv[1]
    params_json = sys.argv[2]
    
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError as e:
        print(json.dumps({
            'success': False,
            'error': f'Invalid JSON parameters: {str(e)}'
        }))
        sys.exit(1)
    
    if command not in COMMANDS:
        print(json.dumps({
            'success': False,
            'error': f'Unknown command: {command}',
            'available_commands': list(COMMANDS.keys())
        }))
        sys.exit(1)
    
    # Execute command
    result = COMMANDS[command](params)
    
    # Output result as JSON
    print(json.dumps(result))


if __name__ == '__main__':
    main()
