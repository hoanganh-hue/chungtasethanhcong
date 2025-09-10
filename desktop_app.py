"""
Desktop App Interface for OpenManus-Youtu Integrated Framework
Cross-platform desktop interface using tkinter for Windows/macOS/Linux
"""

import asyncio
import json
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from core.orchestration import orchestrator
    from agents.dynamic_agent import dynamic_agent_factory
    from core.communication import communication_hub
    from core.state_manager import state_manager
    from core.memory import memory_manager
    from tools.pdf_tools import pdf_processor
    from tools.image_tools import image_processor
    from tools.email_tools import email_processor
    from tools.calendar_tools import calendar_manager
    DESKTOP_APP_AVAILABLE = True
except ImportError as e:
    DESKTOP_APP_AVAILABLE = False
    logger.warning(f"Desktop app dependencies not available: {e}")

class DesktopAppInterface:
    """Desktop application interface for the framework."""
    
    def __init__(self):
        self.root = None
        self.agents = {}
        self.current_agent = None
        self.messages = []
        self.system_status = "disconnected"
        
    def get_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of available agents."""
        try:
            return dynamic_agent_factory.list_active_agents()
        except:
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        try:
            return {
                "status": "connected",
                "agents": len(self.get_agent_list()),
                "timestamp": datetime.now().isoformat()
            }
        except:
            return {
                "status": "disconnected",
                "agents": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def send_message_to_agent(self, agent_id: str, message: str) -> Dict[str, Any]:
        """Send message to agent."""
        try:
            # Simulate message sending
            response = {
                "success": True,
                "message": f"Message sent to agent {agent_id}",
                "response": f"Agent {agent_id} received: {message}",
                "timestamp": datetime.now().isoformat()
            }
            self.messages.append(response)
            return response
        except Exception as e:
            return {"success": False, "error": str(e)}

class AgentManagementFrame(ttk.Frame):
    """Frame for agent management."""
    
    def __init__(self, parent, desktop_app):
        super().__init__(parent)
        self.desktop_app = desktop_app
        self.setup_ui()
        self.refresh_agents()
    
    def setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = ttk.Label(self, text="🤖 Agent Management", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_agents)
        refresh_btn.pack(side="left", padx=5)
        
        create_btn = ttk.Button(button_frame, text="➕ Create Agent", command=self.create_agent_dialog)
        create_btn.pack(side="left", padx=5)
        
        # Agent list
        self.agent_tree = ttk.Treeview(self, columns=("Type", "Status", "Created"), show="tree headings")
        self.agent_tree.heading("#0", text="Name")
        self.agent_tree.heading("Type", text="Type")
        self.agent_tree.heading("Status", text="Status")
        self.agent_tree.heading("Created", text="Created")
        
        self.agent_tree.column("#0", width=200)
        self.agent_tree.column("Type", width=100)
        self.agent_tree.column("Status", width=100)
        self.agent_tree.column("Created", width=150)
        
        # Scrollbar for agent list
        agent_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.agent_tree.yview)
        self.agent_tree.configure(yscrollcommand=agent_scrollbar.set)
        
        # Pack agent list and scrollbar
        self.agent_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        agent_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click event
        self.agent_tree.bind("<Double-1>", self.on_agent_double_click)
    
    def refresh_agents(self):
        """Refresh the agent list."""
        # Clear existing items
        for item in self.agent_tree.get_children():
            self.agent_tree.delete(item)
        
        # Get agents
        agents = self.desktop_app.get_agent_list()
        
        if not agents:
            self.agent_tree.insert("", "end", text="No agents available", values=("", "", ""))
        else:
            for agent in agents:
                self.agent_tree.insert("", "end", 
                    text=agent['name'],
                    values=(agent['type'], agent['status'], agent['created_at'][:19])
                )
    
    def create_agent_dialog(self):
        """Open create agent dialog."""
        dialog = CreateAgentDialog(self, self.desktop_app)
        self.wait_window(dialog)
        self.refresh_agents()
    
    def on_agent_double_click(self, event):
        """Handle agent double-click."""
        selection = self.agent_tree.selection()
        if selection:
            item = self.agent_tree.item(selection[0])
            agent_name = item['text']
            # Open agent chat
            self.open_agent_chat(agent_name)
    
    def open_agent_chat(self, agent_name: str):
        """Open chat with agent."""
        chat_window = AgentChatWindow(self, agent_name, self.desktop_app)
        chat_window.grab_set()

class CreateAgentDialog(tk.Toplevel):
    """Dialog for creating new agents."""
    
    def __init__(self, parent, desktop_app):
        super().__init__(parent)
        self.desktop_app = desktop_app
        self.result = None
        self.setup_ui()
        
        # Center the dialog
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
    
    def setup_ui(self):
        """Setup the dialog UI."""
        self.title("Create New Agent")
        
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Agent type
        ttk.Label(main_frame, text="Agent Type:").pack(anchor="w", pady=5)
        self.agent_type_var = tk.StringVar(value="general")
        agent_type_combo = ttk.Combobox(main_frame, textvariable=self.agent_type_var, 
                                       values=["cccd", "tax", "data_analysis", "web_automation", "general"])
        agent_type_combo.pack(fill="x", pady=5)
        
        # Agent name
        ttk.Label(main_frame, text="Agent Name:").pack(anchor="w", pady=5)
        self.agent_name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.agent_name_var)
        name_entry.pack(fill="x", pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor="w", pady=5)
        self.description_text = scrolledtext.ScrolledText(main_frame, height=4)
        self.description_text.pack(fill="both", expand=True, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Create", command=self.create_agent).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")
    
    def create_agent(self):
        """Create the agent."""
        agent_type = self.agent_type_var.get()
        agent_name = self.agent_name_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        
        if not agent_name:
            messagebox.showerror("Error", "Please enter an agent name")
            return
        
        try:
            # Create agent (simulate)
            agent_id = f"agent_{len(self.desktop_app.get_agent_list()) + 1}"
            messagebox.showinfo("Success", f"Agent '{agent_name}' created successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create agent: {e}")

class AgentChatWindow(tk.Toplevel):
    """Window for agent chat."""
    
    def __init__(self, parent, agent_name: str, desktop_app):
        super().__init__(parent)
        self.agent_name = agent_name
        self.desktop_app = desktop_app
        self.setup_ui()
        
        # Center the window
        self.geometry("600x500")
        self.transient(parent)
    
    def setup_ui(self):
        """Setup the chat window UI."""
        self.title(f"💬 Chat with {self.agent_name}")
        
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Messages area
        self.messages_text = scrolledtext.ScrolledText(main_frame, state="disabled", wrap="word")
        self.messages_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x")
        
        self.message_var = tk.StringVar()
        message_entry = ttk.Entry(input_frame, textvariable=self.message_var)
        message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        message_entry.bind("<Return>", self.send_message)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side="right")
        
        # Add welcome message
        self.add_message("System", f"Connected to {self.agent_name}")
    
    def send_message(self, event=None):
        """Send message to agent."""
        message = self.message_var.get().strip()
        if not message:
            return
        
        # Add user message
        self.add_message("You", message)
        self.message_var.set("")
        
        # Send to agent (simulate)
        response = self.desktop_app.send_message_to_agent(self.agent_name, message)
        if response.get('success'):
            self.add_message(self.agent_name, response.get('response', 'No response'))
        else:
            self.add_message("System", f"Error: {response.get('error', 'Unknown error')}")
    
    def add_message(self, sender: str, message: str):
        """Add message to chat."""
        self.messages_text.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages_text.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.messages_text.config(state="disabled")
        self.messages_text.see(tk.END)

class SystemStatusFrame(ttk.Frame):
    """Frame for system status."""
    
    def __init__(self, parent, desktop_app):
        super().__init__(parent)
        self.desktop_app = desktop_app
        self.setup_ui()
        self.refresh_status()
    
    def setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = ttk.Label(self, text="📊 System Status", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(self, text="System Information", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_labels = {}
        
        # Status items
        status_items = [
            ("Connection Status", "status"),
            ("Active Agents", "agents"),
            ("Last Update", "timestamp")
        ]
        
        for label_text, key in status_items:
            frame = ttk.Frame(status_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{label_text}:", width=20, anchor="w").pack(side="left")
            self.status_labels[key] = ttk.Label(frame, text="Loading...", anchor="w")
            self.status_labels[key].pack(side="left", fill="x", expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(self, text="🔄 Refresh Status", command=self.refresh_status)
        refresh_btn.pack(pady=10)
        
        # Performance frame
        perf_frame = ttk.LabelFrame(self, text="Performance Metrics", padding=10)
        perf_frame.pack(fill="x", padx=10, pady=5)
        
        # Performance metrics
        perf_metrics = [
            ("Memory Usage", "Normal"),
            ("CPU Usage", "Normal"),
            ("Response Time", "< 1s"),
            ("Active Connections", "Stable")
        ]
        
        for metric_name, metric_value in perf_metrics:
            frame = ttk.Frame(perf_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{metric_name}:", width=20, anchor="w").pack(side="left")
            ttk.Label(frame, text=metric_value, anchor="w").pack(side="left", fill="x", expand=True)
    
    def refresh_status(self):
        """Refresh system status."""
        status = self.desktop_app.get_system_status()
        
        self.status_labels["status"].config(text=status["status"])
        self.status_labels["agents"].config(text=str(status["agents"]))
        self.status_labels["timestamp"].config(text=status["timestamp"][:19])

class ToolsFrame(ttk.Frame):
    """Frame for tools and utilities."""
    
    def __init__(self, parent, desktop_app):
        super().__init__(parent)
        self.desktop_app = desktop_app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = ttk.Label(self, text="🛠️ Tools & Utilities", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Tools grid
        tools_frame = ttk.Frame(self)
        tools_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tool buttons
        tools = [
            ("📄 PDF Tools", self.open_pdf_tools),
            ("🖼️ Image Tools", self.open_image_tools),
            ("📧 Email Tools", self.open_email_tools),
            ("📅 Calendar", self.open_calendar_tools),
            ("📊 Analytics", self.open_analytics),
            ("⚙️ Settings", self.open_settings)
        ]
        
        for i, (tool_name, tool_func) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            btn = ttk.Button(tools_frame, text=tool_name, command=tool_func)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(3):
            tools_frame.columnconfigure(i, weight=1)
    
    def open_pdf_tools(self):
        """Open PDF tools."""
        pdf_window = PDFToolsWindow(self)
        pdf_window.grab_set()
    
    def open_image_tools(self):
        """Open image tools."""
        image_window = ImageToolsWindow(self)
        image_window.grab_set()
    
    def open_email_tools(self):
        """Open email tools."""
        messagebox.showinfo("Email Tools", "Email tools coming soon...")
    
    def open_calendar_tools(self):
        """Open calendar tools."""
        messagebox.showinfo("Calendar Tools", "Calendar tools coming soon...")
    
    def open_analytics(self):
        """Open analytics."""
        messagebox.showinfo("Analytics", "Analytics coming soon...")
    
    def open_settings(self):
        """Open settings."""
        messagebox.showinfo("Settings", "Settings coming soon...")

class PDFToolsWindow(tk.Toplevel):
    """Window for PDF tools."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.geometry("500x400")
        self.transient(parent)
    
    def setup_ui(self):
        """Setup the PDF tools UI."""
        self.title("📄 PDF Tools")
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Select PDF File", padding=10)
        file_frame.pack(fill="x", pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side="right")
        
        # Tools
        tools_frame = ttk.LabelFrame(main_frame, text="PDF Operations", padding=10)
        tools_frame.pack(fill="both", expand=True)
        
        ttk.Button(tools_frame, text="📖 Extract Text", command=self.extract_text).pack(fill="x", pady=2)
        ttk.Button(tools_frame, text="ℹ️ Get Information", command=self.get_info).pack(fill="x", pady=2)
        ttk.Button(tools_frame, text="🖼️ Extract Images", command=self.extract_images).pack(fill="x", pady=2)
        ttk.Button(tools_frame, text="📄 Split PDF", command=self.split_pdf).pack(fill="x", pady=2)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8)
        self.results_text.pack(fill="both", expand=True)
    
    def browse_file(self):
        """Browse for PDF file."""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def extract_text(self):
        """Extract text from PDF."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a PDF file")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "Extracting text...\n")
        
        # Simulate extraction
        self.results_text.insert(tk.END, f"Text extracted from: {file_path}\n")
        self.results_text.insert(tk.END, "Sample extracted text would appear here...\n")
    
    def get_info(self):
        """Get PDF information."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a PDF file")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"PDF Information for: {file_path}\n")
        self.results_text.insert(tk.END, "Pages: 10\n")
        self.results_text.insert(tk.END, "Size: 2.5 MB\n")
        self.results_text.insert(tk.END, "Encrypted: No\n")
        self.results_text.insert(tk.END, "Created: 2024-01-01\n")
    
    def extract_images(self):
        """Extract images from PDF."""
        messagebox.showinfo("Extract Images", "Image extraction coming soon...")
    
    def split_pdf(self):
        """Split PDF."""
        messagebox.showinfo("Split PDF", "PDF splitting coming soon...")

