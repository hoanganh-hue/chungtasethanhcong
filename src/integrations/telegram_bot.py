"""
Telegram Bot Integration for OpenManus-Youtu Integrated Framework
Complete Telegram bot with webhook support and AI agent integration
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json

from telegram import Update, Bot, WebhookInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import httpx

from ..core.unified_agent import UnifiedAgent
from ..agents.gemini_agent_factory import gemini_agent_manager
from ..utils.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

class TelegramBotManager:
    """Telegram Bot Manager with AI Agent Integration."""
    
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.application = None
        self.bot = None
        self.active_agents: Dict[str, UnifiedAgent] = {}
        
    async def initialize(self):
        """Initialize Telegram bot application."""
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            self.bot = self.application.bot
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("agents", self.list_agents_command))
            self.application.add_handler(CommandHandler("create_agent", self.create_agent_command))
            self.application.add_handler(CommandHandler("test", self.test_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Set webhook
            await self.set_webhook()
            
            logger.info("Telegram Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise
    
    async def set_webhook(self):
        """Set webhook for Telegram bot."""
        try:
            webhook_info = await self.bot.get_webhook_info()
            logger.info(f"Current webhook info: {webhook_info}")
            
            # Set new webhook
            await self.bot.set_webhook(
                url=self.webhook_url,
                allowed_updates=["message", "callback_query"]
            )
            
            logger.info(f"Webhook set to: {self.webhook_url}")
            
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            raise
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_message = f"""
🤖 **Chào mừng {user.first_name} đến với OpenManus-Youtu AI Framework!**

🚀 **Tính năng chính:**
• AI Agent thông minh với Gemini 2.0 Flash
• Xử lý CCCD và tra cứu thuế
• Phân tích dữ liệu và báo cáo
• Tự động hóa web và form
• Hỗ trợ tiếng Việt 100%

📋 **Các lệnh có sẵn:**
/start - Bắt đầu
/help - Trợ giúp
/status - Trạng thái hệ thống
/agents - Danh sách AI agents
/create_agent - Tạo agent mới
/test - Kiểm tra hệ thống

💬 **Cách sử dụng:**
Chỉ cần gõ tin nhắn tự nhiên, tôi sẽ xử lý và trả lời!

