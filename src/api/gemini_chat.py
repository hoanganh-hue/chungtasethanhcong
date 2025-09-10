"""
Enhanced Chat API with Gemini Integration
Real-time chat with Google Gemini AI Agent
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import uuid

from src.api.gemini_config import get_gemini_agent
from src.security.authentication import get_current_user

router = APIRouter()

class GeminiConnectionManager:
    """Manage WebSocket connections for Gemini chat."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.user_agents: Dict[str, Any] = {}  # user_id -> GeminiAIAgent
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect user to WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Create or get session ID
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = str(uuid.uuid4())
        
        # Initialize Gemini agent for user
        agent = await get_gemini_agent(user_id)
        if agent:
            self.user_agents[user_id] = agent
    
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
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected users."""
        for connection in self.active_connections:
            await self.send_personal_message(message, connection)
    
    def get_user_agent(self, user_id: str):
        """Get user's Gemini agent."""
        return self.user_agents.get(user_id)

# Global connection manager
gemini_manager = GeminiConnectionManager()

@router.websocket("/gemini/chat/ws")
async def gemini_websocket_chat_endpoint(websocket: WebSocket, user_id: str = "anonymous"):
    """WebSocket endpoint for real-time Gemini chat."""
    await gemini_manager.connect(websocket, user_id)
    session_id = gemini_manager.user_sessions[user_id]
    
    try:
        # Send welcome message
        await gemini_manager.send_personal_message(
            json.dumps({
                "type": "system",
                "content": "🤖 **Chào mừng đến với OpenManus-Youtu AI Agent!**\n\nTôi được tích hợp với Google Gemini và có thể giúp bạn:\n\n🔧 **Các tính năng chính:**\n• Tạo và kiểm tra CCCD\n• Tra cứu mã số thuế\n• Phân tích dữ liệu\n• Thu thập dữ liệu web\n• Tự động hóa form\n• Tạo báo cáo\n• Xuất Excel\n\n💬 **Hãy thử:** \"Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975\"",
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
            
            # Check if user has Gemini agent configured
            agent = gemini_manager.get_user_agent(user_id)
            if not agent:
                await gemini_manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "content": "❌ **Chưa cấu hình Gemini API**\n\nVui lòng cấu hình API key của Gemini trước khi sử dụng.\n\n1. Đi tới Settings\n2. Nhập Gemini API key\n3. Chọn model và cài đặt\n4. Test kết nối\n\nSau đó quay lại để trò chuyện!",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                continue
            
            # Send typing indicator
            await gemini_manager.send_personal_message(
                json.dumps({
                    "type": "typing",
                    "message": "🤖 Gemini đang suy nghĩ..."
                }),
                websocket
            )
            
            # Process message with Gemini AI Agent
            response_chunks = []
            
            try:
                async for chunk in agent.process_message(
                    user_input, user_id, session_id, stream=stream
                ):
                    if stream:
                        # Send chunk immediately
                        await gemini_manager.send_personal_message(
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
                    await gemini_manager.send_personal_message(
                        json.dumps({
                            "type": "complete",
                            "content": complete_response,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                
                # Send completion signal
                await gemini_manager.send_personal_message(
                    json.dumps({
                        "type": "complete",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                
            except Exception as e:
                await gemini_manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "content": f"❌ **Lỗi xử lý tin nhắn:**\n\n{str(e)}\n\nVui lòng thử lại hoặc kiểm tra cấu hình Gemini API."
                    }),
                    websocket
                )
            
    except WebSocketDisconnect:
        gemini_manager.disconnect(websocket)
    except Exception as e:
        await gemini_manager.send_personal_message(
            json.dumps({
                "type": "error",
                "content": f"❌ **Lỗi kết nối:** {str(e)}"
            }),
            websocket
        )

@router.post("/gemini/chat/message")
async def send_gemini_message(
    message_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Send message via HTTP API to Gemini."""
    try:
        user_id = str(current_user.id)
        user_input = message_data.get("message", "")
        session_id = message_data.get("session_id", str(uuid.uuid4()))
        stream = message_data.get("stream", False)
        
        if not user_input.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get user's Gemini agent
        agent = await get_gemini_agent(user_id)
        if not agent:
            raise HTTPException(
                status_code=400, 
                detail="Gemini API not configured. Please configure your Gemini API key first."
            )
        
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
                    "session_id": session_id,
                    "ai_provider": "gemini",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/chat/sessions")
async def get_gemini_sessions(current_user = Depends(get_current_user)):
    """Get user's Gemini chat sessions."""
    try:
        user_id = str(current_user.id)
        agent = await get_gemini_agent(user_id)
        
        if agent:
            # Get context summary
            context_summary = await agent.context_manager.get_context_summary(
                user_id, "default"
            )
            
            return {
                "success": True,
                "sessions": [context_summary],
                "ai_provider": "gemini",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Gemini AI Agent not configured",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/gemini/chat/sessions/{session_id}")
async def clear_gemini_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Clear Gemini chat session."""
    try:
        user_id = str(current_user.id)
        agent = await get_gemini_agent(user_id)
        
        if agent:
            await agent.context_manager.clear_context(user_id, session_id)
            
            return {
                "success": True,
                "message": "Gemini session cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Gemini AI Agent not configured"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/chat/capabilities")
async def get_gemini_capabilities():
    """Get Gemini AI Agent capabilities."""
    return {
        "success": True,
        "ai_provider": "gemini",
        "capabilities": {
            "cccd_generation": {
                "name": "Tạo CCCD",
                "description": "Tạo CCCD theo tỉnh, giới tính, năm sinh",
                "parameters": ["province", "gender", "quantity", "birth_year_range"],
                "example": "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975"
            },
            "cccd_check": {
                "name": "Kiểm tra CCCD",
                "description": "Kiểm tra thông tin CCCD",
                "parameters": ["cccd_number"],
                "example": "Kiểm tra CCCD 031089011929"
            },
            "tax_lookup": {
                "name": "Tra cứu mã số thuế",
                "description": "Tra cứu thông tin mã số thuế",
                "parameters": ["tax_code"],
                "example": "Tra cứu mã số thuế 037178000015"
            },
            "data_analysis": {
                "name": "Phân tích dữ liệu",
                "description": "Phân tích và xử lý dữ liệu",
                "parameters": ["analysis_type", "input_data"],
                "example": "Phân tích dữ liệu thống kê từ file CSV"
            },
            "web_scraping": {
                "name": "Thu thập dữ liệu web",
                "description": "Scraping dữ liệu từ website",
                "parameters": ["target_url", "scraping_config"],
                "example": "Thu thập dữ liệu từ website abc.com"
            },
            "form_automation": {
                "name": "Tự động hóa form",
                "description": "Tự động điền và submit form",
                "parameters": ["form_url", "form_data"],
                "example": "Tự động điền form đăng ký"
            },
            "report_generation": {
                "name": "Tạo báo cáo",
                "description": "Tạo báo cáo từ dữ liệu",
                "parameters": ["report_type", "report_data"],
                "example": "Tạo báo cáo tổng hợp dữ liệu"
            },
            "excel_export": {
                "name": "Xuất Excel",
                "description": "Xuất dữ liệu ra file Excel",
                "parameters": ["export_data"],
                "example": "Xuất dữ liệu ra file Excel"
            },
            "general_chat": {
                "name": "Trò chuyện chung",
                "description": "Trò chuyện và hỗ trợ thông tin",
                "parameters": [],
                "example": "Hỏi về cách sử dụng các tính năng"
            }
        },
        "features": [
            "Natural language processing",
            "Function calling",
            "Streaming responses",
            "Context management",
            "Multi-turn conversations",
            "Vietnamese language support"
        ],
        "timestamp": datetime.now().isoformat()
    }