# 🔧 Tools API Reference

## Overview

The OpenManus-Youtu Integrated Framework provides a comprehensive set of tools organized into 8 main categories. Each tool follows a consistent interface and provides specific functionality for different use cases.

## Tool Categories

### 1. 🌐 Web Tools
Tools for web automation, scraping, and browser interactions.

### 2. 🔍 Search Tools
Tools for web search, academic search, and information retrieval.

### 3. 📊 Analysis Tools
Tools for data analysis, statistical analysis, and report generation.

### 4. 🗄️ Data Tools
Tools for data processing, cleaning, transformation, and validation.

### 5. 📁 File Tools
Tools for file operations, format conversion, and document processing.

### 6. 🤖 Automation Tools
Tools for workflow automation, task scheduling, and process management.

### 7. 📧 Communication Tools
Tools for email, messaging, notifications, and team communication.

### 8. 🖥️ System Tools
Tools for system monitoring, resource management, and process control.

---

## Base Tool Interface

All tools inherit from `BaseTool` and implement the following interface:

```python
class BaseTool(ABC):
    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        pass
    
    @abstractmethod
    def _get_definition(self) -> ToolDefinition:
        """Get tool definition."""
        pass
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """Execute the tool implementation."""
        pass
```

### Tool Metadata

```python
@dataclass
class ToolMetadata:
    name: str
    description: str
    category: ToolCategory
    version: str
    author: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    requirements: Optional[Dict[str, Any]] = None
```

### Tool Definition

```python
@dataclass
class ToolDefinition:
    metadata: ToolMetadata
    parameters: Dict[str, ToolParameter]
    return_type: Type
    examples: Optional[List[Dict[str, Any]]] = None
    error_codes: Optional[Dict[str, str]] = None
```

---

## 🌐 Web Tools

### PlaywrightBrowserTool

**Description:** Browser automation tool using Playwright

**Category:** `ToolCategory.WEB`

**Parameters:**
- `action` (str, required): Browser action to perform
  - Choices: `["navigate", "click", "type", "screenshot", "evaluate", "wait"]`
- `url` (str, optional): URL to navigate to
- `selector` (str, optional): CSS selector for element
- `text` (str, optional): Text to type or search for
- `timeout` (int, optional): Timeout in milliseconds (default: 30000)
- `headless` (bool, optional): Run browser in headless mode (default: True)

**Example:**
```python
tool = PlaywrightBrowserTool()
result = await tool.execute(
    action="navigate",
    url="https://example.com",
    headless=True
)
```

### WebScrapingTool

**Description:** Web scraping and data extraction tool

**Category:** `ToolCategory.WEB`

**Parameters:**
- `url` (str, required): URL to scrape
- `selectors` (dict, required): CSS selectors for data extraction
- `wait_time` (int, optional): Wait time in seconds (default: 2)
- `headers` (dict, optional): HTTP headers to send
- `follow_redirects` (bool, optional): Follow HTTP redirects (default: True)

**Example:**
```python
tool = WebScrapingTool()
result = await tool.execute(
    url="https://example.com",
    selectors={"title": "h1", "links": "a", "content": "p"}
)
```

### FormAutomationTool

**Description:** Form automation and submission tool

**Category:** `ToolCategory.WEB`

**Parameters:**
- `form_data` (dict, required): Form field data to fill
- `submit` (bool, optional): Whether to submit the form (default: True)
- `submit_selector` (str, optional): CSS selector for submit button
- `validation` (bool, optional): Validate form before submission (default: True)
- `timeout` (int, optional): Timeout in milliseconds (default: 10000)

**Example:**
```python
tool = FormAutomationTool()
result = await tool.execute(
    form_data={"name": "John Doe", "email": "john@example.com"},
    submit=True
)
```

### ScreenshotCaptureTool

**Description:** Screenshot capture tool for web pages

**Category:** `ToolCategory.WEB`

