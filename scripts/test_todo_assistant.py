#!/usr/bin/env python3
"""
Quick test script for To-Do Assistant
======================================

Tests basic functionality without UI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.todo_assistant.mcp_server import MCPServer
from modules.todo_assistant.todo_agent import TodoAgent


def test_mcp_server():
    """Test MCP server."""
    print("\n=== Testing MCP Server ===")
    
    server = MCPServer(consent_required=False)
    
    print(f"Available tools: {server.list_tools()}")
    
    # Test dry run
    preview = server.dry_run("open_app", name="notepad")
    print(f"Dry run preview: {preview}")
    
    print("✅ MCP Server test passed")


def test_todo_agent():
    """Test Todo agent."""
    print("\n=== Testing Todo Agent ===")
    
    agent = TodoAgent(auto_execute=False)
    
    # Add a task
    task = agent.add_task("open notepad then type 'Hello World'")
    print(f"Task added: #{task.id} - {task.description}")
    print(f"Actions: {len(task.actions)}")
    
    for i, action in enumerate(task.actions, 1):
        print(f"  {i}. {action['tool']}({action['params']})")
    
    # Dry run
    result = agent.execute_task(task.id, dry_run=True)
    print(f"Dry run result: success={result['success']}")
    
    # Stats
    stats = agent.get_stats()
    print(f"Agent stats: {stats}")
    
    print("✅ Todo Agent test passed")


def test_task_parsing():
    """Test task parsing."""
    print("\n=== Testing Task Parser ===")
    
    from modules.todo_assistant.todo_agent.task_parser import TaskParser
    
    parser = TaskParser()
    
    test_tasks = [
        "open excel",
        "click Save button",
        "type 'my text'",
        "open chrome then click File then type 'test'",
        "run script 'test.py'"
    ]
    
    for task_desc in test_tasks:
        actions = parser.parse(task_desc)
        print(f"\nTask: {task_desc}")
        print(f"  Parsed into {len(actions)} action(s):")
        for action in actions:
            print(f"    - {action['tool']}({action['params']})")
    
    print("\n✅ Task Parser test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("To-Do Assistant - Quick Test")
    print("=" * 60)
    
    try:
        test_mcp_server()
        test_task_parsing()
        test_todo_agent()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
        print("\n📝 Next steps:")
        print("  1. Install optional dependencies:")
        print("     pip install streamlit pyautogui pillow")
        print("\n  2. Launch the UI:")
        print("     cd src/modules/todo_assistant/frontend")
        print("     streamlit run app.py")
        print("\n  3. Or use programmatically:")
        print("     from modules.todo_assistant import TodoAgent")
        print("     agent = TodoAgent()")
        print("     task = agent.add_task('open notepad')")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
