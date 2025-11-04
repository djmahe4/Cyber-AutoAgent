"""
Streamlit UI for To-Do Assistant
=================================

Main Streamlit application providing:
- To-Do list management
- PDF upload for RAG
- Custom script editor
- Debug mode and logs
- Vibe coding interface
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import streamlit as st
except ImportError:
    print("ERROR: Streamlit is not installed. Install with: pip install streamlit")
    sys.exit(1)

from modules.todo_assistant.mcp_server import MCPServer
from modules.todo_assistant.rag_engine import RAGEngine
from modules.todo_assistant.todo_agent import TodoAgent, TaskStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="To-Do Desktop Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize Streamlit session state."""
    if "agent" not in st.session_state:
        mcp_server = MCPServer(consent_required=True)
        rag_engine = RAGEngine(vector_store="faiss")
        st.session_state.agent = TodoAgent(
            mcp_server=mcp_server,
            rag_engine=rag_engine,
            auto_execute=False
        )
    
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    if "vibe_code" not in st.session_state:
        st.session_state.vibe_code = ""


def render_header():
    """Render page header."""
    st.title("🤖 To-Do Desktop Assistant")
    st.markdown("""
    **AI-powered desktop automation with MCP + LangChain RAG + PyAutoGUI**
    
    Add tasks in natural language, upload PDF manuals for context, and let the AI automate your desktop!
    """)
    st.divider()


def render_sidebar():
    """Render sidebar with controls and info."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Auto-execute toggle
        auto_execute = st.checkbox(
            "Auto-Execute Tasks",
            value=st.session_state.agent.auto_execute,
            help="Automatically execute tasks after adding them"
        )
        st.session_state.agent.auto_execute = auto_execute
        
        # Debug mode toggle
        st.session_state.debug_mode = st.checkbox(
            "Debug Mode",
            value=st.session_state.debug_mode,
            help="Show detailed logs and execution traces"
        )
        
        st.divider()
        
        # Statistics
        st.header("📊 Statistics")
        stats = st.session_state.agent.get_stats()
        st.metric("Total Tasks", stats["total_tasks"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Completed", stats["status_counts"]["completed"])
        with col2:
            st.metric("Failed", stats["status_counts"]["failed"])
        
        st.divider()
        
        # MCP Tools
        st.header("🛠️ Available Tools")
        tools = st.session_state.agent.mcp_server.list_tools()
        for tool in tools:
            st.text(f"• {tool}")
        
        st.divider()
        
        # RAG Status
        st.header("📚 RAG Status")
        rag_stats = st.session_state.agent.rag_engine.get_stats()
        st.metric("Documents", rag_stats["num_documents"])
        st.text(f"Store: {rag_stats['vector_store_type']}")


def render_todo_section():
    """Render to-do list section."""
    st.header("📝 To-Do List")
    
    # Task input
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        task_input = st.text_input(
            "Add a new task",
            placeholder="e.g., 'Open Excel then click Save button'",
            label_visibility="collapsed"
        )
    
    with col2:
        add_button = st.button("➕ Add Task", use_container_width=True)
    
    with col3:
        dry_run = st.checkbox("Dry Run", help="Preview actions without executing")
    
    # Add task
    if add_button and task_input:
        with st.spinner("Parsing task..."):
            try:
                task = st.session_state.agent.add_task(task_input)
                st.success(f"✅ Task #{task.id} added with {len(task.actions)} actions")
            except Exception as e:
                st.error(f"❌ Failed to add task: {str(e)}")
    
    st.divider()
    
    # Display tasks
    tasks = st.session_state.agent.list_tasks()
    
    if not tasks:
        st.info("No tasks yet. Add your first task above!")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["All Tasks", "Pending", "Completed"])
    
    with tab1:
        render_task_list(tasks)
    
    with tab2:
        pending = [t for t in tasks if t["status"] == "pending"]
        render_task_list(pending)
    
    with tab3:
        completed = [t for t in tasks if t["status"] == "completed"]
        render_task_list(completed)


def render_task_list(tasks):
    """Render a list of tasks."""
    if not tasks:
        st.info("No tasks in this category")
        return
    
    for task in reversed(tasks):  # Show newest first
        render_task_card(task)


def render_task_card(task):
    """Render a single task card."""
    status = task["status"]
    status_emoji = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫"
    }.get(status, "❓")
    
    with st.expander(f"{status_emoji} Task #{task['id']}: {task['description']}", expanded=False):
        # Task details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.text(f"Status: {status.upper()}")
            st.text(f"Actions: {len(task['actions'])}")
            st.text(f"Created: {task['created_at'][:19]}")
        
        with col2:
            if status == "pending":
                if st.button("▶️ Execute", key=f"exec_{task['id']}"):
                    execute_task_ui(task['id'])
                if st.button("🚫 Cancel", key=f"cancel_{task['id']}"):
                    st.session_state.agent.cancel_task(task['id'])
                    st.rerun()
        
        # Show actions
        st.subheader("Actions")
        for i, action in enumerate(task['actions'], 1):
            st.code(f"{i}. {action['tool']}({action['params']})", language="python")
        
        # Show results if completed or failed
        if task.get("result"):
            st.subheader("Results")
            st.json(task["result"])
        
        if task.get("error"):
            st.error(f"Error: {task['error']}")


def execute_task_ui(task_id):
    """Execute a task with UI feedback."""
    with st.spinner(f"Executing task #{task_id}..."):
        result = st.session_state.agent.execute_task(task_id)
        
        if result["success"]:
            st.success(f"✅ Task #{task_id} completed successfully!")
        else:
            st.error(f"❌ Task #{task_id} failed: {result.get('error', 'Unknown error')}")
        
        st.rerun()


def render_pdf_section():
    """Render PDF upload section."""
    st.header("📚 PDF Manual Upload")
    st.markdown("Upload PDF manuals to enhance the AI's knowledge for better task automation.")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload software manuals, documentation, or guides"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.text(f"File: {uploaded_file.name}")
            st.text(f"Size: {uploaded_file.size / 1024:.2f} KB")
        
        with col2:
            if st.button("📥 Upload & Index", use_container_width=True):
                with st.spinner("Processing PDF..."):
                    try:
                        # Save temporarily
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Ingest into RAG
                        result = st.session_state.agent.rag_engine.ingest_pdf(temp_path)
                        
                        if result["success"]:
                            st.success(f"✅ PDF indexed! {result['num_documents']} chunks added.")
                        else:
                            st.error(f"❌ Failed: {result['error']}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")


def render_scripts_section():
    """Render custom scripts section."""
    st.header("🔧 Custom Automation Scripts")
    st.markdown("Create and manage custom Python scripts for complex automation tasks.")
    
    # Script directory
    scripts_dir = Path("./src/modules/todo_assistant/ui_scripts")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # List existing scripts
    scripts = list(scripts_dir.glob("*.py"))
    
    if scripts:
        st.subheader("Existing Scripts")
        for script in scripts:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(script.name)
            with col2:
                if st.button("▶️ Run", key=f"run_{script.name}"):
                    run_custom_script_ui(str(script))
            with col3:
                if st.button("👁️ View", key=f"view_{script.name}"):
                    st.session_state.viewing_script = script.name
    
    st.divider()
    
    # Script editor
    st.subheader("Script Editor")
    
    script_name = st.text_input("Script name", placeholder="my_script.py")
    script_code = st.text_area(
        "Script code",
        height=300,
        placeholder="# Write your Python automation script here\n\nimport pyautogui\n\n# Your code..."
    )
    
    if st.button("💾 Save Script"):
        if script_name and script_code:
            if not script_name.endswith(".py"):
                script_name += ".py"
            
            script_path = scripts_dir / script_name
            script_path.write_text(script_code)
            st.success(f"✅ Script saved: {script_name}")
            st.rerun()
        else:
            st.error("Please provide both script name and code")


def run_custom_script_ui(script_path):
    """Run a custom script with UI feedback."""
    with st.spinner(f"Running {Path(script_path).name}..."):
        result = st.session_state.agent.mcp_server.execute_tool(
            "run_custom_script",
            file=script_path
        )
        
        if result.success:
            st.success("✅ Script completed!")
            if st.session_state.debug_mode:
                st.code(result.data.get("stdout", ""), language="text")
        else:
            st.error(f"❌ Script failed: {result.error}")


def render_debug_section():
    """Render debug and logs section."""
    if not st.session_state.debug_mode:
        return
    
    st.header("🐛 Debug Mode")
    
    # Execution log
    st.subheader("Execution Log")
    log = st.session_state.agent.mcp_server.get_execution_log()
    
    if log:
        for i, entry in enumerate(reversed(log), 1):
            with st.expander(f"#{i} - {entry['tool']}", expanded=False):
                st.json(entry)
    else:
        st.info("No executions yet")
    
    if st.button("🗑️ Clear Log"):
        st.session_state.agent.mcp_server.clear_log()
        st.rerun()


def render_vibe_coding():
    """Render vibe coding interface."""
    st.header("✨ Vibe Coding Mode")
    st.markdown("**Gemini-style creative coding interface** - Draft, preview, and execute code conversationally!")
    
    # Conversational panel
    st.subheader("💬 Describe Your Automation")
    description = st.text_area(
        "What would you like to automate?",
        height=100,
        placeholder="e.g., 'Create a script that opens Chrome, navigates to GitHub, and takes a screenshot'"
    )
    
    if st.button("🪄 Generate Code"):
        if description:
            with st.spinner("Generating code..."):
                # Placeholder for LLM code generation
                # In production, this would call an LLM to generate code
                st.session_state.vibe_code = f"""# Generated automation script
