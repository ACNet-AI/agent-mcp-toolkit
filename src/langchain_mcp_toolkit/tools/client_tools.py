"""
MCP Client Tools Module

This module provides a collection of client tools for interacting with the MCP server. These tools allow creating client connections,
calling server tools, managing resources and prompts, as well as integrating with LangChain.

Main tools:
- ClientCreateTool: Create connection to MCP server
- ClientCallToolTool: Call tools on the MCP server
- ClientListToolsTool: List available tools on the server
- ClientListResourcesTool: List available resources on the server
- ClientReadResourceTool: Read resources from the server
- ClientListPromptsTool: List available prompts on the server
- ClientGetPromptTool: Get prompts from the server
- GetLangChainToolsTool: Convert MCP tools to LangChain tools
- GetLangChainPromptTool: Convert MCP prompts to LangChain prompts

These tools can be obtained through MCPToolkit and integrated into an Agent.
"""

from typing import Any

from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage
from pydantic import ConfigDict, Field

from ..services.client_service import MCPClientService
from .base import MCPBaseTool


class ClientCreateTool(MCPBaseTool):
    """
    Create MCP Client Tool

    This tool is used to create a connection to an MCP server. Supports standard server connections (SSE) and local process connections (stdio).
    This tool must be called before using other client tools.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # Use tool to create client connection
        create_tool = [t for t in tools if t.name == "client_create"][0]
        await create_tool.invoke({
            "server_url": "http://localhost:8000",
            "transport_type": "sse"
        })
        ```
    """

    name: str = "client_create"
    description: str = "Create an MCP client, connecting to the specified server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, *args: Any, **kwargs: Any) -> str:
        """Create MCP client

        Args:
            *args: Positional arguments, first argument is server_url
            **kwargs: Keyword arguments, including transport_type

        Returns:
            str: Creation result

        Raises:
            ValueError: When client_service is not set
        """
        if not self.client_service:
            raise ValueError("Client service not set")

        server_url = args[0] if args else kwargs.get("server_url", "")
        transport_type = kwargs.get("transport_type", "stdio")

        return self.client_service.create(server_url, transport_type)


class ClientCallToolTool(MCPBaseTool):
    """
    Call MCP Tool

    This tool is used to call tools on the MCP server, allowing specification of server name, tool name, and parameters.
    Client connection must be created before using this tool.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # Use tool to call a tool on the server
        call_tool = [t for t in tools if t.name == "client_call_tool"][0]
        result = await call_tool.invoke({
            "server_name": "default",
            "tool_name": "get_weather",
            "arguments": {"city": "New York"}
        })
        ```
    """

    name: str = "client_call_tool"
    description: str = "Call a tool on the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        """
        Run the tool, calling a tool on the server

        Args:
            server_name: Server name, typically "default" for single server
            tool_name: Tool name
            arguments: Tool parameter dictionary

        Returns:
            Any: Tool call result

        Raises:
            ValueError: If client service is not set

        Example:
            ```python
            # Call weather query tool
            result = await tool.invoke({
                "server_name": "weather_server",
                "tool_name": "get_weather",
                "arguments": {"city": "New York", "format": "concise"}
            })

            # Call translation tool
            result = await tool.invoke({
                "server_name": "translation_server",
                "tool_name": "translate",
                "arguments": {
                    "text": "Hello, world!",
                    "target_language": "Chinese"
                }
            })
            ```
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        return await self.client_service.call_tool(server_name, tool_name, **arguments)


class ClientListToolsTool(MCPBaseTool):
    """
    List tools available on the MCP server

    This tool is used to get a list of all available MCP tools and their descriptions.
    For multi-server scenarios, you can choose whether to include server prefixes.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # List all tools on the server
        list_tools = [t for t in tools if t.name == "client_list_tools"][0]
        available_tools = await list_tools.invoke({
            "include_server_prefix": True
        })
        ```
    """

    name: str = "client_list_tools"
    description: str = "List available tools on the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, include_server_prefix: bool = True) -> list[dict[str, str]]:
        """
        Run the tool, listing tools on the MCP server

        Args:
            include_server_prefix: Whether to include server prefix in tool names for multi-server

        Returns:
            list[dict[str, str]]: List of tools with name and description

        Raises:
            ValueError: If client service is not set
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        tools = await self.client_service.list_tools(include_server_prefix=include_server_prefix)
        return tools


class ClientListResourcesTool(MCPBaseTool):
    """
    List resources available on the MCP server

    This tool is used to get a list of resources of a specific type on the specified server.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # List resources
        list_resources = [t for t in tools if t.name == "client_list_resources"][0]
        resources = await list_resources.invoke({
            "server_name": "default",
            "resource_type": "collection"
        })
        ```
    """

    name: str = "client_list_resources"
    description: str = "List resources on the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Run the tool, listing resources on the MCP server

        Args:
            *args: Positional arguments, first argument is server_name
            **kwargs: Keyword arguments, including resource_type

        Returns:
            list[dict[str, Any]]: List of resources

        Raises:
            ValueError: If client service is not set
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        server_name = args[0] if args else kwargs.get("server_name", "default")
        return await self.client_service.list_resources(server_name)


class ClientReadResourceTool(MCPBaseTool):
    """
    Read resource from the MCP server

    This tool is used to read the content of a specific resource on the specified server.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # Read resource
        read_resource = [t for t in tools if t.name == "client_read_resource"][0]
        content = await read_resource.invoke({
            "server_name": "default",
            "resource_type": "collection",
            "resource_id": "cities"
        })
        ```
    """

    name: str = "client_read_resource"
    description: str = "Read resource from the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, resource_name: str, server_name: str = "") -> dict[str, Any]:
        """
        Run the tool, read a resource from the MCP server

        Args:
            resource_name: Resource name
            server_name: Server name, defaults to empty string

        Returns:
            dict: Resource content

        Raises:
            ValueError: If client service is not set

        Example:
            ```python
            resource = await tool.invoke({
                "resource_name": "cities",
                "server_name": "default"
            })
            print(resource)  # Output: {"content": ["New York", "Los Angeles", "Chicago", ...]}
            ```
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        return await self.client_service.read_resource(server_name, resource_name)


