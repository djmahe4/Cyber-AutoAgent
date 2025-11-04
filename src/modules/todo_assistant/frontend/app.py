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
    
    if "vision_mode" not in st.session_state:
        st.session_state.vision_mode = False
    
    if "action_logs" not in st.session_state:
        st.session_state.action_logs = []


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
        
        # Vision Mode toggle
        vision_mode = st.checkbox(
            "🔍 Vision Mode / Pixel-Click Fallback",
            value=st.session_state.vision_mode,
            help="Use OpenCV + PyAutoGUI for pixel-based UI element detection"
        )
        
        if vision_mode != st.session_state.vision_mode:
            st.session_state.vision_mode = vision_mode
            # Update MCP server to use vision mode
            try:
                from modules.todo_assistant.mcp_server import tools
                tools.set_vision_mode(vision_mode)
                st.success(f"Vision mode {'enabled' if vision_mode else 'disabled'}")
            except Exception as e:
                st.error(f"Failed to set vision mode: {str(e)}")
        
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
    """Render enhanced debug dashboard with logs, screenshots, and timeline."""
    st.header("🐛 Debug Dashboard")
    
    # Get action logger if available
    try:
        from modules.todo_assistant.mcp_server import tools
        action_logger = tools.get_logger()
        log_entries = action_logger.get_session_log()
        summary = action_logger.get_action_summary()
    except Exception as e:
        st.error(f"Failed to load action logger: {str(e)}")
        log_entries = []
        summary = {}
    
    # Summary metrics
    st.subheader("📊 Session Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Actions", summary.get("total_actions", 0))
    with col2:
        st.metric("Successful", summary.get("successful_actions", 0))
    with col3:
        st.metric("Failed", summary.get("failed_actions", 0))
    with col4:
        st.metric("Anomalies", summary.get("anomalies", 0))
    
    st.divider()
    
    # Tab interface for different views
    debug_tab1, debug_tab2, debug_tab3, debug_tab4, debug_tab5 = st.tabs([
        "📁 Run Log Timeline",
        "🖼️ Screenshots",
        "🕒 Execution Trace",
        "🧠 Platform Info",
        "🛑 Controls"
    ])
    
    with debug_tab1:
        render_run_log_timeline(log_entries)
    
    with debug_tab2:
        render_screenshot_viewer(log_entries, summary)
    
    with debug_tab3:
        render_execution_trace(log_entries)
    
    with debug_tab4:
        render_platform_info()
    
    with debug_tab5:
        render_debug_controls()


