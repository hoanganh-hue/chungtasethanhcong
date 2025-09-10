"""
Enhanced AI Agent with Google Gemini Integration
Natural language processing with function calling capabilities
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import httpx

from .gemini_client import GeminiClient, GeminiConfig, GeminiMessage, GeminiModel, OpenManusFunctions
from .context_manager import ContextManager, InputStandardizer, StandardizedInput, ChatContext
from src.integrations.supabase.client import SupabaseClient

logger = logging.getLogger(__name__)

class GeminiAIAgent:
    """Enhanced AI Agent with Google Gemini integration."""
    
    def __init__(
        self, 
        gemini_config: GeminiConfig,
        supabase_client: SupabaseClient = None
    ):
        self.gemini_client = GeminiClient(gemini_config)
        self.context_manager = ContextManager()
        self.standardizer = InputStandardizer()
        self.supabase = supabase_client
        
        # Function handlers
        self.function_handlers = {
            "generate_cccd": self._handle_cccd_generation,
            "check_cccd": self._handle_cccd_check,
            "lookup_tax": self._handle_tax_lookup,
            "analyze_data": self._handle_data_analysis,
            "scrape_web": self._handle_web_scraping,
            "automate_form": self._handle_form_automation,
            "generate_report": self._handle_report_generation,
            "export_excel": self._handle_excel_export
        }
        
        # Initialize function definitions
        self._register_functions()
    
    async def initialize(self) -> bool:
        """Initialize the AI Agent."""
        try:
            # Initialize Gemini client
            if not await self.gemini_client.initialize():
                return False
            
            self.logger.info("Gemini AI Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI Agent: {e}")
            return False
    
    def _register_functions(self):
        """Register all available functions with Gemini."""
        # Register CCCD generation function
        cccd_gen_func = OpenManusFunctions.get_cccd_generation_function()
        self.gemini_client.register_function(cccd_gen_func, self._handle_cccd_generation)
        
        # Register CCCD check function
        cccd_check_func = OpenManusFunctions.get_cccd_check_function()
        self.gemini_client.register_function(cccd_check_func, self._handle_cccd_check)
        
        # Register tax lookup function
        tax_lookup_func = OpenManusFunctions.get_tax_lookup_function()
        self.gemini_client.register_function(tax_lookup_func, self._handle_tax_lookup)
        
        # Register data analysis function
        data_analysis_func = OpenManusFunctions.get_data_analysis_function()
        self.gemini_client.register_function(data_analysis_func, self._handle_data_analysis)
        
        # Register web scraping function
        web_scraping_func = OpenManusFunctions.get_web_scraping_function()
        self.gemini_client.register_function(web_scraping_func, self._handle_web_scraping)
        
        # Register form automation function
        form_automation_func = OpenManusFunctions.get_form_automation_function()
        self.gemini_client.register_function(form_automation_func, self._handle_form_automation)
        
        # Register report generation function
        report_generation_func = OpenManusFunctions.get_report_generation_function()
        self.gemini_client.register_function(report_generation_func, self._handle_report_generation)
        
        # Register Excel export function
        excel_export_func = OpenManusFunctions.get_excel_export_function()
        self.gemini_client.register_function(excel_export_func, self._handle_excel_export)
    
    async def process_message(
        self, 
        user_input: str, 
        user_id: str, 
        session_id: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Process user message with Gemini AI."""
        try:
            # Standardize input
            standardized_input = self.standardizer.standardize_input(
                user_input, user_id, session_id
            )
            
            # Add user message to context
            await self.context_manager.add_message(
                user_id, session_id, "user", user_input
            )
            
            # Get context
            context = await self.context_manager.get_or_create_context(
                user_id, session_id, self._get_system_prompt()
            )
            
            # Convert context to Gemini messages
            gemini_messages = self._convert_to_gemini_messages(context.messages)
            
            # Generate response using Gemini
            response_chunks = []
            async for chunk in self.gemini_client.generate_content(
                gemini_messages, stream=stream
            ):
                if stream:
                    yield chunk
                else:
                    response_chunks.append(chunk)
            
            # Add assistant response to context
            if not stream:
                complete_response = "".join(response_chunks)
                await self.context_manager.add_message(
                    user_id, session_id, "assistant", complete_response
                )
            
            # Save conversation to database
            if self.supabase:
                await self._save_conversation(user_id, session_id, user_input, "gemini_chat")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            yield f"Lỗi khi xử lý tin nhắn: {str(e)}"
    
    def _convert_to_gemini_messages(self, messages: List) -> List[GeminiMessage]:
        """Convert context messages to Gemini format."""
        gemini_messages = []
        
        for msg in messages:
            if msg.role == "system":
                # Convert system message to user message with instruction
                gemini_msg = GeminiMessage(
                    role="user",
                    parts=[{"text": f"System: {msg.content}"}],
                    timestamp=msg.timestamp
                )
            elif msg.role == "user":
                gemini_msg = GeminiMessage(
                    role="user",
                    parts=[{"text": msg.content}],
                    timestamp=msg.timestamp
                )
            elif msg.role == "assistant":
                gemini_msg = GeminiMessage(
                    role="model",
                    parts=[{"text": msg.content}],
                    timestamp=msg.timestamp
                )
            else:
                continue
            
            gemini_messages.append(gemini_msg)
        
        return gemini_messages
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for Gemini."""
        return """
