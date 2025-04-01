"""
MCP Tool Factory Module

This module provides a factory class for creating and managing MCP tools. MCPToolFactory is responsible for initializing services and creating tool instances,
and is one of the core components of MCPToolkit. The factory pattern simplifies the creation and management of tools, allowing users to easily obtain the required tool collections.

Main features:
- Initialize client and server services
- Create client tool collections
- Create server tool collections
- Create complete tool collections
- Get specific tools by name
"""


from langchain.tools import BaseTool

from langchain_mcp_toolkit.services.client_service import MCPClientService
from langchain_mcp_toolkit.services.server_service import MCPServerService
from langchain_mcp_toolkit.tools import (
    ClientCallToolTool,
    ClientCreateTool,
    ClientGetPromptTool,
    ClientListPromptsTool,
    ClientListResourcesTool,
    ClientListToolsTool,
    ClientReadResourceTool,
    GetLangChainPromptTool,
    GetLangChainToolsTool,
    ServerAddPromptTool,
    ServerAddResourceTool,
    ServerAddToolTool,
    ServerGetUrlTool,
    ServerStartTool,
    ServerStopTool,
)


class MCPToolFactory:
    """
    MCP Tool Factory class, used to create MCP tool instances

    This class is responsible for initializing services and creating tool instances, and is one of the core components of MCPToolkit.
    The factory pattern simplifies the tool creation and management process, allowing users to easily obtain the required tool collections.

    Attributes:
        _client_service: Client service instance
        _server_service: Server service instance

    Example:
        ```python
        # Create factory instance
        factory = MCPToolFactory()

        # Initialize services
        factory.init_client_service()
        factory.init_server_service()

        # Get all tools
        all_tools = factory.create_all_tools()

        # Get specific tools by name
        specific_tools = factory.get_tools_by_names(["server_start", "client_create"])
        ```
    """

    def __init__(self) -> None:
        """
        Initialize tool factory

        Creates a new tool factory instance, but does not automatically initialize any services.
        Need to call init_client_service and init_server_service methods separately.
        """
        self._client_service: MCPClientService | None = None
        self._server_service: MCPServerService | None = None

    @property
    def client_service(self) -> MCPClientService | None:
        """
        Get client service instance

        Returns:
            MCPClientService | None: Client service instance, returns None if not created

        Example:
            ```python
            factory = MCPToolFactory()

            # Check if client service is initialized
            if factory.client_service is None:
                factory.init_client_service()

            # Use client service
            client_service = factory.client_service
            ```
        """
        return self._client_service

    @property
    def server_service(self) -> MCPServerService | None:
        """
        Get server service instance

        Returns:
            MCPServerService | None: Server service instance, returns None if not created

        Example:
            ```python
            factory = MCPToolFactory()

            # Check if server service is initialized
            if factory.server_service is None:
                factory.init_server_service()

            # Use server service
            server_service = factory.server_service
            ```
        """
        return self._server_service

    def init_client_service(self) -> MCPClientService:
        """
        Initialize client service

        Creates and initializes a new MCPClientService instance.

        Returns:
            MCPClientService: Initialized client service instance

        Example:
            ```python
            factory = MCPToolFactory()
            client_service = factory.init_client_service()

            # Use client service
            await client_service.create("http://localhost:8000")
            ```
        """
        client_service = MCPClientService()
        self._client_service = client_service
        return client_service

    def init_server_service(self) -> MCPServerService:
        """
        Initialize server service

        Creates and initializes a new MCPServerService instance.

        Returns:
            MCPServerService: Initialized server service instance

        Example:
            ```python
            factory = MCPToolFactory()
            server_service = factory.init_server_service()

            # Use server service
            await server_service.start("localhost", 8000)
            ```
        """
        server_service = MCPServerService()
        self._server_service = server_service
        return server_service

    def create_client_tools(self) -> list[BaseTool]:
        """
        Create all client tools

        Creates and returns a list of all available client tools, including tools for creating clients, calling tools,
        operating on resources and prompts, etc.

        Returns:
            list[BaseTool]: List of client tools

        Raises:
            ValueError: If client service is not initialized

        Example:
            ```python
            factory = MCPToolFactory()
            factory.init_client_service()

            # Get all client tools
            client_tools = factory.create_client_tools()

            # Use tools
            client_create_tool = client_tools[0]
            await client_create_tool.invoke({"url": "http://localhost:8000"})
            ```
        """
        if not self._client_service:
            raise ValueError("Client service not initialized, please call init_client_service first")


        client_tools: list[BaseTool] = [
            ClientCreateTool(client_service=self._client_service),
            ClientCallToolTool(client_service=self._client_service),
            ClientListToolsTool(client_service=self._client_service),
            ClientListResourcesTool(client_service=self._client_service),
            ClientReadResourceTool(client_service=self._client_service),
            ClientListPromptsTool(client_service=self._client_service),
            ClientGetPromptTool(client_service=self._client_service),
            GetLangChainToolsTool(client_service=self._client_service),
            GetLangChainPromptTool(client_service=self._client_service),
        ]

        return client_tools

    def create_server_tools(self) -> list[BaseTool]:
        """
        Create all server tools

        Creates and returns a list of all available server tools, including tools for starting and stopping servers,
        adding tools, resources, and prompts.

        Returns:
            list[BaseTool]: List of server tools

        Raises:
            ValueError: If server service is not initialized

        Example:
            ```python
            factory = MCPToolFactory()
            factory.init_server_service()

            # Get all server tools
            server_tools = factory.create_server_tools()

            # Use tools
            server_start_tool = server_tools[0]
            await server_start_tool.invoke({"host": "localhost", "port": 8000})
            ```
        """
        if not self._server_service:
            raise ValueError("Server service not initialized, please call init_server_service first")

        server_tools: list[BaseTool] = [
            ServerStartTool(server_service=self._server_service),
            ServerStopTool(server_service=self._server_service),
            ServerGetUrlTool(server_service=self._server_service),
            ServerAddToolTool(server_service=self._server_service),
            ServerAddResourceTool(server_service=self._server_service),
            ServerAddPromptTool(server_service=self._server_service),
        ]

        return server_tools

    def create_all_tools(self) -> list[BaseTool]:
        """
        Create all tools

        Creates and returns a list of all available tools, including both client and server tools.
        If a service is not initialized, its tools will not be included.

        Returns:
            list[BaseTool]: List of all tools

        Example:
            ```python
            factory = MCPToolFactory()

            # Initialize both services
            factory.init_client_service()
            factory.init_server_service()

            # Get all tools
            all_tools = factory.create_all_tools()

            # Use tools
            server_start_tool = [t for t in all_tools if t.name == "server_start"][0]
            await server_start_tool.invoke({"host": "localhost", "port": 8000})
            ```
        """
        tools: list[BaseTool] = []

        if self._client_service:
            tools.extend(self.create_client_tools())

        if self._server_service:
            tools.extend(self.create_server_tools())

        return tools

    def get_tools_by_names(self, names: list[str]) -> list[BaseTool]:
        """
        Get tools by names

        Returns a list of tools matching the specified names.
        If a tool is not found, it will be skipped.

        Args:
            names: List of tool names to retrieve

        Returns:
            list[BaseTool]: List of found tools

        Example:
            ```python
            factory = MCPToolFactory()

            # Initialize both services
            factory.init_client_service()
            factory.init_server_service()

            # Get all tools
            all_tools = factory.create_all_tools()

            # Use tools
            server_start_tool = [t for t in all_tools if t.name == "server_start"][0]
            await server_start_tool.invoke({"host": "localhost", "port": 8000})
            ```
        """
        all_tools = self.create_all_tools()
        result: list[BaseTool] = []

        for name in names:
            matching_tools = [tool for tool in all_tools if tool.name == name]
            if matching_tools:
                result.append(matching_tools[0])

        return result
