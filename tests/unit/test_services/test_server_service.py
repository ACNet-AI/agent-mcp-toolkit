"""Server Service Unit Tests"""

from unittest.mock import MagicMock, patch

import pytest
import importlib

from langchain_mcp_toolkit.services.server_service import MCPServerService, ServerProtocol


class TestMCPServerService:
    """Test MCPServerService class"""

    def test_initialization(self) -> None:
        """Test service initialization"""
        service = MCPServerService()
        assert isinstance(service._server, ServerProtocol)
        assert service._is_running is False
        assert service._host == "localhost"
        assert service._port == 8000

    def test_server_property_without_server(self) -> None:
        """Test getting server property without server instance"""
        service = MCPServerService()

        # First set _server to None to test the server property getter
        original_server = service._server
        service._server = None

        with patch.object(service, "_create_default_server") as mock_create:
            mock_instance = MagicMock()
            mock_create.return_value = mock_instance

            server = service.server

            assert server == mock_instance
            mock_create.assert_called_once()

        # Restore original server instance
        service._server = original_server

    def test_create_default_server(self) -> None:
        """Test creating default server"""
        # Use patch to replace MCPServerClass for testing
        with patch("langchain_mcp_toolkit.services.server_service.MCPServerClass") as mock_server_class:
            mock_instance = MagicMock()
            mock_server_class.return_value = mock_instance

            # Call static method _create_default_server directly without creating service instance
            # This avoids MCPServerClass being called twice
            server = MCPServerService._create_default_server(None)  # None as self parameter

            mock_server_class.assert_called_once()
            assert server == mock_instance

    @patch('langchain_mcp_toolkit.services.server_service.MCPServerClass', side_effect=ImportError("Test import error"))
    def test_create_default_server_import_error(self, mock_server_class: MagicMock) -> None:
        """Test import error when creating default server"""
        with pytest.raises(RuntimeError, match="Failed to create default MCP server"):
            MCPServerService._create_default_server(None)  # None as self parameter

    @patch('langchain_mcp_toolkit.services.server_service.MCPServerClass', side_effect=Exception("Other error"))
    def test_create_default_server_other_error(self, mock_server_class: MagicMock) -> None:
        """Test other error when creating default server"""
        with pytest.raises(RuntimeError, match="Failed to create default MCP server"):
            MCPServerService._create_default_server(None)  # None as self parameter

    def test_start(self) -> None:
        """Test starting server"""
        service = MCPServerService()
        mock_server = MagicMock()
        service._server = mock_server

        result = service.start("localhost", 8000)

        mock_server.start.assert_called_once_with(host="localhost", port=8000)
        assert service._is_running is True
        assert service._host == "localhost"
        assert service._port == 8000
        assert "Server started at http://localhost:8000" == result

    def test_start_already_running(self) -> None:
        """Test starting an already running server"""
        service = MCPServerService()
        service._is_running = True
        service._host = "localhost"
        service._port = 8000

        result = service.start()

        assert "Server is already running: http://localhost:8000" == result

    def test_start_exception(self) -> None:
        """Test exception when starting server"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.start.side_effect = Exception("Start failed")
        service._server = mock_server

        with pytest.raises(RuntimeError, match="Failed to start server: Start failed"):
            service.start("localhost", 8000)

        assert service._is_running is False

    def test_stop(self) -> None:
        """Test stopping server"""
        service = MCPServerService()
        mock_server = MagicMock()
        service._server = mock_server
        service._is_running = True

        result = service.stop()

        mock_server.stop.assert_called_once()
        assert service._is_running is False
        assert "Server stopped" == result

    def test_stop_not_running(self) -> None:
        """Test stopping a server that is not running"""
        service = MCPServerService()
        service._is_running = False

        result = service.stop()

        assert "Server is not currently running" == result

    def test_stop_exception(self) -> None:
        """Test exception when stopping server"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.stop.side_effect = Exception("Stop failed")
        service._server = mock_server
        service._is_running = True

        with pytest.raises(RuntimeError, match="Failed to stop server: Stop failed"):
            service.stop()

    def test_get_url(self) -> None:
        """Test getting server URL"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.get_url.return_value = "http://localhost:8000"
        service._server = mock_server
        service._is_running = True
        service._host = "localhost"
        service._port = 8000

        result = service.get_url()

        mock_server.get_url.assert_called_once()
        assert result == "http://localhost:8000"

    def test_get_url_not_running(self) -> None:
        """Test getting URL of a server that is not running"""
        service = MCPServerService()
        service._is_running = False

        result = service.get_url()

        assert result == "Server is not currently running"

    def test_get_url_exception(self) -> None:
        """Test exception when getting URL"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.get_url.side_effect = Exception("Failed to get URL")
        service._server = mock_server
        service._is_running = True

        with pytest.raises(RuntimeError, match="Failed to get server URL: Failed to get URL"):
            service.get_url()

    def test_get_url_no_url(self) -> None:
        """Test getting URL when it returns None"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.get_url.return_value = None
        service._server = mock_server
        service._is_running = True
        service._host = "localhost"
        service._port = 8000

        result = service.get_url()

        mock_server.get_url.assert_called_once()
        assert result == "http://localhost:8000"

    def test_is_running(self) -> None:
        """Test is_running method"""
        service = MCPServerService()
        service._is_running = True
        assert service.is_running() is True

        service._is_running = False
        assert service.is_running() is False

    def test_add_tool(self) -> None:
        """Test adding tool"""
        service = MCPServerService()
        mock_server = MagicMock()
        service._server = mock_server
        service._is_running = True

        # 模拟_compile_tool_code方法
        mock_tool_func = MagicMock()
        with patch.object(
            service, "_compile_tool_code", return_value=mock_tool_func
        ) as mock_compile:
            result = service.add_tool("test_tool", "Test tool", "return 'Hello'", "python")

            mock_compile.assert_called_once_with("test_tool", "return 'Hello'")
            mock_server.add_tool.assert_called_once_with("test_tool", mock_tool_func, "Test tool")
            assert result == "Tool 'test_tool' added to server"

    def test_add_tool_server_not_running(self) -> None:
        """Test adding tool when server is not running"""
        service = MCPServerService()
        service._is_running = False

        result = service.add_tool("test_tool", "Test tool", "return 'Hello'")

        assert result == "Error: Server is not currently running, please start the server first"

    def test_add_tool_exception(self) -> None:
        """Test exception when adding tool"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.add_tool.side_effect = Exception("Add tool failed")
        service._server = mock_server
        service._is_running = True

        with patch.object(service, "_compile_tool_code", return_value=MagicMock()):
            with pytest.raises(RuntimeError, match="Failed to add tool: Add tool failed"):
                service.add_tool("test_tool", "Test tool", "return 'Hello'")

    def test_add_resource(self) -> None:
        """Test adding resource"""
        service = MCPServerService()
        mock_server = MagicMock()
        service._server = mock_server
        service._is_running = True

        result = service.add_resource("test_resource", "Test resource content")

        mock_server.add_resource.assert_called_once_with("test_resource", "Test resource content")
        assert result == "Resource 'test_resource' added to server"

    def test_add_resource_dict(self) -> None:
        """Test adding dictionary resource"""
        service = MCPServerService()
        mock_server = MagicMock()
        service._server = mock_server
        service._is_running = True

        test_dict = {"key": "value"}
        result = service.add_resource("test_resource", test_dict)

        mock_server.add_resource.assert_called_once_with("test_resource", test_dict)
        assert result == "Resource 'test_resource' added to server"

    def test_add_resource_server_not_running(self) -> None:
        """Test adding resource when server is not running"""
        service = MCPServerService()
        service._is_running = False

        result = service.add_resource("test_resource", "Test resource content")

        assert result == "Error: Server is not currently running, please start the server first"

    def test_add_resource_exception(self) -> None:
        """Test exception when adding resource"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.add_resource.side_effect = Exception("Add resource failed")
        service._server = mock_server
        service._is_running = True

        with pytest.raises(RuntimeError, match="Failed to add resource: Add resource failed"):
            service.add_resource("test_resource", "Test resource content")

    def test_add_prompt(self) -> None:
        """Test adding prompt"""
        service = MCPServerService()
        mock_server = MagicMock()
        service._server = mock_server
        service._is_running = True

        result = service.add_prompt("test_prompt", "Test prompt content")

        mock_server.add_prompt.assert_called_once_with("test_prompt", "Test prompt content")
        assert result == "Prompt 'test_prompt' added to server"

    def test_add_prompt_server_not_running(self) -> None:
        """Test adding prompt when server is not running"""
        service = MCPServerService()
        service._is_running = False

        result = service.add_prompt("test_prompt", "Test prompt content")

        assert result == "Error: Server is not currently running, please start the server first"

    def test_add_prompt_exception(self) -> None:
        """Test exception when adding prompt"""
        service = MCPServerService()
        mock_server = MagicMock()
        mock_server.add_prompt.side_effect = Exception("Add prompt failed")
        service._server = mock_server
        service._is_running = True

        with pytest.raises(RuntimeError, match="Failed to add prompt: Add prompt failed"):
            service.add_prompt("test_prompt", "Test prompt content")

    def test_compile_tool_code(self) -> None:
        """Test compiling tool code"""
        service = MCPServerService()

        # Test simple tool function compilation
        test_code = "return len(kwargs.get('text', ''))"
        tool_func = service._compile_tool_code("test_tool", test_code)

        # Verify compiled function works normally
        result = tool_func(text="Hello")
        assert result == 5

    def test_compile_tool_code_with_json(self) -> None:
        """Test compiling tool code using json module"""
        service = MCPServerService()

        test_code = "return json.dumps({'result': kwargs.get('value', 0)})"
        tool_func = service._compile_tool_code("json_tool", test_code)

        # Verify compiled function works normally and uses json module
        result = tool_func(value=42)
        assert result == '{"result": 42}'

    @pytest.mark.asyncio
    async def test_async_start_server(self) -> None:
        """Test asynchronous server start"""
        service = MCPServerService()

        with patch.object(
            service, "start", return_value="Server started at http://localhost:8000"
        ) as mock_start:
            result = await service.async_start_server("localhost", 8000)

            mock_start.assert_called_once_with("localhost", 8000)
            assert result == "Server started at http://localhost:8000"

    @pytest.mark.asyncio
    async def test_async_stop_server(self) -> None:
        """Test asynchronous server stop"""
        service = MCPServerService()

        with patch.object(service, "stop", return_value="Server stopped") as mock_stop:
            result = await service.async_stop_server()

            mock_stop.assert_called_once()
            assert result == "Server stopped"

    def test_create_custom_server_unsupported(self) -> None:
        """Test creating unsupported custom server type"""
        with pytest.raises(RuntimeError, match="Unsupported server type"):
            MCPServerService._create_custom_server(None, "unsupported")  # None as self parameter

    def test_create_custom_server_import_error(self) -> None:
        """Test import error when creating custom server"""
        # Mock import error
        with patch("langchain_mcp_toolkit.services.server_service.MCPServerService._create_custom_server",
                  side_effect=ImportError("Import error")):
            # Create service
            with pytest.raises(RuntimeError, match="Failed to create MCP server"):
                MCPServerService(server_type="custom_type")

    def test_create_custom_server_fastmcp_import_error(self) -> None:
        """Test import error when creating FastMCP server"""

        # Define import error mock
        def mock_import_error(name, *args, **kwargs):
            if "mcp.server.fastmcp" in name:
                raise ImportError("Failed to import FastMCP")
            return importlib.__import__(name, *args, **kwargs)

        # Test with patched import function
        with patch("builtins.__import__", side_effect=mock_import_error):
            with pytest.raises(RuntimeError, match="Failed to import server type 'fastmcp'"):
                MCPServerService._create_custom_server(None, "fastmcp")  # None as self parameter

    def test_create_custom_server_other_error(self) -> None:
        """Test other error when creating custom server"""
        # Mock other error
        with patch("langchain_mcp_toolkit.services.server_service.MCPServerService._create_custom_server",
                  side_effect=Exception("Other error")):
            # Create service
            with pytest.raises(RuntimeError, match="Failed to create MCP server"):
                MCPServerService(server_type="custom_type")

    def test_create_fastmcp_server_other_error(self) -> None:
        """Test other error when creating FastMCP server"""
        with patch("mcp.server.fastmcp.FastMCP", side_effect=Exception("Failed to create FastMCP")):
            with pytest.raises(RuntimeError, match="Failed to create server type 'fastmcp'"):
                MCPServerService._create_custom_server(None, "fastmcp")  # None as self parameter

    @pytest.mark.asyncio
    async def test_async_start_server_success(self) -> None:
        """Test successful async server start"""
        service = MCPServerService()

        with patch.object(service, "start", return_value="Server started at http://localhost:8000") as mock_start:
            result = await service.async_start_server(host="localhost", port=8000)

            mock_start.assert_called_once_with("localhost", 8000)
            assert result == "Server started at http://localhost:8000"

    @pytest.mark.asyncio
    async def test_async_start_server_default_params(self) -> None:
        """Test async server start with default parameters"""
        service = MCPServerService()

        with patch.object(service, "start", return_value="Server started at http://localhost:8000") as mock_start:
            result = await service.async_start_server()

            mock_start.assert_called_once_with("localhost", 8000)
            assert result == "Server started at http://localhost:8000"

    @pytest.mark.asyncio
    async def test_async_start_server_error(self) -> None:
        """Test error during async server start"""
        service = MCPServerService()

        with patch.object(service, "start", side_effect=RuntimeError("Failed to start server")):
            with pytest.raises(RuntimeError, match="Failed to start server"):
                await service.async_start_server()

    def test_server_protocol_methods(self) -> None:
        """Test ServerProtocol class methods"""
        protocol = ServerProtocol()

        # Test initialization
        protocol.__init__()

        # Test start method
        protocol.start("localhost", 8000)

        # Test stop method
        protocol.stop()

        # Test get_url method
        assert protocol.get_url() == ""

        # Test add_tool method
        protocol.add_tool("test_tool", lambda: None, "Test tool")

        # Test add_resource method
        protocol.add_resource("test_resource", {}, "Test resource")

        # Test add_prompt method
        protocol.add_prompt("test_prompt", "Test content", "Test prompt")

    @pytest.mark.asyncio
    async def test_async_get_url(self) -> None:
        """Test async get URL"""
        service = MCPServerService()
        service._is_running = True

        with patch.object(service, "get_url", return_value="http://localhost:8000") as mock_get_url:
            result = await service.async_get_url()

            mock_get_url.assert_called_once()
            assert result == "http://localhost:8000"

    @pytest.mark.asyncio
    async def test_async_get_url_error(self) -> None:
        """Test error during async get URL"""
        service = MCPServerService()

        with patch.object(service, "get_url", side_effect=RuntimeError("Failed to get URL")):
            with pytest.raises(RuntimeError, match="Failed to get URL"):
                await service.async_get_url()

    @pytest.mark.asyncio
    async def test_async_add_tool(self) -> None:
        """Test async add tool"""
        service = MCPServerService()

        with patch.object(service, "add_tool", return_value="Tool added") as mock_add_tool:
            result = await service.async_add_tool("test_tool", "Test tool", "def test(): pass")

            mock_add_tool.assert_called_once_with("test_tool", "Test tool", "def test(): pass", "python")
            assert result == "Tool added"

    @pytest.mark.asyncio
    async def test_async_add_resource(self) -> None:
        """Test async add resource"""
        service = MCPServerService()

        with patch.object(service, "add_resource", return_value="Resource added") as mock_add_resource:
            result = await service.async_add_resource("test_resource", {"data": "value"}, "Test resource")

            mock_add_resource.assert_called_once_with("test_resource", {"data": "value"}, "Test resource")
            assert result == "Resource added"

    @pytest.mark.asyncio
    async def test_async_add_prompt(self) -> None:
        """Test async add prompt"""
        service = MCPServerService()

        with patch.object(service, "add_prompt", return_value="Prompt added") as mock_add_prompt:
            result = await service.async_add_prompt("test_prompt", "Test content", "Test prompt")

            mock_add_prompt.assert_called_once_with("test_prompt", "Test content", "Test prompt")
            assert result == "Prompt added"

    def test_create_with_server_type(self) -> None:
        """Test creating service with custom server type"""
        with patch("langchain_mcp_toolkit.services.server_service.MCPServerService._create_custom_server") as mock_create_custom:
            # Create service with server_type
            # Remove unused variable service
            MCPServerService(server_type="fastmcp")

            # Verify _create_custom_server method was called
            mock_create_custom.assert_called_once_with("fastmcp")
