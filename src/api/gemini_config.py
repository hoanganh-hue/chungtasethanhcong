"""
Gemini API Configuration API endpoints
Allow users to configure their Gemini API keys and settings
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import json
import hashlib
from datetime import datetime
import asyncio

from src.ai.gemini_client import GeminiClient, GeminiConfig, GeminiModel
from src.ai.gemini_agent import GeminiAIAgent
from src.security.authentication import get_current_user
from src.integrations.supabase.client import SupabaseClient

router = APIRouter()

# Global AI Agent instance
gemini_agent: Optional[GeminiAIAgent] = None

class GeminiConfigManager:
    """Manage Gemini API configurations."""
    
    def __init__(self, supabase_client: SupabaseClient = None):
        self.supabase = supabase_client
        self.config_cache: Dict[str, Dict[str, Any]] = {}
    
    async def save_user_config(
        self, 
        user_id: str, 
        api_key: str, 
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> bool:
        """Save user's Gemini configuration."""
        try:
            # Hash API key for security
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            config_data = {
                "user_id": user_id,
                "api_key_hash": api_key_hash,
                "api_key_encrypted": self._encrypt_api_key(api_key),  # Simple encryption
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if self.supabase:
                # Check if config exists
                existing = await self.supabase.select_data(
                    "gemini_configs",
                    filters={"user_id": user_id}
                )
                
                if existing:
                    # Update existing config
                    await self.supabase.update_data(
                        "gemini_configs",
                        config_data,
                        {"user_id": user_id}
                    )
                else:
                    # Insert new config
                    await self.supabase.insert_data("gemini_configs", config_data)
            
            # Cache the config
            self.config_cache[user_id] = {
                "api_key": api_key,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            return True
            
        except Exception as e:
            print(f"Error saving Gemini config: {e}")
            return False
    
    async def get_user_config(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's Gemini configuration."""
        try:
            # Check cache first
            if user_id in self.config_cache:
                return self.config_cache[user_id]
            
            if self.supabase:
                configs = await self.supabase.select_data(
                    "gemini_configs",
                    filters={"user_id": user_id}
                )
                
                if configs:
                    config = configs[0]
                    # Decrypt API key
                    api_key = self._decrypt_api_key(config["api_key_encrypted"])
                    
                    user_config = {
                        "api_key": api_key,
                        "model": config.get("model", "gemini-1.5-flash"),
                        "temperature": config.get("temperature", 0.7),
                        "max_tokens": config.get("max_tokens", 2048)
                    }
                    
                    # Cache the config
                    self.config_cache[user_id] = user_config
                    return user_config
            
            return None
            
        except Exception as e:
            print(f"Error getting Gemini config: {e}")
            return None
    
    async def test_api_key(self, api_key: str, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """Test Gemini API key."""
        try:
            config = GeminiConfig(
                api_key=api_key,
                model=model,
                temperature=0.7,
                max_tokens=100
            )
            
            client = GeminiClient(config)
            
            # Test connection
            if await client.initialize():
                # Test simple generation
                test_message = GeminiMessage(
                    role="user",
                    parts=[{"text": "Hello, this is a test message."}],
                    timestamp=datetime.now()
                )
                
                response_chunks = []
                async for chunk in client.generate_content([test_message], stream=False):
                    response_chunks.append(chunk)
                
                await client.close()
                
                return {
                    "success": True,
                    "message": "API key is valid and working",
                    "test_response": "".join(response_chunks)[:100] + "..." if response_chunks else "No response"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to initialize Gemini client"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"API key test failed: {str(e)}"
            }
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Simple encryption for API key (for demo purposes)."""
        # In production, use proper encryption
        return api_key[::-1]  # Simple reverse
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Simple decryption for API key (for demo purposes)."""
        # In production, use proper decryption
        return encrypted_key[::-1]  # Simple reverse

# Global config manager
config_manager = GeminiConfigManager()

async def get_gemini_agent(user_id: str) -> Optional[GeminiAIAgent]:
    """Get or create Gemini AI Agent for user."""
    global gemini_agent
    
    try:
        # Get user's config
        user_config = await config_manager.get_user_config(user_id)
        
        if not user_config:
            return None
        
        # Create Gemini config
        gemini_config = GeminiConfig(
            api_key=user_config["api_key"],
            model=user_config["model"],
            temperature=user_config["temperature"],
            max_tokens=user_config["max_tokens"]
        )
        
        # Create AI Agent
        supabase_client = SupabaseClient()
        agent = GeminiAIAgent(gemini_config, supabase_client)
        
        if await agent.initialize():
            return agent
        else:
            return None
            
    except Exception as e:
        print(f"Error creating Gemini agent: {e}")
        return None

@router.post("/gemini/config")
async def save_gemini_config(
    config_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Save user's Gemini API configuration."""
    try:
        user_id = str(current_user.id)
        api_key = config_data.get("api_key", "")
        model = config_data.get("model", "gemini-1.5-flash")
        temperature = config_data.get("temperature", 0.7)
        max_tokens = config_data.get("max_tokens", 2048)
        
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Validate model
        valid_models = [model.value for model in GeminiModel]
        if model not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid model. Valid models: {valid_models}")
        
        # Validate temperature
        if not 0.0 <= temperature <= 2.0:
            raise HTTPException(status_code=400, detail="Temperature must be between 0.0 and 2.0")
        
        # Validate max_tokens
        if not 1 <= max_tokens <= 8192:
            raise HTTPException(status_code=400, detail="Max tokens must be between 1 and 8192")
        
        # Save configuration
        success = await config_manager.save_user_config(
            user_id, api_key, model, temperature, max_tokens
        )
        
        if success:
            return {
                "success": True,
                "message": "Gemini configuration saved successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/config")
async def get_gemini_config(current_user = Depends(get_current_user)):
    """Get user's Gemini API configuration."""
    try:
        user_id = str(current_user.id)
        config = await config_manager.get_user_config(user_id)
        
        if config:
            # Don't return the actual API key for security
            return {
                "success": True,
                "config": {
                    "model": config["model"],
                    "temperature": config["temperature"],
                    "max_tokens": config["max_tokens"],
                    "has_api_key": bool(config.get("api_key"))
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "config": None,
                "message": "No Gemini configuration found",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gemini/test")
async def test_gemini_api(
    test_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Test Gemini API key."""
    try:
        api_key = test_data.get("api_key", "")
        model = test_data.get("model", "gemini-1.5-flash")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Test the API key
        result = await config_manager.test_api_key(api_key, model)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "test_response": result.get("test_response", ""),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/gemini/config")
async def delete_gemini_config(current_user = Depends(get_current_user)):
    """Delete user's Gemini API configuration."""
    try:
        user_id = str(current_user.id)
        
        if config_manager.supabase:
            # Delete from database
            await config_manager.supabase.delete_data(
                "gemini_configs",
                {"user_id": user_id}
            )
        
        # Remove from cache
        if user_id in config_manager.config_cache:
            del config_manager.config_cache[user_id]
        
        return {
            "success": True,
            "message": "Gemini configuration deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/models")
async def get_available_models():
    """Get available Gemini models."""
    try:
        models = [
            {
                "id": model.value,
                "name": model.value.replace("-", " ").title(),
                "description": f"Google {model.value.replace('-', ' ').title()} model"
            }
            for model in GeminiModel
        ]
        
        return {
            "success": True,
            "models": models,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/status")
async def get_gemini_status(current_user = Depends(get_current_user)):
    """Get Gemini AI Agent status."""
    try:
        user_id = str(current_user.id)
        agent = await get_gemini_agent(user_id)
        
        if agent:
            return {
                "success": True,
                "status": "active",
                "message": "Gemini AI Agent is ready",
                "capabilities": [
                    "cccd_generation",
                    "cccd_check", 
                    "tax_lookup",
                    "data_analysis",
                    "web_scraping",
                    "form_automation",
                    "report_generation",
                    "excel_export"
                ],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "status": "inactive",
                "message": "Gemini AI Agent is not configured or not working",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))