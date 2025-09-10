"""
Telegram Bot Integration for OpenManus-Youtu Integrated Framework
Bot for module communication and data persistence
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from telegram.constants import ParseMode
import httpx
from .client import SupabaseClient
from .models import (
    ModuleRequest, CCCDGenerationData, CCCDCheckData, TaxLookupData,
    DataAnalysisData, WebScrapingData, FormAutomationData,
    ReportGenerationData, ExcelExportData, TelegramUser, TelegramSession,
    ModuleType, RequestStatus
)

logger = logging.getLogger(__name__)


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    bot_token: str
    webhook_url: Optional[str] = None
    webhook_port: int = 8443
    api_base_url: str = "http://localhost:8000"
    supabase_client: Optional[SupabaseClient] = None
    allowed_users: Optional[List[str]] = None
    admin_users: Optional[List[str]] = None


class TelegramBot:
    """Telegram bot for module communication."""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
        self.supabase = config.supabase_client
        self.logger = logging.getLogger(f"{__name__}.TelegramBot")
        
        # Conversation states
        self.WAITING_FOR_MODULE = 1
        self.WAITING_FOR_PARAMS = 2
        self.WAITING_FOR_CONFIRMATION = 3
        
        # Module handlers
        self.module_handlers: Dict[str, Callable] = {
            ModuleType.CCCD_GENERATION.value: self._handle_cccd_generation,
            ModuleType.CCCD_CHECK.value: self._handle_cccd_check,
            ModuleType.TAX_LOOKUP.value: self._handle_tax_lookup,
            ModuleType.DATA_ANALYSIS.value: self._handle_data_analysis,
            ModuleType.WEB_SCRAPING.value: self._handle_web_scraping,
            ModuleType.FORM_AUTOMATION.value: self._handle_form_automation,
            ModuleType.REPORT_GENERATION.value: self._handle_report_generation,
            ModuleType.EXCEL_EXPORT.value: self._handle_excel_export
        }
    
    async def initialize(self) -> bool:
        """Initialize the Telegram bot."""
        try:
            self.logger.info("Initializing Telegram bot...")
            
            # Create bot instance
            self.bot = Bot(token=self.config.bot_token)
            
            # Create application
            self.application = Application.builder().bot(self.bot).build()
            
            # Add handlers
            self._add_handlers()
            
            # Test bot connection
            bot_info = await self.bot.get_me()
            self.logger.info(f"Bot initialized: @{bot_info.username}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram bot: {e}")
            return False
    
    def _add_handlers(self):
        """Add command and message handlers."""
        # Start command
        self.application.add_handler(CommandHandler("start", self._start_command))
        
        # Help command
        self.application.add_handler(CommandHandler("help", self._help_command))
        
        # Status command
        self.application.add_handler(CommandHandler("status", self._status_command))
        
        # Modules command
        self.application.add_handler(CommandHandler("modules", self._modules_command))
        
        # Conversation handler for module operations
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("run", self._run_module_command)],
            states={
                self.WAITING_FOR_MODULE: [CallbackQueryHandler(self._select_module)],
                self.WAITING_FOR_PARAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_parameters)],
                self.WAITING_FOR_CONFIRMATION: [CallbackQueryHandler(self._confirm_execution)]
            },
            fallbacks=[CommandHandler("cancel", self._cancel_command)]
        )
        self.application.add_handler(conv_handler)
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self._handle_callback))
        
        # Message handler for general messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    async def start_polling(self):
        """Start the bot in polling mode."""
        try:
            self.logger.info("Starting Telegram bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            self.logger.error(f"Error in polling: {e}")
        finally:
            await self.stop()
    
    async def start_webhook(self):
        """Start the bot with webhook."""
        try:
            self.logger.info("Starting Telegram bot webhook...")
            
            # Set webhook
            await self.bot.set_webhook(
                url=self.config.webhook_url,
                allowed_updates=["message", "callback_query"]
            )
            
            # Start application
            await self.application.initialize()
            await self.application.start()
            
            self.logger.info(f"Webhook set to: {self.config.webhook_url}")
            
        except Exception as e:
            self.logger.error(f"Failed to start webhook: {e}")
    
    async def stop(self):
        """Stop the bot."""
        try:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            self.logger.info("Telegram bot stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Register user in database
        await self._register_user(user)
        
        welcome_message = f"""