def render_run_log_timeline(log_entries):
    """Render run log timeline with all actions."""
    st.subheader("📁 Action Timeline")
    
    if not log_entries:
        st.info("No actions logged yet. Execute some tasks to see them here.")
        return
    
    # Display entries in reverse chronological order
    for entry in reversed(log_entries):
        if entry.get("type") == "anomaly":
            # Anomaly entry
            with st.expander(
                f"⚠️ ANOMALY: {entry.get('anomaly_type', 'Unknown')} - {entry.get('timestamp', '')}",
                expanded=True
            ):
                st.error(entry.get("description", "No description"))
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Expected:**")
                    st.code(str(entry.get("expected", "N/A")))
                with col2:
                    st.write("**Actual:**")
                    st.code(str(entry.get("actual", "N/A")))
                
                if entry.get("screenshot"):
                    try:
                        from PIL import Image
                        img = Image.open(entry["screenshot"])
                        st.image(img, caption="Screenshot at anomaly", use_container_width=True)
                    except Exception as e:
                        st.error(f"Failed to load screenshot: {str(e)}")
        else:
            # Regular action entry
            action_id = entry.get("action_id", "?")
            action_type = entry.get("action_type", "unknown")
            target = entry.get("target", "unknown")
            timestamp = entry.get("timestamp", "")
            success = entry.get("result", {}).get("success", False)
            method = entry.get("method", "unknown")
            
            status_icon = "✅" if success else "❌"
            
            with st.expander(
                f"{status_icon} #{action_id} - {action_type}({target}) - {timestamp}",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Action:** {action_type}")
                    st.write(f"**Target:** {target}")
                    st.write(f"**Method:** {method}")
                    st.write(f"**Status:** {'Success' if success else 'Failed'}")
                
                with col2:
                    st.write("**Result:**")
                    result_data = entry.get("result", {})
                    if result_data.get("error"):
                        st.error(result_data["error"])
                    st.json(result_data.get("data", {}))
                
                # Show screenshots if available
                screenshots = entry.get("screenshots", {})
                if screenshots.get("after"):
                    try:
                        from PIL import Image
                        img = Image.open(screenshots["after"])
                        st.image(img, caption="After action", use_container_width=True)
                    except Exception as e:
                        st.text(f"Screenshot: {screenshots['after']}")


def render_screenshot_viewer(log_entries, summary):
    """Render screenshot viewer."""
    st.subheader("🖼️ Screenshot Viewer")
    
    screenshot_dir = summary.get("screenshot_dir")
    if not screenshot_dir:
        st.info("No screenshot directory available")
        return
    
    from pathlib import Path
    screenshot_path = Path(screenshot_dir)
    
    if not screenshot_path.exists():
        st.info("Screenshot directory not found")
        return
    
    # List all screenshots
    screenshots = sorted(screenshot_path.glob("*.png"))
    
    if not screenshots:
        st.info("No screenshots available yet")
        return
    
    st.write(f"**Directory:** {screenshot_dir}")
    st.write(f"**Total screenshots:** {len(screenshots)}")
    
    # Select screenshot to view
    screenshot_names = [s.name for s in screenshots]
    selected = st.selectbox("Select screenshot:", screenshot_names)
    
    if selected:
        selected_path = screenshot_path / selected
        try:
            from PIL import Image
            img = Image.open(selected_path)
            st.image(img, caption=selected, use_container_width=True)
            
            # Show file info
            st.text(f"Size: {selected_path.stat().st_size / 1024:.2f} KB")
            st.text(f"Path: {selected_path}")
        except Exception as e:
            st.error(f"Failed to load screenshot: {str(e)}")


def render_execution_trace(log_entries):
    """Render execution trace with timing information."""
    st.subheader("🕒 Execution Trace")
    
    if not log_entries:
        st.info("No execution trace available yet")
        return
    
    # Filter out anomalies for trace
    action_entries = [e for e in log_entries if e.get("type") != "anomaly"]
    
    if not action_entries:
        st.info("No actions in trace")
        return
    
    # Create trace table
    trace_data = []
    for entry in action_entries:
        trace_data.append({
            "ID": entry.get("action_id", "?"),
            "Timestamp": entry.get("timestamp", "")[:19],
            "Action": entry.get("action_type", "?"),
            "Target": entry.get("target", "?")[:30],
            "Method": entry.get("method", "?"),
            "Status": "✅ Success" if entry.get("result", {}).get("success") else "❌ Failed"
        })
    
    st.dataframe(trace_data, use_container_width=True)
    
    # Show methods distribution
    st.subheader("Methods Used")
    methods = {}
    for entry in action_entries:
        method = entry.get("method", "unknown")
        methods[method] = methods.get(method, 0) + 1
    
    if methods:
        st.bar_chart(methods)


def render_platform_info():
    """Render platform and automation library information."""
    st.subheader("🧠 Platform & Automation Info")
    
    try:
        from modules.todo_assistant.mcp_server import tools
        automation = tools.get_automation()
        info = automation.get_automation_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Platform:**", info.get("platform", "Unknown"))
            st.write("**Vision Mode:**", "✅ Enabled" if info.get("vision_mode") else "❌ Disabled")
            st.write("**Primary Method:**", info.get("primary_method", "Unknown"))
        
        with col2:
            st.write("**Available Methods:**")
            for method in info.get("available_methods", []):
                st.write(f"  • {method}")
        
        st.divider()
        
        st.subheader("Available Libraries")
        libraries = info.get("libraries", {})
        
        for lib, available in libraries.items():
            status = "✅ Available" if available else "❌ Not Available"
            st.write(f"**{lib}:** {status}")
    
    except Exception as e:
        st.error(f"Failed to get platform info: {str(e)}")


def render_debug_controls():
    """Render debug controls for interrupting and managing execution."""
    st.subheader("🛑 Debug Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Execution Log", use_container_width=True):
            try:
                st.session_state.agent.mcp_server.clear_log()
                st.success("Execution log cleared")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to clear log: {str(e)}")
    
    with col2:
        if st.button("📊 Export Session Log", use_container_width=True):
            try:
                from modules.todo_assistant.mcp_server import tools
                action_logger = tools.get_logger()
                summary = action_logger.get_action_summary()
                
                st.json(summary)
                st.success(f"Log file: {summary.get('log_file')}")
            except Exception as e:
                st.error(f"Failed to export log: {str(e)}")
    
    st.divider()
    
    st.subheader("Switch to Vision Mode")
    st.info("""
    Vision Mode uses OpenCV + PyAutoGUI for pixel-based UI matching.
    
    **When to use:**
    - Platform-specific tools aren't working
    - Need precise pixel-level clicking
    - Working with custom or non-standard UI elements
    
    **Requirements:**
    - Template images for UI elements
    - OpenCV and PyAutoGUI installed
    
    Toggle Vision Mode in the sidebar settings.
    """)
    
    st.divider()
    
    st.subheader("Replay Actions")
    st.info("Action replay feature coming soon - will allow replaying logged actions step by step.")


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