Bạn là OpenManus-Youtu AI Agent, một trợ lý AI thông minh được tích hợp với Google Gemini.

🔧 **Chức năng chính:**
- Tạo và kiểm tra CCCD
- Tra cứu mã số thuế  
- Phân tích dữ liệu
- Thu thập dữ liệu web
- Tự động hóa form
- Tạo báo cáo
- Xuất Excel

📋 **Hướng dẫn:**
1. Luôn trả lời bằng tiếng Việt
2. Sử dụng function calling khi người dùng yêu cầu thực hiện tác vụ cụ thể
3. Cung cấp thông tin chính xác và hữu ích
4. Hướng dẫn người dùng sử dụng các tính năng
5. Xử lý yêu cầu một cách chuyên nghiệp

🎯 **Mục tiêu:** Hỗ trợ người dùng hoàn thành các tác vụ một cách hiệu quả và chính xác thông qua natural language processing và function calling.

💡 **Ví dụ sử dụng:**
- "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975"
- "Kiểm tra CCCD 031089011929"
- "Tra cứu mã số thuế 037178000015"
        """
    
    # Function handlers
    async def _handle_cccd_generation(self, args: Dict[str, Any]) -> str:
        """Handle CCCD generation function call."""
        try:
            province = args.get("province", "")
            gender = args.get("gender", "")
            birth_year_range = args.get("birth_year_range", "1965-1975")
            quantity = args.get("quantity", 100)
            
            # Call CCCD generation API
            if self.supabase:
                result = await self._call_cccd_generation_api({
                    "province": province,
                    "gender": gender,
                    "birth_year_range": birth_year_range,
                    "quantity": quantity
                })
                
                if result.get("success"):
                    return f"""
✅ **Hoàn thành tạo CCCD!**

📊 **Kết quả:**
• Tỉnh: {province}
• Giới tính: {gender}
• Năm sinh: {birth_year_range}
• Số lượng: {quantity}
• Thành công: {result.get('success_count', 0)} CCCD
• Thời gian: {result.get('processing_time', 0):.2f}s

💾 Dữ liệu đã được lưu vào cơ sở dữ liệu.
                    """
                else:
                    return f"❌ Lỗi: {result.get('error', 'Không thể tạo CCCD')}"
            else:
                return "❌ Lỗi: Không thể kết nối đến cơ sở dữ liệu"
                
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_cccd_check(self, args: Dict[str, Any]) -> str:
        """Handle CCCD check function call."""
        try:
            cccd_number = args.get("cccd_number", "")
            
            if not cccd_number:
                return "❌ Vui lòng cung cấp số CCCD để kiểm tra"
            
            # Call CCCD check API
            if self.supabase:
                result = await self._call_cccd_check_api(cccd_number)
                
                if result.get("success"):
                    check_result = result.get("check_result", {})
                    
                    if check_result.get("status") == "found":
                        return f"""
✅ **Kết quả kiểm tra CCCD:**