🤖 **Chào mừng đến với OpenManus-Youtu Bot!**

Xin chào {user.first_name}! Tôi là bot hỗ trợ các tính năng:

🔧 **Các module có sẵn:**
• CCCD Generation - Tạo CCCD
• CCCD Check - Kiểm tra CCCD  
• Tax Lookup - Tra cứu mã số thuế
• Data Analysis - Phân tích dữ liệu
• Web Scraping - Thu thập dữ liệu web
• Form Automation - Tự động hóa form
• Report Generation - Tạo báo cáo
• Excel Export - Xuất Excel

📋 **Các lệnh:**
/start - Bắt đầu
/help - Trợ giúp
/modules - Xem modules
/run - Chạy module
/status - Trạng thái hệ thống

Sử dụng /run để bắt đầu sử dụng các tính năng!
        """
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📚 **Hướng dẫn sử dụng OpenManus-Youtu Bot**

🔧 **Các lệnh chính:**
/start - Khởi động bot
/help - Hiển thị trợ giúp này
/modules - Xem danh sách modules
/run - Chạy một module
/status - Kiểm tra trạng thái hệ thống
/cancel - Hủy thao tác hiện tại

🚀 **Cách sử dụng:**
1. Sử dụng /run để chọn module
2. Nhập tham số theo yêu cầu
3. Xác nhận và chờ kết quả
4. Dữ liệu sẽ được lưu tự động

📊 **Modules có sẵn:**
• **CCCD Generation**: Tạo CCCD theo tỉnh, giới tính, năm sinh
• **CCCD Check**: Kiểm tra thông tin CCCD
• **Tax Lookup**: Tra cứu mã số thuế
• **Data Analysis**: Phân tích dữ liệu
• **Web Scraping**: Thu thập dữ liệu từ web
• **Form Automation**: Tự động điền form
• **Report Generation**: Tạo báo cáo
• **Excel Export**: Xuất dữ liệu ra Excel

❓ **Hỗ trợ:** Liên hệ admin nếu cần trợ giúp
        """
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            # Check system status
            status_info = await self._get_system_status()
            
            status_message = f"""
📊 **Trạng thái hệ thống**

🟢 **Bot Status**: Hoạt động bình thường
🟢 **Database**: {'Kết nối' if self.supabase and self.supabase.connected else 'Mất kết nối'}
🟢 **API Server**: {'Hoạt động' if status_info.get('api_online') else 'Không hoạt động'}

📈 **Thống kê:**
• Tổng requests: {status_info.get('total_requests', 0)}
• Requests hôm nay: {status_info.get('today_requests', 0)}
• Modules hoạt động: {len(self.module_handlers)}

🕐 **Thời gian**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """
            
            await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            await update.message.reply_text("❌ Lỗi khi lấy trạng thái hệ thống")
    
    async def _modules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /modules command."""
        modules_message = """
🔧 **Danh sách Modules**

1️⃣ **CCCD Generation**
   - Tạo CCCD theo tỉnh, giới tính, năm sinh
   - Tham số: province, gender, birth_year_range, quantity

2️⃣ **CCCD Check** 
   - Kiểm tra thông tin CCCD
   - Tham số: cccd_number

3️⃣ **Tax Lookup**
   - Tra cứu mã số thuế
   - Tham số: tax_code

4️⃣ **Data Analysis**
   - Phân tích dữ liệu
   - Tham số: analysis_type, input_data

5️⃣ **Web Scraping**
   - Thu thập dữ liệu từ web
   - Tham số: target_url, scraping_config

6️⃣ **Form Automation**
   - Tự động điền form
   - Tham số: form_url, form_data

7️⃣ **Report Generation**
   - Tạo báo cáo
   - Tham số: report_type, report_data

8️⃣ **Excel Export**
   - Xuất dữ liệu ra Excel
   - Tham số: export_data

