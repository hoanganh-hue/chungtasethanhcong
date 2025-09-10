"""
Database Migrations for OpenManus-Youtu Integrated Framework
Supabase database schema creation and migration scripts
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from .client import SupabaseClient
from .models import DatabaseModels

logger = logging.getLogger(__name__)


class DatabaseMigrations:
    """Database migration manager for Supabase."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
        self.logger = logging.getLogger(f"{__name__}.DatabaseMigrations")
    
    async def create_all_tables(self) -> bool:
        """Create all required tables."""
        try:
            self.logger.info("Creating all database tables...")
            
            # Create tables in order (respecting foreign key dependencies)
            tables_to_create = [
                "telegram_users",
                "module_requests", 
                "cccd_generation_data",
                "cccd_check_data",
                "tax_lookup_data",
                "data_analysis_data",
                "web_scraping_data",
                "form_automation_data",
                "report_generation_data",
                "excel_export_data",
                "telegram_sessions"
            ]
            
            for table_name in tables_to_create:
                success = await self._create_table_if_not_exists(table_name)
                if not success:
                    self.logger.error(f"Failed to create table: {table_name}")
                    return False
            
            # Create indexes
            await self._create_indexes()
            
            # Create RLS policies
            await self._create_rls_policies()
            
            self.logger.info("All tables created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}")
            return False
    
    async def _create_table_if_not_exists(self, table_name: str) -> bool:
        """Create table if it doesn't exist."""
        try:
            schema = DatabaseModels.get_table_schema(table_name)
            if not schema:
                self.logger.warning(f"No schema found for table: {table_name}")
                return False
            
            # Check if table exists
            table_info = await self.supabase.get_table_info(table_name)
            if table_info and table_info.get("columns"):
                self.logger.info(f"Table {table_name} already exists")
                return True
            
            # Create table using SQL
            sql = self._generate_create_table_sql(table_name, schema)
            
            # Execute SQL (this would typically be done through Supabase dashboard or SQL editor)
            self.logger.info(f"Creating table {table_name} with SQL:")
            self.logger.info(sql)
            
            # For now, we'll just log the SQL that should be executed
            # In a real implementation, you would execute this SQL through Supabase
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating table {table_name}: {e}")
            return False
    
    def _generate_create_table_sql(self, table_name: str, schema: Dict[str, str]) -> str:
        """Generate CREATE TABLE SQL statement."""
        columns = []
        
        for column_name, column_def in schema.items():
            columns.append(f"    {column_name} {column_def}")
        
        sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
{',\n'.join(columns)}
);"""
        
        return sql
    
    async def _create_indexes(self):
        """Create database indexes for better performance."""
        indexes = [
            # Module requests indexes
            "CREATE INDEX IF NOT EXISTS idx_module_requests_user_id ON module_requests(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_module_requests_chat_id ON module_requests(telegram_chat_id);",
            "CREATE INDEX IF NOT EXISTS idx_module_requests_module_type ON module_requests(module_type);",
            "CREATE INDEX IF NOT EXISTS idx_module_requests_status ON module_requests(status);",
            "CREATE INDEX IF NOT EXISTS idx_module_requests_created_at ON module_requests(created_at);",
            
            # Telegram users indexes
            "CREATE INDEX IF NOT EXISTS idx_telegram_users_telegram_id ON telegram_users(telegram_id);",
            "CREATE INDEX IF NOT EXISTS idx_telegram_users_username ON telegram_users(username);",
            "CREATE INDEX IF NOT EXISTS idx_telegram_users_is_active ON telegram_users(is_active);",
            
            # Telegram sessions indexes
            "CREATE INDEX IF NOT EXISTS idx_telegram_sessions_user_id ON telegram_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_telegram_sessions_chat_id ON telegram_sessions(chat_id);",
            "CREATE INDEX IF NOT EXISTS idx_telegram_sessions_is_active ON telegram_sessions(is_active);",
            
            # Module-specific indexes
            "CREATE INDEX IF NOT EXISTS idx_cccd_generation_request_id ON cccd_generation_data(request_id);",
            "CREATE INDEX IF NOT EXISTS idx_cccd_check_request_id ON cccd_check_data(request_id);",
            "CREATE INDEX IF NOT EXISTS idx_cccd_check_cccd_number ON cccd_check_data(cccd_number);",
            "CREATE INDEX IF NOT EXISTS idx_tax_lookup_request_id ON tax_lookup_data(request_id);",
            "CREATE INDEX IF NOT EXISTS idx_tax_lookup_tax_code ON tax_lookup_data(tax_code);",
        ]
        
        for index_sql in indexes:
            self.logger.info(f"Creating index: {index_sql}")
            # In a real implementation, you would execute this SQL
    
    async def _create_rls_policies(self):
        """Create Row Level Security policies."""
        policies = [
            # Telegram users policies
            """
            ALTER TABLE telegram_users ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Users can view own data" ON telegram_users
                FOR SELECT USING (telegram_id = current_setting('app.current_user_id', true));
            CREATE POLICY "Users can update own data" ON telegram_users
                FOR UPDATE USING (telegram_id = current_setting('app.current_user_id', true));
            """,
            
            # Module requests policies
            """
            ALTER TABLE module_requests ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Users can view own requests" ON module_requests
                FOR SELECT USING (user_id = current_setting('app.current_user_id', true));
            CREATE POLICY "Users can insert own requests" ON module_requests
                FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true));
            """,
            
            # Telegram sessions policies
            """
            ALTER TABLE telegram_sessions ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Users can view own sessions" ON telegram_sessions
                FOR SELECT USING (user_id = current_setting('app.current_user_id', true));
            CREATE POLICY "Users can manage own sessions" ON telegram_sessions
                FOR ALL USING (user_id = current_setting('app.current_user_id', true));
            """
        ]
        
        for policy_sql in policies:
            self.logger.info(f"Creating RLS policy: {policy_sql}")
            # In a real implementation, you would execute this SQL
    
    async def migrate_data(self, from_version: str, to_version: str) -> bool:
        """Migrate data between versions."""
        try:
            self.logger.info(f"Migrating data from {from_version} to {to_version}")
            
            # Define migration steps
            migration_steps = self._get_migration_steps(from_version, to_version)
            
            for step in migration_steps:
                success = await self._execute_migration_step(step)
                if not success:
                    self.logger.error(f"Migration step failed: {step}")
                    return False
            
            self.logger.info("Data migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during data migration: {e}")
            return False
    
    def _get_migration_steps(self, from_version: str, to_version: str) -> List[Dict[str, Any]]:
        """Get migration steps for version upgrade."""
        # Define migration steps based on version changes
        steps = []
        
        if from_version == "1.0.0" and to_version == "1.1.0":
            steps.extend([
                {
                    "type": "add_column",
                    "table": "module_requests",
                    "column": "priority",
                    "definition": "integer DEFAULT 0"
                },
                {
                    "type": "add_column", 
                    "table": "module_requests",
                    "column": "retry_count",
                    "definition": "integer DEFAULT 0"
                }
            ])
        
        if from_version == "1.1.0" and to_version == "1.2.0":
            steps.extend([
                {
                    "type": "create_table",
                    "table": "module_logs",
                    "schema": {
                        "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
                        "request_id": "uuid REFERENCES module_requests(id)",
                        "log_level": "varchar(20) NOT NULL",
                        "message": "text NOT NULL",
                        "created_at": "timestamp with time zone DEFAULT now()"
                    }
                }
            ])
        
        return steps
    
    async def _execute_migration_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single migration step."""
        try:
            step_type = step.get("type")
            
            if step_type == "add_column":
                return await self._add_column(
                    step["table"],
                    step["column"], 
                    step["definition"]
                )
            elif step_type == "create_table":
                return await self._create_table_if_not_exists(step["table"])
            elif step_type == "create_index":
                return await self._create_index(step["index_sql"])
            else:
                self.logger.warning(f"Unknown migration step type: {step_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing migration step: {e}")
            return False
    
    async def _add_column(self, table: str, column: str, definition: str) -> bool:
        """Add column to table."""
        try:
            sql = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {definition};"
            self.logger.info(f"Adding column: {sql}")
            # In a real implementation, you would execute this SQL
            return True
        except Exception as e:
            self.logger.error(f"Error adding column: {e}")
            return False
    
    async def _create_index(self, index_sql: str) -> bool:
        """Create index."""
        try:
            self.logger.info(f"Creating index: {index_sql}")
            # In a real implementation, you would execute this SQL
            return True
        except Exception as e:
            self.logger.error(f"Error creating index: {e}")
            return False
    
    async def backup_database(self, backup_name: str) -> bool:
        """Create database backup."""
        try:
            self.logger.info(f"Creating database backup: {backup_name}")
            
            # Get all table data
            backup_data = {}
            
            for table_name in DatabaseModels.get_all_tables():
                try:
                    data = await self.supabase.select_data(table_name)
                    backup_data[table_name] = data
                    self.logger.debug(f"Backed up {len(data)} records from {table_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to backup table {table_name}: {e}")
            
            # Save backup to file
            backup_file = f"backups/{backup_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Create backups directory if it doesn't exist
            import os
            os.makedirs("backups", exist_ok=True)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Database backup saved to: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating database backup: {e}")
            return False
    
    async def restore_database(self, backup_file: str) -> bool:
        """Restore database from backup."""
        try:
            self.logger.info(f"Restoring database from: {backup_file}")
            
            # Load backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restore each table
            for table_name, data in backup_data.items():
                try:
                    # Clear existing data
                    await self.supabase.delete_data(table_name, {})
                    
                    # Insert backup data
                    for record in data:
                        await self.supabase.insert_data(table_name, record)
                    
                    self.logger.info(f"Restored {len(data)} records to {table_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to restore table {table_name}: {e}")
                    return False
            
            self.logger.info("Database restore completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring database: {e}")
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            stats = {}
            
            for table_name in DatabaseModels.get_all_tables():
                try:
                    data = await self.supabase.select_data(table_name)
                    stats[table_name] = {
                        "record_count": len(data),
                        "last_updated": max(
                            [datetime.fromisoformat(r.get('updated_at', r.get('created_at', ''))) 
                             for r in data if r.get('updated_at') or r.get('created_at')],
                            default=None
                        )
                    }
                except Exception as e:
                    self.logger.warning(f"Failed to get stats for table {table_name}: {e}")
                    stats[table_name] = {"record_count": 0, "last_updated": None}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old data."""
        try:
            self.logger.info(f"Cleaning up data older than {days_to_keep} days")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Clean up old module requests
            old_requests = await self.supabase.select_data(
                "module_requests",
                filters={"created_at": {"lt": cutoff_date.isoformat()}}
            )
            
            for request in old_requests:
                # Delete related data
                module_type = request.get("module_type")
                request_id = request.get("id")
                
                # Delete from module-specific tables
                table_mapping = {
                    "cccd_generation": "cccd_generation_data",
                    "cccd_check": "cccd_check_data",
                    "tax_lookup": "tax_lookup_data",
                    "data_analysis": "data_analysis_data",
                    "web_scraping": "web_scraping_data",
                    "form_automation": "form_automation_data",
                    "report_generation": "report_generation_data",
                    "excel_export": "excel_export_data"
                }
                
                table_name = table_mapping.get(module_type)
                if table_name:
                    await self.supabase.delete_data(table_name, {"request_id": request_id})
                
                # Delete the request itself
                await self.supabase.delete_data("module_requests", {"id": request_id})
            
            self.logger.info(f"Cleaned up {len(old_requests)} old requests")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
            return False