**Parameters:**
- `url` (str, required): URL to capture
- `filename` (str, optional): Screenshot filename
- `full_page` (bool, optional): Capture full page (default: False)
- `viewport` (dict, optional): Viewport dimensions (default: {"width": 1920, "height": 1080})
- `quality` (int, optional): Image quality 0-100 (default: 90)

**Example:**
```python
tool = ScreenshotCaptureTool()
result = await tool.execute(
    url="https://example.com",
    filename="example_page.png",
    full_page=True
)
```

### ElementInteractionTool

**Description:** Web page element interaction tool

**Category:** `ToolCategory.WEB`

**Parameters:**
- `selector` (str, required): CSS selector for element
- `action` (str, required): Interaction action
  - Choices: `["click", "hover", "double_click", "right_click", "focus", "blur", "scroll"]`
- `text` (str, optional): Text to type (for input elements)
- `wait_for` (str, optional): Wait for element state
- `timeout` (int, optional): Timeout in milliseconds (default: 5000)

**Example:**
```python
tool = ElementInteractionTool()
result = await tool.execute(
    selector="button.submit",
    action="click",
    timeout=10000
)
```

---

## 🔍 Search Tools

### WebSearchTool

**Description:** General web search tool

**Category:** `ToolCategory.RESEARCH`

**Parameters:**
- `query` (str, required): Search query
- `max_results` (int, optional): Maximum number of results (default: 10)
- `language` (str, optional): Search language (default: "en")
- `region` (str, optional): Search region (default: "us")
- `safe_search` (bool, optional): Enable safe search (default: True)

**Example:**
```python
tool = WebSearchTool()
result = await tool.execute(
    query="artificial intelligence machine learning",
    max_results=5
)
```

### GoogleSearchTool

**Description:** Google search tool with advanced features

**Category:** `ToolCategory.RESEARCH`

**Parameters:**
- `query` (str, required): Google search query
- `max_results` (int, optional): Maximum number of results (default: 10)
- `search_type` (str, optional): Type of search (default: "web")
- `date_restrict` (str, optional): Date restriction for results
- `exact_terms` (str, optional): Exact terms to search for

**Example:**
```python
tool = GoogleSearchTool()
result = await tool.execute(
    query="machine learning algorithms",
    search_type="web",
    max_results=5
)
```

### BingSearchTool

**Description:** Bing search tool

**Category:** `ToolCategory.RESEARCH`

**Parameters:**
- `query` (str, required): Bing search query
- `max_results` (int, optional): Maximum number of results (default: 10)
- `market` (str, optional): Market for search results (default: "en-US")
- `safesearch` (str, optional): Safe search setting (default: "Moderate")

**Example:**
```python
tool = BingSearchTool()
result = await tool.execute(
    query="artificial intelligence trends",
    market="en-US"
)
```

### DuckDuckGoSearchTool

**Description:** DuckDuckGo search tool (privacy-focused)

**Category:** `ToolCategory.RESEARCH`

**Parameters:**
- `query` (str, required): DuckDuckGo search query
- `max_results` (int, optional): Maximum number of results (default: 10)
- `region` (str, optional): Search region (default: "us-en")
- `safe_search` (bool, optional): Enable safe search (default: True)

**Example:**
```python
tool = DuckDuckGoSearchTool()
result = await tool.execute(
    query="privacy-focused search engine",
    region="us-en"
)
```

### AcademicSearchTool

**Description:** Academic and scholarly search tool

**Category:** `ToolCategory.RESEARCH`

**Parameters:**
- `query` (str, required): Academic search query
- `max_results` (int, optional): Maximum number of results (default: 10)
- `database` (str, optional): Academic database to search (default: "all")
- `year_from` (int, optional): Start year for search
- `year_to` (int, optional): End year for search
- `publication_type` (str, optional): Type of publication (default: "all")

**Example:**
```python
tool = AcademicSearchTool()
result = await tool.execute(
    query="deep learning neural networks",
    database="arxiv",
    year_from=2020
)
```

---

## 📊 Analysis Tools

### DataAnalysisTool

**Description:** General data analysis tool

**Category:** `ToolCategory.ANALYSIS`