Sử dụng /run để chọn và chạy module!
        """
        
        await update.message.reply_text(modules_message, parse_mode=ParseMode.MARKDOWN)
    
    async def _run_module_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /run command - start module selection."""
        keyboard = [
            [InlineKeyboardButton("1️⃣ CCCD Generation", callback_data="module_cccd_generation")],
            [InlineKeyboardButton("2️⃣ CCCD Check", callback_data="module_cccd_check")],
            [InlineKeyboardButton("3️⃣ Tax Lookup", callback_data="module_tax_lookup")],
            [InlineKeyboardButton("4️⃣ Data Analysis", callback_data="module_data_analysis")],
            [InlineKeyboardButton("5️⃣ Web Scraping", callback_data="module_web_scraping")],
            [InlineKeyboardButton("6️⃣ Form Automation", callback_data="module_form_automation")],
            [InlineKeyboardButton("7️⃣ Report Generation", callback_data="module_report_generation")],
            [InlineKeyboardButton("8️⃣ Excel Export", callback_data="module_excel_export")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 **Chọn module để chạy:**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return self.WAITING_FOR_MODULE
    
    async def _select_module(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle module selection."""
        query = update.callback_query
        await query.answer()
        
        module_type = query.data.replace("module_", "")
        context.user_data['selected_module'] = module_type
        
        # Get module parameters info
        params_info = self._get_module_parameters(module_type)
        
        await query.edit_message_text(
            f"📋 **Module: {module_type.replace('_', ' ').title()}**\n\n"
            f"Tham số cần thiết:\n{params_info}\n\n"
            f"Vui lòng nhập tham số theo định dạng JSON:",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return self.WAITING_FOR_PARAMS
    
    async def _get_parameters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get module parameters from user."""
        try:
            parameters_text = update.message.text
            parameters = json.loads(parameters_text)
            
            context.user_data['parameters'] = parameters
            
            # Show confirmation
            confirmation_text = f"""
✅ **Xác nhận thực thi**

🔧 **Module**: {context.user_data['selected_module'].replace('_', ' ').title()}
📋 **Tham số**: 
```json
{json.dumps(parameters, indent=2, ensure_ascii=False)}
```

Bạn có muốn tiếp tục?
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ Xác nhận", callback_data="confirm_yes")],
                [InlineKeyboardButton("❌ Hủy", callback_data="confirm_no")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                confirmation_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
            return self.WAITING_FOR_CONFIRMATION
            
        except json.JSONDecodeError:
            await update.message.reply_text(
                "❌ **Lỗi định dạng JSON!**\n\n"
                "Vui lòng nhập tham số theo định dạng JSON hợp lệ.\n"
                "Ví dụ:\n"
                "```json\n"
                '{"province": "Hưng Yên", "gender": "nữ", "quantity": 100}\n'
                "```",
                parse_mode=ParseMode.MARKDOWN
            )
            return self.WAITING_FOR_PARAMS
        except Exception as e:
            self.logger.error(f"Error parsing parameters: {e}")
            await update.message.reply_text("❌ Lỗi khi xử lý tham số")
            return ConversationHandler.END
    
    async def _confirm_execution(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle execution confirmation."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_yes":
            # Execute module
            await self._execute_module(update, context)
        else:
            await query.edit_message_text("❌ Đã hủy thao tác")
        
        return ConversationHandler.END
    
    async def _execute_module(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute the selected module."""
        query = update.callback_query
        module_type = context.user_data['selected_module']
        parameters = context.user_data['parameters']
        
        try:
            # Update message to show processing
            await query.edit_message_text(
                f"⏳ **Đang xử lý...**\n\n"
                f"Module: {module_type.replace('_', ' ').title()}\n"
                f"Vui lòng chờ trong giây lát...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Create module request
            request = await self._create_module_request(
                module_type=module_type,
                user_id=str(update.effective_user.id),
                chat_id=str(update.effective_chat.id),
                request_data=parameters
            )
            
            # Execute module
            result = await self._call_module_api(module_type, parameters)
            
            # Save result to database
            await self._save_module_result(module_type, request.id, result)
            
            # Send result to user
            await self._send_result_to_user(update, module_type, result)
            
        except Exception as e:
            self.logger.error(f"Error executing module {module_type}: {e}")
            await query.edit_message_text(
                f"❌ **Lỗi khi thực thi module**\n\n"
                f"Module: {module_type.replace('_', ' ').title()}\n"
                f"Lỗi: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries."""
        query = update.callback_query
        await query.answer()
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages."""
        await update.message.reply_text(
            "🤖 Sử dụng /help để xem hướng dẫn hoặc /run để chạy module!"
        )
    
    async def _cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command."""
        await update.message.reply_text("❌ Đã hủy thao tác")
        return ConversationHandler.END
    
    # Module handlers
    async def _handle_cccd_generation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CCCD generation module."""
        # Implementation for CCCD generation
        return {"status": "success", "message": "CCCD generation completed"}
    
    async def _handle_cccd_check(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CCCD check module."""
        # Implementation for CCCD check
        return {"status": "success", "message": "CCCD check completed"}
    
    async def _handle_tax_lookup(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tax lookup module."""
        # Implementation for tax lookup
        return {"status": "success", "message": "Tax lookup completed"}
    
    async def _handle_data_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data analysis module."""
        # Implementation for data analysis
        return {"status": "success", "message": "Data analysis completed"}
    
    async def _handle_web_scraping(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web scraping module."""
        # Implementation for web scraping
        return {"status": "success", "message": "Web scraping completed"}
    
    async def _handle_form_automation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle form automation module."""
        # Implementation for form automation
        return {"status": "success", "message": "Form automation completed"}
    
    async def _handle_report_generation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report generation module."""
        # Implementation for report generation
        return {"status": "success", "message": "Report generation completed"}
    
    async def _handle_excel_export(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Excel export module."""
        # Implementation for Excel export
        return {"status": "success", "message": "Excel export completed"}
    
    # Helper methods
    async def _register_user(self, user):
        """Register user in database."""
        if not self.supabase:
            return
        
        try:
            user_data = {
                "telegram_id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.is_bot,
                "language_code": user.language_code,
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Check if user exists
            existing = await self.supabase.select_data(
                "telegram_users",
                filters={"telegram_id": str(user.id)}
            )
            
            if existing:
                # Update existing user
                await self.supabase.update_data(
                    "telegram_users",
                    user_data,
                    {"telegram_id": str(user.id)}
                )
            else:
                # Insert new user
                await self.supabase.insert_data("telegram_users", user_data)
                
        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
    
    async def _create_module_request(self, module_type: str, user_id: str, 
                                   chat_id: str, request_data: Dict[str, Any]) -> ModuleRequest:
        """Create module request in database."""
        if not self.supabase:
            raise Exception("Supabase client not available")
        
        request_data_dict = {
            "module_type": module_type,
            "user_id": user_id,
            "telegram_chat_id": chat_id,
            "request_data": request_data,
            "status": RequestStatus.PENDING.value
        }
        
        result = await self.supabase.insert_data("module_requests", request_data_dict)
        
        return ModuleRequest.from_dict(result)
    
    async def _call_module_api(self, module_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call module API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.api_base_url}/modules/{module_type}/execute",
                    json=parameters,
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"API error: {response.status_code}")
                    
        except Exception as e:
            self.logger.error(f"Error calling module API: {e}")
            raise
    
    async def _save_module_result(self, module_type: str, request_id: str, result: Dict[str, Any]):
        """Save module result to appropriate table."""
        if not self.supabase:
            return
        
        try:
            # Map module type to table name
            table_mapping = {
                ModuleType.CCCD_GENERATION.value: "cccd_generation_data",
                ModuleType.CCCD_CHECK.value: "cccd_check_data",
                ModuleType.TAX_LOOKUP.value: "tax_lookup_data",
                ModuleType.DATA_ANALYSIS.value: "data_analysis_data",
                ModuleType.WEB_SCRAPING.value: "web_scraping_data",
                ModuleType.FORM_AUTOMATION.value: "form_automation_data",
                ModuleType.REPORT_GENERATION.value: "report_generation_data",
                ModuleType.EXCEL_EXPORT.value: "excel_export_data"
            }
            
            table_name = table_mapping.get(module_type)
            if not table_name:
                self.logger.warning(f"No table mapping for module type: {module_type}")
                return
            
            # Prepare data for specific table
            data = {
                "request_id": request_id,
                "success": result.get("status") == "success",
                "error_message": result.get("error") if result.get("status") != "success" else None
            }
            
            # Add module-specific fields
            if module_type == ModuleType.CCCD_GENERATION.value:
                data.update({
                    "province": result.get("province", ""),
                    "gender": result.get("gender", ""),
                    "birth_year_range": result.get("birth_year_range", ""),
                    "quantity": result.get("quantity", 0),
                    "generated_cccds": result.get("generated_cccds", []),
                    "generation_time": result.get("processing_time", 0),
                    "success_count": result.get("success_count", 0),
                    "failure_count": result.get("failure_count", 0)
                })
            elif module_type == ModuleType.CCCD_CHECK.value:
                data.update({
                    "cccd_number": result.get("cccd_number", ""),
                    "check_result": result.get("check_result", {}),
                    "check_time": result.get("processing_time", 0)
                })
            # Add more module-specific mappings as needed
            
            await self.supabase.insert_data(table_name, data)
            
        except Exception as e:
            self.logger.error(f"Error saving module result: {e}")
    
    async def _send_result_to_user(self, update: Update, module_type: str, result: Dict[str, Any]):
        """Send result to user."""
        try:
            if result.get("status") == "success":
                message = f"""
✅ **Hoàn thành thành công!**

🔧 **Module**: {module_type.replace('_', ' ').title()}
📊 **Kết quả**: {result.get('message', 'Thành công')}

📋 **Chi tiết**:
```json
{json.dumps(result, indent=2, ensure_ascii=False)}
```

💾 **Dữ liệu đã được lưu vào cơ sở dữ liệu**
                """
            else:
                message = f"""
❌ **Lỗi khi thực thi**

🔧 **Module**: {module_type.replace('_', ' ').title()}
🚫 **Lỗi**: {result.get('error', 'Lỗi không xác định')}
                """
            
            await update.callback_query.edit_message_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error sending result to user: {e}")
    
    def _get_module_parameters(self, module_type: str) -> str:
        """Get module parameters description."""
        parameters = {
            ModuleType.CCCD_GENERATION.value: """
• province: Tỉnh (string)
• gender: Giới tính (string) 
• birth_year_range: Khoảng năm sinh (string)
• quantity: Số lượng (integer)
            """,
            ModuleType.CCCD_CHECK.value: """
• cccd_number: Số CCCD (string)
            """,
            ModuleType.TAX_LOOKUP.value: """
• tax_code: Mã số thuế (string)
            """,
            ModuleType.DATA_ANALYSIS.value: """
• analysis_type: Loại phân tích (string)
• input_data: Dữ liệu đầu vào (object)
            """,
            ModuleType.WEB_SCRAPING.value: """
• target_url: URL đích (string)
• scraping_config: Cấu hình scraping (object)
            """,
            ModuleType.FORM_AUTOMATION.value: """
• form_url: URL form (string)
• form_data: Dữ liệu form (object)
            """,
            ModuleType.REPORT_GENERATION.value: """
• report_type: Loại báo cáo (string)
• report_data: Dữ liệu báo cáo (object)
            """,
            ModuleType.EXCEL_EXPORT.value: """
• export_data: Dữ liệu xuất (object)
            """
        }
        
        return parameters.get(module_type, "Không có thông tin tham số")
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        try:
            # Check API server
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.config.api_base_url}/health", timeout=5.0)
                    api_online = response.status_code == 200
                except:
                    api_online = False
            
            # Get database stats
            total_requests = 0
            today_requests = 0
            
            if self.supabase and self.supabase.connected:
                try:
                    requests = await self.supabase.select_data("module_requests")
                    total_requests = len(requests)
                    
                    today = datetime.now().date()
                    today_requests = len([
                        r for r in requests 
                        if datetime.fromisoformat(r['created_at']).date() == today
                    ])
                except:
                    pass
            
            return {
                "api_online": api_online,
                "total_requests": total_requests,
                "today_requests": today_requests
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                "api_online": False,
                "total_requests": 0,
                "today_requests": 0
            }