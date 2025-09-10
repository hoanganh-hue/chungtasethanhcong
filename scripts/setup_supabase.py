#!/usr/bin/env python3
"""
Supabase Setup Script for OpenManus-Youtu Integrated Framework
Setup database tables, migrations, and initial configuration
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.supabase import SupabaseClient, SupabaseConfig, DatabaseMigrations
from integrations.supabase.models import DatabaseModels

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_supabase():
    """Setup Supabase database."""
    try:
        logger.info("Starting Supabase setup...")
        
        # Get configuration from environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("Missing required environment variables: SUPABASE_URL, SUPABASE_ANON_KEY")
            return False
        
        # Create Supabase client
        config = SupabaseConfig(
            url=supabase_url,
            key=supabase_key,
            service_role_key=supabase_service_key
        )
        
        client = SupabaseClient(config)
        
        # Connect to Supabase
        logger.info("Connecting to Supabase...")
        success = await client.connect()
        
        if not success:
            logger.error("Failed to connect to Supabase")
            return False
        
        logger.info("Successfully connected to Supabase")
        
        # Create migrations manager
        migrations = DatabaseMigrations(client)
        
        # Create all tables
        logger.info("Creating database tables...")
        success = await migrations.create_all_tables()
        
        if not success:
            logger.error("Failed to create database tables")
            return False
        
        logger.info("Database tables created successfully")
        
        # Get database statistics
        logger.info("Getting database statistics...")
        stats = await migrations.get_database_stats()
        
        logger.info("Database statistics:")
        for table_name, table_stats in stats.items():
            logger.info(f"  {table_name}: {table_stats['record_count']} records")
        
        # Test database operations
        logger.info("Testing database operations...")
        await test_database_operations(client)
        
        logger.info("Supabase setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during Supabase setup: {e}")
        return False
    finally:
        if 'client' in locals():
            await client.disconnect()


async def test_database_operations(client: SupabaseClient):
    """Test basic database operations."""
    try:
        # Test inserting a test user
        test_user = {
            "telegram_id": "test_user_123",
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
            "is_bot": False,
            "language_code": "vi"
        }
        
        logger.info("Testing user insertion...")
        result = await client.insert_data("telegram_users", test_user)
        
        if result:
            logger.info(f"Test user inserted with ID: {result.get('id')}")
            
            # Test updating the user
            logger.info("Testing user update...")
            update_data = {"last_activity": "2025-01-10T10:00:00Z"}
            updated = await client.update_data(
                "telegram_users",
                update_data,
                {"telegram_id": "test_user_123"}
            )
            
            if updated:
                logger.info("Test user updated successfully")
            
            # Test selecting the user
            logger.info("Testing user selection...")
            users = await client.select_data(
                "telegram_users",
                filters={"telegram_id": "test_user_123"}
            )
            
            if users:
                logger.info(f"Test user retrieved: {users[0]['username']}")
            
            # Test deleting the user
            logger.info("Testing user deletion...")
            deleted = await client.delete_data(
                "telegram_users",
                {"telegram_id": "test_user_123"}
            )
            
            if deleted:
                logger.info("Test user deleted successfully")
        
        # Test module request insertion
        logger.info("Testing module request insertion...")
        test_request = {
            "module_type": "cccd_generation",
            "user_id": "test_user_123",
            "telegram_chat_id": "test_chat_123",
            "request_data": {
                "province": "Hưng Yên",
                "gender": "nữ",
                "birth_year_range": "1965-1975",
                "quantity": 100
            },
            "status": "pending"
        }
        
        result = await client.insert_data("module_requests", test_request)
        
        if result:
            logger.info(f"Test module request inserted with ID: {result.get('id')}")
            
            # Clean up test data
            await client.delete_data("module_requests", {"id": result.get('id')})
            logger.info("Test module request cleaned up")
        
        logger.info("Database operations test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database operations test: {e}")


async def create_sample_data():
    """Create sample data for testing."""
    try:
        logger.info("Creating sample data...")
        
        # Get configuration
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("Missing required environment variables")
            return False
        
        config = SupabaseConfig(url=supabase_url, key=supabase_key)
        client = SupabaseClient(config)
        
        success = await client.connect()
        if not success:
            logger.error("Failed to connect to Supabase")
            return False
        
        # Create sample users
        sample_users = [
            {
                "telegram_id": "user_001",
                "username": "admin_user",
                "first_name": "Admin",
                "last_name": "User",
                "is_bot": False,
                "language_code": "vi"
            },
            {
                "telegram_id": "user_002", 
                "username": "test_user",
                "first_name": "Test",
                "last_name": "User",
                "is_bot": False,
                "language_code": "vi"
            }
        ]
        
        for user in sample_users:
            await client.insert_data("telegram_users", user)
            logger.info(f"Created sample user: {user['username']}")
        
        # Create sample module requests
        sample_requests = [
            {
                "module_type": "cccd_generation",
                "user_id": "user_001",
                "telegram_chat_id": "chat_001",
                "request_data": {
                    "province": "Hưng Yên",
                    "gender": "nữ",
                    "birth_year_range": "1965-1975",
                    "quantity": 1000
                },
                "status": "completed"
            },
            {
                "module_type": "cccd_check",
                "user_id": "user_002",
                "telegram_chat_id": "chat_002",
                "request_data": {
                    "cccd_number": "031089011929"
                },
                "status": "completed"
            }
        ]
        
        for request in sample_requests:
            await client.insert_data("module_requests", request)
            logger.info(f"Created sample request: {request['module_type']}")
        
        await client.disconnect()
        logger.info("Sample data created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return False


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Supabase setup script")
    parser.add_argument("--create-sample-data", action="store_true", 
                       help="Create sample data after setup")
    parser.add_argument("--test-only", action="store_true",
                       help="Only run database tests")
    
    args = parser.parse_args()
    
    if args.test_only:
        # Only run tests
        logger.info("Running database tests only...")
        success = await test_database_operations(None)
        return success
    
    # Run full setup
    success = await setup_supabase()
    
    if success and args.create_sample_data:
        logger.info("Creating sample data...")
        await create_sample_data()
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)