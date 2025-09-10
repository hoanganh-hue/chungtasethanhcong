"""
Unified Gemini API endpoints
API endpoints for managing and interacting with Gemini-powered agents
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import uuid

from ..agents.gemini_agent_factory import gemini_agent_manager, GeminiAgentFactory
from ..core.config import UnifiedConfig
from ..security.authentication import get_current_user

router = APIRouter()

class UnifiedGeminiConnectionManager:
    """Manage WebSocket connections for unified Gemini agents."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_agents: Dict[str, str] = {}  # user_id -> agent_name
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    async def connect(self, websocket: WebSocket, user_id: str, agent_name: str):
        """Connect user to WebSocket with specific agent."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Create or get session ID
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = str(uuid.uuid4())
        
        # Set user's agent
        self.user_agents[user_id] = agent_name
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect user from WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific user."""
        try:
            await websocket.send_text(message)
        except:
            await self.disconnect(websocket)
    
    def get_user_agent(self, user_id: str) -> Optional[str]:
        """Get user's assigned agent."""
        return self.user_agents.get(user_id)

# Global connection manager
unified_gemini_manager = UnifiedGeminiConnectionManager()

@router.post("/agents/create")
async def create_gemini_agent(
    agent_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Create a new Gemini agent."""
    try:
        user_id = str(current_user.id)
        agent_type = agent_data.get("agent_type", "general")
        api_key = agent_data.get("api_key", "")
        agent_name = agent_data.get("name", f"{agent_type}_agent_{user_id}")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Create agent
        agent = await gemini_agent_manager.create_agent(
            agent_type=agent_type,
            api_key=api_key,
            name=agent_name,
            **agent_data.get("config", {})
        )
        
        return {
            "success": True,
            "agent_name": agent.name,
            "agent_type": agent_type,
            "capabilities": await agent.get_capabilities(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def list_gemini_agents(current_user = Depends(get_current_user)):
    """List all available Gemini agents."""
    try:
        agents = await gemini_agent_manager.list_agents()
        
        return {
            "success": True,
            "agents": agents,
            "total": len(agents),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_name}")
async def get_agent_info(
    agent_name: str,
    current_user = Depends(get_current_user)
):
    """Get information about a specific agent."""
    try:
        agent = await gemini_agent_manager.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        capabilities = await agent.get_capabilities()
        
        return {
            "success": True,
            "agent": capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agents/{agent_name}")
async def delete_agent(
    agent_name: str,
    current_user = Depends(get_current_user)
):
    """Delete a Gemini agent."""
    try:
        agent = await gemini_agent_manager.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        await agent.close()
        del gemini_agent_manager.agents[agent_name]
        
        return {
            "success": True,
            "message": f"Agent '{agent_name}' deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/agents/{agent_name}/chat/ws")
async def unified_gemini_websocket_chat(
    websocket: WebSocket,
    agent_name: str,
    user_id: str = "anonymous"
):
    """WebSocket endpoint for real-time chat with unified Gemini agent."""
    await unified_gemini_manager.connect(websocket, user_id, agent_name)
    session_id = unified_gemini_manager.user_sessions[user_id]
    
    try:
        # Get agent
        agent = await gemini_agent_manager.get_agent(agent_name)
        if not agent:
            await unified_gemini_manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "content": f"❌ Agent '{agent_name}' not found"
                }),
                websocket
            )
            return
        
        # Send welcome message
        capabilities = await agent.get_capabilities()
        welcome_message = f"""
🤖 **Chào mừng đến với {agent.name}!**

{capabilities.get('description', '')}

🔧 **Khả năng:**
{', '.join(capabilities.get('capabilities', {}).keys())}

🛠️ **Tools có sẵn:**
{', '.join(capabilities.get('available_tools', []))}

💬 **Hãy thử:** "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975"
        """
        
        await unified_gemini_manager.send_personal_message(
            json.dumps({
                "type": "system",
                "content": welcome_message,
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_input = message_data.get("message", "")
            stream = message_data.get("stream", True)
            
            if not user_input.strip():
                continue
            
            # Send typing indicator
            await unified_gemini_manager.send_personal_message(
                json.dumps({
                    "type": "typing",
                    "message": f"🤖 {agent.name} đang suy nghĩ..."
                }),
                websocket
            )
            
            # Process message with agent
            response_chunks = []
            
            try:
                async for chunk in agent.process_message(
                    user_input, user_id, session_id, stream=stream
                ):
                    if stream:
                        # Send chunk immediately
                        await unified_gemini_manager.send_personal_message(
                            json.dumps({
                                "type": "chunk",
                                "content": chunk,
                                "timestamp": datetime.now().isoformat()
                            }),
                            websocket
                        )
                    else:
                        response_chunks.append(chunk)
                
                if not stream:
                    # Send complete response
                    complete_response = "".join(response_chunks)
                    await unified_gemini_manager.send_personal_message(
                        json.dumps({
                            "type": "complete",
                            "content": complete_response,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                
                # Send completion signal
                await unified_gemini_manager.send_personal_message(
                    json.dumps({
                        "type": "complete",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                
            except Exception as e:
                await unified_gemini_manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "content": f"❌ **Lỗi xử lý tin nhắn:**\n\n{str(e)}"
                    }),
                    websocket
                )
            
    except WebSocketDisconnect:
        unified_gemini_manager.disconnect(websocket)
    except Exception as e:
        await unified_gemini_manager.send_personal_message(
            json.dumps({
                "type": "error",
                "content": f"❌ **Lỗi kết nối:** {str(e)}"
            }),
            websocket
        )

@router.post("/agents/{agent_name}/chat/message")
async def send_agent_message(
    agent_name: str,
    message_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Send message via HTTP API to specific agent."""
    try:
        user_id = str(current_user.id)
        user_input = message_data.get("message", "")
        session_id = message_data.get("session_id", str(uuid.uuid4()))
        stream = message_data.get("stream", False)
        
        if not user_input.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get agent
        agent = await gemini_agent_manager.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if stream:
            # Return streaming response
            async def generate_response():
                try:
                    async for chunk in agent.process_message(
                        user_input, user_id, session_id, stream=True
                    ):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_response(),
                media_type="text/plain"
            )
        else:
            # Return complete response
            response_chunks = []
            try:
                async for chunk in agent.process_message(
                    user_input, user_id, session_id, stream=False
                ):
                    response_chunks.append(chunk)
                
                complete_response = "".join(response_chunks)
                
                return {
                    "success": True,
                    "response": complete_response,
                    "agent_name": agent_name,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_name}/capabilities")
