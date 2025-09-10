"""
Telegram Webhook Handler for OpenManus-Youtu Integrated Framework
Handles incoming webhook requests from Telegram
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
from typing import Dict, Any

from ..integrations.telegram_bot import get_telegram_bot
from ..utils.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

router = APIRouter()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook."""
    try:
        # Get request body
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Received Telegram webhook: {data}")
        
        # Get bot manager
        bot_manager = await get_telegram_bot()
        if not bot_manager:
            logger.error("Telegram bot manager not initialized")
            raise HTTPException(status_code=500, detail="Bot not initialized")
        
        # Process update
        from telegram import Update
        update = Update.de_json(data, bot_manager.bot)
        
        # Process update through bot application
        await bot_manager.application.process_update(update)
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhook/telegram")
async def telegram_webhook_info():
    """Get Telegram webhook information."""
    try:
        bot_manager = await get_telegram_bot()
        if not bot_manager:
            return JSONResponse(content={"error": "Bot not initialized"})
        
        webhook_info = await bot_manager.bot.get_webhook_info()
        
        return JSONResponse(content={
            "webhook_info": webhook_info.to_dict(),
            "status": "active"
        })
        
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return JSONResponse(content={"error": str(e)})