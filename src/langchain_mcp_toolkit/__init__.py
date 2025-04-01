"""
LangChain Integration Toolkit for MCP

This package provides tools and services for integrating MCP (Model Compositional Programming) into the LangChain ecosystem.
MCP is a programming paradigm for composing AI models and tools, and this toolkit enables LangChain users to easily
create, manage, and use MCP servers and clients.

Main features:
- Create and manage MCP server instances
- Add custom tools, resources, and prompts to the server
- Create MCP clients to connect to servers
- Call tools on the server and get results
- Provide LangChain-compatible tools for use in agent workflows

Usage:
```python
from langchain_mcp_toolkit import MCPToolkit

# Create toolkit instance
toolkit = MCPToolkit()

# Start server
await toolkit.start_server(host="localhost", port=8000)

# Add tool
await toolkit.add_tool(
    name="hello",
    description="Return a greeting",
    code="def run(**kwargs):\n    return 'Hello, World!'"
)

# Create tool list for LangChain
tools = toolkit.get_all_tools()
```

This package also provides various data models and service classes for low-level integration and customization.
"""

__version__ = "0.0.1"

from langchain_mcp_toolkit.factory import MCPToolFactory
from langchain_mcp_toolkit.prompts import (
    ADD_PROMPT_PROMPT,
    ADD_RESOURCE_PROMPT,
    ADD_TOOL_PROMPT,
    CALL_TOOL_PROMPT,
    CREATE_CLIENT_PROMPT,
    GET_LANGCHAIN_PROMPT_PROMPT,
    GET_LANGCHAIN_TOOLS_PROMPT,
    GET_PROMPT_PROMPT,
    GET_SERVER_URL_PROMPT,
    LIST_PROMPTS_PROMPT,
    LIST_RESOURCES_PROMPT,
    LIST_TOOLS_PROMPT,
    READ_RESOURCE_PROMPT,
    SERVER_CREATE_PROMPT,
    START_SERVER_PROMPT,
    STOP_SERVER_PROMPT,
)
from langchain_mcp_toolkit.schemas import (
    ClientConfig,
    LangChainPromptConfig,
    LangChainToolsConfig,
    NoInput,
    PromptDefinition,
    PromptName,
    ResourceDefinition,
    ResourceName,
    ServerConfig,
    ToolCall,
    ToolDefinition,
)
from langchain_mcp_toolkit.services import MCPAdapterService, MCPClientService, MCPServerService
from langchain_mcp_toolkit.toolkit import MCPToolkit
from langchain_mcp_toolkit.tools.base import MCPBaseTool

__all__ = [
    "MCPToolkit",
    "MCPToolFactory",
    "MCPClientService",
    "MCPServerService",
    "MCPBaseTool",
    "MCPAdapterService",
    # Data models
    "ClientConfig",
    "LangChainPromptConfig",
    "LangChainToolsConfig",
    "NoInput",
    "PromptDefinition",
    "PromptName",
    "ResourceDefinition",
    "ResourceName",
    "ServerConfig",
    "ToolCall",
    "ToolDefinition",
    # Prompts
    "ADD_PROMPT_PROMPT",
    "ADD_RESOURCE_PROMPT",
    "ADD_TOOL_PROMPT",
    "CALL_TOOL_PROMPT",
    "CREATE_CLIENT_PROMPT",
    "GET_LANGCHAIN_PROMPT_PROMPT",
    "GET_LANGCHAIN_TOOLS_PROMPT",
    "GET_PROMPT_PROMPT",
    "GET_SERVER_URL_PROMPT",
    "LIST_PROMPTS_PROMPT",
    "LIST_RESOURCES_PROMPT",
    "LIST_TOOLS_PROMPT",
    "READ_RESOURCE_PROMPT",
    "SERVER_CREATE_PROMPT",
    "START_SERVER_PROMPT",
    "STOP_SERVER_PROMPT",
]