async def get_agent_capabilities(
    agent_name: str,
    current_user = Depends(get_current_user)
):
    """Get agent capabilities."""
    try:
        agent = await gemini_agent_manager.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        capabilities = await agent.get_capabilities()
        
        return {
            "success": True,
            "agent_name": agent_name,
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/types")
async def get_available_agent_types():
    """Get available agent types."""
    return {
        "success": True,
        "agent_types": {
            "cccd": {
                "name": "CCCD Agent",
                "description": "AI Agent chuyên xử lý các tác vụ liên quan đến CCCD",
                "capabilities": ["cccd_generation", "cccd_check", "cccd_analysis"]
            },
            "tax": {
                "name": "Tax Agent", 
                "description": "AI Agent chuyên xử lý các tác vụ liên quan đến thuế",
                "capabilities": ["tax_lookup", "tax_analysis", "tax_reporting"]
            },
            "data_analysis": {
                "name": "Data Analysis Agent",
                "description": "AI Agent chuyên phân tích dữ liệu và tạo báo cáo",
                "capabilities": ["data_analysis", "statistical_analysis", "report_generation"]
            },
            "web_automation": {
                "name": "Web Automation Agent",
                "description": "AI Agent chuyên tự động hóa web và scraping dữ liệu",
                "capabilities": ["web_scraping", "form_automation", "web_interaction"]
            },
            "general": {
                "name": "General Purpose Agent",
                "description": "AI Agent đa năng có thể xử lý nhiều loại tác vụ",
                "capabilities": ["natural_language_processing", "function_calling", "tool_integration"]
            }
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/agents/{agent_name}/tools/execute")
async def execute_agent_tool(
    agent_name: str,
    tool_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Execute a tool through the agent."""
    try:
        agent = await gemini_agent_manager.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        tool_name = tool_data.get("tool_name", "")
        tool_input = tool_data.get("input", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        # Execute tool through agent
        if hasattr(agent, 'tool_registry'):
            tool = agent.tool_registry.get_tool(tool_name)
            if tool:
                result = await tool.execute(tool_input)
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        else:
            raise HTTPException(status_code=400, detail="Agent does not support tool execution")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))