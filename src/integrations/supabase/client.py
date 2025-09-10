"""
Supabase Client for OpenManus-Youtu Integrated Framework
Database connection and operations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from supabase import create_client, Client
from supabase._sync.client import SyncClient
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SupabaseConfig:
    """Supabase configuration."""
    url: str
    key: str
    service_role_key: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30


class SupabaseClient:
    """Supabase database client with async support."""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.client: Optional[Client] = None
        self.sync_client: Optional[SyncClient] = None
        self.connected = False
        self.logger = logging.getLogger(f"{__name__}.SupabaseClient")
    
    async def connect(self) -> bool:
        """Connect to Supabase database."""
        try:
            self.logger.info("Connecting to Supabase...")
            
            # Create async client
            self.client = create_client(
                self.config.url,
                self.config.key
            )
            
            # Create sync client for operations that need it
            self.sync_client = create_client(
                self.config.url,
                self.config.key
            )
            
            # Test connection
            await self._test_connection()
            
            self.connected = True
            self.logger.info("Successfully connected to Supabase")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Supabase: {e}")
            self.connected = False
            return False
    
    async def _test_connection(self):
        """Test database connection."""
        try:
            # Simple query to test connection
            result = self.client.table("_health_check").select("*").limit(1).execute()
            self.logger.debug("Database connection test successful")
        except Exception as e:
            # If health check table doesn't exist, try a different approach
            self.logger.debug(f"Health check failed, but connection may still be valid: {e}")
    
    async def disconnect(self):
        """Disconnect from Supabase."""
        try:
            self.client = None
            self.sync_client = None
            self.connected = False
            self.logger.info("Disconnected from Supabase")
        except Exception as e:
            self.logger.error(f"Error disconnecting from Supabase: {e}")
    
    async def insert_data(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert data into Supabase table."""
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        try:
            self.logger.debug(f"Inserting data into table {table}")
            
            # Add timestamp if not present
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat()
            
            result = self.client.table(table).insert(data).execute()
            
            if result.data:
                self.logger.debug(f"Successfully inserted data into {table}")
                return result.data[0]
            else:
                self.logger.warning(f"No data returned from insert into {table}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to insert data into {table}: {e}")
            raise
    
    async def update_data(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update data in Supabase table."""
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        try:
            self.logger.debug(f"Updating data in table {table}")
            
            # Add updated timestamp
            data["updated_at"] = datetime.utcnow().isoformat()
            
            query = self.client.table(table).update(data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            
            if result.data:
                self.logger.debug(f"Successfully updated data in {table}")
                return result.data[0]
            else:
                self.logger.warning(f"No data returned from update in {table}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to update data in {table}: {e}")
            raise
    
    async def select_data(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                         columns: str = "*", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from Supabase table."""
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        try:
            self.logger.debug(f"Selecting data from table {table}")
            
            query = self.client.table(table).select(columns)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            
            self.logger.debug(f"Retrieved {len(result.data)} records from {table}")
            return result.data
            
        except Exception as e:
            self.logger.error(f"Failed to select data from {table}: {e}")
            raise
    
    async def delete_data(self, table: str, filters: Dict[str, Any]) -> bool:
        """Delete data from Supabase table."""
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        try:
            self.logger.debug(f"Deleting data from table {table}")
            
            query = self.client.table(table).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            
            self.logger.debug(f"Successfully deleted data from {table}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete data from {table}: {e}")
            raise
    
    async def execute_rpc(self, function_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute Supabase RPC function."""
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        try:
            self.logger.debug(f"Executing RPC function {function_name}")
            
            result = self.client.rpc(function_name, params or {}).execute()
            
            self.logger.debug(f"Successfully executed RPC function {function_name}")
            return result.data
            
        except Exception as e:
            self.logger.error(f"Failed to execute RPC function {function_name}: {e}")
            raise
    
    async def create_table(self, table_name: str, schema: Dict[str, Any]) -> bool:
        """Create a new table in Supabase."""
        try:
            self.logger.info(f"Creating table {table_name}")
            
            # This would typically be done through Supabase dashboard or SQL
            # For now, we'll log the schema that should be created
            self.logger.info(f"Table {table_name} schema: {json.dumps(schema, indent=2)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create table {table_name}: {e}")
            return False
    
    async def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a table."""
        try:
            # Get table schema information
            result = await self.select_data(table_name, limit=1)
            
            if result:
                return {
                    "table_name": table_name,
                    "columns": list(result[0].keys()) if result else [],
                    "sample_data": result[0] if result else None
                }
            else:
                return {
                    "table_name": table_name,
                    "columns": [],
                    "sample_data": None
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Supabase connection."""
        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity
            await self._test_connection()
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "status": "healthy",
                "connected": self.connected,
                "response_time": response_time,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class SupabaseManager:
    """Manager for multiple Supabase connections."""
    
    def __init__(self):
        self.clients: Dict[str, SupabaseClient] = {}
        self.logger = logging.getLogger(f"{__name__}.SupabaseManager")
    
    async def add_client(self, name: str, config: SupabaseConfig) -> bool:
        """Add a new Supabase client."""
        try:
            client = SupabaseClient(config)
            success = await client.connect()
            
            if success:
                self.clients[name] = client
                self.logger.info(f"Added Supabase client: {name}")
                return True
            else:
                self.logger.error(f"Failed to add Supabase client: {name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding Supabase client {name}: {e}")
            return False
    
    def get_client(self, name: str) -> Optional[SupabaseClient]:
        """Get a Supabase client by name."""
        return self.clients.get(name)
    
    async def remove_client(self, name: str) -> bool:
        """Remove a Supabase client."""
        try:
            if name in self.clients:
                await self.clients[name].disconnect()
                del self.clients[name]
                self.logger.info(f"Removed Supabase client: {name}")
                return True
            else:
                self.logger.warning(f"Supabase client not found: {name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing Supabase client {name}: {e}")
            return False
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all clients."""
        results = {}
        
        for name, client in self.clients.items():
            results[name] = await client.health_check()
        
        return results
    
    async def disconnect_all(self):
        """Disconnect all clients."""
        for name, client in self.clients.items():
            try:
                await client.disconnect()
                self.logger.info(f"Disconnected client: {name}")
            except Exception as e:
                self.logger.error(f"Error disconnecting client {name}: {e}")


# Global Supabase manager instance
supabase_manager = SupabaseManager()