class ClientListPromptsTool(MCPBaseTool):
    """
    List prompts available on the MCP server

    This tool is used to get a list of all available prompt templates on the specified server.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # List prompts
        list_prompts = [t for t in tools if t.name == "client_list_prompts"][0]
        prompts = await list_prompts.invoke({
            "server_name": "default"
        })
        ```
    """

    name: str = "client_list_prompts"
    description: str = "List available prompts on the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, server_name: str) -> list[dict[str, Any]]:
        """
        Run the tool, listing prompts on the MCP server

        Args:
            server_name: Server name

        Returns:
            list[dict[str, Any]]: List of prompts

        Raises:
            ValueError: If client service is not set
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        return await self.client_service.list_prompts(server_name)


class ClientGetPromptTool(MCPBaseTool):
    """
    Get prompt from the MCP server

    This tool is used to get the content of a specific prompt on the specified server.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # Get prompt
        get_prompt = [t for t in tools if t.name == "client_get_prompt"][0]
        prompt = await get_prompt.invoke({
            "server_name": "default",
            "prompt_name": "greeting"
        })
        ```
    """

    name: str = "client_get_prompt"
    description: str = "Get prompt from the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self, server_name: str, prompt_name: str) -> Any:
        """
        Run the tool, getting prompt from the MCP server

        Args:
            server_name: Server name
            prompt_name: Prompt name

        Returns:
            Any: Prompt content

        Raises:
            ValueError: If client service is not set
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        # Default arguments - empty dictionary
        arguments = {}
        return await self.client_service.get_prompt(prompt_name, arguments, server_name)


class GetLangChainToolsTool(MCPBaseTool):
    """
    Get LangChain Tools

    This tool is used to convert tools on the MCP server to LangChain format tools,
    for easy use within the LangChain framework.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit
        from langchain.agents import create_react_agent

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # Get LangChain tools
        get_lc_tools = [t for t in tools if t.name == "get_langchain_tools"][0]
        lc_tools = await get_lc_tools.invoke()

        # Create Agent with LangChain tools
        agent = create_react_agent(model, lc_tools)
        ```
    """

    name: str = "get_langchain_tools"
    description: str = "Get LangChain tools from the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(self) -> list[BaseTool]:
        """
        Run the tool, getting LangChain tools from the MCP server

        Returns:
            list[BaseTool]: List of LangChain tools

        Raises:
            ValueError: If client service is not set
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        return await self.client_service.get_langchain_tools()


class GetLangChainPromptTool(MCPBaseTool):
    """
    Get LangChain Prompt

    This tool is used to convert prompts on the MCP server to LangChain format prompts,
    for easy use within the LangChain framework. Supports providing parameters to fill prompt templates.

    Attributes:
        name: Tool name
        description: Tool description
        client_service: MCP client service instance

    Example:
        ```python
        from langchain_mcp_toolkit import MCPToolkit

        # Get toolkit
        toolkit = MCPToolkit(mode="client")
        tools = toolkit.get_tools()

        # Get LangChain prompt
        get_lc_prompt = [t for t in tools if t.name == "get_langchain_prompt"][0]
        messages = await get_lc_prompt.invoke({
            "server_name": "default",
            "prompt_name": "weather_query",
            "arguments": {"city": "New York"}
        })

        # Use prompt
        response = await llm.ainvoke(messages)
        ```
    """

    name: str = "get_langchain_prompt"
    description: str = "Get LangChain prompt from the MCP server"
    client_service: MCPClientService | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, client_service: MCPClientService, **kwargs: Any) -> None:
        """
        Initialize the tool

        Args:
            client_service: MCP client service instance
            **kwargs: Other parameters
        """
        super().__init__(**kwargs)
        self.client_service = client_service

    async def _run(
        self,
        server_name: str,
        prompt_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> list[BaseMessage]:
        """
        Run the tool, getting LangChain prompt from the MCP server

        Args:
            server_name: Server name
            prompt_name: Prompt name
            arguments: Prompt arguments for template variables

        Returns:
            list[BaseMessage]: List of LangChain messages

        Raises:
            ValueError: If client service is not set
        """
        if self.client_service is None:
            raise ValueError("Client service not set")

        args = arguments or {}
        return await self.client_service.get_langchain_prompt(prompt_name, args, server_name)
