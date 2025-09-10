"""
Mobile App Interface for OpenManus-Youtu Integrated Framework
Cross-platform mobile interface using Kivy for Android/iOS compatibility
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.popup import Popup
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.switch import Switch
    from kivy.uix.slider import Slider
    from kivy.uix.spinner import Spinner
    from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
    from kivy.uix.image import Image
    from kivy.uix.filechooser import FileChooserListView
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.utils import platform
    MOBILE_APP_AVAILABLE = True
except ImportError:
    MOBILE_APP_AVAILABLE = False
    logger.warning("Mobile app libraries not available. Install kivy for mobile support.")

# Add src to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

if MOBILE_APP_AVAILABLE:
    from core.orchestration import orchestrator
    from agents.dynamic_agent import dynamic_agent_factory
    from core.communication import communication_hub
    from core.state_manager import state_manager
    from core.memory import memory_manager

class MobileAppInterface:
    """Mobile app interface for the framework."""
    
    def __init__(self):
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

if MOBILE_APP_AVAILABLE:
    class AgentListWidget(BoxLayout):
        """Widget for displaying agent list."""
        
        def __init__(self, mobile_app, **kwargs):
            super().__init__(**kwargs)
            self.mobile_app = mobile_app
            self.orientation = 'vertical'
            self.spacing = 10
            self.padding = 10
            
            # Title
            title = Label(text='🤖 Active Agents', size_hint_y=None, height=40)
            self.add_widget(title)
            
            # Refresh button
            refresh_btn = Button(text='🔄 Refresh', size_hint_y=None, height=40)
            refresh_btn.bind(on_press=self.refresh_agents)
            self.add_widget(refresh_btn)
            
            # Agent list
            self.agent_list = ScrollView()
            self.agent_container = BoxLayout(orientation='vertical', size_hint_y=None)
            self.agent_container.bind(minimum_height=self.agent_container.setter('height'))
            self.agent_list.add_widget(self.agent_container)
            self.add_widget(self.agent_list)
            
            # Load initial agents
            self.refresh_agents()
        
        def refresh_agents(self, instance=None):
            """Refresh agent list."""
            self.agent_container.clear_widgets()
            agents = self.mobile_app.get_agent_list()
            
            if not agents:
                no_agents = Label(text='No agents available', size_hint_y=None, height=40)
                self.agent_container.add_widget(no_agents)
            else:
                for agent in agents:
                    agent_widget = self.create_agent_widget(agent)
                    self.agent_container.add_widget(agent_widget)
        
        def create_agent_widget(self, agent: Dict[str, Any]) -> BoxLayout:
            """Create widget for individual agent."""
            widget = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
            
            # Agent info
            info_layout = BoxLayout(orientation='vertical')
            name_label = Label(text=agent['name'], size_hint_y=None, height=30)
            type_label = Label(text=f"Type: {agent['type']}", size_hint_y=None, height=20)
            status_label = Label(text=f"Status: {agent['status']}", size_hint_y=None, height=20)
            
            info_layout.add_widget(name_label)
            info_layout.add_widget(type_label)
            info_layout.add_widget(status_label)
            
            # Action button
            action_btn = Button(text='💬 Chat', size_hint_x=None, width=100)
            action_btn.bind(on_press=lambda x: self.open_agent_chat(agent))
            
            widget.add_widget(info_layout)
            widget.add_widget(action_btn)
            
            return widget
        
        def open_agent_chat(self, agent: Dict[str, Any]):
            """Open chat with agent."""
            chat_popup = AgentChatPopup(agent, self.mobile_app)
            chat_popup.open()

    class AgentChatPopup(Popup):
        """Popup for agent chat."""
        
        def __init__(self, agent: Dict[str, Any], mobile_app, **kwargs):
            super().__init__(**kwargs)
            self.agent = agent
            self.mobile_app = mobile_app
            self.title = f"💬 Chat with {agent['name']}"
            self.size_hint = (0.9, 0.8)
            
            # Main layout
            main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
            
            # Messages area
            self.messages_scroll = ScrollView()
            self.messages_container = BoxLayout(orientation='vertical', size_hint_y=None)
            self.messages_container.bind(minimum_height=self.messages_container.setter('height'))
            self.messages_scroll.add_widget(self.messages_container)
            main_layout.add_widget(self.messages_scroll)
            
            # Input area
            input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
            self.message_input = TextInput(hint_text='Type your message...', multiline=False)
            send_btn = Button(text='Send', size_hint_x=None, width=100)
            send_btn.bind(on_press=self.send_message)
            
            input_layout.add_widget(self.message_input)
            input_layout.add_widget(send_btn)
            main_layout.add_widget(input_layout)
            
            self.add_widget(main_layout)
            
            # Load initial messages
            self.load_messages()
        
        def send_message(self, instance):
            """Send message to agent."""
            message = self.message_input.text.strip()
            if not message:
                return
            
            # Add user message
            self.add_message("You", message, "user")
            self.message_input.text = ""
            
            # Send to agent
            response = self.mobile_app.send_message_to_agent(self.agent['agent_id'], message)
            if response.get('success'):
                self.add_message(self.agent['name'], response.get('response', 'No response'), "agent")
            else:
                self.add_message("System", f"Error: {response.get('error', 'Unknown error')}", "system")
        
        def add_message(self, sender: str, message: str, msg_type: str):
            """Add message to chat."""
            message_widget = BoxLayout(orientation='vertical', size_hint_y=None, height=60)
            
            sender_label = Label(text=sender, size_hint_y=None, height=20, 
                               color=(0.2, 0.6, 1, 1) if msg_type == "agent" else (0.8, 0.8, 0.8, 1))
            message_label = Label(text=message, size_hint_y=None, height=40, 
                                text_size=(None, None), halign='left', valign='middle')
            
            message_widget.add_widget(sender_label)
            message_widget.add_widget(message_label)
            self.messages_container.add_widget(message_widget)
        
        def load_messages(self):
            """Load initial messages."""
            self.add_message("System", f"Connected to {self.agent['name']}", "system")

    class SystemStatusWidget(BoxLayout):
        """Widget for system status."""
        
        def __init__(self, mobile_app, **kwargs):
            super().__init__(**kwargs)
            self.mobile_app = mobile_app
            self.orientation = 'vertical'
            self.spacing = 10
            self.padding = 10
            
            # Title
            title = Label(text='📊 System Status', size_hint_y=None, height=40)
            self.add_widget(title)
            
            # Status info
            self.status_label = Label(text='Loading...', size_hint_y=None, height=40)
            self.add_widget(self.status_label)
            
            # Refresh button
            refresh_btn = Button(text='🔄 Refresh Status', size_hint_y=None, height=40)
            refresh_btn.bind(on_press=self.refresh_status)
            self.add_widget(refresh_btn)
            
            # Load initial status
            self.refresh_status()
        
        def refresh_status(self, instance=None):
            """Refresh system status."""
            status = self.mobile_app.get_system_status()
            
            status_text = f"Status: {status['status']}\n"
            status_text += f"Active Agents: {status['agents']}\n"
            status_text += f"Last Update: {status['timestamp']}"
            
            self.status_label.text = status_text

    class ToolsWidget(BoxLayout):
        """Widget for tools and utilities."""
        
        def __init__(self, mobile_app, **kwargs):
            super().__init__(**kwargs)
            self.mobile_app = mobile_app
            self.orientation = 'vertical'
            self.spacing = 10
            self.padding = 10
            
            # Title
            title = Label(text='🛠️ Tools & Utilities', size_hint_y=None, height=40)
            self.add_widget(title)
            
            # Tools grid
            tools_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
            tools_grid.bind(minimum_height=tools_grid.setter('height'))
            
            # Tool buttons
            tools = [
                ("📄 PDF Tools", self.open_pdf_tools),
                ("🖼️ Image Tools", self.open_image_tools),
                ("📧 Email Tools", self.open_email_tools),
                ("📅 Calendar", self.open_calendar_tools),
                ("📊 Analytics", self.open_analytics),
                ("⚙️ Settings", self.open_settings)
            ]
            
            for tool_name, tool_func in tools:
                btn = Button(text=tool_name, size_hint_y=None, height=60)
                btn.bind(on_press=tool_func)
                tools_grid.add_widget(btn)
            
            self.add_widget(tools_grid)
        
        def open_pdf_tools(self, instance):
            """Open PDF tools."""
            popup = Popup(title='📄 PDF Tools', size_hint=(0.8, 0.6))
            content = Label(text='PDF tools coming soon...')
            popup.add_widget(content)
            popup.open()
        
        def open_image_tools(self, instance):
            """Open image tools."""
            popup = Popup(title='🖼️ Image Tools', size_hint=(0.8, 0.6))
            content = Label(text='Image tools coming soon...')
            popup.add_widget(content)
            popup.open()
        
        def open_email_tools(self, instance):
            """Open email tools."""
            popup = Popup(title='📧 Email Tools', size_hint=(0.8, 0.6))
            content = Label(text='Email tools coming soon...')
            popup.add_widget(content)
            popup.open()
        
        def open_calendar_tools(self, instance):
            """Open calendar tools."""
            popup = Popup(title='📅 Calendar Tools', size_hint=(0.8, 0.6))
            content = Label(text='Calendar tools coming soon...')
            popup.add_widget(content)
            popup.open()
        
        def open_analytics(self, instance):
            """Open analytics."""
            popup = Popup(title='📊 Analytics', size_hint=(0.8, 0.6))
            content = Label(text='Analytics coming soon...')
            popup.add_widget(content)
            popup.open()
        
        def open_settings(self, instance):
            """Open settings."""
            popup = Popup(title='⚙️ Settings', size_hint=(0.8, 0.6))
            content = Label(text='Settings coming soon...')
            popup.add_widget(content)
            popup.open()

    class OpenManusMobileApp(App):
        """Main mobile application."""
        
        def build(self):
            """Build the mobile app interface."""
            self.mobile_app = MobileAppInterface()
            
            # Main tabbed panel
            main_panel = TabbedPanel(do_default_tab=False)
            
            # Agents tab
            agents_tab = TabbedPanelItem(text='🤖 Agents')
            agents_tab.add_widget(AgentListWidget(self.mobile_app))
            main_panel.add_widget(agents_tab)
            
            # Status tab
            status_tab = TabbedPanelItem(text='📊 Status')
            status_tab.add_widget(SystemStatusWidget(self.mobile_app))
            main_panel.add_widget(status_tab)
            
            # Tools tab
            tools_tab = TabbedPanelItem(text='🛠️ Tools')
            tools_tab.add_widget(ToolsWidget(self.mobile_app))
            main_panel.add_widget(tools_tab)
            
            return main_panel
        
        def on_start(self):
            """Called when app starts."""
            logger.info("Mobile app started")
        
        def on_stop(self):
            """Called when app stops."""
            logger.info("Mobile app stopped")

def run_mobile_app():
    """Run the mobile application."""
    if not MOBILE_APP_AVAILABLE:
        print("❌ Mobile app libraries not available. Install kivy for mobile support.")
        return False
    
    try:
        app = OpenManusMobileApp()
        app.run()
        return True
    except Exception as e:
        logger.error(f"Mobile app error: {e}")
        return False

if __name__ == "__main__":
    run_mobile_app()