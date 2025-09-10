"""
Voice Interface for OpenManus-Youtu Integrated Framework
Advanced voice recognition and text-to-speech capabilities
"""

import asyncio
import logging
import json
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import queue
import time

logger = logging.getLogger(__name__)

try:
    import speech_recognition as sr
    import pyttsx3
    import pyaudio
    VOICE_INTERFACE_AVAILABLE = True
except ImportError:
    VOICE_INTERFACE_AVAILABLE = False
    logger.warning("Voice interface libraries not available. Install speech_recognition, pyttsx3, and pyaudio.")

# Add src to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

if VOICE_INTERFACE_AVAILABLE:
    from core.orchestration import orchestrator
    from agents.dynamic_agent import dynamic_agent_factory
    from core.communication import communication_hub

class VoiceInterface:
    """Advanced voice interface for the framework."""
    
    def __init__(self):
        self.recognizer = None
        self.tts_engine = None
        self.microphone = None
        self.is_listening = False
        self.is_speaking = False
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.voice_commands = {}
        self.agents = {}
        self.current_agent = None
        
        if VOICE_INTERFACE_AVAILABLE:
            self.initialize_voice_components()
            self.setup_voice_commands()
    
    def initialize_voice_components(self):
        """Initialize voice recognition and TTS components."""
        try:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Initialize text-to-speech
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            
            logger.info("Voice components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice components: {e}")
    
    def setup_voice_commands(self):
        """Setup voice command handlers."""
        self.voice_commands = {
            "hello": self.handle_greeting,
            "hi": self.handle_greeting,
            "good morning": self.handle_greeting,
            "good afternoon": self.handle_greeting,
            "good evening": self.handle_greeting,
            "create agent": self.handle_create_agent,
            "list agents": self.handle_list_agents,
            "switch to": self.handle_switch_agent,
            "send message": self.handle_send_message,
            "system status": self.handle_system_status,
            "help": self.handle_help,
            "stop": self.handle_stop,
            "exit": self.handle_exit,
            "quit": self.handle_exit,
            "thank you": self.handle_thanks,
            "thanks": self.handle_thanks
        }
    
    async def start_listening(self):
        """Start continuous voice listening."""
        if not VOICE_INTERFACE_AVAILABLE:
            logger.error("Voice interface not available")
            return
        
        self.is_listening = True
        logger.info("Voice interface started listening")
        
        # Speak welcome message
        await self.speak("Voice interface activated. How can I help you?")
        
        while self.is_listening:
            try:
                # Listen for voice input
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"Recognized: {text}")
                    
                    # Process command
                    await self.process_voice_command(text)
                    
                except sr.UnknownValueError:
                    # Could not understand audio
                    pass
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    await self.speak("Sorry, I couldn't process your request. Please try again.")
                
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                pass
            except Exception as e:
                logger.error(f"Voice listening error: {e}")
                await asyncio.sleep(1)
    
    async def process_voice_command(self, text: str):
        """Process recognized voice command."""
        # Find matching command
        matched_command = None
        for command, handler in self.voice_commands.items():
            if command in text:
                matched_command = (command, handler)
                break
        
        if matched_command:
            command, handler = matched_command
            try:
                await handler(text)
            except Exception as e:
                logger.error(f"Error executing voice command '{command}': {e}")
                await self.speak("Sorry, I encountered an error processing your request.")
        else:
            # No specific command matched, try to handle as general message
            await self.handle_general_message(text)
    
    async def speak(self, text: str):
        """Convert text to speech."""
        if not VOICE_INTERFACE_AVAILABLE or not self.tts_engine:
            print(f"TTS: {text}")
            return
        
        try:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
            logger.info(f"Spoke: {text}")
        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.is_speaking = False
    
    async def handle_greeting(self, text: str):
        """Handle greeting commands."""
        greetings = [
            "Hello! How can I assist you today?",
            "Hi there! What would you like me to help you with?",
            "Good to see you! How can I be of service?",
            "Hello! I'm ready to help with your AI agent tasks."
        ]
        
        import random
        response = random.choice(greetings)
        await self.speak(response)
    
    async def handle_create_agent(self, text: str):
        """Handle agent creation commands."""
        # Extract agent type from text
        agent_types = ["cccd", "tax", "data", "web", "general"]
        agent_type = "general"
        
        for atype in agent_types:
            if atype in text:
                agent_type = atype
                break
        
        try:
            agent = create_agent_from_template(agent_type, {"name": f"{agent_type.title()} Agent"})
            if agent:
                await self.speak(f"Successfully created {agent_type} agent. Agent ID is {agent.config.agent_id[:8]}")
            else:
                await self.speak("Sorry, I couldn't create the agent. Please try again.")
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            await self.speak("Sorry, there was an error creating the agent.")
    
    async def handle_list_agents(self, text: str):
        """Handle list agents command."""
        try:
            agents = dynamic_agent_factory.list_active_agents()
            if agents:
                agent_list = ", ".join([agent['name'] for agent in agents])
                await self.speak(f"I found {len(agents)} active agents: {agent_list}")
            else:
                await self.speak("No active agents found. Would you like me to create one?")
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            await self.speak("Sorry, I couldn't retrieve the agent list.")
    
    async def handle_switch_agent(self, text: str):
        """Handle switch agent command."""
        # Extract agent name from text
        agent_name = None
        try:
            agents = dynamic_agent_factory.list_active_agents()
            for agent in agents:
                if agent['name'].lower() in text:
                    agent_name = agent['name']
                    break
            
            if agent_name:
                self.current_agent = agent_name
                await self.speak(f"Switched to {agent_name}. How can I help you?")
            else:
                await self.speak("I couldn't find that agent. Please try again.")
        except Exception as e:
            logger.error(f"Error switching agent: {e}")
            await self.speak("Sorry, I couldn't switch to that agent.")
    
    async def handle_send_message(self, text: str):
        """Handle send message command."""
        if not self.current_agent:
            await self.speak("Please select an agent first by saying 'switch to' followed by the agent name.")
            return
        
        # Extract message from text
        message = text.replace("send message", "").strip()
        if not message:
            await self.speak("What message would you like me to send?")
            return
        
        try:
            # Find agent ID
            agents = dynamic_agent_factory.list_active_agents()
            agent_id = None
            for agent in agents:
                if agent['name'] == self.current_agent:
                    agent_id = agent['agent_id']
                    break
            
            if agent_id:
                response = self.desktop_app.send_message_to_agent(agent_id, message)
                if response.get('success'):
                    await self.speak(f"Message sent to {self.current_agent}. Response: {response.get('response', 'No response')}")
                else:
                    await self.speak("Sorry, I couldn't send the message.")
            else:
                await self.speak("I couldn't find the current agent.")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await self.speak("Sorry, there was an error sending the message.")
    
    async def handle_system_status(self, text: str):
        """Handle system status command."""
        try:
            agents = dynamic_agent_factory.list_active_agents()
            status_text = f"System status: {len(agents)} active agents"
            
            if self.current_agent:
                status_text += f". Currently connected to {self.current_agent}"
            
            await self.speak(status_text)
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            await self.speak("Sorry, I couldn't retrieve the system status.")
    
    async def handle_help(self, text: str):
        """Handle help command."""
        help_text = """
        Available voice commands:
        - Say 'create agent' to create a new agent
        - Say 'list agents' to see all active agents
        - Say 'switch to' followed by agent name to connect to an agent
        - Say 'send message' followed by your message to send it to the current agent
        - Say 'system status' to check the system status
        - Say 'help' to hear this help message
        - Say 'stop' or 'exit' to stop the voice interface
        """
        await self.speak(help_text)
    
    async def handle_stop(self, text: str):
        """Handle stop command."""
        await self.speak("Stopping voice interface. Goodbye!")
        self.is_listening = False
    
    async def handle_exit(self, text: str):
        """Handle exit command."""
        await self.speak("Exiting voice interface. Goodbye!")
        self.is_listening = False
    
    async def handle_thanks(self, text: str):
        """Handle thanks command."""
        responses = [
            "You're welcome!",
            "Happy to help!",
            "My pleasure!",
            "Glad I could assist you!"
        ]
        import random
        response = random.choice(responses)
        await self.speak(response)
    
    async def handle_general_message(self, text: str):
        """Handle general messages not matching specific commands."""
        if self.current_agent:
            # Send to current agent
            await self.handle_send_message(f"send message {text}")
        else:
            # General response
            responses = [
                "I'm not sure what you mean. Try saying 'help' for available commands.",
                "Could you please be more specific? Say 'help' to see what I can do.",
                "I didn't understand that. You can say 'help' to see available commands."
            ]
            import random
            response = random.choice(responses)
            await self.speak(response)
    
    def stop_listening(self):
        """Stop voice listening."""
        self.is_listening = False
        logger.info("Voice interface stopped listening")
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Get voice interface status."""
        return {
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "current_agent": self.current_agent,
            "available_commands": list(self.voice_commands.keys()),
            "voice_interface_available": VOICE_INTERFACE_AVAILABLE
        }

class VoiceInterfaceManager:
    """Manager for voice interface operations."""
    
    def __init__(self):
        self.voice_interface = VoiceInterface()
        self.listening_task = None
    
    async def start_voice_interface(self):
        """Start the voice interface."""
        if not VOICE_INTERFACE_AVAILABLE:
            print("❌ Voice interface not available. Install required libraries.")
            return False
        
        try:
            print("🎤 Starting voice interface...")
            self.listening_task = asyncio.create_task(self.voice_interface.start_listening())
            await self.listening_task
            return True
        except Exception as e:
            logger.error(f"Voice interface error: {e}")
            return False
    
    def stop_voice_interface(self):
        """Stop the voice interface."""
        if self.voice_interface:
            self.voice_interface.stop_listening()
        if self.listening_task:
            self.listening_task.cancel()
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice interface status."""
        return self.voice_interface.get_voice_status()