**Parameters:**
- `data` (str, required): Data to analyze (JSON string or file path)
- `analysis_type` (str, required): Type of analysis to perform
  - Choices: `["descriptive", "correlation", "regression", "clustering", "classification", "time_series"]`
- `columns` (list, optional): Specific columns to analyze
- `output_format` (str, optional): Output format for results (default: "json")
- `include_visualizations` (bool, optional): Include data visualizations (default: True)

**Example:**
```python
tool = DataAnalysisTool()
result = await tool.execute(
    data='{"values": [1, 2, 3, 4, 5]}',
    analysis_type="descriptive"
)
```

### CSVAnalysisTool

**Description:** CSV file analysis tool

**Category:** `ToolCategory.ANALYSIS`

**Parameters:**
- `file_path` (str, required): Path to CSV file
- `delimiter` (str, optional): CSV delimiter (default: ",")
- `header` (bool, optional): File has header row (default: True)
- `encoding` (str, optional): File encoding (default: "utf-8")
- `analysis_types` (list, optional): Types of analysis to perform

**Example:**
```python
tool = CSVAnalysisTool()
result = await tool.execute(
    file_path="data/sample.csv",
    analysis_types=["summary", "missing", "duplicates"]
)
```

### ChartGenerationTool

**Description:** Chart and visualization generation tool

**Category:** `ToolCategory.ANALYSIS`

**Parameters:**
- `data` (dict, required): Data to visualize
- `chart_type` (str, required): Type of chart to generate
  - Choices: `["line", "bar", "scatter", "histogram", "pie", "heatmap", "box", "violin"]`
- `title` (str, optional): Chart title
- `x_label` (str, optional): X-axis label
- `y_label` (str, optional): Y-axis label
- `output_format` (str, optional): Output format (default: "png")
- `width` (int, optional): Chart width in pixels (default: 800)
- `height` (int, optional): Chart height in pixels (default: 600)

**Example:**
```python
tool = ChartGenerationTool()
result = await tool.execute(
    data={"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]},
    chart_type="line",
    title="Sample Line Chart"
)
```

### StatisticalAnalysisTool

**Description:** Statistical analysis tool

**Category:** `ToolCategory.ANALYSIS`

**Parameters:**
- `data` (list, required): Data for statistical analysis
- `test_type` (str, required): Type of statistical test
  - Choices: `["t_test", "chi_square", "anova", "correlation", "regression", "normality"]`
- `alpha` (float, optional): Significance level (default: 0.05)
- `alternative` (str, optional): Alternative hypothesis (default: "two-sided")
- `group_column` (str, optional): Column for grouping (for ANOVA)

**Example:**
```python
tool = StatisticalAnalysisTool()
result = await tool.execute(
    data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    test_type="t_test",
    alpha=0.05
)
```

### ReportGenerationTool

**Description:** Analysis report generation tool

**Category:** `ToolCategory.ANALYSIS`

**Parameters:**
- `analysis_results` (dict, required): Analysis results to include in report
- `report_type` (str, required): Type of report to generate
  - Choices: `["summary", "detailed", "executive", "technical", "visual"]`
- `output_format` (str, optional): Output format for report (default: "html")
- `include_charts` (bool, optional): Include charts and visualizations (default: True)
- `template` (str, optional): Report template to use (default: "default")

**Example:**
```python
tool = ReportGenerationTool()
result = await tool.execute(
    analysis_results={"summary": "Data analysis completed"},
    report_type="summary",
    output_format="html"
)
```

---

## 🗄️ Data Tools

### DataCleaningTool

**Description:** Data cleaning and preprocessing tool

**Category:** `ToolCategory.DATA`

**Parameters:**
- `data` (str, required): Data to clean (JSON string or file path)
- `cleaning_options` (list, required): Cleaning operations to perform
  - Choices: `["remove_duplicates", "handle_missing", "remove_outliers", "normalize", "standardize", "encode_categorical"]`
