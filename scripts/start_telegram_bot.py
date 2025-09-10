#!/usr/bin/env python3
"""
Telegram Bot Startup Script for OpenManus-Youtu Integrated Framework
Start the Telegram bot with Supabase integration
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.supabase import SupabaseClient, SupabaseConfig, TelegramBot, TelegramConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_telegram_bot():
    """Start the Telegram bot."""
    try:
        logger.info("Starting Telegram bot...")
        
        # Get configuration from environment variables
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        if not telegram_token:
            logger.error("Missing required environment variable: TELEGRAM_BOT_TOKEN")
            return False
        
        if not supabase_url or not supabase_key:
            logger.error("Missing required environment variables: SUPABASE_URL, SUPABASE_ANON_KEY")
            return False
        
        # Create Supabase client
        supabase_config = SupabaseConfig(
            url=supabase_url,
            key=supabase_key
        )
        
        supabase_client = SupabaseClient(supabase_config)
        
        # Connect to Supabase
        logger.info("Connecting to Supabase...")
        success = await supabase_client.connect()
        
        if not success:
            logger.error("Failed to connect to Supabase")
            return False
        
        logger.info("Successfully connected to Supabase")
        
        # Create Telegram bot configuration
        telegram_config = TelegramConfig(
            bot_token=telegram_token,
            webhook_url=telegram_webhook_url,
            api_base_url=api_base_url,
            supabase_client=supabase_client
        )
        
        # Create and initialize Telegram bot
        bot = TelegramBot(telegram_config)
        
        logger.info("Initializing Telegram bot...")
        success = await bot.initialize()
        
        if not success:
            logger.error("Failed to initialize Telegram bot")
            return False
        
        logger.info("Telegram bot initialized successfully")
        
        # Start the bot
        if telegram_webhook_url:
            logger.info("Starting bot with webhook...")
            await bot.start_webhook()
        else:
            logger.info("Starting bot with polling...")
            await bot.start_polling()
        
        return True
        
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
        return False


async def test_telegram_bot():
    """Test Telegram bot functionality."""
    try:
        logger.info("Testing Telegram bot...")
        
        # Get configuration
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not all([telegram_token, supabase_url, supabase_key]):
            logger.error("Missing required environment variables for testing")
            return False
        
        # Create Supabase client
        supabase_config = SupabaseConfig(url=supabase_url, key=supabase_key)
        supabase_client = SupabaseClient(supabase_config)
        
        success = await supabase_client.connect()
        if not success:
            logger.error("Failed to connect to Supabase for testing")
            return False
        
        # Create Telegram bot configuration
        telegram_config = TelegramConfig(
            bot_token=telegram_token,
            supabase_client=supabase_client
        )
        
        # Create and initialize bot
        bot = TelegramBot(telegram_config)
        success = await bot.initialize()
        
        if not success:
            logger.error("Failed to initialize Telegram bot for testing")
            return False
        
        # Test bot info
        bot_info = await bot.bot.get_me()
        logger.info(f"Bot info: @{bot_info.username} ({bot_info.first_name})")
        
        # Test database connection
        health_check = await supabase_client.health_check()
        logger.info(f"Database health: {health_check['status']}")
        
        await bot.stop()
        await supabase_client.disconnect()
        
        logger.info("Telegram bot test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Telegram bot: {e}")
        return False


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Telegram bot startup script")
    parser.add_argument("--test", action="store_true", help="Test bot functionality only")
    parser.add_argument("--webhook", action="store_true", help="Start with webhook mode")
    parser.add_argument("--polling", action="store_true", help="Start with polling mode")
    
    args = parser.parse_args()
    
    if args.test:
        # Only run tests
        logger.info("Running Telegram bot tests...")
        success = await test_telegram_bot()
        return success
    
    # Set webhook mode if specified
    if args.webhook:
        os.environ["TELEGRAM_WEBHOOK_URL"] = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    elif args.polling:
        os.environ["TELEGRAM_WEBHOOK_URL"] = ""
    
    # Start the bot
    success = await start_telegram_bot()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)