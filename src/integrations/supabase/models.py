"""
Database Models for OpenManus-Youtu Integrated Framework
Supabase table schemas and data models for module features
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json


class ModuleType(Enum):
    """Module type enumeration."""
    CCCD_GENERATION = "cccd_generation"
    CCCD_CHECK = "cccd_check"
    TAX_LOOKUP = "tax_lookup"
    DATA_ANALYSIS = "data_analysis"
    WEB_SCRAPING = "web_scraping"
    FORM_AUTOMATION = "form_automation"
    REPORT_GENERATION = "report_generation"
    EXCEL_EXPORT = "excel_export"


class RequestStatus(Enum):
    """Request status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BaseModel:
    """Base model for all database entities."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary."""
        # Convert ISO strings back to datetime objects
        for key, value in data.items():
            if key in ['created_at', 'updated_at'] and isinstance(value, str):
                try:
                    data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    pass
        return cls(**data)


@dataclass
class ModuleRequest(BaseModel):
    """Model for module requests."""
    module_type: str
    user_id: str
    telegram_chat_id: str
    request_data: Dict[str, Any]
    status: str = RequestStatus.PENDING.value
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['request_data'] = json.dumps(self.request_data) if isinstance(self.request_data, dict) else self.request_data
        data['response_data'] = json.dumps(self.response_data) if isinstance(self.response_data, dict) else self.response_data
        return data


@dataclass
class CCCDGenerationData(BaseModel):
    """Model for CCCD generation data."""
    request_id: str
    province: str
    gender: str
    birth_year_range: str
    quantity: int
    generated_cccds: List[str]
    generation_time: float
    success_count: int
    failure_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['generated_cccds'] = json.dumps(self.generated_cccds)
        return data


@dataclass
class CCCDCheckData(BaseModel):
    """Model for CCCD check data."""
    request_id: str
    cccd_number: str
    check_result: Dict[str, Any]
    check_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['check_result'] = json.dumps(self.check_result)
        return data


@dataclass
class TaxLookupData(BaseModel):
    """Model for tax lookup data."""
    request_id: str
    tax_code: str
    lookup_result: Dict[str, Any]
    lookup_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['lookup_result'] = json.dumps(self.lookup_result)
        return data


@dataclass
class DataAnalysisData(BaseModel):
    """Model for data analysis data."""
    request_id: str
    analysis_type: str
    input_data: Dict[str, Any]
    analysis_result: Dict[str, Any]
    analysis_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['input_data'] = json.dumps(self.input_data)
        data['analysis_result'] = json.dumps(self.analysis_result)
        return data


@dataclass
class WebScrapingData(BaseModel):
    """Model for web scraping data."""
    request_id: str
    target_url: str
    scraping_config: Dict[str, Any]
    scraped_data: Dict[str, Any]
    scraping_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['scraping_config'] = json.dumps(self.scraping_config)
        data['scraped_data'] = json.dumps(self.scraped_data)
        return data


@dataclass
class FormAutomationData(BaseModel):
    """Model for form automation data."""
    request_id: str
    form_url: str
    form_data: Dict[str, Any]
    automation_result: Dict[str, Any]
    automation_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['form_data'] = json.dumps(self.form_data)
        data['automation_result'] = json.dumps(self.automation_result)
        return data


@dataclass
class ReportGenerationData(BaseModel):
    """Model for report generation data."""
    request_id: str
    report_type: str
    report_data: Dict[str, Any]
    generated_report: Dict[str, Any]
    generation_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['report_data'] = json.dumps(self.report_data)
        data['generated_report'] = json.dumps(self.generated_report)
        return data


@dataclass
class ExcelExportData(BaseModel):
    """Model for Excel export data."""
    request_id: str
    export_data: Dict[str, Any]
    file_path: str
    file_size: int
    export_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['export_data'] = json.dumps(self.export_data)
        return data


@dataclass
class TelegramUser(BaseModel):
    """Model for Telegram user data."""
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_bot: bool = False
    language_code: Optional[str] = None
    is_active: bool = True
    last_activity: Optional[datetime] = None