- `missing_strategy` (str, optional): Strategy for handling missing values (default: "drop")
- `outlier_method` (str, optional): Method for outlier detection (default: "iqr")
- `output_format` (str, optional): Output format for cleaned data (default: "json")

**Example:**
```python
tool = DataCleaningTool()
result = await tool.execute(
    data='{"values": [1, 2, null, 4, 5]}',
    cleaning_options=["handle_missing", "remove_outliers"]
)
```

### DataTransformationTool

**Description:** Data transformation and feature engineering tool

**Category:** `ToolCategory.DATA`

**Parameters:**
- `data` (str, required): Data to transform
- `transformations` (list, required): Transformation operations to apply
  - Choices: `["log_transform", "sqrt_transform", "polynomial", "binning", "scaling", "encoding", "feature_creation"]`
- `target_column` (str, optional): Target column for supervised transformations
- `feature_columns` (list, optional): Columns to transform
- `polynomial_degree` (int, optional): Degree for polynomial features (default: 2)
- `bins` (int, optional): Number of bins for binning (default: 5)

**Example:**
```python
tool = DataTransformationTool()
result = await tool.execute(
    data='{"values": [1, 2, 3, 4, 5]}',
    transformations=["log_transform", "scaling"]
)
```

### DataValidationTool

**Description:** Data validation and quality assessment tool

**Category:** `ToolCategory.DATA`

**Parameters:**
- `data` (str, required): Data to validate
- `validation_rules` (dict, required): Validation rules to apply
- `strict_mode` (bool, optional): Use strict validation mode (default: False)
- `generate_report` (bool, optional): Generate validation report (default: True)

**Example:**
```python
tool = DataValidationTool()
result = await tool.execute(
    data='{"values": [1, 2, 3, 4, 5]}',
    validation_rules={"min_value": 0, "max_value": 10}
)
```

### DataMergeTool

**Description:** Data merging and joining tool

**Category:** `ToolCategory.DATA`

**Parameters:**
- `datasets` (list, required): List of datasets to merge
- `merge_type` (str, required): Type of merge operation
  - Choices: `["inner", "outer", "left", "right", "cross"]`
- `join_keys` (list, optional): Keys to join on
- `suffixes` (list, optional): Suffixes for overlapping columns
- `validate` (str, optional): Validation type for merge (default: "one_to_one")

**Example:**
```python
tool = DataMergeTool()
result = await tool.execute(
    datasets=["dataset1.csv", "dataset2.csv"],
    merge_type="inner",
    join_keys=["id"]
)
```

### DataAggregationTool

**Description:** Data aggregation and grouping tool

**Category:** `ToolCategory.DATA`

**Parameters:**
- `data` (str, required): Data to aggregate
- `group_columns` (list, required): Columns to group by
- `agg_functions` (dict, required): Aggregation functions to apply
- `reset_index` (bool, optional): Reset index after aggregation (default: True)
- `sort_by` (str, optional): Column to sort results by
- `ascending` (bool, optional): Sort in ascending order (default: True)

**Example:**
```python
tool = DataAggregationTool()
result = await tool.execute(
    data="sales_data.csv",
    group_columns=["region", "product"],
    agg_functions={"sales": "sum", "quantity": "mean"}
)
```

---

## 📁 File Tools

### FileReaderTool

**Description:** File reading tool for various formats

**Category:** `ToolCategory.FILE`

**Parameters:**
- `file_path` (str, required): Path to file to read
- `file_format` (str, optional): Format of the file (default: "auto")
- `encoding` (str, optional): File encoding (default: "utf-8")
- `sheet_name` (str, optional): Excel sheet name (for Excel files)
- `header` (bool, optional): File has header row (for CSV files) (default: True)
- `delimiter` (str, optional): CSV delimiter (default: ",")

**Example:**
```python
tool = FileReaderTool()
result = await tool.execute(
    file_path="data/sample.csv",
    file_format="csv"
)
```

### FileWriterTool

**Description:** File writing tool for various formats

**Category:** `ToolCategory.FILE`

