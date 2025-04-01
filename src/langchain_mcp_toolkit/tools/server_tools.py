"""
MCP Server Tools Module

This module provides a collection of tools for managing MCP servers. These tools allow starting and stopping servers,
adding tools, resources, and prompts, as well as managing server status.

Main tools:
- ServerStartTool: Start MCP server
- ServerStopTool: Stop MCP server
- ServerGetUrlTool: Get server URL
- ServerAddToolTool: Add tool to server
- ServerAddResourceTool: Add resource to server
- ServerAddPromptTool: Add prompt to server

These tools can be obtained through MCPToolkit and integrated into an Agent, allowing the Agent to
create and manage its own MCP server instances.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from langchain_mcp_toolkit.prompts import (
    ADD_PROMPT_PROMPT,
    ADD_RESOURCE_PROMPT,
    ADD_TOOL_PROMPT,
    GET_SERVER_URL_PROMPT,
    START_SERVER_PROMPT,
    STOP_SERVER_PROMPT,
)
from langchain_mcp_toolkit.schemas import (
    NoInput,
    PromptDefinition,
    ResourceDefinition,
    ServerConfig,
    ToolDefinition,
)
from langchain_mcp_toolkit.services.server_service import MCPServerService
from langchain_mcp_toolkit.tools.base import MCPBaseTool


class ServerStartTool(MCPBaseTool):
    """
    Start MCP Server Tool

    This tool is used to start an MCP server on the specified host and port.

    Attributes:
        name: Tool name
        description: Tool description
        args_schema: Parameter schema
        server_service: MCP server service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="server")
        tools = toolkit.get_tools()

        # Start server
        start_tool = [t for t in tools if t.name == "server_start"][0]
        url = await start_tool.invoke({
            "host": "localhost",
            "port": 8000
        })
        print(url)  # Output: Server started at http://localhost:8000
        ```
    """

    name: str = "server_start"
    description: str = START_SERVER_PROMPT
    args_schema: type[BaseModel] = ServerConfig
    server_service: MCPServerService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, server_service: MCPServerService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            server_service: MCP server service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.server_service = server_service

    async def _run(self, host: str = "localhost", port: int = 8000) -> str:
        """
        Run the tool, start MCP server

        Args:
            host: Server host address, defaults to "localhost"
            port: Server port, defaults to 8000

        Returns:
            str: Operation result message

        Raises:
            ValueError: If server service is not set

        Example:
            ```python
            # Start server with default parameters
            url = await tool.invoke()
            # Output: Server started at http://localhost:8000

            # Start server with specific host and port
            url = await tool.invoke({
                "host": "0.0.0.0",  # Allow external access
                "port": 8888
            })
            # Output: Server started at http://0.0.0.0:8888
            ```
        """
        if self.server_service is None:
            raise ValueError("Server service not set")

        return await self.server_service.async_start_server(host, port)


class ServerStopTool(MCPBaseTool):
    """
    Stop MCP Server Tool

    This tool is used to stop the currently running MCP server.

    Attributes:
        name: Tool name
        description: Tool description
        args_schema: Parameter schema
        server_service: MCP server service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="server")
        tools = toolkit.get_tools()

        # Stop server
        stop_tool = [t for t in tools if t.name == "server_stop"][0]
        result = await stop_tool.invoke()
        print(result)  # Output: Server stopped
        ```
    """

    name: str = "server_stop"
    description: str = STOP_SERVER_PROMPT
    args_schema: type[BaseModel] = NoInput
    server_service: MCPServerService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, server_service: MCPServerService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            server_service: MCP server service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.server_service = server_service

    async def _run(self) -> str:
        """
        Run the tool, stop MCP server

        Returns:
            str: Operation result message

        Raises:
            ValueError: If server service is not set

        Example:
            ```python
            # Stop server
            result = await tool.invoke()
            # Output: Server stopped

            # If server is not running
            result = await tool.invoke()
            # Output: Server not currently running
            ```
        """
        if self.server_service is None:
            raise ValueError("Server service not set")

        return await self.server_service.async_stop_server()


class ServerGetUrlTool(MCPBaseTool):
    """
    Get MCP Server URL Tool

    This tool is used to get the URL of the currently running MCP server.

    Attributes:
        name: Tool name
        description: Tool description
        args_schema: Parameter schema
        server_service: MCP server service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="server")
        tools = toolkit.get_tools()

        # Get server URL
        get_url_tool = [t for t in tools if t.name == "server_get_url"][0]
        url = await get_url_tool.invoke()
        print(url)  # Output: http://localhost:8000
        ```
    """

    name: str = "server_get_url"
    description: str = GET_SERVER_URL_PROMPT
    args_schema: type[BaseModel] = NoInput
    server_service: MCPServerService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, server_service: MCPServerService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            server_service: MCP server service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.server_service = server_service

    async def _run(self) -> str:
        """
        Run the tool, get MCP server URL

        Returns:
            str: Server URL or status message

        Raises:
            ValueError: If server service is not set

        Example:
            ```python
            # Get server URL
            url = await tool.invoke()
            # Output: http://localhost:8000

            # If server is not running
            url = await tool.invoke()
            # Output: Server not currently running
            ```
        """
        if self.server_service is None:
            raise ValueError("Server service not set")

        return await self.server_service.async_get_url()


class ServerAddToolTool(MCPBaseTool):
    """
    Add Tool to MCP Server

    This tool is used to dynamically add new tools to the MCP server. Tool code will be executed in a secure sandbox.

    Attributes:
        name: Tool name
        description: Tool description
        args_schema: Parameter schema
        server_service: MCP server service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="server")
        tools = toolkit.get_tools()

        # Add tool
        add_tool = [t for t in tools if t.name == "server_add_tool"][0]
        result = await add_tool.invoke({
            "name": "get_weather",
            "description": "Get city weather",
            "code": "return f'Today in {kwargs.get(\"city\")} the weather is sunny, 25°C'"
        })
        ```
    """

    name: str = "server_add_tool"
    description: str = ADD_TOOL_PROMPT
    args_schema: type[BaseModel] = ToolDefinition
    server_service: MCPServerService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, server_service: MCPServerService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            server_service: MCP server service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.server_service = server_service

    async def _run(self, name: str, description: str, code: str, code_type: str = "python") -> str:
        """
        Run the tool, add tool to MCP server

        Args:
            name: Tool name
            description: Tool description
            code: Tool code
            code_type: Code type, defaults to "python"

        Returns:
            str: Operation result message

        Raises:
            ValueError: If server service is not set

        Example:
            ```python
            # Add a simple calculator tool
            result = await tool.invoke({
                "name": "add_numbers",
                "description": "Add two numbers",
                "code": "return kwargs.get('a', 0) + kwargs.get('b', 0)"
            })

            # Add a more complex tool with external library
            result = await tool.invoke({
                "name": "get_weather",
                "description": "Get weather for a city",
                "code": "def get_weather(**kwargs):\n    import requests\n    city = kwargs.get('city', 'New York')\n    api_key = 'demo_key'\n    url = f'https://api.example.com/weather?q={city}&appid={api_key}'\n\n    try:\n        response = requests.get(url)\n        data = response.json()\n        temp = data['main']['temp']\n        conditions = data['weather'][0]['description']\n        return f'Weather in {city}: {temp}°C, {conditions}'\n    except Exception as e:\n        return f'Error getting weather: {str(e)}'"
            })
            ```
        """
        if self.server_service is None:
            raise ValueError("Server service not set")

        return await self.server_service.async_add_tool(name, description, code, code_type)


class ServerAddResourceTool(MCPBaseTool):
    """
    Add Resource to MCP Server

    This tool is used to add various types of resources to the MCP server, such as strings, dictionaries, or lists.

    Attributes:
        name: Tool name
        description: Tool description
        args_schema: Parameter schema
        server_service: MCP server service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="server")
        tools = toolkit.get_tools()

        # Add resource
        add_resource = [t for t in tools if t.name == "server_add_resource"][0]
        result = await add_resource.invoke({
            "name": "cities",
            "content": ["New York", "Los Angeles", "Chicago", "San Francisco"],
            "description": "Major US cities"
        })
        ```
    """

    name: str = "server_add_resource"
    description: str = ADD_RESOURCE_PROMPT
    args_schema: type[BaseModel] = ResourceDefinition
    server_service: MCPServerService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, server_service: MCPServerService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            server_service: MCP server service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.server_service = server_service

    async def _run(
        self, name: str, content: str | dict[str, Any] | list[Any], description: str = ""
    ) -> str:
        """
        Run the tool, add resource to MCP server

        Args:
            name: Resource name
            content: Resource content (string, dictionary, or list)
            description: Resource description, defaults to empty string

        Returns:
            str: Operation result message

        Raises:
            ValueError: If server service is not set

        Example:
            ```python
            # Add string resource
            result = await tool.invoke({
                "name": "greeting_template",
                "content": "Hello, {name}! Welcome to our service.",
                "description": "Greeting template with name placeholder"
            })

            # Add dictionary resource
            result = await tool.invoke({
                "name": "country_codes",
                "content": {
                    "US": "United States",
                    "UK": "United Kingdom",
                    "CA": "Canada",
                    "AU": "Australia"
                },
                "description": "Country codes and names"
            })

            # Add list resource
            result = await tool.invoke({
                "name": "colors",
                "content": ["red", "green", "blue", "yellow", "purple"],
                "description": "List of basic colors"
            })
            ```
        """
        if self.server_service is None:
            raise ValueError("Server service not set")

        return await self.server_service.async_add_resource(name, content, description)


class ServerAddPromptTool(MCPBaseTool):
    """
    Add Prompt to MCP Server

    This tool is used to add prompt templates to the MCP server, which can be used for text generation or building conversations.

    Attributes:
        name: Tool name
        description: Tool description
        args_schema: Parameter schema
        server_service: MCP server service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="server")
        tools = toolkit.get_tools()

        # Add prompt
        add_prompt = [t for t in tools if t.name == "server_add_prompt"][0]
        result = await add_prompt.invoke({
            "name": "weather_query",
            "content": "Please check the weather in {city}"
        })
        ```
    """

    name: str = "server_add_prompt"
    description: str = ADD_PROMPT_PROMPT
    args_schema: type[BaseModel] = PromptDefinition
    server_service: MCPServerService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, server_service: MCPServerService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            server_service: MCP server service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.server_service = server_service

    async def _run(self, name: str, content: str) -> str:
        """
        Run the tool, add prompt to MCP server

        Args:
            name: Prompt name
            content: Prompt content with optional template variables in {variable} format

        Returns:
            str: Operation result message

        Raises:
            ValueError: If server service is not set

        Example:
            ```python
            # Add a simple greeting prompt
            result = await tool.invoke({
                "name": "greeting",
                "content": "Hello, {name}! How can I help you today?"
            })

            # Add a more complex prompt
            result = await tool.invoke({
                "name": "travel_itinerary",
                "content": "Please create a {duration} day travel itinerary for {destination}. Include recommended activities, restaurants, and accommodations."
            })

            # Add a multi-message conversation prompt
            result = await tool.invoke({
                "name": "weather_conversation",
                "content": [
                    {"role": "system", "content": "You are a helpful weather assistant."},
                    {"role": "user", "content": "What's the weather like in {city}?"},
                    {"role": "assistant", "content": "Let me check the weather in {city} for you."}
                ]
            })
            ```
        """
        if self.server_service is None:
            raise ValueError("Server service not set")

        return await self.server_service.async_add_prompt(name, content)