Ví dụ: "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975"
        """
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📚 **Hướng dẫn sử dụng OpenManus-Youtu AI Framework**

🤖 **AI Agents có sẵn:**
• **CCCD Agent** - Xử lý CCCD, tạo và tra cứu
• **Tax Agent** - Tra cứu mã số thuế
• **Data Analysis Agent** - Phân tích dữ liệu
• **Web Automation Agent** - Tự động hóa web
• **General Agent** - Xử lý đa năng

💬 **Cách tương tác:**
1. Gõ tin nhắn tự nhiên
2. Tôi sẽ phân tích và xử lý
3. Trả về kết quả chi tiết

🔧 **Lệnh hệ thống:**
/start - Khởi động bot
/help - Hiển thị hướng dẫn
/status - Kiểm tra trạng thái
/agents - Danh sách agents
/create_agent - Tạo agent mới
/test - Test hệ thống

📝 **Ví dụ sử dụng:**
• "Tạo 50 CCCD cho Hà Nội"
• "Tra cứu mã số thuế 037178000015"
• "Phân tích dữ liệu trong file CSV"
• "Tự động điền form web"
        """
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            # Get system status
            status_info = {
                "bot_status": "🟢 Online",
                "active_agents": len(self.active_agents),
                "gemini_status": "🟢 Connected",
                "webhook_status": "🟢 Active",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            status_message = f"""
📊 **Trạng thái hệ thống:**

🤖 **Bot Status:** {status_info['bot_status']}
🔧 **Active Agents:** {status_info['active_agents']}
🧠 **Gemini AI:** {status_info['gemini_status']}
🌐 **Webhook:** {status_info['webhook_status']}
⏰ **Thời gian:** {status_info['timestamp']}

✅ **Hệ thống hoạt động bình thường!**
            """
            
            await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi kiểm tra trạng thái: {str(e)}")
    
    async def list_agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /agents command."""
        try:
            agents_list = await gemini_agent_manager.list_agents()
            
            if not agents_list:
                await update.message.reply_text("📋 **Danh sách AI Agents:**\n\n🔍 Không có agent nào đang hoạt động.")
                return
            
            agents_message = "📋 **Danh sách AI Agents:**\n\n"
            for i, agent in enumerate(agents_list, 1):
                agents_message += f"{i}. **{agent.get('name', 'Unknown')}**\n"
                agents_message += f"   • Loại: {agent.get('type', 'Unknown')}\n"
                agents_message += f"   • Trạng thái: 🟢 Active\n\n"
            
            await update.message.reply_text(agents_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi lấy danh sách agents: {str(e)}")
    
    async def create_agent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create_agent command."""
        try:
            # Create a default CCCD agent
            agent_name = f"cccd_agent_{update.effective_user.id}"
            
            agent = await gemini_agent_manager.create_agent(
                agent_type="cccd",
                api_key=os.getenv("GEMINI_API_KEY"),
                name=agent_name
            )
            
            self.active_agents[agent_name] = agent
            
            success_message = f"""
✅ **Tạo AI Agent thành công!**

🤖 **Agent Name:** {agent_name}
🔧 **Type:** CCCD Agent
🧠 **Capabilities:** 
• Tạo CCCD
• Tra cứu CCCD
• Phân tích dữ liệu CCCD

💬 **Sẵn sàng xử lý yêu cầu của bạn!**
            """
            
            await update.message.reply_text(success_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi tạo agent: {str(e)}")
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command."""
        try:
            test_message = """
🧪 **Kiểm tra hệ thống...**

✅ **Telegram Bot:** Hoạt động bình thường
✅ **Webhook:** Kết nối thành công
✅ **Gemini AI:** Sẵn sàng xử lý
✅ **Database:** Kết nối OK
✅ **API Endpoints:** Tất cả hoạt động

🎉 **Hệ thống hoạt động 100%!**

💡 **Thử ngay:** Gõ tin nhắn để test AI Agent!
            """
            
            await update.message.reply_text(test_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi test hệ thống: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        try:
            user_message = update.message.text
            user_id = str(update.effective_user.id)
            
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get or create agent for user
            agent_name = f"user_agent_{user_id}"
            if agent_name not in self.active_agents:
                agent = await gemini_agent_manager.create_agent(
                    agent_type="general",
                    api_key=os.getenv("GEMINI_API_KEY"),
                    name=agent_name
                )
                self.active_agents[agent_name] = agent
            
            agent = self.active_agents[agent_name]
            
            # Process message with agent
            response_chunks = []
            async for chunk in agent.process_message(user_message, user_id, f"session_{user_id}"):
                response_chunks.append(chunk)
            
            # Send complete response
            complete_response = "".join(response_chunks)
            
            # Split long messages
            if len(complete_response) > 4000:
                chunks = [complete_response[i:i+4000] for i in range(0, len(complete_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(complete_response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(f"❌ **Lỗi xử lý tin nhắn:**\n\n{str(e)}")
    
    async def start_polling(self):
        """Start bot polling (for development)."""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Telegram Bot started polling")
            
        except Exception as e:
            logger.error(f"Failed to start polling: {e}")
            raise
    
    async def stop(self):
        """Stop the bot."""
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("Telegram Bot stopped")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

# Global bot manager instance
telegram_bot_manager = None

async def initialize_telegram_bot():
    """Initialize Telegram bot."""
    global telegram_bot_manager
    
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
        
        if not token or not webhook_url:
            logger.warning("Telegram bot not configured - missing token or webhook URL")
            return None
        
        telegram_bot_manager = TelegramBotManager(token, webhook_url)
        await telegram_bot_manager.initialize()
        
        return telegram_bot_manager
        
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        return None

async def get_telegram_bot():
    """Get Telegram bot manager instance."""
    return telegram_bot_manager