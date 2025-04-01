"""Factory Class Unit Test"""


import pytest
from langchain.tools import BaseTool

from langchain_mcp_toolkit.factory import MCPToolFactory
from langchain_mcp_toolkit.services.client_service import MCPClientService
from langchain_mcp_toolkit.services.server_service import MCPServerService


class TestMCPToolFactory:
    """Test MCPToolFactory class"""

    def test_initialization(self) -> None:
        """Test factory initialization"""
        factory = MCPToolFactory()
        assert factory.client_service is None
        assert factory.server_service is None

    def test_init_client_service(self) -> None:
        """Test initializing client service"""
        factory = MCPToolFactory()
        client_service = factory.init_client_service()
        assert factory.client_service is not None
        assert isinstance(client_service, MCPClientService)
        assert factory.client_service == client_service

    def test_init_server_service(self) -> None:
        """Test initializing server service"""
        factory = MCPToolFactory()
        server_service = factory.init_server_service()
        assert factory.server_service is not None
        assert isinstance(server_service, MCPServerService)
        assert factory.server_service == server_service

    def test_create_client_tools_without_initialization(self) -> None:
        """Test creating client tools without initializing client service"""
        factory = MCPToolFactory()
        with pytest.raises(ValueError, match="Client service not initialized"):
            factory.create_client_tools()

    def test_create_server_tools_without_initialization(self) -> None:
        """Test creating server tools without initializing server service"""
        factory = MCPToolFactory()
        with pytest.raises(ValueError, match="Server service not initialized"):
            factory.create_server_tools()

    def test_create_client_tools(self) -> None:
        """Test creating client tools"""
        factory = MCPToolFactory()
        factory.init_client_service()
        client_tools = factory.create_client_tools()

        assert isinstance(client_tools, list)
        assert len(client_tools) > 0
        assert all(isinstance(tool, BaseTool) for tool in client_tools)

    def test_create_server_tools(self) -> None:
        """Test creating server tools"""
        factory = MCPToolFactory()
        factory.init_server_service()
        server_tools = factory.create_server_tools()

        assert isinstance(server_tools, list)
        assert len(server_tools) > 0
        assert all(isinstance(tool, BaseTool) for tool in server_tools)

    def test_create_all_tools(self) -> None:
        """Test creating all tools"""
        factory = MCPToolFactory()

        # Need to initialize both services first
        factory.init_client_service()
        factory.init_server_service()

        all_tools = factory.create_all_tools()
        client_tools = factory.create_client_tools()
        server_tools = factory.create_server_tools()

        assert isinstance(all_tools, list)
        assert len(all_tools) == len(client_tools) + len(server_tools)
        assert all(isinstance(tool, BaseTool) for tool in all_tools)

    def test_get_tools_by_names(self) -> None:
        """Test getting tools by names"""
        factory = MCPToolFactory()
        factory.init_client_service()
        factory.init_server_service()

        # Get specific tools
        tool_names = ["client_create", "server_start"]
        tools = factory.get_tools_by_names(tool_names)

        assert isinstance(tools, list)
        assert len(tools) == len(tool_names)
        assert all(isinstance(tool, BaseTool) for tool in tools)
        assert all(tool.name in tool_names for tool in tools)

    def test_get_tools_by_invalid_names(self) -> None:
        """Test getting tools by invalid names"""
        factory = MCPToolFactory()
        factory.init_client_service()
        factory.init_server_service()

        # Test with invalid tool names
        tools = factory.get_tools_by_names(["invalid_tool1", "invalid_tool2"])
        # Should not raise an exception, just return empty list
        assert len(tools) == 0

    def test_create_all_tools_without_client_service(self) -> None:
        """Test creating all tools without client service"""
        factory = MCPToolFactory()
        # Client service is not initialized
        # Server service is initialized
        factory.init_server_service()

        tools = factory.create_all_tools()
        # Should not raise an exception, just return server tools
        assert len(tools) > 0
        assert all(hasattr(tool, "server_service") for tool in tools)

    def test_create_all_tools_without_server_service(self) -> None:
        """Test creating all tools without server service"""
        factory = MCPToolFactory()
        # Client service is initialized
        factory.init_client_service()
        # Server service is not initialized

        tools = factory.create_all_tools()
        # Should not raise an exception, just return client tools
        assert len(tools) > 0
        assert all(hasattr(tool, "client_service") for tool in tools)