**Parameters:**
- `data` (dict, required): Data to write to file
- `file_path` (str, required): Output file path
- `file_format` (str, required): Output file format
  - Choices: `["csv", "json", "excel", "txt", "xml", "yaml"]`
- `encoding` (str, optional): File encoding (default: "utf-8")
- `mode` (str, optional): Write mode (default: "w")
- `indent` (int, optional): JSON indentation (default: 2)

**Example:**
```python
tool = FileWriterTool()
result = await tool.execute(
    data={"users": [{"id": 1, "name": "John"}]},
    file_path="output/users.json",
    file_format="json"
)
```

### PDFProcessorTool

**Description:** PDF processing and manipulation tool

**Category:** `ToolCategory.FILE`

**Parameters:**
- `file_path` (str, required): Path to PDF file
- `operation` (str, required): PDF operation to perform
  - Choices: `["extract_text", "extract_images", "merge", "split", "compress", "convert_to_images"]`
- `output_path` (str, optional): Output file path
- `pages` (list, optional): Specific pages to process
- `quality` (int, optional): Output quality for images (default: 90)

**Example:**
```python
tool = PDFProcessorTool()
result = await tool.execute(
    file_path="document.pdf",
    operation="extract_text"
)
```

### ExcelProcessorTool

**Description:** Excel file processing and manipulation tool

**Category:** `ToolCategory.FILE`

**Parameters:**
- `file_path` (str, required): Path to Excel file
- `operation` (str, required): Excel operation to perform
  - Choices: `["read", "write", "merge_sheets", "split_sheets", "format", "convert"]`
- `sheet_name` (str, optional): Excel sheet name
- `output_path` (str, optional): Output file path
- `data` (dict, optional): Data to write (for write operation)

**Example:**
```python
tool = ExcelProcessorTool()
result = await tool.execute(
    file_path="data.xlsx",
    operation="read",
    sheet_name="Sheet1"
)
```

### ImageProcessorTool

**Description:** Image processing and manipulation tool

**Category:** `ToolCategory.FILE`

**Parameters:**
- `file_path` (str, required): Path to image file
- `operation` (str, required): Image operation to perform
  - Choices: `["resize", "crop", "rotate", "flip", "filter", "convert", "compress", "extract_text"]`
- `output_path` (str, optional): Output file path
- `width` (int, optional): Target width (for resize)
- `height` (int, optional): Target height (for resize)
- `quality` (int, optional): Output quality (default: 90)
- `format` (str, optional): Output format (default: "PNG")

**Example:**
```python
tool = ImageProcessorTool()
result = await tool.execute(
    file_path="image.jpg",
    operation="resize",
    width=800,
    height=600
)
```

---

## 🤖 Automation Tools

### WorkflowAutomationTool

**Description:** Workflow automation and orchestration tool

**Category:** `ToolCategory.AUTOMATION`

**Parameters:**
- `workflow_definition` (dict, required): Workflow definition with steps and dependencies
- `execution_mode` (str, optional): Execution mode for the workflow (default: "sequential")
- `timeout` (int, optional): Workflow timeout in seconds (default: 3600)
- `retry_attempts` (int, optional): Number of retry attempts for failed steps (default: 3)
- `monitoring` (bool, optional): Enable workflow monitoring (default: True)

**Example:**
```python
tool = WorkflowAutomationTool()
result = await tool.execute(
    workflow_definition={
        "steps": [
            {"id": "step1", "action": "data_extraction"},
            {"id": "step2", "action": "data_processing", "depends_on": ["step1"]}
        ]
    },
    execution_mode="sequential"
)
```

### TaskSchedulerTool

**Description:** Task scheduling and cron-like automation tool

**Category:** `ToolCategory.AUTOMATION`

**Parameters:**
- `task_definition` (dict, required): Task definition with action and parameters
- `schedule` (str, required): Schedule specification (cron format or interval)
- `timezone` (str, optional): Timezone for scheduling (default: "UTC")
- `enabled` (bool, optional): Enable the scheduled task (default: True)
- `max_executions` (int, optional): Maximum number of executions