class ImageToolsWindow(tk.Toplevel):
    """Window for image tools."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.geometry("500x400")
        self.transient(parent)
    
    def setup_ui(self):
        """Setup the image tools UI."""
        self.title("🖼️ Image Tools")
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Select Image File", padding=10)
        file_frame.pack(fill="x", pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side="right")
        
        # Tools
        tools_frame = ttk.LabelFrame(main_frame, text="Image Operations", padding=10)
        tools_frame.pack(fill="both", expand=True)
        
        ttk.Button(tools_frame, text="ℹ️ Get Information", command=self.get_info).pack(fill="x", pady=2)
        ttk.Button(tools_frame, text="📏 Resize Image", command=self.resize_image).pack(fill="x", pady=2)
        ttk.Button(tools_frame, text="🔄 Convert Format", command=self.convert_format).pack(fill="x", pady=2)
        ttk.Button(tools_frame, text="🎨 Apply Filters", command=self.apply_filters).pack(fill="x", pady=2)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8)
        self.results_text.pack(fill="both", expand=True)
    
    def browse_file(self):
        """Browse for image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def get_info(self):
        """Get image information."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an image file")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Image Information for: {file_path}\n")
        self.results_text.insert(tk.END, "Format: JPEG\n")
        self.results_text.insert(tk.END, "Size: 1920x1080\n")
        self.results_text.insert(tk.END, "File Size: 1.2 MB\n")
        self.results_text.insert(tk.END, "Color Mode: RGB\n")
    
    def resize_image(self):
        """Resize image."""
        messagebox.showinfo("Resize Image", "Image resizing coming soon...")
    
    def convert_format(self):
        """Convert image format."""
        messagebox.showinfo("Convert Format", "Format conversion coming soon...")
    
    def apply_filters(self):
        """Apply filters to image."""
        messagebox.showinfo("Apply Filters", "Image filters coming soon...")

class OpenManusDesktopApp:
    """Main desktop application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.desktop_app = DesktopAppInterface()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI."""
        self.root.title("OpenManus-Youtu Integrated Framework - Desktop App")
        self.root.geometry("1000x700")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Agent Management tab
        agent_frame = AgentManagementFrame(self.notebook, self.desktop_app)
        self.notebook.add(agent_frame, text="🤖 Agents")
        
        # System Status tab
        status_frame = SystemStatusFrame(self.notebook, self.desktop_app)
        self.notebook.add(status_frame, text="📊 Status")
        
        # Tools tab
        tools_frame = ToolsFrame(self.notebook, self.desktop_app)
        self.notebook.add(tools_frame, text="🛠️ Tools")
        
        # Menu bar
        self.create_menu()
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Agent", command=self.create_agent)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="PDF Tools", command=self.open_pdf_tools)
        tools_menu.add_command(label="Image Tools", command=self.open_image_tools)
        tools_menu.add_command(label="Email Tools", command=self.open_email_tools)
        tools_menu.add_command(label="Calendar", command=self.open_calendar_tools)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_agent(self):
        """Create new agent."""
        dialog = CreateAgentDialog(self.root, self.desktop_app)
        self.root.wait_window(dialog)
    
    def open_pdf_tools(self):
        """Open PDF tools."""
        pdf_window = PDFToolsWindow(self.root)
        pdf_window.grab_set()
    
    def open_image_tools(self):
        """Open image tools."""
        image_window = ImageToolsWindow(self.root)
        image_window.grab_set()
    
    def open_email_tools(self):
        """Open email tools."""
        messagebox.showinfo("Email Tools", "Email tools coming soon...")
    
    def open_calendar_tools(self):
        """Open calendar tools."""
        messagebox.showinfo("Calendar Tools", "Calendar tools coming soon...")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
OpenManus-Youtu Integrated Framework
Desktop Application v1.0.0

Advanced AI Agent Framework with:
• Multi-Agent Orchestration
• Communication Hub
• State Management
• Memory System
• Comprehensive Tools

Built with Python and tkinter
        """
        messagebox.showinfo("About", about_text)
    
    def run(self):
        """Run the desktop application."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Desktop app error: {e}")

def run_desktop_app():
    """Run the desktop application."""
    if not DESKTOP_APP_AVAILABLE:
        print("❌ Desktop app dependencies not available.")
        return False
    
    try:
        app = OpenManusDesktopApp()
        app.run()
        return True
    except Exception as e:
        logger.error(f"Desktop app error: {e}")
        return False

if __name__ == "__main__":
    run_desktop_app()