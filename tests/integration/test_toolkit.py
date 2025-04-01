"""Toolkit Integration Tests"""

from unittest.mock import MagicMock, patch

import pytest
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage

from langchain_mcp_toolkit.factory import MCPToolFactory
from langchain_mcp_toolkit.services.client_service import MCPClientService
from langchain_mcp_toolkit.services.server_service import MCPServerService
from langchain_mcp_toolkit.toolkit import MCPToolkit


class TestMCPToolkit:
    """Test MCPToolkit class"""

    def test_initialization_client_mode(self) -> None:
        """Test initializing toolkit in client mode"""
        with patch.object(MCPToolFactory, "init_client_service") as mock_init_client:
            with patch.object(MCPToolFactory, "init_server_service") as mock_init_server:
                toolkit = MCPToolkit(mode="client")

                assert toolkit.mode == "client"
                mock_init_client.assert_called_once()
                mock_init_server.assert_not_called()

    def test_initialization_server_mode(self) -> None:
        """Test initializing toolkit in server mode"""
        with patch.object(MCPToolFactory, "init_client_service") as mock_init_client:
            with patch.object(MCPToolFactory, "init_server_service") as mock_init_server:
                toolkit = MCPToolkit(mode="server")

                assert toolkit.mode == "server"
                mock_init_client.assert_not_called()
                mock_init_server.assert_called_once()

    def test_initialization_client_and_server_mode(self) -> None:
        """Test initializing toolkit in client and server mode"""
        with patch.object(MCPToolFactory, "init_client_service") as mock_init_client:
            with patch.object(MCPToolFactory, "init_server_service") as mock_init_server:
                toolkit = MCPToolkit(mode="client_and_server")

                assert toolkit.mode == "client_and_server"
                mock_init_client.assert_called_once()
                mock_init_server.assert_called_once()

    def test_get_tools_client_mode(self) -> None:
        """Test getting tools in client mode"""
        mock_tools = [MagicMock(spec=BaseTool) for _ in range(3)]

        with patch.object(
            MCPToolFactory, "create_client_tools", return_value=mock_tools
        ) as mock_create_client:
            with patch.object(MCPToolFactory, "create_server_tools") as mock_create_server:
                with patch.object(MCPToolFactory, "create_all_tools") as mock_create_all:
                    toolkit = MCPToolkit(mode="client")
                    tools = toolkit.get_tools()

                    assert tools == mock_tools
                    mock_create_client.assert_called_once()
                    mock_create_server.assert_not_called()
                    mock_create_all.assert_not_called()

    def test_get_tools_server_mode(self) -> None:
        """Test getting tools in server mode"""
        mock_tools = [MagicMock(spec=BaseTool) for _ in range(3)]

        with patch.object(MCPToolFactory, "create_client_tools") as mock_create_client:
            with patch.object(
                MCPToolFactory, "create_server_tools", return_value=mock_tools
            ) as mock_create_server:
                with patch.object(MCPToolFactory, "create_all_tools") as mock_create_all:
                    toolkit = MCPToolkit(mode="server")
                    tools = toolkit.get_tools()

                    assert tools == mock_tools
                    mock_create_client.assert_not_called()
                    mock_create_server.assert_called_once()
                    mock_create_all.assert_not_called()

    def test_get_tools_client_and_server_mode(self) -> None:
        """Test getting tools in client and server mode"""
        mock_tools = [MagicMock(spec=BaseTool) for _ in range(5)]

        with patch.object(MCPToolFactory, "create_client_tools") as mock_create_client:
            with patch.object(MCPToolFactory, "create_server_tools") as mock_create_server:
                with patch.object(
                    MCPToolFactory, "create_all_tools", return_value=mock_tools
                ) as mock_create_all:
                    toolkit = MCPToolkit(mode="client_and_server")
                    tools = toolkit.get_tools()

                    assert tools == mock_tools
                    mock_create_client.assert_not_called()
                    mock_create_server.assert_not_called()
                    mock_create_all.assert_called_once()

    def test_get_client_service(self) -> None:
        """Test getting client service"""
        mock_client_service = MagicMock(spec=MCPClientService)

        with patch.object(
            MCPToolkit, "get_client_service", return_value=mock_client_service
        ) as mock_get_client:
            toolkit = MCPToolkit(mode="client")
            client_service = toolkit.get_client_service()

            assert client_service == mock_client_service
            mock_get_client.assert_called_once()

    def test_get_client_service_invalid_mode(self) -> None:
        """Test getting client service in invalid mode"""
        toolkit = MCPToolkit(mode="server")
        with pytest.raises(ValueError, match="Current mode 'server' does not support client services"):
            toolkit.get_client_service()

    def test_get_server_service(self) -> None:
        """Test getting server service"""
        mock_server_service = MagicMock(spec=MCPServerService)

        with patch.object(
            MCPToolkit, "get_server_service", return_value=mock_server_service
        ) as mock_get_server:
            toolkit = MCPToolkit(mode="server")
            server_service = toolkit.get_server_service()

            assert server_service == mock_server_service
            mock_get_server.assert_called_once()

    def test_get_server_service_invalid_mode(self) -> None:
        """Test getting server service in invalid mode"""
        toolkit = MCPToolkit(mode="client")
        with pytest.raises(ValueError, match="Current mode 'client' does not support server services"):
            toolkit.get_server_service()

    def test_get_tools_by_names(self) -> None:
        """Test getting tools by names"""
        mock_tools = [MagicMock(spec=BaseTool) for _ in range(2)]

        with patch.object(
            MCPToolFactory, "get_tools_by_names", return_value=mock_tools
        ) as mock_get_tools:
            toolkit = MCPToolkit()

            # Patch tools with specific names
            with patch.object(toolkit.factory, "_client_service", create=True):
                with patch.object(toolkit.factory, "_server_service", create=True):
                    tools = toolkit.get_tools_by_names(["tool1", "tool2"])

                    assert tools == mock_tools
                    mock_get_tools.assert_called_once_with(["tool1", "tool2"])

    def test_from_client(self) -> None:
        """Test creating toolkit from client"""
        with patch("langchain_mcp_toolkit.toolkit.MCPToolkit.__init__") as mock_init:
            mock_init.return_value = None

            MCPToolkit.from_client()

            mock_init.assert_called_once_with(mode="client")

    def test_from_server(self) -> None:
        """Test creating toolkit from server"""
        with patch("langchain_mcp_toolkit.toolkit.MCPToolkit.__init__") as mock_init:
            mock_init.return_value = None

            MCPToolkit.from_server()

            mock_init.assert_called_once_with(mode="server")

    def test_from_server_and_api_key(self) -> None:
        """Test creating toolkit from server URL and API key"""
        mock_toolkit = MagicMock(spec=MCPToolkit)

        with patch(
            "langchain_mcp_toolkit.toolkit.MCPToolkit",
            return_value=mock_toolkit,
        ) as mock_init:
            result = MCPToolkit.from_server_and_api_key(
                "http://localhost:8000", "api_key_123"
            )

            mock_init.assert_called_once_with(
                mode="client",
                server_url="http://localhost:8000",
                api_key="api_key_123",
            )
            assert result == mock_toolkit

    def test_from_api_key(self) -> None:
        """Test creating toolkit from API key"""
        mock_toolkit = MagicMock(spec=MCPToolkit)

        with patch(
            "langchain_mcp_toolkit.toolkit.MCPToolkit",
            return_value=mock_toolkit,
        ) as mock_init:
            result = MCPToolkit.from_api_key("api_key_123")

            mock_init.assert_called_once_with(
                mode="client",
                api_key="api_key_123",
            )
            assert result == mock_toolkit

    @pytest.mark.asyncio
    async def test_get_langchain_tools(self) -> None:
        """Test getting LangChain tools"""
        mock_tools = [MagicMock(spec=BaseTool) for _ in range(3)]
        mock_client = MagicMock()
        mock_client_service = MagicMock(spec=MCPClientService)
        mock_client_service.client = mock_client

        with patch.object(MCPToolkit, "get_client_service", return_value=mock_client_service):
            with patch(
                "langchain_mcp_toolkit.services.adapters.MCPAdapterService.load_tools_from_session",
                return_value=mock_tools,
            ) as mock_load:
                toolkit = MCPToolkit(mode="client")
                result = await toolkit.get_langchain_tools()

                mock_load.assert_called_once_with(mock_client)
                assert result == mock_tools

    @pytest.mark.asyncio
    async def test_get_langchain_tools_invalid_mode(self) -> None:
        """Test getting LangChain tools in invalid mode"""
        toolkit = MCPToolkit(mode="server")

        with pytest.raises(ValueError, match="Current mode 'server' does not support client services"):
            await toolkit.get_langchain_tools()

    @pytest.mark.asyncio
    async def test_get_tools_from_multiple_servers(self) -> None:
        """Test getting tools from multiple servers"""
        mock_tools = [MagicMock(spec=BaseTool) for _ in range(3)]
        mock_client = MagicMock()
        server_urls = {
            "server1": "http://localhost:8000",
            "server2": "http://localhost:8001",
        }
        expected_configs = {
            "server1": {"url": "http://localhost:8000", "transport": "sse"},
            "server2": {"url": "http://localhost:8001", "transport": "sse"},
        }

        with patch(
            "langchain_mcp_toolkit.services.adapters.MCPAdapterService.create_multi_server_client",
            return_value=mock_client,
        ) as mock_create:
            with patch(
                "langchain_mcp_toolkit.services.adapters.MCPAdapterService.load_tools_from_session",
                return_value=mock_tools,
            ) as mock_load:
                toolkit = MCPToolkit()
                result = await toolkit.get_tools_from_multiple_servers(server_urls)

                mock_create.assert_called_once_with(expected_configs)
                mock_load.assert_called_once_with(mock_client)
                assert result == mock_tools

    @pytest.mark.asyncio
    async def test_create_multi_server_client(self) -> None:
        """Test creating multi-server client"""
        mock_client = MagicMock()
        server_urls = {
            "server1": "http://localhost:8000",
            "server2": "http://localhost:8001",
        }
        expected_configs = {
            "server1": {"url": "http://localhost:8000", "transport": "sse"},
            "server2": {"url": "http://localhost:8001", "transport": "sse"},
        }

        with patch(
            "langchain_mcp_toolkit.services.adapters.MCPAdapterService.create_multi_server_client",
            return_value=mock_client,
        ) as mock_create:
            toolkit = MCPToolkit()
            result = await toolkit.create_multi_server_client(server_urls)

            mock_create.assert_called_once_with(expected_configs)
            assert result == mock_client

    @pytest.mark.asyncio
    async def test_load_prompt(self) -> None:
        """Test loading prompt"""
        mock_messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
        mock_client = MagicMock()
        mock_client_service = MagicMock(spec=MCPClientService)
        mock_client_service.client = mock_client

        with patch.object(MCPToolkit, "get_client_service", return_value=mock_client_service):
            with patch(
                "langchain_mcp_toolkit.services.adapters.MCPAdapterService.load_prompt_from_session",
                return_value=mock_messages,
            ) as mock_load:
                toolkit = MCPToolkit(mode="client")
                result = await toolkit.load_prompt("test_prompt", {"key": "value"})

                mock_load.assert_called_once_with(mock_client, "test_prompt", {"key": "value"})
                assert result == mock_messages

    @pytest.mark.asyncio
    async def test_load_prompt_no_arguments(self) -> None:
        """Test loading prompt without arguments"""
        mock_messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
        mock_client = MagicMock()
        mock_client_service = MagicMock(spec=MCPClientService)
        mock_client_service.client = mock_client

        with patch.object(MCPToolkit, "get_client_service", return_value=mock_client_service):
            with patch(
                "langchain_mcp_toolkit.services.adapters.MCPAdapterService.load_prompt_from_session",
                return_value=mock_messages,
            ) as mock_load:
                toolkit = MCPToolkit(mode="client")
                result = await toolkit.load_prompt("test_prompt")

                mock_load.assert_called_once_with(mock_client, "test_prompt", None)
                assert result == mock_messages

    @pytest.mark.asyncio
    async def test_load_prompt_invalid_mode(self) -> None:
        """Test loading prompt in invalid mode"""
        toolkit = MCPToolkit(mode="server")

        with pytest.raises(ValueError, match="Current mode 'server' does not support client services"):
            await toolkit.load_prompt("weather_query")

    def test_get_client_service_with_server_mode(self) -> None:
        """Test getting client service in server mode"""
        toolkit = MCPToolkit(mode="server")
        with pytest.raises(ValueError, match="Current mode 'server' does not support client services"):
            toolkit.get_client_service()

    def test_get_server_service_with_client_mode(self) -> None:
        """Test getting server service in client mode"""
        toolkit = MCPToolkit(mode="client")
        with pytest.raises(ValueError, match="Current mode 'client' does not support server services"):
            toolkit.get_server_service()