# Global voice interface manager
voice_manager = VoiceInterfaceManager()

# Convenience functions
async def start_voice_interface():
    """Start voice interface."""
    return await voice_manager.start_voice_interface()

def stop_voice_interface():
    """Stop voice interface."""
    voice_manager.stop_voice_interface()

def get_voice_status():
    """Get voice interface status."""
    return voice_manager.get_status()

async def speak_text(text: str):
    """Speak text using TTS."""
    if voice_manager.voice_interface:
        await voice_manager.voice_interface.speak(text)

def main():
    """Main function for voice interface."""
    if not VOICE_INTERFACE_AVAILABLE:
        print("❌ Voice interface libraries not available.")
        print("Please install: pip install speech_recognition pyttsx3 pyaudio")
        return
    
    print("🎤 OpenManus-Youtu Voice Interface")
    print("=" * 50)
    print("Voice commands available:")
    print("- 'Hello' or 'Hi' - Greeting")
    print("- 'Create agent' - Create new agent")
    print("- 'List agents' - List active agents")
    print("- 'Switch to [agent name]' - Connect to agent")
    print("- 'Send message [text]' - Send message to current agent")
    print("- 'System status' - Check system status")
    print("- 'Help' - Show help")
    print("- 'Stop' or 'Exit' - Stop voice interface")
    print("=" * 50)
    
    try:
        asyncio.run(start_voice_interface())
    except KeyboardInterrupt:
        print("\n👋 Voice interface stopped by user")
    except Exception as e:
        print(f"❌ Voice interface error: {e}")

if __name__ == "__main__":
    main()