# Task: {description}

import pyautogui
import time

# Your automation code here
print("Automation script generated")
"""
                st.success("✅ Code generated!")
    
    st.divider()
    
    # Code preview
    if st.session_state.vibe_code:
        st.subheader("📝 Generated Code")
        edited_code = st.text_area(
            "Edit code if needed",
            value=st.session_state.vibe_code,
            height=300,
            key="vibe_code_editor"
        )
        st.session_state.vibe_code = edited_code
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Run in Sandbox"):
                st.info("Sandbox execution not yet implemented")
        
        with col2:
            if st.button("💾 Save as Script"):
                scripts_dir = Path("./src/modules/todo_assistant/ui_scripts")
                scripts_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = Path(__file__).stat().st_mtime
                script_name = f"vibe_script_{int(timestamp)}.py"
                script_path = scripts_dir / script_name
                script_path.write_text(st.session_state.vibe_code)
                
                st.success(f"✅ Saved as {script_name}")
        
        with col3:
            if st.button("🗑️ Clear"):
                st.session_state.vibe_code = ""
                st.rerun()


def main():
    """Main application."""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 To-Do List",
        "📚 PDF Upload",
        "🔧 Scripts",
        "✨ Vibe Coding",
        "🐛 Debug"
    ])
    
    with tab1:
        render_todo_section()
    
    with tab2:
        render_pdf_section()
    
    with tab3:
        render_scripts_section()
    
    with tab4:
        render_vibe_coding()
    
    with tab5:
        render_debug_section()


if __name__ == "__main__":
    main()