📋 **Thông tin:**
• Số CCCD: {check_result.get('cccd_number', 'N/A')}
• Họ tên: {check_result.get('full_name', 'N/A')}
• Ngày sinh: {check_result.get('birth_date', 'N/A')}
• Giới tính: {check_result.get('gender', 'N/A')}
• Địa chỉ: {check_result.get('address', 'N/A')}
• Thời gian kiểm tra: {result.get('processing_time', 0):.2f}s
                        """
                    else:
                        return f"❌ Không tìm thấy thông tin CCCD: {check_result.get('reason', 'Không xác định')}"
                else:
                    return f"❌ Lỗi: {result.get('error', 'Không thể kiểm tra CCCD')}"
            else:
                return "❌ Lỗi: Không thể kết nối đến cơ sở dữ liệu"
                
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_tax_lookup(self, args: Dict[str, Any]) -> str:
        """Handle tax lookup function call."""
        try:
            tax_code = args.get("tax_code", "")
            
            if not tax_code:
                return "❌ Vui lòng cung cấp mã số thuế để tra cứu"
            
            # Call tax lookup API
            if self.supabase:
                result = await self._call_tax_lookup_api(tax_code)
                
                if result.get("success"):
                    lookup_result = result.get("lookup_result", {})
                    
                    if lookup_result.get("status") == "found":
                        return f"""
✅ **Kết quả tra cứu mã số thuế:**

📋 **Thông tin:**
• Mã số thuế: {lookup_result.get('tax_code', 'N/A')}
• Tên công ty: {lookup_result.get('company_name', 'N/A')}
• Địa chỉ: {lookup_result.get('address', 'N/A')}
• Ngành nghề: {lookup_result.get('business_type', 'N/A')}
• Thời gian tra cứu: {result.get('processing_time', 0):.2f}s
                        """
                    else:
                        return f"❌ Không tìm thấy thông tin mã số thuế: {lookup_result.get('reason', 'Không xác định')}"
                else:
                    return f"❌ Lỗi: {result.get('error', 'Không thể tra cứu mã số thuế')}"
            else:
                return "❌ Lỗi: Không thể kết nối đến cơ sở dữ liệu"
                
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_data_analysis(self, args: Dict[str, Any]) -> str:
        """Handle data analysis function call."""
        try:
            analysis_type = args.get("analysis_type", "")
            input_data = args.get("input_data", "")
            
            return f"🔧 **Phân tích dữ liệu**\n\nLoại phân tích: {analysis_type}\nDữ liệu: {input_data}\n\nTính năng này đang được phát triển..."
            
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_web_scraping(self, args: Dict[str, Any]) -> str:
        """Handle web scraping function call."""
        try:
            target_url = args.get("target_url", "")
            scraping_config = args.get("scraping_config", {})
            
            return f"🔧 **Web Scraping**\n\nURL: {target_url}\nCấu hình: {scraping_config}\n\nTính năng này đang được phát triển..."
            
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_form_automation(self, args: Dict[str, Any]) -> str:
        """Handle form automation function call."""
        try:
            form_url = args.get("form_url", "")
            form_data = args.get("form_data", {})
            
            return f"🔧 **Tự động hóa Form**\n\nURL: {form_url}\nDữ liệu: {form_data}\n\nTính năng này đang được phát triển..."
            
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_report_generation(self, args: Dict[str, Any]) -> str:
        """Handle report generation function call."""
        try:
            report_type = args.get("report_type", "")
            report_data = args.get("report_data", {})
            
            return f"🔧 **Tạo báo cáo**\n\nLoại báo cáo: {report_type}\nDữ liệu: {report_data}\n\nTính năng này đang được phát triển..."
            
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _handle_excel_export(self, args: Dict[str, Any]) -> str:
        """Handle Excel export function call."""
        try:
            export_data = args.get("export_data", {})
            filename = args.get("filename", "export.xlsx")
            
            return f"🔧 **Xuất Excel**\n\nDữ liệu: {export_data}\nTên file: {filename}\n\nTính năng này đang được phát triển..."
            
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    # API calling methods
    async def _call_cccd_generation_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call CCCD generation API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/modules/cccd_generation/execute",
                    json=params,
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _call_cccd_check_api(self, cccd_number: str) -> Dict[str, Any]:
        """Call CCCD check API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/modules/cccd_check/execute",
                    json={"cccd_number": cccd_number},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _call_tax_lookup_api(self, tax_code: str) -> Dict[str, Any]:
        """Call tax lookup API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/modules/tax_lookup/execute",
                    json={"tax_code": tax_code},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _save_conversation(
        self, 
        user_id: str, 
        session_id: str, 
        user_input: str, 
        intent: str
    ):
        """Save conversation to database."""
        try:
            conversation_data = {
                "user_id": user_id,
                "session_id": session_id,
                "user_input": user_input,
                "intent": intent,
                "ai_provider": "gemini",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.supabase.insert_data("ai_conversations", conversation_data)
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
    
    async def close(self):
        """Close the AI Agent."""
        await self.gemini_client.close()