"""
Agent Communication System for OpenManus-Youtu Integrated Framework
Advanced inter-agent communication and message passing
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    DATA = "data"
    COMMAND = "command"

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class AgentMessage:
    """Agent communication message."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: MessageType = MessageType.REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: int = 3600  # Time to live in seconds
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

@dataclass
class CommunicationChannel:
    """Communication channel between agents."""
    channel_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    participants: List[str] = field(default_factory=list)
    message_history: List[AgentMessage] = field(default_factory=list)
    max_history: int = 1000
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

class MessageHandler(ABC):
    """Abstract base class for message handlers."""
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming message."""
        pass

class AgentCommunicationHub:
    """Central hub for agent communication."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.channels: Dict[str, CommunicationChannel] = {}
        self.message_handlers: Dict[str, List[MessageHandler]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.message_history: List[AgentMessage] = []
        self.max_history = 10000
        
    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """Register an agent for communication."""
        self.agents[agent_id] = agent_instance
        self.message_handlers[agent_id] = []
        logger.info(f"Registered agent for communication: {agent_id}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            if agent_id in self.message_handlers:
                del self.message_handlers[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def add_message_handler(self, agent_id: str, handler: MessageHandler) -> None:
        """Add message handler for an agent."""
        if agent_id not in self.message_handlers:
            self.message_handlers[agent_id] = []
        self.message_handlers[agent_id].append(handler)
    
    def create_channel(self, name: str, participants: List[str]) -> str:
        """Create a communication channel."""
        channel = CommunicationChannel(
            name=name,
            participants=participants
        )
        self.channels[channel.channel_id] = channel
        logger.info(f"Created communication channel: {name}")
        return channel.channel_id
    
    def join_channel(self, channel_id: str, agent_id: str) -> bool:
        """Join an agent to a communication channel."""
        if channel_id in self.channels:
            if agent_id not in self.channels[channel_id].participants:
                self.channels[channel_id].participants.append(agent_id)
                logger.info(f"Agent {agent_id} joined channel {channel_id}")
                return True
        return False
    
    def leave_channel(self, channel_id: str, agent_id: str) -> bool:
        """Remove an agent from a communication channel."""
        if channel_id in self.channels:
            if agent_id in self.channels[channel_id].participants:
                self.channels[channel_id].participants.remove(agent_id)
                logger.info(f"Agent {agent_id} left channel {channel_id}")
                return True
        return False
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message between agents."""
        try:
            # Validate message
            if not self._validate_message(message):
                return False
            
            # Add to message history
            self.message_history.append(message)
            if len(self.message_history) > self.max_history:
                self.message_history = self.message_history[-self.max_history:]
            
            # Route message
            if message.message_type == MessageType.BROADCAST:
                await self._broadcast_message(message)
            elif message.receiver_id in self.agents:
                await self._deliver_message(message)
            else:
                logger.warning(f"Message receiver not found: {message.receiver_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def send_request(self, sender_id: str, receiver_id: str, content: Dict[str, Any], 
                          priority: MessagePriority = MessagePriority.NORMAL) -> Optional[AgentMessage]:
        """Send a request message and wait for response."""
        request = AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            priority=priority,
            content=content
        )
        
        if await self.send_message(request):
            # Wait for response
            response = await self._wait_for_response(request.message_id, timeout=30)
            return response
        
        return None
    
    async def send_notification(self, sender_id: str, receiver_id: str, content: Dict[str, Any]) -> bool:
        """Send a notification message."""
        notification = AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.NOTIFICATION,
            content=content
        )
        return await self.send_message(notification)
    
    async def broadcast_message(self, sender_id: str, content: Dict[str, Any], 
                               channel_id: Optional[str] = None) -> int:
        """Broadcast a message to multiple agents."""
        broadcast = AgentMessage(
            sender_id=sender_id,
            message_type=MessageType.BROADCAST,
            content=content
        )
        
        if channel_id and channel_id in self.channels:
            broadcast.metadata["channel_id"] = channel_id
            recipients = self.channels[channel_id].participants
        else:
            recipients = list(self.agents.keys())
        
        broadcast.metadata["recipients"] = recipients
        await self.send_message(broadcast)
        
        return len(recipients)
    
    def _validate_message(self, message: AgentMessage) -> bool:
        """Validate message before sending."""
        if not message.sender_id or not message.receiver_id:
            return False
        
        if message.sender_id not in self.agents:
            logger.warning(f"Message sender not registered: {message.sender_id}")
            return False
        
        # Check TTL
        if (datetime.now() - message.timestamp).total_seconds() > message.ttl:
            logger.warning(f"Message expired: {message.message_id}")
            return False
        
        return True
    
    async def _deliver_message(self, message: AgentMessage) -> None:
        """Deliver message to specific agent."""
        receiver_id = message.receiver_id
        
        if receiver_id in self.message_handlers:
            for handler in self.message_handlers[receiver_id]:
                try:
                    response = await handler.handle_message(message)
                    if response:
                        await self.send_message(response)
                except Exception as e:
                    logger.error(f"Message handler error: {e}")
    
    async def _broadcast_message(self, message: AgentMessage) -> None:
        """Broadcast message to multiple agents."""
        recipients = message.metadata.get("recipients", list(self.agents.keys()))
        
        for recipient_id in recipients:
            if recipient_id != message.sender_id:  # Don't send to sender
                broadcast_message = AgentMessage(
                    sender_id=message.sender_id,
                    receiver_id=recipient_id,
                    message_type=message.message_type,
                    priority=message.priority,
                    content=message.content,
                    metadata=message.metadata,
                    correlation_id=message.correlation_id
                )
                await self._deliver_message(broadcast_message)
    
    async def _wait_for_response(self, request_id: str, timeout: int = 30) -> Optional[AgentMessage]:
        """Wait for response to a request."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            # Check recent messages for response
            for message in reversed(self.message_history[-100:]):  # Check last 100 messages
                if (message.correlation_id == request_id and 
                    message.message_type == MessageType.RESPONSE):
                    return message
            
            await asyncio.sleep(0.1)  # Small delay
        
        return None
    
    def get_agent_messages(self, agent_id: str, limit: int = 100) -> List[AgentMessage]:
        """Get recent messages for an agent."""
        messages = []
        for message in reversed(self.message_history):
            if message.sender_id == agent_id or message.receiver_id == agent_id:
                messages.append(message)
                if len(messages) >= limit:
                    break
        
        return messages
    
    def get_channel_messages(self, channel_id: str, limit: int = 100) -> List[AgentMessage]:
        """Get recent messages from a channel."""
        if channel_id not in self.channels:
            return []
        
        messages = []
        for message in reversed(self.message_history):
            if (message.metadata.get("channel_id") == channel_id or
                message.message_type == MessageType.BROADCAST):
                messages.append(message)
                if len(messages) >= limit:
                    break
        
        return messages
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication system statistics."""
        return {
            "total_agents": len(self.agents),
            "total_channels": len(self.channels),
            "total_messages": len(self.message_history),
            "active_channels": len([c for c in self.channels.values() if c.is_active]),
            "message_types": {
                msg_type.value: len([m for m in self.message_history if m.message_type == msg_type])
                for msg_type in MessageType
            }
        }

# Global communication hub
communication_hub = AgentCommunicationHub()

# Convenience functions
async def send_agent_request(sender_id: str, receiver_id: str, content: Dict[str, Any]) -> Optional[AgentMessage]:
    """Send a request to another agent."""
    return await communication_hub.send_request(sender_id, receiver_id, content)

async def send_agent_notification(sender_id: str, receiver_id: str, content: Dict[str, Any]) -> bool:
    """Send a notification to another agent."""
    return await communication_hub.send_notification(sender_id, receiver_id, content)

async def broadcast_to_agents(sender_id: str, content: Dict[str, Any], channel_id: Optional[str] = None) -> int:
    """Broadcast message to multiple agents."""
    return await communication_hub.broadcast_message(sender_id, content, channel_id)

def register_agent_for_communication(agent_id: str, agent_instance: Any) -> None:
    """Register an agent for communication."""
    communication_hub.register_agent(agent_id, agent_instance)

def create_agent_channel(name: str, participants: List[str]) -> str:
    """Create a communication channel for agents."""
    return communication_hub.create_channel(name, participants)