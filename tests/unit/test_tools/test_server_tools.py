"""Server Tools Test Module"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from langchain_mcp_toolkit.services.server_service import MCPServerService
from langchain_mcp_toolkit.tools.server_tools import (
    ServerAddPromptTool,
    ServerAddResourceTool,
    ServerAddToolTool,
    ServerGetUrlTool,
    ServerStartTool,
    ServerStopTool,
)


class TestServerStartTool:
    """Test ServerStartTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        mock_server_service = MagicMock(spec=MCPServerService)
        tool = ServerStartTool(server_service=mock_server_service)
        assert tool.name == "server_start"
        assert "This tool is used to start an MCP server" in tool.description

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        mock_server_service = AsyncMock(spec=MCPServerService)
        mock_server_service.async_start_server.return_value = "Server started"
        tool = ServerStartTool(server_service=mock_server_service)

        result = await tool._run("localhost", 8000)
        assert result == "Server started"
        mock_server_service.async_start_server.assert_called_once_with(
            "localhost", 8000
        )


class TestServerStopTool:
    """Test ServerStopTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        mock_server_service = MagicMock(spec=MCPServerService)
        tool = ServerStopTool(server_service=mock_server_service)
        assert tool.name == "server_stop"
        assert "This tool is used to stop the currently running MCP server" in tool.description

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        mock_server_service = AsyncMock(spec=MCPServerService)
        mock_server_service.async_stop_server.return_value = "Server stopped"
        tool = ServerStopTool(server_service=mock_server_service)

        result = await tool._run()
        assert result == "Server stopped"
        mock_server_service.async_stop_server.assert_called_once()


class TestServerGetUrlTool:
    """Test ServerGetUrlTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        mock_server_service = MagicMock(spec=MCPServerService)
        tool = ServerGetUrlTool(server_service=mock_server_service)
        assert tool.name == "server_get_url"
        assert "This tool is used to get the URL of the currently running MCP server" in tool.description

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        mock_server_service = AsyncMock(spec=MCPServerService)
        mock_server_service.async_get_url.return_value = "http://localhost:8000"
        tool = ServerGetUrlTool(server_service=mock_server_service)

        result = await tool._run()
        assert result == "http://localhost:8000"
        mock_server_service.async_get_url.assert_called_once()


class TestServerAddToolTool:
    """Test ServerAddToolTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        mock_server_service = MagicMock(spec=MCPServerService)
        tool = ServerAddToolTool(server_service=mock_server_service)
        assert tool.name == "server_add_tool"
        assert "This tool is used to add a tool to the MCP server" in tool.description

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        mock_server_service = AsyncMock(spec=MCPServerService)
        mock_server_service.async_add_tool.return_value = "Tool added"
        tool = ServerAddToolTool(server_service=mock_server_service)

        result = await tool._run("test_tool", "Test tool", "return 'Hello'")
        assert result == "Tool added"
        mock_server_service.async_add_tool.assert_called_once_with(
            "test_tool", "Test tool", "return 'Hello'", "python"
        )


class TestServerAddResourceTool:
    """Test ServerAddResourceTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        mock_server_service = MagicMock(spec=MCPServerService)
        tool = ServerAddResourceTool(server_service=mock_server_service)
        assert tool.name == "server_add_resource"
        assert "This tool is used to add a resource to the MCP server" in tool.description

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        mock_server_service = AsyncMock(spec=MCPServerService)
        mock_server_service.async_add_resource.return_value = "Resource added"
        tool = ServerAddResourceTool(server_service=mock_server_service)

        result = await tool._run("test_resource", {"content": "Resource content"}, "Test resource")
        assert result == "Resource added"
        mock_server_service.async_add_resource.assert_called_once_with(
            "test_resource", {"content": "Resource content"}, "Test resource"
        )


class TestServerAddPromptTool:
    """Test ServerAddPromptTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        mock_server_service = MagicMock(spec=MCPServerService)
        tool = ServerAddPromptTool(server_service=mock_server_service)
        assert tool.name == "server_add_prompt"
        assert "This tool is used to add prompt templates to the MCP server" in tool.description

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        mock_server_service = AsyncMock(spec=MCPServerService)
        mock_server_service.async_add_prompt.return_value = "Prompt added"
        tool = ServerAddPromptTool(server_service=mock_server_service)

        result = await tool._run("test_prompt", "This is a test prompt")
        assert result == "Prompt added"
        mock_server_service.async_add_prompt.assert_called_once_with(
            "test_prompt", "This is a test prompt"
        )
