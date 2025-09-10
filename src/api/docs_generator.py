"""
API Documentation Generator for OpenManus-Youtu Integrated Framework
Automated generation of comprehensive API documentation
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class APIDocumentationGenerator:
    """Generate comprehensive API documentation."""
    
    def __init__(self):
        self.api_info = {
            "title": "OpenManus-Youtu Integrated Framework API",
            "version": "1.0.0",
            "description": "Advanced AI Agent Framework with Multi-Agent Orchestration, Communication, and Comprehensive Tools",
            "contact": {
                "name": "OpenManus-Youtu Team",
                "email": "support@openmanus-youtu.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        }
        
        self.base_url = "http://localhost:8000"
        self.endpoints = []
        self.models = []
        self.examples = {}
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": self.api_info,
            "servers": [
                {
                    "url": self.base_url,
                    "description": "Development server"
                }
            ],
            "paths": self._generate_paths(),
            "components": {
                "schemas": self._generate_schemas(),
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [
                {
                    "BearerAuth": []
                }
            ],
            "tags": self._generate_tags()
        }
        
        return openapi_spec
    
    def _generate_paths(self) -> Dict[str, Any]:
        """Generate API paths documentation."""
        paths = {
            # Health and Status
            "/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Health Check",
                    "description": "Check API health status",
                    "responses": {
                        "200": {
                            "description": "API is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/health/detailed": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Detailed Health Check",
                    "description": "Get detailed health status of all components",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Detailed health information",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DetailedHealthResponse"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Agent Management
            "/agents": {
                "get": {
                    "tags": ["Agents"],
                    "summary": "List Agents",
                    "description": "Get list of all active agents",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "List of agents",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AgentListResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/agents/create": {
                "post": {
                    "tags": ["Agents"],
                    "summary": "Create Agent",
                    "description": "Create a new AI agent",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AgentCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Agent created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AgentResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/agents/{agent_id}": {
                "get": {
                    "tags": ["Agents"],
                    "summary": "Get Agent",
                    "description": "Get agent information by ID",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "agent_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Agent ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Agent information",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AgentResponse"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "tags": ["Agents"],
                    "summary": "Delete Agent",
                    "description": "Delete an agent",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "agent_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Agent ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Agent deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Agent Communication
            "/agents/{agent_id}/message": {
                "post": {
                    "tags": ["Communication"],
                    "summary": "Send Message to Agent",
                    "description": "Send a message to a specific agent",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "agent_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Agent ID"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AgentMessageRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Message sent successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MessageResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/agents/{agent_id}/conversation": {
                "get": {
                    "tags": ["Communication"],
                    "summary": "Get Agent Conversation",
                    "description": "Get conversation history with an agent",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "agent_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Agent ID"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 50},
                            "description": "Number of messages to retrieve"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Conversation history",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ConversationResponse"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Orchestration
            "/orchestration/execute": {
                "post": {
                    "tags": ["Orchestration"],
                    "summary": "Execute Orchestration",
                    "description": "Execute multi-agent orchestration plan",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OrchestrationRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Orchestration executed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrchestrationResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/orchestration/status": {
                "get": {
                    "tags": ["Orchestration"],
                    "summary": "Get Orchestration Status",
                    "description": "Get orchestration system status",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Orchestration status",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrchestrationStatusResponse"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Memory Management
            "/memory/{agent_id}/store": {
                "post": {
                    "tags": ["Memory"],
                    "summary": "Store Memory",
                    "description": "Store memory for an agent",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "agent_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Agent ID"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MemoryStoreRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Memory stored successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MemoryResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/memory/{agent_id}/search": {
                "get": {
                    "tags": ["Memory"],
                    "summary": "Search Memory",
                    "description": "Search agent memories",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "agent_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Agent ID"
                        },
                        {
                            "name": "query",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Search query"
                        },
                        {
                            "name": "memory_types",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Comma-separated memory types"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 10},
                            "description": "Maximum results"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Search results",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MemorySearchResponse"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Tools
            "/tools/execute": {
                "post": {
                    "tags": ["Tools"],
                    "summary": "Execute Tool",
                    "description": "Execute tool operation",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ToolRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Tool executed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ToolResponse"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Streaming
            "/stream/agent-activity": {
                "get": {
                    "tags": ["Streaming"],
                    "summary": "Stream Agent Activity",
                    "description": "Stream real-time agent activity",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Real-time agent activity stream",
                            "content": {
                                "text/plain": {
                                    "schema": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "/stream/system-metrics": {
                "get": {
                    "tags": ["Streaming"],
                    "summary": "Stream System Metrics",
                    "description": "Stream real-time system metrics",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Real-time system metrics stream",
                            "content": {
                                "text/plain": {
                                    "schema": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            
            # Analytics
            "/analytics/performance": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Performance Analytics",
                    "description": "Get performance analytics",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "time_range",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "24h"},
                            "description": "Time range (1h, 24h, 7d, 30d)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Performance analytics",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AnalyticsResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/analytics/usage": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Usage Analytics",
                    "description": "Get usage analytics",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "time_range",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "7d"},
                            "description": "Time range (1h, 24h, 7d, 30d)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Usage analytics",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UsageAnalyticsResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return paths
    
    def _generate_schemas(self) -> Dict[str, Any]:
        """Generate API schemas."""
        schemas = {
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "version": {"type": "string", "example": "1.0.0"}
                }
            },
            "DetailedHealthResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "health": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string", "format": "date-time"},
                            "overall_status": {"type": "string", "example": "healthy"},
                            "components": {"type": "object"},
                            "system_info": {"type": "object"}
                        }
                    }
                }
            },
            "AgentCreateRequest": {
                "type": "object",
                "required": ["name", "agent_type"],
                "properties": {
                    "name": {"type": "string", "example": "My CCCD Agent"},
                    "agent_type": {
                        "type": "string",
                        "enum": ["cccd", "tax", "data_analysis", "web_automation", "general"],
                        "example": "cccd"
                    },
                    "description": {"type": "string", "example": "Agent for CCCD processing"},
                    "config": {"type": "object", "additionalProperties": True}
                }
            },
            "AgentResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "agent_id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "status": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "AgentListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "agents": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/AgentInfo"}
                    },
                    "total_count": {"type": "integer"}
                }
            },
            "AgentInfo": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "status": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "last_activity": {"type": "string", "format": "date-time"}
                }
            },
            "AgentMessageRequest": {
                "type": "object",
                "required": ["message"],
                "properties": {
                    "message": {"type": "string", "example": "Hello, how are you?"},
                    "context": {"type": "object", "additionalProperties": True}
                }
            },
            "MessageResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "agent_id": {"type": "string"},
                    "message": {"type": "string"},
                    "response": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "ConversationResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "agent_id": {"type": "string"},
                    "conversation": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "total_messages": {"type": "integer"}
                }
            },
            "OrchestrationRequest": {
                "type": "object",
                "required": ["tasks"],
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["sequential", "parallel", "pipeline"],
                        "default": "sequential"
                    },
                    "max_concurrent": {"type": "integer", "default": 5}
                }
            },
            "OrchestrationResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "plan_id": {"type": "string"},
                    "result": {"type": "object"},
                    "execution_time": {"type": "number"}
                }
            },
            "OrchestrationStatusResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "status": {"type": "object"}
                }
            },
            "MemoryStoreRequest": {
                "type": "object",
                "required": ["memory_type", "content"],
                "properties": {
                    "memory_type": {
                        "type": "string",
                        "enum": ["conversation", "knowledge", "experience", "context", "preference", "skill", "fact", "procedure"],
                        "example": "knowledge"
                    },
                    "content": {"type": "object", "additionalProperties": True},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["important", "work"]
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "critical"],
                        "default": "normal"
                    }
                }
            },
            "MemoryResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "memory_id": {"type": "string"},
                    "agent_id": {"type": "string"},
                    "memory_type": {"type": "string"},
                    "stored_at": {"type": "string", "format": "date-time"}
                }
            },
            "MemorySearchResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "agent_id": {"type": "string"},
                    "query": {"type": "string"},
                    "memories": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "total_found": {"type": "integer"}
                }
            },
            "ToolRequest": {
                "type": "object",
                "required": ["tool_type", "operation"],
                "properties": {
                    "tool_type": {
                        "type": "string",
                        "enum": ["pdf", "image", "email", "calendar"],
                        "example": "pdf"
                    },
                    "operation": {
                        "type": "string",
                        "example": "extract_text"
                    },
                    "parameters": {"type": "object", "additionalProperties": True}
                }
            },
            "ToolResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "tool_type": {"type": "string"},
                    "operation": {"type": "string"},
                    "result": {"type": "object"},
                    "executed_at": {"type": "string", "format": "date-time"}
                }
            },
            "AnalyticsResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "analytics": {"type": "object"}
                }
            },
            "UsageAnalyticsResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "usage": {"type": "object"}
                }
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "detail": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        }
        
        return schemas
    
    def _generate_tags(self) -> List[Dict[str, str]]:
        """Generate API tags."""
        return [
            {
                "name": "Health",
                "description": "Health check and system status endpoints"
            },
            {
                "name": "Agents",
                "description": "AI agent management and operations"
            },
            {
                "name": "Communication",
                "description": "Agent communication and messaging"
            },
            {
                "name": "Orchestration",
                "description": "Multi-agent orchestration and workflow management"
            },
            {
                "name": "Memory",
                "description": "Agent memory management and retrieval"
            },
            {
                "name": "Tools",
                "description": "Tool execution and operations"
            },
            {
                "name": "Streaming",
                "description": "Real-time data streaming endpoints"
            },
            {
                "name": "Analytics",
                "description": "Performance and usage analytics"
            }
        ]
    
    def generate_markdown_docs(self) -> str:
        """Generate Markdown documentation."""
        openapi_spec = self.generate_openapi_spec()
        
        md_content = f"""# {self.api_info['title']}