@dataclass
class TelegramSession(BaseModel):
    """Model for Telegram session data."""
    user_id: str
    chat_id: str
    session_data: Dict[str, Any]
    is_active: bool = True
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON serialization."""
        data = super().to_dict()
        data['session_data'] = json.dumps(self.session_data)
        return data


class DatabaseModels:
    """Database models manager."""
    
    # Table schemas
    TABLE_SCHEMAS = {
        "module_requests": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "module_type": "varchar(50) NOT NULL",
            "user_id": "varchar(100) NOT NULL",
            "telegram_chat_id": "varchar(100) NOT NULL",
            "request_data": "jsonb NOT NULL",
            "status": "varchar(20) DEFAULT 'pending'",
            "response_data": "jsonb",
            "error_message": "text",
            "processing_time": "float",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "cccd_generation_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "province": "varchar(100) NOT NULL",
            "gender": "varchar(10) NOT NULL",
            "birth_year_range": "varchar(20) NOT NULL",
            "quantity": "integer NOT NULL",
            "generated_cccds": "jsonb NOT NULL",
            "generation_time": "float NOT NULL",
            "success_count": "integer NOT NULL",
            "failure_count": "integer NOT NULL",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "cccd_check_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "cccd_number": "varchar(20) NOT NULL",
            "check_result": "jsonb NOT NULL",
            "check_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "tax_lookup_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "tax_code": "varchar(20) NOT NULL",
            "lookup_result": "jsonb NOT NULL",
            "lookup_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "data_analysis_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "analysis_type": "varchar(50) NOT NULL",
            "input_data": "jsonb NOT NULL",
            "analysis_result": "jsonb NOT NULL",
            "analysis_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "web_scraping_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "target_url": "text NOT NULL",
            "scraping_config": "jsonb NOT NULL",
            "scraped_data": "jsonb NOT NULL",
            "scraping_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "form_automation_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "form_url": "text NOT NULL",
            "form_data": "jsonb NOT NULL",
            "automation_result": "jsonb NOT NULL",
            "automation_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "report_generation_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "report_type": "varchar(50) NOT NULL",
            "report_data": "jsonb NOT NULL",
            "generated_report": "jsonb NOT NULL",
            "generation_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "excel_export_data": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "request_id": "uuid REFERENCES module_requests(id)",
            "export_data": "jsonb NOT NULL",
            "file_path": "text NOT NULL",
            "file_size": "integer NOT NULL",
            "export_time": "float NOT NULL",
            "success": "boolean NOT NULL",
            "error_message": "text",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "telegram_users": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "telegram_id": "varchar(100) UNIQUE NOT NULL",
            "username": "varchar(100)",
            "first_name": "varchar(100)",
            "last_name": "varchar(100)",
            "is_bot": "boolean DEFAULT false",
            "language_code": "varchar(10)",
            "is_active": "boolean DEFAULT true",
            "last_activity": "timestamp with time zone",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        },
        "telegram_sessions": {
            "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
            "user_id": "uuid REFERENCES telegram_users(id)",
            "chat_id": "varchar(100) NOT NULL",
            "session_data": "jsonb NOT NULL",
            "is_active": "boolean DEFAULT true",
            "expires_at": "timestamp with time zone",
            "created_at": "timestamp with time zone DEFAULT now()",
            "updated_at": "timestamp with time zone DEFAULT now()"
        }
    }
    
    # Model mappings
    MODEL_MAPPINGS = {
        "module_requests": ModuleRequest,
        "cccd_generation_data": CCCDGenerationData,
        "cccd_check_data": CCCDCheckData,
        "tax_lookup_data": TaxLookupData,
        "data_analysis_data": DataAnalysisData,
        "web_scraping_data": WebScrapingData,
        "form_automation_data": FormAutomationData,
        "report_generation_data": ReportGenerationData,
        "excel_export_data": ExcelExportData,
        "telegram_users": TelegramUser,
        "telegram_sessions": TelegramSession
    }
    
    @classmethod
    def get_table_schema(cls, table_name: str) -> Dict[str, str]:
        """Get table schema."""
        return cls.TABLE_SCHEMAS.get(table_name, {})
    
    @classmethod
    def get_model_class(cls, table_name: str):
        """Get model class for table."""
        return cls.MODEL_MAPPINGS.get(table_name)
    
    @classmethod
    def get_all_tables(cls) -> List[str]:
        """Get all table names."""
        return list(cls.TABLE_SCHEMAS.keys())
    
    @classmethod
    def get_module_tables(cls) -> List[str]:
        """Get module-specific table names."""
        return [
            "cccd_generation_data",
            "cccd_check_data", 
            "tax_lookup_data",
            "data_analysis_data",
            "web_scraping_data",
            "form_automation_data",
            "report_generation_data",
            "excel_export_data"
        ]
    
    @classmethod
    def get_telegram_tables(cls) -> List[str]:
        """Get Telegram-specific table names."""
        return ["telegram_users", "telegram_sessions"]