**Example:**
```python
tool = TaskSchedulerTool()
result = await tool.execute(
    task_definition={
        "action": "data_backup",
        "parameters": {"source": "/data", "destination": "/backup"}
    },
    schedule="0 2 * * *"
)
```

### ProcessAutomationTool

**Description:** Process automation and system integration tool

**Category:** `ToolCategory.AUTOMATION`

**Parameters:**
- `process_definition` (dict, required): Process definition with command and parameters
- `execution_environment` (str, optional): Execution environment (default: "local")
- `timeout` (int, optional): Process timeout in seconds (default: 300)
- `retry_attempts` (int, optional): Number of retry attempts (default: 1)
- `monitoring` (bool, optional): Enable process monitoring (default: True)

**Example:**
```python
tool = ProcessAutomationTool()
result = await tool.execute(
    process_definition={
        "command": "python",
        "args": ["script.py", "--input", "data.csv"],
        "working_directory": "/app"
    },
    execution_environment="local"
)
```

---

## 📧 Communication Tools

### EmailTool

**Description:** Email sending and automation tool

**Category:** `ToolCategory.COMMUNICATION`

**Parameters:**
- `to` (list, required): Recipient email addresses
- `subject` (str, required): Email subject
- `body` (str, required): Email body content
- `from_email` (str, optional): Sender email address
- `cc` (list, optional): CC email addresses
- `bcc` (list, optional): BCC email addresses
- `attachments` (list, optional): Email attachments
- `html` (bool, optional): Send as HTML email (default: False)

**Example:**
```python
tool = EmailTool()
result = await tool.execute(
    to=["user@example.com"],
    subject="Test Email",
    body="This is a test email message."
)
```

### SlackTool

**Description:** Slack messaging and automation tool

**Category:** `ToolCategory.COMMUNICATION`

**Parameters:**
- `channel` (str, required): Slack channel to send message to
- `message` (str, required): Message content
- `username` (str, optional): Bot username
- `icon_emoji` (str, optional): Bot icon emoji (default: ":robot_face:")
- `attachments` (list, optional): Message attachments
- `thread_ts` (str, optional): Thread timestamp for replies

**Example:**
```python
tool = SlackTool()
result = await tool.execute(
    channel="#general",
    message="Hello from the bot!",
    username="AI Assistant"
)
```

### DiscordTool

**Description:** Discord messaging and automation tool

**Category:** `ToolCategory.COMMUNICATION`

**Parameters:**
- `channel_id` (str, required): Discord channel ID
- `message` (str, required): Message content
- `username` (str, optional): Bot username
- `avatar_url` (str, optional): Bot avatar URL
- `embeds` (list, optional): Message embeds
- `tts` (bool, optional): Text-to-speech (default: False)

**Example:**
```python
tool = DiscordTool()
result = await tool.execute(
    channel_id="123456789012345678",
    message="Hello from Discord bot!",
    username="AI Assistant"
)
```

### WebhookTool

**Description:** Webhook notifications and API calls tool

**Category:** `ToolCategory.COMMUNICATION`

**Parameters:**
- `url` (str, required): Webhook URL
- `method` (str, optional): HTTP method (default: "POST")
- `data` (dict, optional): Request data
- `headers` (dict, optional): Request headers
- `timeout` (int, optional): Request timeout in seconds (default: 30)
- `retry_attempts` (int, optional): Number of retry attempts (default: 3)

**Example:**
```python
tool = WebhookTool()
result = await tool.execute(
    url="https://hooks.slack.com/services/...",
    method="POST",
    data={"text": "Hello from webhook!"}
)
```

### NotificationTool

**Description:** General notifications and alerts tool

**Category:** `ToolCategory.COMMUNICATION`

**Parameters:**
- `message` (str, required): Notification message
- `notification_type` (str, required): Type of notification
  - Choices: `["info", "warning", "error", "success", "alert"]`
- `recipients` (list, required): Notification recipients
- `channels` (list, optional): Notification channels (default: ["email"])
- `priority` (str, optional): Notification priority (default: "normal")
- `expires_at` (str, optional): Notification expiration time

