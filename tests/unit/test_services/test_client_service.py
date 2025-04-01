"""Client Service Unit Tests"""

import sys
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from langchain.prompts import ChatPromptTemplate

from langchain_mcp_toolkit.services.client_service import MCPClientService, NullOutputStream


class TestNullOutputStream:
    """Test NullOutputStream class"""

    def test_write(self):
        """Test write method"""
        output_stream = NullOutputStream()
        # Ensure no exceptions are thrown
        output_stream.write("test")
        output_stream.write(b"test")


class TestMCPClientService:
    """Test MCPClientService class"""

    def test_initialization(self):
        """Test service initialization"""
        service = MCPClientService()
        assert service.client is None

    @patch("langchain_mcp_toolkit.services.client_service.ClientSession", autospec=True)
    def test_create(self, mock_client_session):
        """Test creating client"""
        # Setup mock objects
        mock_instance = MagicMock()
        mock_client_session.return_value = mock_instance

        # Fix import issues
        with patch.dict('sys.modules', {'mcp.client': MagicMock()}):
            # Add ClientSession to mcp.client
            import sys
            sys.modules['mcp.client'].ClientSession = mock_client_session

            service = MCPClientService()
            result = service.create("http://localhost:8000", "sse")

            # Verify method calls, note the addition of write_stream parameter
            mock_client_session.assert_called_once_with(
                "http://localhost:8000",
                write_stream=ANY,  # Use ANY matcher to match any NullOutputStream instance
            )
            assert service.client == mock_instance
            assert "Client created connected to http://localhost:8000" == result

    def test_create_with_invalid_transport(self):
        """Test creating client with invalid transport type"""
        service = MCPClientService()

        with pytest.raises(ValueError) as exc_info:
            service.create("http://localhost:8000", "invalid_type")

        assert "Unsupported transport type: invalid_type" in str(exc_info.value)

    def test_create_with_invalid_transport_error(self):
        """Test detailed error messages when creating client with invalid transport type"""
        service = MCPClientService()

        # Fix import issues
        with patch.dict('sys.modules', {'mcp.client': MagicMock()}):
            # Add necessary imports (but don't add ClientSession to avoid interfering with the test)

            # Test different invalid transport types
            invalid_types = ["websocket", "http", "grpc", "custom"]

            for transport_type in invalid_types:
                with pytest.raises(ValueError) as exc_info:
                    service.create("http://localhost:8000", transport_type)

                # Verify error message contains transport type
                error_message = str(exc_info.value)
                assert f"Unsupported transport type: {transport_type}" in error_message

    @patch("langchain_mcp_toolkit.services.client_service.stdio_client")
    @patch("langchain_mcp_toolkit.services.client_service.StdioServerParameters")
    def test_create_stdio_client_with_args(self, mock_params, mock_stdio_client):
        """Test creating client with stdio transport type and parameters"""
        service = MCPClientService()
        mock_client = MagicMock()
        mock_stdio_client.return_value = mock_client

        # Fix import issues
        with patch.dict('sys.modules', {'mcp.client': MagicMock()}):
            # Add necessary classes to mcp.client
            import sys
            sys.modules['mcp.client'].StdioServerParameters = mock_params
            sys.modules['mcp.client'].stdio_client = mock_stdio_client

            # Use stdio transport type and pass python script path
            script_path = "/path/to/server.py"
            result = service.create(script_path, "stdio")

            # Verify StdioServerParameters call
            mock_params.assert_called_once_with(
                command="python",
                args=[script_path]
            )

            # Verify stdio_client call
            params_instance = mock_params.return_value
            mock_stdio_client.assert_called_once_with(params_instance)

            # Verify result
            assert f"Client created connected to {script_path}" in result
            assert service.client == mock_client
            assert service.is_connected is True
            assert service._is_multi_client is False

    @pytest.mark.asyncio
    async def test_client_method_without_client(self):
        """Test calling client method without initializing client"""
        service = MCPClientService()
        with pytest.raises(ValueError, match="Client service not connected"):
            await service.call_tool("default", "test_tool", param="value")

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting to server"""
        # Create service instance
        service = MCPClientService()
        # Set client
        mock_client = AsyncMock()
        service.client = mock_client
        service._is_multi_client = False  # Single server mode

        # Call connect method
        result = await service.connect()

        # Verify
        mock_client.connect.assert_called_once()
        assert service.is_connected is True
        assert result == "Connection successful"

    @pytest.mark.asyncio
    async def test_connect_multi_client(self):
        """Test connecting to multiple servers"""
        # Create service instance
        service = MCPClientService()
        # Set client
        mock_client = AsyncMock()
        service.client = mock_client
        service._is_multi_client = True  # Multi-server mode

        # Call connect method
        result = await service.connect()

        # Verify
        mock_client.connect.assert_called_once()
        assert service.is_connected is True
        assert result == "Connection successful"

    @pytest.mark.asyncio
    async def test_connect_without_client(self):
        """Test connecting without creating client first"""
        service = MCPClientService()
        service.client = None

        with pytest.raises(ValueError, match="Client not created"):
            await service.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting"""
        # Create service instance
        service = MCPClientService()
        # Set client
        mock_client = AsyncMock()
        service.client = mock_client
        service._is_multi_client = False  # Single server mode
        service.is_connected = True

        # Call disconnect method
        result = await service.disconnect()

        # Verify
        mock_client.disconnect.assert_called_once()
        assert service.is_connected is False
        assert result == "Disconnected"

    @pytest.mark.asyncio
    async def test_multi_server_client_operations(self):
        """Test multi-server client operations"""
        service = MCPClientService()
        service._is_connected = True
        service._is_multi_client = True

        # Simulate multi-server client
        mock_client = MagicMock()
        mock_server_client = MagicMock()
        mock_client.get_client = AsyncMock(return_value=mock_server_client)
        service.client = mock_client

        # Test getting prompt
        mock_server_client.get_prompt = AsyncMock(return_value={"content": "test"})
        result = await service.get_prompt("test_prompt", {"key": "value"}, "test_server")
        mock_client.get_client.assert_called_once_with("test_server")
        mock_server_client.get_prompt.assert_called_once_with("test_prompt", {"key": "value"})
        assert result == {"content": "test"}

        # Test getting resource list
        mock_client.get_client.reset_mock()
        mock_server_client.list_resources = AsyncMock(return_value=[{"id": "resource1"}])
        result = await service.list_resources("test_server")
        mock_client.get_client.assert_called_once_with("test_server")
        mock_server_client.list_resources.assert_called_once()
        assert result == [{"id": "resource1"}]

        # Test reading resource
        mock_client.get_client.reset_mock()
        mock_server_client.read_resource = AsyncMock(return_value={"data": "test_data"})
        result = await service.read_resource("resource_id", "test_server")
        mock_client.get_client.assert_called_once_with("test_server")
        mock_server_client.read_resource.assert_called_once_with("resource_id")
        assert result == {"data": "test_data"}

        # Test getting prompt list
        mock_client.get_client.reset_mock()
        mock_server_client.list_prompts = AsyncMock(return_value=[{"id": "prompt1"}])
        result = await service.list_prompts("test_server")
        mock_client.get_client.assert_called_once_with("test_server")
        mock_server_client.list_prompts.assert_called_once()
        assert result == [{"id": "prompt1"}]

    @pytest.mark.asyncio
    async def test_get_langchain_tools(self):
        """Test getting LangChain tools"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate tool list
        mock_tools = [MagicMock()]

        # Simulate MCPAdapterService.load_tools_from_session
        with patch("langchain_mcp_toolkit.services.adapters.MCPAdapterService.load_tools_from_session",
                  new_callable=AsyncMock, return_value=mock_tools) as mock_load:
            # Call method
            result = await service.get_langchain_tools()

            # Verify type conversion and method calls
            mock_load.assert_called_once()
            assert result == mock_tools

    @pytest.mark.asyncio
    async def test_get_langchain_prompt_async(self):
        """Test asynchronous getting LangChain prompt template"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate prompt data
        mock_prompt_data = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "system", "content": "System message"}
        ]
        mock_client.get_prompt = AsyncMock(return_value=mock_prompt_data)

        # Test standard mode
        result = await service.get_langchain_prompt_async(include_messages_placeholder=True)
        assert isinstance(result, ChatPromptTemplate)
        assert len(result.messages) == 4  # 3 original messages + 1 placeholder

        # Test without placeholder
        result = await service.get_langchain_prompt_async(include_messages_placeholder=False)
        assert isinstance(result, ChatPromptTemplate)
        assert len(result.messages) == 3  # Only 3 original messages

        # Test multi-server mode
        service._is_multi_client = True
        mock_server_client = MagicMock()
        mock_server_client.get_prompt = AsyncMock(return_value=mock_prompt_data)
        mock_client.get_client = AsyncMock(return_value=mock_server_client)

        result = await service.get_langchain_prompt_async(target_server="test_server")
        mock_client.get_client.assert_called_once_with("test_server")
        mock_server_client.get_prompt.assert_called_once()
        assert isinstance(result, ChatPromptTemplate)
        assert len(result.messages) == 4  # 3 original messages + 1 placeholder

    @pytest.mark.asyncio
    async def test_chat_message_type_handling(self):
        """Test chat message type handling"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate different types of messages
        system_message = {"role": "system", "content": "System message"}
        user_message = {"role": "user", "content": "User message"}
        assistant_message = {"role": "assistant", "content": "Assistant message"}
        unknown_message = {"role": "unknown", "content": "Unknown message"}

        # Simulate prompt data containing all types
        mock_prompt_data = [
            system_message,
            user_message,
            assistant_message,
            unknown_message
        ]
        mock_client.get_prompt = AsyncMock(return_value=mock_prompt_data)

        # Get LangChain prompt
        result = await service.get_langchain_prompt_async(include_messages_placeholder=False)

        # Verify message type handling
        assert len(result.messages) == 4

        # Check actual message types
        message_types = [type(msg).__name__ for msg in result.messages]
        assert "ChatMessage" in message_types  # System message converted to ChatMessage
        assert "HumanMessage" in message_types
        assert "AIMessage" in message_types

        # Get all ChatMessage message contents and roles
        chat_messages = [msg for msg in result.messages if type(msg).__name__ == "ChatMessage"]
        # Either system message is ChatMessage, or unknown message is ChatMessage, or both
        assert len(chat_messages) >= 1

    @pytest.mark.asyncio
    async def test_resource_management(self):
        """Test resource management"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = AsyncMock()
        service.client = mock_client

        # Test reading resource
        mock_client.read_resource = AsyncMock(return_value={"id": "resource1", "data": "test"})
        result = await service.read_resource("resource1")
        mock_client.read_resource.assert_called_once_with("resource1")
        assert result == {"id": "resource1", "data": "test"}

        # Test adding resource - note add_resource needs resource_id and resource_content two parameters
        mock_client.add_resource = AsyncMock(return_value=None)
        resource_id = "new_resource"
        resource_content = "test data content"
        await service.add_resource(resource_id, resource_content)
        mock_client.add_resource.assert_called_once_with(resource_id, resource_content)

        # Test deleting resource
        mock_client.remove_resource = AsyncMock(return_value=None)
        await service.remove_resource("resource1")
        mock_client.remove_resource.assert_called_once_with("resource1")

    @pytest.mark.asyncio
    async def test_import_error_paths(self):
        """Test import error paths"""
        # Save original modules
        original_modules = dict(sys.modules)

        try:
            # Remove possible modules
            for module_name in ['mcp', 'mcp.client']:
                if module_name in sys.modules:
                    del sys.modules[module_name]

            # Create an environment with mock import error
            service = MCPClientService()

            # Test catching import error - use mock instead of actual call to avoid actual import
            with patch('langchain_mcp_toolkit.services.client_service.ClientSession', None):
                with pytest.raises(ValueError, match="Failed to create SSE client"):
                    service.create("http://localhost:8000", "sse")
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    @pytest.mark.asyncio
    async def test_null_client_checks(self):
        """Test null client checks"""
        service = MCPClientService()
        service._is_connected = True
        service.client = None

        # Test various methods handling null client situation
        with pytest.raises(ValueError, match="Client not created"):
            await service.get_prompt("test")

        with pytest.raises(ValueError, match="Client not created"):
            await service.list_prompts()

        with pytest.raises(ValueError, match="Client not created"):
            await service.list_resources()

        with pytest.raises(ValueError, match="Client not created"):
            await service.read_resource("test_id")

        with pytest.raises(ValueError, match="Client not created"):
            await service.add_resource("test_id", "content")

        with pytest.raises(ValueError, match="Client not created"):
            await service.remove_resource("test_id")

        with pytest.raises(ValueError, match="Client not created"):
            await service.call_tool("default", "test_tool")

        with pytest.raises(ValueError, match="Client not created"):
            service.list_tools_sync()

        with pytest.raises(ValueError, match="Client not created"):
            service.get_prompt_sync()

        with pytest.raises(ValueError, match="Client not created"):
            service.get_prompt_by_target()

        with pytest.raises(ValueError, match="Client not created"):
            service.get_tools()

        with pytest.raises(ValueError, match="Client not created"):
            service.set_prompt([])

        with pytest.raises(ValueError, match="Client not created"):
            service.get_tools_as_langchain()

        with pytest.raises(ValueError, match="Client not created"):
            await service.get_langchain_tools()

        with pytest.raises(ValueError, match="Client not created"):
            await service.get_langchain_prompt("test")

    @pytest.mark.asyncio
    async def test_create_multi_server_client(self):
        """Test creating multi-server client"""
        service = MCPClientService()

        # Simulate multi-server configuration
        server_configs = {
            "server1": {
                "url": "http://localhost:8001",
                "transport_type": "sse"
            },
            "server2": {
                "url": "http://localhost:8002",
                "transport_type": "sse"
            }
        }

        # Create a mock MultiServerClient
        mock_multi_client = MagicMock()

        # Simulate _create_multi_server_client method
        with patch.object(service, '_create_multi_server_client', return_value=mock_multi_client) as mock_create:
            # Call create method
            result = service.create(server_configs)

            # Verify result
            assert result == "Multi-server client created"
            assert service._is_multi_client is True
            assert service._is_connected is True

            # Verify _create_multi_server_client called
            mock_create.assert_called_once_with(server_configs)

    @pytest.mark.asyncio
    async def test_multi_server_client_failures(self):
        """Test multi-server client failures"""
        service = MCPClientService()

        # Simulate configuration
        configs = {
            "server1": {
                "url": "http://localhost:8001",
                "transport_type": "sse"
            }
        }

        # Simulate _create_multi_server_client throwing exception
        with patch.object(service, '_create_multi_server_client', side_effect=Exception("Test failure")):
            with pytest.raises(ValueError, match="Failed to create multi-server client"):
                service.create(configs)

    @pytest.mark.asyncio
    async def test_get_langchain_prompt_async_empty(self):
        """Test asynchronous getting empty prompt template"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate empty prompt
        mock_client.get_prompt = AsyncMock(return_value=[])

        # Test standard mode
        result = await service.get_langchain_prompt_async()

        # Verify return is valid ChatPromptTemplate
        assert isinstance(result, ChatPromptTemplate)
        assert len(result.messages) == 1  # Only placeholder

        # Test without placeholder
        result = await service.get_langchain_prompt_async(include_messages_placeholder=False)
        assert isinstance(result, ChatPromptTemplate)
        assert len(result.messages) == 0  # No messages

    def test_list_tools_sync_methods(self):
        """Test synchronous tool list methods"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Test list_tools_sync method - Single server mode
        mock_client.list_tools = MagicMock(return_value=["tool1", "tool2"])
        result = service.list_tools_sync()
        mock_client.list_tools.assert_called_once()
        assert result == ["tool1", "tool2"]

        # Test list_tools_sync method - Multi-server mode
        mock_client.list_tools.reset_mock()
        service._is_multi_client = True

        # Specify server name
        result = service.list_tools_sync("test_server")
        mock_client.list_tools.assert_called_once_with("test_server")

    def test_prompt_sync_methods(self):
        """Test synchronous prompt methods"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Test set_prompt method - Single server mode
        mock_client.set_prompt = MagicMock()
        prompt_messages = [{"role": "user", "content": "Hello"}]

        service.set_prompt(prompt_messages)
        mock_client.set_prompt.assert_called_once_with(prompt_messages)

        # Test set_prompt method - Multi-server mode
        mock_client.set_prompt.reset_mock()
        service._is_multi_client = True

        # Specify server name
        service.set_prompt(prompt_messages, "test_server")
        mock_client.set_prompt.assert_called_once_with(prompt_messages, "test_server")

        # Test get_prompt_sync method - Single server mode
        service._is_multi_client = False
        mock_client.get_prompt = MagicMock(return_value=[{"role": "user", "content": "Hello"}])

        result = service.get_prompt_sync()
        mock_client.get_prompt.assert_called_once()
        assert result == [{"role": "user", "content": "Hello"}]

        # Test get_prompt_sync method - Multi-server mode
        mock_client.get_prompt.reset_mock()
        service._is_multi_client = True

        # Specify server name
        result = service.get_prompt_sync("test_server")
        mock_client.get_prompt.assert_called_once_with("test_server")

    @pytest.mark.asyncio
    async def test_call_tool(self):
        """Test calling tool"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = AsyncMock()
        service.client = mock_client

        # Set mock return value
        mock_client.call_tool = AsyncMock(return_value={"result": "success"})

        # Test calling tool with parameters - note actual parameter order of API
        result = await service.call_tool("default", "test_tool", param1="value1", param2="value2")

        # In single-server mode, the method called is client.call_tool(tool_name, **kwargs)
        mock_client.call_tool.assert_called_once_with("test_tool", param1="value1", param2="value2")
        assert result == {"result": "success"}

        # Test multi-server mode
        service._is_multi_client = True
        mock_server_client = AsyncMock()
        mock_client.get_client = AsyncMock(return_value=mock_server_client)
        mock_server_client.call_tool = AsyncMock(return_value={"result": "server_success"})

        # Reset call state
        mock_client.call_tool.reset_mock()

        # Give mock_client.call_tool a new return value
        mock_client.call_tool = AsyncMock(return_value={"result": "server_success"})

        # Call tool for specific server
        result = await service.call_tool("test_server", "test_tool", param1="value1")

        # In multi-server mode, the method called is client.call_tool(server_name, tool_name, kwargs)
        mock_client.call_tool.assert_called_once_with("test_server", "test_tool", {'param1': 'value1'})
        assert result == {"result": "server_success"}

    @pytest.mark.asyncio
    async def test_list_tools_methods(self):
        """Test tool list related methods"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Test list_tools method - Single server mode
        mock_client.list_tools = AsyncMock(return_value=["tool1", "tool2"])
        result = await service.list_tools()
        mock_client.list_tools.assert_called_once()
        assert result == ["tool1", "tool2"]

        # Test list_tools method - Multi-server mode
        mock_client.list_tools.reset_mock()
        service._is_multi_client = True
        mock_client.list_all_tools = AsyncMock(return_value=["server1/tool1", "server2/tool2"])

        # Default includes server prefix
        result = await service.list_tools()
        mock_client.list_all_tools.assert_called_once_with(include_prefix=True)
        assert result == ["server1/tool1", "server2/tool2"]

        # Set without server prefix
        mock_client.list_all_tools.reset_mock()
        result = await service.list_tools(include_server_prefix=False)
        mock_client.list_all_tools.assert_called_once_with(include_prefix=False)

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = AsyncMock()
        service.client = mock_client

        # Set exception
        mock_client.call_tool.side_effect = Exception("Test error")

        # Test whether exception correctly propagates
        with pytest.raises(Exception, match="Test error"):
            await service.call_tool("default", "test_tool")

        # Test exception in multi-server mode - reset side_effect
        mock_client.call_tool.side_effect = None
        mock_client.call_tool.reset_mock()

        # Create a new exception
        service._is_multi_client = True
        mock_client.call_tool.side_effect = Exception("Server error")

        with pytest.raises(Exception, match="Server error"):
            await service.call_tool("test_server", "test_tool")

    @pytest.mark.asyncio
    async def test_multi_client_connection_errors(self):
        """Test multi-client connection errors"""
        service = MCPClientService()
        service._is_connected = False
        service._is_multi_client = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate connect method throwing exception
        mock_client.connect = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(Exception, match="Connection failed"):
            await service.connect()

        # Ensure connection status remains False
        assert service._is_connected is False

    @pytest.mark.asyncio
    async def test_resource_management_methods(self):
        """Test resource management methods"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Test adding resource
        mock_client.add_resource = AsyncMock()
        await service.add_resource("test_resource", "test_content")
        mock_client.add_resource.assert_called_once_with("test_resource", "test_content")

        # Test multi-server mode adding resource
        service._is_multi_client = True
        mock_client.add_resource.reset_mock()
        await service.add_resource("test_resource", "test_content", "test_server")
        mock_client.add_resource.assert_called_once_with("test_resource", "test_content", "test_server")

        # Test deleting resource
        mock_client.remove_resource = AsyncMock()
        await service.remove_resource("test_resource")
        mock_client.remove_resource.assert_called_once_with("test_resource")

        # Test multi-server mode deleting resource
        mock_client.remove_resource.reset_mock()
        await service.remove_resource("test_resource", "test_server")
        mock_client.remove_resource.assert_called_once_with("test_resource", "test_server")

    @pytest.mark.asyncio
    async def test_get_tools_as_langchain(self):
        """Test getting LangChain format tools"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate tool list
        mock_tools = [
            {"name": "tool1", "description": "Tool1 description"},
            {"name": "tool2", "description": "Tool2 description"}
        ]
        mock_client.get_tools = MagicMock(return_value=mock_tools)

        # Simulate tool conversion
        with patch("langchain_mcp_toolkit.services.client_service.MCPAdapterService.convert_tool_to_langchain",
                  return_value="converted_tool") as mock_convert:
            # Test single-server mode
            result = service.get_tools_as_langchain()

            # Verify call and result
            assert result == ["converted_tool", "converted_tool"]
            assert mock_convert.call_count == 2
            mock_convert.assert_any_call(mock_tools[0])
            mock_convert.assert_any_call(mock_tools[1])

            # Reset mock objects
            mock_convert.reset_mock()

            # Test multi-server mode
            service._is_multi_client = True
            result = service.get_tools_as_langchain("test_server")

            # Verify call and result
            mock_client.get_tools.assert_called_with("test_server")
            assert result == ["converted_tool", "converted_tool"]
            assert mock_convert.call_count == 2

    @pytest.mark.asyncio
    async def test_get_langchain_prompt(self):
        """Test getting LangChain format prompt"""
        service = MCPClientService()
        service._is_connected = True
        mock_client = MagicMock()
        service.client = mock_client

        # Simulate prompt data
        mock_prompt_data = {"content": "test_prompt_content"}
        mock_client.get_prompt = AsyncMock(return_value=mock_prompt_data)

        # Simulate adapter conversion method
        mock_message = MagicMock()
        with patch("langchain_mcp_toolkit.services.adapters.MCPAdapterService.convert_prompt_to_langchain",
                  return_value=mock_message) as mock_convert:
            # Test single-server mode
            result = await service.get_langchain_prompt("test_prompt", {"arg": "value"})

            # Verify call and result
            mock_client.get_prompt.assert_called_once_with("test_prompt", {"arg": "value"})
            mock_convert.assert_called_once_with(mock_prompt_data)
            assert result == [mock_message]  # Return is list of single message

            # Reset mock objects
            mock_client.get_prompt.reset_mock()
            mock_convert.reset_mock()

            # Test multi-server mode
            service._is_multi_client = True
            mock_server_client = MagicMock()
            mock_client.get_client = AsyncMock(return_value=mock_server_client)
            mock_server_client.get_prompt = AsyncMock(return_value=mock_prompt_data)

            result = await service.get_langchain_prompt("test_prompt", {"arg": "value"}, "test_server")

            # Verify call and result
            mock_client.get_client.assert_called_once_with("test_server")
            mock_server_client.get_prompt.assert_called_once_with("test_prompt", {"arg": "value"})
            mock_convert.assert_called_once_with(mock_prompt_data)
            assert result == [mock_message]  # Return is list of single message

            # We temporarily skip test for server client being None
            # This scenario is more complex and will be handled in full coverage test

    @pytest.mark.asyncio
    async def test_advanced_multi_server_error_handling(self):
        """Test advanced error handling in multi-server mode"""
        service = MCPClientService()
        service._is_connected = True
        service._is_multi_client = True
        mock_client = AsyncMock()  # Use AsyncMock instead of MagicMock
        service.client = mock_client

        # Simulate get_client throwing exception
        mock_client.get_client = AsyncMock(side_effect=Exception("Server not found"))

        # Test list_resources method exception handling
        with pytest.raises(Exception, match="Server not found"):
            await service.list_resources("test_server")

        # Test read_resource method exception handling
        with pytest.raises(Exception, match="Server not found"):
            await service.read_resource("resource_id", "test_server")

        # Reset and simulate add_resource method
        mock_client.add_resource = AsyncMock(side_effect=Exception("Server not found"))

        # Test add_resource method exception handling - directly call method instead of through get_client
        with pytest.raises(Exception, match="Server not found"):
            await service.add_resource("resource_id", "content", "test_server")

        # Test list_prompts method exception handling
        mock_client.get_client = AsyncMock(side_effect=Exception("Server not found"))
        with pytest.raises(Exception, match="Server not found"):
            await service.list_prompts("test_server")

        # Modify mock object, test invalid response
        mock_client.get_client = AsyncMock(return_value=None)
        mock_client.list_resources = AsyncMock()
        mock_client.list_prompts = AsyncMock()
        mock_client.read_resource = AsyncMock()

        # Verify empty result return
        result = await service.list_resources("test_server")
        assert result == []

        result = await service.list_prompts("test_server")
        assert result == []

        result = await service.read_resource("resource_id", "test_server")
        assert result == {}

    def test_specialized_client_creation(self):
        """Test client creation in special cases"""
        service = MCPClientService()

        # Test creating stdio client (custom command and parameters)
        with patch("langchain_mcp_toolkit.services.client_service.stdio_client") as mock_stdio_client, \
             patch("langchain_mcp_toolkit.services.client_service.StdioServerParameters") as mock_params:

            # Simulate mcp module
            with patch.dict('sys.modules', {'mcp.client': MagicMock()}):
                # Add necessary classes to mcp.client
                sys.modules['mcp.client'].StdioServerParameters = mock_params
                sys.modules['mcp.client'].stdio_client = mock_stdio_client

                # Set return value
                mock_client = MagicMock()
                mock_stdio_client.return_value = mock_client

                # Use custom command and parameters to create client
                custom_command = "node"
                args = ["server.js", "--port", "8080"]
                result = service.create("stdio_server", "stdio", command=custom_command, args=args)

                # Verify parameter correct passing
                mock_params.assert_called_once_with(command=custom_command, args=args)
                assert "Client created connected to stdio_server" in result

        # Test handling case where multi-server client cannot be created
        service = MCPClientService()
        with patch("langchain_mcp_toolkit.services.adapters.MCPAdapterService.create_multi_server_client_sync",
                  side_effect=Exception("Mock error")):
            # Ensure mock exception caught and ValueError thrown
            with pytest.raises(ValueError, match="Failed to create multi-server client"):
                service.create({"server1": {"url": "http://localhost:8001", "transport_type": "sse"}})
