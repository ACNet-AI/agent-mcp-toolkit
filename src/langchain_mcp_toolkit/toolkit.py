"""
MCP Toolkit Module

This module provides the main interface for creating and managing MCP tools. The MCPToolkit class is the core of the toolkit,
used for creating MCP tools, managing server and client services, and providing integration methods with LangChain.

Main features:
- Create and manage MCP tool collections
- Provide access interfaces for server and client services
- Support multi-server connections and management
- Provide integration methods with LangChain and LangGraph
"""

from typing import Any, Literal

from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools.base import BaseToolkit
from pydantic import ConfigDict, Field

from langchain_mcp_toolkit.factory import MCPToolFactory
from langchain_mcp_toolkit.services.adapters import MCPAdapterService
from langchain_mcp_toolkit.services.client_service import MCPClientService
from langchain_mcp_toolkit.services.server_service import MCPServerService


class MCPToolkit(BaseToolkit):
    """
    MCP Toolkit for creating and managing MCP tool collections

    This class is the main entry point for agent-mcp-toolkit, providing a unified interface for creating and managing MCP tools.
    Depending on the mode, it can create client tools, server tools, or a combination of both.

    Attributes:
        mode: Toolkit mode, options are "client", "server", or "client_and_server"
        factory: MCP tool factory instance, used for creating various MCP tools
        adapter: MCP adapter service instance, used for integration with LangChain

    Example:
        ```python
        # Create a toolkit with both client and server tools
        toolkit = MCPToolkit()

        # Create a toolkit with only client tools
        client_toolkit = MCPToolkit(mode="client")

        # Create a toolkit with only server tools
        server_toolkit = MCPToolkit(mode="server")

        # Get all tools in the toolkit
        tools = toolkit.get_tools()
        ```
    """

    mode: Literal["client", "server", "client_and_server"] = Field(
        default="client_and_server",
        description="Toolkit mode, supports 'client', 'server', and 'client_and_server'",
    )
    factory: MCPToolFactory = Field(default_factory=MCPToolFactory)
    adapter: MCPAdapterService = Field(default_factory=MCPAdapterService)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any) -> None:
        """
        Initialize the MCP toolkit

        Initializes the appropriate client and server services based on the specified mode.

        Parameters:
            **data: Parameters passed to the parent class constructor

        Note:
            If the mode includes "client", the client service will be initialized
            If the mode includes "server", the server service will be initialized
        """
        super().__init__(**data)

        # Initialize services based on mode
        if self.mode in ["client", "client_and_server"]:
            self.factory.init_client_service()

        if self.mode in ["server", "client_and_server"]:
            self.factory.init_server_service()

    def get_tools(self) -> list[BaseTool]:
        """
        Get all tools in the toolkit

        Returns the appropriate tool collection based on the current mode.
        - client mode: returns client tools
        - server mode: returns server tools
        - client_and_server mode: returns all tools

        Returns:
            list[BaseTool]: List of tools, can be used directly to create an Agent

        Example:
            ```python
            toolkit = MCPToolkit()
            tools = toolkit.get_tools()
            agent = create_react_agent(model, tools)
            ```
        """
        if self.mode == "client":
            return self.factory.create_client_tools()
        elif self.mode == "server":
            return self.factory.create_server_tools()
        else:  # client_and_server
            return self.factory.create_all_tools()

    def get_client_service(self) -> MCPClientService:
        """
        Get the client service instance

        This method provides access to the underlying client service, allowing direct interaction with MCP servers.

        Returns:
            MCPClientService: Client service instance

        Exceptions:
            ValueError: If the current mode does not support client services (i.e., mode is "server")

        Example:
            ```python
            toolkit = MCPToolkit()
            client_service = toolkit.get_client_service()

            # Create client connection
            client_service.create("http://localhost:8000", "sse")
            await client_service.connect()

            # Call tool
            result = await client_service.call_tool("default", "my_tool", argument="value")
            ```
        """
        if self.mode not in ["client", "client_and_server"]:
            raise ValueError(f"Current mode '{self.mode}' does not support client services")

        # Ensure client_service is not None
        if self.factory.client_service is None:
            self.factory.init_client_service()
        assert self.factory.client_service is not None, "Could not initialize client service"
        return self.factory.client_service

    def get_server_service(self) -> MCPServerService:
        """
        Get the server service instance

        This method provides access to the underlying server service, allowing management of MCP servers.

        Returns:
            MCPServerService: Server service instance

        Exceptions:
            ValueError: If the current mode does not support server services (i.e., mode is "client")

        Example:
            ```python
            toolkit = MCPToolkit()
            server_service = toolkit.get_server_service()

            # Start server
            await server_service.start(name="MyServer", port=8000)

            # Add tool
            tool_code = "def my_tool(): return 'Hello, world!'"
            await server_service.add_tool("my_tool", "Example tool", tool_code)
            ```
        """
        if self.mode not in ["server", "client_and_server"]:
            raise ValueError(f"Current mode '{self.mode}' does not support server services")

        # Ensure server_service is not None
        if self.factory.server_service is None:
            self.factory.init_server_service()
        assert self.factory.server_service is not None, "Could not initialize server service"
        return self.factory.server_service

    def get_tools_by_names(self, names: list[str]) -> list[BaseTool]:
        """
        Get tools by their names

        Allows selective retrieval of specific tools from the toolkit.

        Parameters:
            names: List of tool names

        Returns:
            list[BaseTool]: List of tool instances

        Example:
            ```python
            toolkit = MCPToolkit()
            # Only get tools for starting server and creating client
            specific_tools = toolkit.get_tools_by_names(["mcp_start_server", "mcp_create_client"])
            ```
        """
        return self.factory.get_tools_by_names(names)

    @classmethod
    def from_client(cls) -> "MCPToolkit":
        """
        Create toolkit from client

        Creates a toolkit that only contains client tools.

        Returns:
            MCPToolkit: Toolkit instance

        Example:
            ```python
            client_toolkit = MCPToolkit.from_client()
            client_tools = client_toolkit.get_tools()
            ```
        """
        return cls(mode="client")

    @classmethod
    def from_server(cls) -> "MCPToolkit":
        """
        Create toolkit from server

        Creates a toolkit that only contains server tools.

        Returns:
            MCPToolkit: Toolkit instance

        Example:
            ```python
            server_toolkit = MCPToolkit.from_server()
            server_tools = server_toolkit.get_tools()
            ```
        """
        return cls(mode="server")

    @classmethod
    def from_server_and_api_key(cls, server_url: str, api_key: str | None = None, **kwargs: Any) -> "MCPToolkit":
        """
        Create toolkit from server and API key

        Creates a toolkit containing both server and client tools, and sets up the server and API key.
        This is a convenient method for creating a complete toolkit.

        Parameters:
            server_url: Server URL
            api_key: OpenAI API key, optional
            **kwargs: Other parameters

        Returns:
            MCPToolkit: Toolkit instance

        Example:
            ```python
            # Create a toolkit with server and client
            toolkit = MCPToolkit.from_server_and_api_key(
                server_url="http://localhost:8000/sse",
                api_key="your-openai-api-key"
            )
            ```
        """
        # Set API key
        if api_key:
            from os import environ
            environ["OPENAI_API_KEY"] = api_key

        # Use direct call to constructor to create instance
        return MCPToolkit(
            mode="client",
            server_url=server_url,
            api_key=api_key,
            **kwargs
        )

    @classmethod
    def from_api_key(cls, api_key: str, **kwargs: Any) -> "MCPToolkit":
        """
        Create toolkit from API key

        Creates a toolkit that only contains client tools, and sets the API key.

        Parameters:
            api_key: OpenAI API key
            **kwargs: Other parameters

        Returns:
            MCPToolkit: Toolkit instance

        Example:
            ```python
            client_toolkit = MCPToolkit.from_api_key(api_key="sk-...")
            ```
        """
        # Set OpenAI API key
        from os import environ
        environ["OPENAI_API_KEY"] = api_key

        # Use direct call to constructor to create instance
        return MCPToolkit(
            mode="client",
            api_key=api_key,
            **kwargs
        )

    async def get_langchain_tools(self) -> list[BaseTool]:
        """
        Get current client service LangChain tools

        Converts MCP server tools to LangChain format tools.

        Returns:
            list[BaseTool]: LangChain tool list

        Exceptions:
            ValueError: If mode does not support client or client is not connected

        Example:
            ```python
            toolkit = MCPToolkit(mode="client")
            client_service = toolkit.get_client_service()
            client_service.create("http://localhost:8000", "sse")
            await client_service.connect()

            # Get LangChain tools
            lc_tools = await toolkit.get_langchain_tools()
            ```
        """
        client_service = self.get_client_service()
        return await MCPAdapterService.load_tools_from_session(client_service.client)

    async def get_tools_from_multiple_servers(self, server_urls: dict[str, str]) -> list[BaseTool]:
        """
        Get LangChain tools from multiple servers

        Connects to multiple MCP servers and gets tools from all servers.

        Parameters:
            server_urls: Server URL dictionary, format is {"server_name": "http://localhost:8000"}

        Returns:
            list[BaseTool]: All server LangChain tool list

        Example:
            ```python
            toolkit = MCPToolkit()

            # Get tools from multiple servers
            server_urls = {
                "weather": "http://localhost:8000",
                "news": "http://localhost:8001"
            }
            tools = await toolkit.get_tools_from_multiple_servers(server_urls)
            ```
        """
        server_configs = {
            name: {"url": url, "transport": "sse"} for name, url in server_urls.items()
        }
        client = await MCPAdapterService.create_multi_server_client(server_configs)
        return await MCPAdapterService.load_tools_from_session(client)

    async def create_multi_server_client(self, server_urls: dict[str, str]) -> Any:
        """
        Create multi-server MCP client

        Creates a client that connects to multiple MCP servers.

        Parameters:
            server_urls: Server URL dictionary, format is {"server_name": "http://localhost:8000"}

        Returns:
            MultiServerMCPClient: Multi-server client instance

        Example:
            ```python
            toolkit = MCPToolkit()

            server_urls = {
                "weather": "http://localhost:8000",
                "news": "http://localhost:8001"
            }
            multi_client = await toolkit.create_multi_server_client(server_urls)

            # Connect to all servers
            await multi_client.connect()
            ```
        """
        # Convert simple URL dictionary to required format
        server_configs = {
            name: {"url": url, "transport": "sse"} for name, url in server_urls.items()
        }
        return await MCPAdapterService.create_multi_server_client(server_configs)

    async def load_prompt(
        self, prompt_name: str, arguments: dict[str, Any] | None = None
    ) -> list[HumanMessage | AIMessage]:
        """
        Load MCP prompt and convert to LangChain messages

        Loads prompt from MCP server and converts it to LangChain format message list.

        Parameters:
            prompt_name: Prompt name
            arguments: Prompt parameters, optional

        Returns:
            list[HumanMessage | AIMessage]: LangChain message list

        Exceptions:
            ValueError: If mode does not support client or client is not connected

        Example:
            ```python
            toolkit = MCPToolkit(mode="client")
            client_service = toolkit.get_client_service()
            client_service.create("http://localhost:8000", "sse")
            await client_service.connect()

            # Load prompt
            messages = await toolkit.load_prompt(
                "weather_query",
                {"city": "New York"}
            )
            ```
        """
        client_service = self.get_client_service()
        return await MCPAdapterService.load_prompt_from_session(
            client_service.client, prompt_name, arguments
        )