**Version:** {self.api_info['version']}  
**Description:** {self.api_info['description']}  
**Base URL:** {self.base_url}

## Table of Contents

- [Authentication](#authentication)
- [Health & Status](#health--status)
- [Agent Management](#agent-management)
- [Communication](#communication)
- [Orchestration](#orchestration)
- [Memory Management](#memory-management)
- [Tools](#tools)
- [Streaming](#streaming)
- [Analytics](#analytics)
- [Error Handling](#error-handling)

## Authentication

All API endpoints require authentication using Bearer token:

```bash
Authorization: Bearer your_token_here
```

## Health & Status

### Health Check
```http
GET /health
```

Returns basic health status of the API.

**Response:**
```json
{{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}}
```

### Detailed Health Check
```http
GET /health/detailed
```

Returns detailed health status of all system components.

## Agent Management

### List Agents
```http
GET /agents
```

Get list of all active agents.

**Response:**
```json
{{
  "success": true,
  "agents": [
    {{
      "agent_id": "agent_123",
      "name": "CCCD Agent",
      "type": "cccd",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }}
  ],
  "total_count": 1
}}
```

### Create Agent
```http
POST /agents/create
```

Create a new AI agent.

**Request Body:**
```json
{{
  "name": "My CCCD Agent",
  "agent_type": "cccd",
  "description": "Agent for CCCD processing",
  "config": {{}}
}}
```

**Available Agent Types:**
- `cccd` - CCCD processing agent
- `tax` - Tax lookup agent
- `data_analysis` - Data analysis agent
- `web_automation` - Web automation agent
- `general` - General purpose agent

### Get Agent
```http
GET /agents/{{agent_id}}
```

Get detailed information about a specific agent.

### Delete Agent
```http
DELETE /agents/{{agent_id}}
```

Delete an agent.

## Communication

### Send Message to Agent
```http
POST /agents/{{agent_id}}/message
```

Send a message to a specific agent.

**Request Body:**
```json
{{
  "message": "Hello, how are you?",
  "context": {{}}
}}
```

### Get Agent Conversation
```http
GET /agents/{{agent_id}}/conversation?limit=50
```

Get conversation history with an agent.

## Orchestration

### Execute Orchestration
```http
POST /orchestration/execute
```

Execute multi-agent orchestration plan.

**Request Body:**
```json
{{
  "tasks": [
    {{
      "agent_id": "agent_123",
      "task_type": "process_data",
      "parameters": {{"data": "example"}}
    }}
  ],
  "mode": "sequential",
  "max_concurrent": 5
}}
```

**Orchestration Modes:**
- `sequential` - Execute tasks one after another
- `parallel` - Execute tasks simultaneously
- `pipeline` - Pass output of one task as input to next

### Get Orchestration Status
```http
GET /orchestration/status
```

Get orchestration system status.

## Memory Management

### Store Memory
```http
POST /memory/{{agent_id}}/store
```

Store memory for an agent.

**Request Body:**
```json
{{
  "memory_type": "knowledge",
  "content": {{"fact": "The sky is blue"}},
  "tags": ["important", "general"],
  "priority": "normal"
}}
```

**Memory Types:**
- `conversation` - Conversation history
- `knowledge` - General knowledge
- `experience` - Learning experiences
- `context` - Contextual information
- `preference` - User preferences
- `skill` - Learned skills
- `fact` - Facts and information
- `procedure` - Step-by-step procedures

### Search Memory
```http
GET /memory/{{agent_id}}/search?query=sky&memory_types=knowledge&limit=10
```

Search agent memories.

## Tools

### Execute Tool
```http
POST /tools/execute
```

Execute tool operation.

**Request Body:**
```json
{{
  "tool_type": "pdf",
  "operation": "extract_text",
  "parameters": {{
    "file_path": "/path/to/document.pdf"
  }}
}}
```

**Available Tools:**
- **PDF Tools:** `extract_text`, `get_info`, `extract_images`, `merge`, `split`
- **Image Tools:** `resize`, `convert`, `get_info`, `apply_filters`
- **Email Tools:** `send`, `send_report`
- **Calendar Tools:** `create_event`, `list_events`, `get_upcoming`

## Streaming

### Stream Agent Activity
```http
GET /stream/agent-activity
```

Stream real-time agent activity updates.

### Stream System Metrics
```http
GET /stream/system-metrics
```

Stream real-time system metrics.

## Analytics

### Performance Analytics
```http
GET /analytics/performance?time_range=24h
```

Get performance analytics for specified time range.

### Usage Analytics
```http
GET /analytics/usage?time_range=7d
```

Get usage analytics for specified time range.

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

**Error Response Format:**
```json
{{
  "error": "Error message",
  "detail": "Detailed error description",
  "timestamp": "2024-01-01T00:00:00Z"
}}
```

## Examples

### Complete Workflow Example

1. **Create an agent:**
```bash
curl -X POST "{self.base_url}/agents/create" \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "My CCCD Agent",
    "agent_type": "cccd",
    "description": "Agent for CCCD processing"
  }}'
```

2. **Send a message to the agent:**
```bash
curl -X POST "{self.base_url}/agents/agent_123/message" \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "message": "Generate 100 CCCD for Hanoi",
    "context": {{"location": "Hanoi", "count": 100}}
  }}'
```

3. **Store memory for the agent:**
```bash
curl -X POST "{self.base_url}/memory/agent_123/store" \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "memory_type": "knowledge",
    "content": {{"preference": "Hanoi location"}},
    "tags": ["location", "preference"]
  }}'
```

4. **Execute a tool:**
```bash
curl -X POST "{self.base_url}/tools/execute" \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "tool_type": "pdf",
    "operation": "extract_text",
    "parameters": {{"file_path": "/path/to/document.pdf"}}
  }}'
```

---

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return md_content
    
    def save_documentation(self, output_dir: str = "docs"):
        """Save documentation files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save OpenAPI spec
        openapi_spec = self.generate_openapi_spec()
        with open(output_path / "openapi.json", "w") as f:
            json.dump(openapi_spec, f, indent=2)
        
        with open(output_path / "openapi.yaml", "w") as f:
            yaml.dump(openapi_spec, f, default_flow_style=False)
        
        # Save Markdown docs
        md_content = self.generate_markdown_docs()
        with open(output_path / "API_Documentation.md", "w") as f:
            f.write(md_content)
        
        logger.info(f"Documentation saved to {output_path}")
        return output_path

# Global documentation generator
docs_generator = APIDocumentationGenerator()

# Convenience functions
def generate_api_docs(output_dir: str = "docs") -> Path:
    """Generate and save API documentation."""
    return docs_generator.save_documentation(output_dir)

def get_openapi_spec() -> Dict[str, Any]:
    """Get OpenAPI specification."""
    return docs_generator.generate_openapi_spec()

def get_markdown_docs() -> str:
    """Get Markdown documentation."""
    return docs_generator.generate_markdown_docs()

if __name__ == "__main__":
    # Generate documentation
    output_path = generate_api_docs()
    print(f"API documentation generated and saved to: {output_path}")
    print("Files created:")
    print("- openapi.json (OpenAPI 3.0 specification)")
    print("- openapi.yaml (OpenAPI 3.0 specification in YAML)")
    print("- API_Documentation.md (Markdown documentation)")