**Example:**
```python
tool = NotificationTool()
result = await tool.execute(
    message="System maintenance scheduled",
    notification_type="info",
    recipients=["admin@example.com"],
    channels=["email", "slack"]
)
```

---

## 🖥️ System Tools

### SystemMonitorTool

**Description:** System monitoring and resource tracking tool

**Category:** `ToolCategory.SYSTEM`

**Parameters:**
- `monitoring_type` (str, required): Type of system monitoring
  - Choices: `["cpu", "memory", "disk", "network", "processes", "all"]`
- `interval` (int, optional): Monitoring interval in seconds (default: 1)
- `duration` (int, optional): Monitoring duration in seconds (default: 10)
- `thresholds` (dict, optional): Alert thresholds
- `output_format` (str, optional): Output format for monitoring data (default: "json")

**Example:**
```python
tool = SystemMonitorTool()
result = await tool.execute(
    monitoring_type="cpu",
    interval=5,
    duration=30
)
```

### ResourceManagerTool

**Description:** System resource management tool

**Category:** `ToolCategory.SYSTEM`

**Parameters:**
- `resource_type` (str, required): Type of resource to manage
  - Choices: `["memory", "cpu", "disk", "network", "processes"]`
- `action` (str, required): Management action to perform
  - Choices: `["cleanup", "optimize", "limit", "monitor", "kill"]`
- `target` (str, optional): Target resource or process
- `limit` (float, optional): Resource limit
- `force` (bool, optional): Force the action (default: False)

**Example:**
```python
tool = ResourceManagerTool()
result = await tool.execute(
    resource_type="memory",
    action="cleanup"
)
```

### ProcessManagerTool

**Description:** Process management and control tool

**Category:** `ToolCategory.SYSTEM`

**Parameters:**
- `action` (str, required): Process action to perform
  - Choices: `["list", "kill", "suspend", "resume", "monitor", "info"]`
- `process_id` (int, optional): Process ID
- `process_name` (str, optional): Process name
- `signal` (str, optional): Signal to send (for kill action) (default: "SIGTERM")
- `force` (bool, optional): Force the action (default: False)

**Example:**
```python
tool = ProcessManagerTool()
result = await tool.execute(
    action="list",
    process_name="python"
)
```

---

## Tool Registry

The `ToolRegistry` class provides functionality to register, discover, and manage tools:

```python
from src.tools.base_tool import ToolRegistry

# Create registry
registry = ToolRegistry()

# Register tools
registry.register_tool(tool_instance)

# Get tools
tool = registry.get_tool("tool_name")
tools = registry.get_tools_by_category(ToolCategory.WEB)
all_tools = registry.get_all_tools()

# Search tools
results = registry.search_tools("search_query")

# Get tool information
info = registry.get_tool_info("tool_name")
stats = registry.get_registry_stats()
```

---

## Error Handling

All tools use consistent error handling with the `ToolError` exception:

```python
from src.utils.exceptions import ToolError

try:
    result = await tool.execute(**parameters)
except ToolError as e:
    print(f"Tool execution failed: {e}")
```

---

## Best Practices

1. **Parameter Validation**: Always validate parameters before tool execution
2. **Error Handling**: Use try-catch blocks for tool execution
3. **Resource Management**: Clean up resources after tool execution
4. **Logging**: Use structured logging for tool operations
5. **Testing**: Test tools with various parameter combinations
6. **Documentation**: Document tool usage and examples
7. **Performance**: Monitor tool execution time and resource usage

---

## Examples

See the `examples/tools_example.py` file for comprehensive examples of using all tool categories.

---

## Contributing

When adding new tools:

1. Inherit from `BaseTool`
2. Implement required abstract methods
3. Define tool metadata and parameters
4. Add comprehensive tests
5. Update documentation
6. Add examples

---

**Last Updated:** 2025-01-10  
**Version:** 1.0.0  
**Author:** OpenManus-Youtu Integration Team