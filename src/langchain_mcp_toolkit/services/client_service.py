"""
MCP Client Service Module

Provides client services for communicating with MCP servers, supporting SSE and stdio transport.
"""

from typing import Any, Protocol, TypeVar, cast

from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, BaseMessage, ChatMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder

# Use try/except for imports to allow for mocking in tests
try:
    from mcp import ClientSession  # type: ignore
except ImportError:
    # Don't try to assign None to a class, define the type for the variable
    ClientSession = None  # type: ignore

try:
    from mcp.stdio import StdioServerParameters, stdio_client  # type: ignore
except ImportError:
    StdioServerParameters = None  # type: ignore
    stdio_client = None  # type: ignore

try:
    from mcp.types import PromptMessage, Tool  # type: ignore
except ImportError:
    # Properly use Any type
    class PromptMessage:  # type: ignore
        pass

    class Tool:  # type: ignore
        pass


from langchain_mcp_toolkit.services.adapters import MCPAdapterService, SessionProtocol

# Define type variable instead of directly using variable
ToolType = TypeVar("ToolType")
PromptMessageType = TypeVar("PromptMessageType")


class ClientProtocol(Protocol):
    """Client interface protocol"""

    def connect(self) -> None:
        """Connect to server"""
        ...

    def call_tool(self, tool_name: str, input_value: Any) -> Any:
        """Call tool"""
        ...

    def get_tools(self) -> list[Any]:  # Use Any instead of Tool
        """Get tool list"""
        ...

    def list_tools(self) -> list[str]:
        """Get tool name list"""
        ...

    def set_prompt(self, prompt_msgs: list[Any]) -> None:  # Use Any instead of PromptMessage
        """Set prompt"""
        ...

    def get_prompt(self) -> list[Any]:  # Use Any instead of PromptMessage
        """Get prompt"""
        ...


class NullOutputStream:
    """Empty output stream for discarding output"""

    def write(self, data: str) -> None:
        """Write data (discarded)"""
        pass

    def flush(self) -> None:
        """Flush buffer (no operation)"""
        pass


class MCPClientService:
    """MCP client service

    Provides MCP client functionality for applications, supporting SSE and stdio transport.
    """

    def __init__(self, verbose: bool = False) -> None:
        """Initialize MCP client service

        Args:
            verbose: Whether to enable detailed logging
        """
        self.client: Any = None
        self._is_connected: bool = False
        self._is_multi_client: bool = False
        self._verbose: bool = verbose

    @property
    def is_connected(self) -> bool:
        """Get connection status"""
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value: bool) -> None:
        """Set connection status (for testing only)"""
        self._is_connected = value

    def _check_connection(self) -> None:
        """Check connection status

        If client is not connected, raise ValueError
        """
        if not self._is_connected:
            raise ValueError("Client service not connected")

    def _create_multi_server_client(
        self, server_configs: dict[str, dict[str, Any]]
    ) -> Any:
        """Create multi-server client

        Args:
            server_configs: Server configuration dictionary, format: {
                "server_name": {
                    "url": "http://localhost:8000/sse",  # SSE connection
                    "transport": "sse"
                },
                "server_name2": {
                    "command": "python",  # STDIO connection
                    "args": ["path/to/server.py"],
                    "transport": "stdio"
                }
            }

        Returns:
            Any: Multi-server client instance
        """
        try:
            from langchain_mcp_toolkit.services.adapters import MCPAdapterService

            return MCPAdapterService.create_multi_server_client_sync(server_configs)
        except Exception as e:
            raise ValueError(f"Failed to create multi-server client: {e}") from e

    def create(
        self,
        url_or_configs: str | dict[str, dict[str, Any]],
        transport_type: str = "sse",
        command: str | None = None,
        args: list[str] | None = None,
        output_stream: Any | None = None,
    ) -> str:
        """Create MCP client

        Args:
            url_or_configs: Server URL or multi-server configuration dictionary
            transport_type: Transport type, optional values are "sse" or "stdio", default is "sse"
            command: Command, valid when transport_type is "stdio", default is "python"
            args: Command arguments, valid when transport_type is "stdio", default is []
            output_stream: Output stream, for receiving server response

        Returns:
            str: Operation result information
        """
        if self._is_connected:
            raise ValueError("Client service already connected")

        # Handle output stream
        if output_stream is None:
            output_stream = NullOutputStream()

        # Check if it's multi-server configuration
        if isinstance(url_or_configs, dict):
            try:
                self.client = self._create_multi_server_client(url_or_configs)
                self._is_multi_client = True
                self._is_connected = True
                return "Multi-server client created"
            except Exception as e:
                raise ValueError(f"Failed to create multi-server client: {e}") from e

        # Handle single-server configuration
        url = url_or_configs

        if transport_type == "sse":
            try:
                if ClientSession is None:
                    raise ImportError("ClientSession not defined")
                # Type annotation issue: here we use type conversion to explicitly tell mypy this is acceptable
                # Actually, this part of the code should be refactored, but for now, ensure type check passes
                self.client = cast(
                    Any,
                    ClientSession(
                        cast(Any, url), write_stream=cast(Any, output_stream)
                    ),
                )
                self._is_connected = True
                self._is_multi_client = False
                return f"Client created connected to {url}"
            except Exception as e:
                raise ValueError(f"Failed to create SSE client: {e}") from e
        elif transport_type == "stdio":
            try:
                if StdioServerParameters is None or stdio_client is None:
                    raise ImportError("StdioServerParameters or stdio_client not defined")

                cmd = command or "python"
                cmd_args = args or [url]

                params = StdioServerParameters(command=cmd, args=cmd_args)
                self.client = stdio_client(params)
                self._is_connected = True
                self._is_multi_client = False
                return f"Client created connected to {url}"
            except Exception as e:
                raise ValueError(f"Failed to create stdio client: {e}") from e
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

    async def connect(self) -> str:
        """Connect to server

        Connect to MCP server. Should be called after create method.

        Returns:
            str: Operation result information

        Raises:
            ValueError: If client is not created
        """
        if self.client is None:
            raise ValueError("Client not created")

        # Get client instance
        client = self.client

        # Connect to server
        await client.connect()

        self._is_connected = True
        return "Connection successful"

    async def disconnect(self) -> str:
        """Disconnect

        Disconnect from MCP server.

        Returns:
            str: Operation result information

        Raises:
            ValueError: If client is not created
        """
        if self.client is None:
            raise ValueError("Client not created")

        # Get client instance
        client = self.client

        # Disconnect
        await client.disconnect()

        self._is_connected = False
        return "Disconnected"

    async def call_tool(self, server_name: str, tool_name: str, **kwargs: Any) -> Any:
        """Call tool

        Args:
            server_name: Server name
            tool_name: Tool name
            **kwargs: Tool parameters

        Returns:
            Any: Tool call result
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client:
            return await self.client.call_tool(server_name, tool_name, kwargs)
        else:
            return await self.client.call_tool(tool_name, **kwargs)

    async def list_tools(
        self, include_server_prefix: bool = True
    ) -> list[dict[str, Any]]:
        """List all tools

        Args:
            include_server_prefix: Whether to include server prefix

        Returns:
            list[dict[str, Any]]: Tool list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client:
            return cast(
                list[dict[str, Any]],
                await self.client.list_all_tools(include_prefix=include_server_prefix),
            )
        else:
            return cast(list[dict[str, Any]], await self.client.list_tools())

    def list_tools_sync(self, target_server: str | None = None) -> list[str]:
        """Synchronously get tool name list

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[str]: Tool name list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(list[str], self.client.list_tools(target_server))
        return cast(list[str], self.client.list_tools())

    def get_tools(self, target_server: str | None = None) -> list[Any]:  # Use Any instead of Tool
        """Get tool list

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[Any]: Tool list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(list[Any], self.client.get_tools(target_server))
        return cast(list[Any], self.client.get_tools())

    def set_prompt(
        self,
        prompt_msgs: list[Any],  # Use Any instead of PromptMessage
        target_server: str | None = None,
    ) -> None:
        """Set prompt

        Args:
            prompt_msgs: Prompt message list
            target_server: Target server name, valid only in multi-server mode
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            self.client.set_prompt(prompt_msgs, target_server)
        else:
            self.client.set_prompt(prompt_msgs)

    def get_prompt_sync(
        self, target_server: str | None = None
    ) -> list[Any]:  # Use Any instead of PromptMessage
        """Get prompt (synchronous version)

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[Any]: Prompt message list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(list[Any], self.client.get_prompt(target_server))
        return cast(list[Any], self.client.get_prompt())

    def get_prompt_by_target(
        self, target_server: str | None = None
    ) -> list[Any]:  # Use Any instead of PromptMessage
        """Get prompt (by target server)

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[Any]: Prompt message list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(list[Any], self.client.get_prompt(target_server))
        return cast(list[Any], self.client.get_prompt())

    async def get_prompt(
        self,
        prompt_name: str,
        arguments: dict[str, Any] | None = None,
        server_name: str = "default",
    ) -> dict[str, Any]:
        """Asynchronously get prompt (compatible with old API)

        Args:
            prompt_name: Prompt name
            arguments: Prompt parameters, optional
            server_name: Server name, valid only in multi-server mode, default is "default"

        Returns:
            dict[str, Any]: Prompt content
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client:
            # Get specific server's client
            client = await self.client.get_client(server_name)
            if client:
                return cast(
                    dict[str, Any],
                    await client.get_prompt(prompt_name, arguments or {}),
                )
            else:
                return {}
        else:
            # Directly get prompt
            return cast(
                dict[str, Any], await self.client.get_prompt(prompt_name, arguments)
            )

    async def list_resources(
        self, server_name: str = "default"
    ) -> list[dict[str, Any]]:
        """Get resource list

        Args:
            server_name: Server name, valid only in multi-server mode, default is "default"

        Returns:
            list[dict[str, Any]]: Resource list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client:
            # Get specific server's client
            client = await self.client.get_client(server_name)
            if client:
                return cast(list[dict[str, Any]], await client.list_resources())
            else:
                return []
        else:
            # Directly get resources
            return cast(list[dict[str, Any]], await self.client.list_resources())

    async def read_resource(
        self,
        resource_name: str = "",
        server_name: str = "default",
    ) -> dict[str, Any]:
        """Read resource content

        Args:
            resource_name: Resource name
            server_name: Server name, valid only in multi-server mode, default is "default"

        Returns:
            dict[str, Any]: Resource content
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client:
            # Get specific server's client
            client = await self.client.get_client(server_name)
            if client:
                return cast(dict[str, Any], await client.read_resource(resource_name))
            else:
                return {}
        else:
            # Directly read resource
            return cast(dict[str, Any], await self.client.read_resource(resource_name))

    async def list_prompts(
        self,
        server_name: str = "default",
    ) -> list[dict[str, Any]]:
        """Get prompt list

        Args:
            server_name: Server name, valid only in multi-server mode, default is "default"

        Returns:
            list[dict[str, Any]]: Prompt list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client:
            # Get specific server's client
            client = await self.client.get_client(server_name)
            if client:
                return cast(list[dict[str, Any]], await client.list_prompts())
            else:
                return []
        else:
            # Directly get prompt list
            return cast(list[dict[str, Any]], await self.client.list_prompts())

    def get_tools_as_langchain(
        self, target_server: str | None = None
    ) -> list[BaseTool]:
        """Get LangChain format tool

        Convert MCP tool list to LangChain tool list

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[BaseTool]: LangChain tool list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        # Get MCP tool list
        if self._is_multi_client and target_server:
            mcp_tools = self.client.get_tools(target_server)
        else:
            mcp_tools = self.client.get_tools()

        # Use adapter service to convert to LangChain tool
        return [MCPAdapterService.convert_tool_to_langchain(tool) for tool in mcp_tools]

    async def get_langchain_tools(self, server_name: str = "default") -> list[BaseTool]:
        """Asynchronously get LangChain format tool (compatible with old API for testing)

        Args:
            server_name: Server name, valid only in multi-server mode, default is "default"

        Returns:
            list[BaseTool]: LangChain tool list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        # Use adapter service to load tools
        from langchain_mcp_toolkit.services.adapters import MCPAdapterService

        session_protocol = cast("SessionProtocol", self.client)
        return await MCPAdapterService.load_tools_from_session(session_protocol)

    async def get_langchain_prompt(
        self,
        prompt_name: str,
        arguments: dict[str, Any] | None = None,
        server_name: str = "default",
    ) -> list[BaseMessage]:
        """Asynchronously get LangChain format prompt (compatible with old API for testing)

        Args:
            prompt_name: Prompt name
            arguments: Prompt parameters, optional
            server_name: Server name, valid only in multi-server mode, default is "default"

        Returns:
            list[BaseMessage]: LangChain message list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        # Get prompt
        prompt_data = await self.get_prompt(prompt_name, arguments, server_name)

        # Convert to LangChain message
        from langchain_mcp_toolkit.services.adapters import MCPAdapterService

        # Use type conversion to tell mypy this is acceptable
        prompt_message = cast(PromptMessage, prompt_data)
        message = MCPAdapterService.convert_prompt_to_langchain(prompt_message)

        return [message]

    async def get_langchain_prompt_async(
        self,
        target_server: str | None = None,
        include_messages_placeholder: bool = True,
    ) -> ChatPromptTemplate:
        """Asynchronously get LangChain format chat prompt template

        Convert MCP prompt to LangChain format prompt template, including message placeholder

        Args:
            target_server: Target server name, valid only in multi-server mode
            include_messages_placeholder: Whether to include message placeholder, for adding history messages

        Returns:
            ChatPromptTemplate: LangChain chat prompt template
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        # Get MCP prompt
        if self._is_multi_client and target_server:
            client = await self.client.get_client(target_server)
            mcp_prompt = await client.get_prompt() if client else []
        else:
            # Directly get prompt
            mcp_prompt = await self.client.get_prompt()

        # Convert to LangChain message
        messages: list[BaseMessage] = []
        for msg in mcp_prompt:
            if msg.get("role", "") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role", "") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
            else:
                messages.append(
                    ChatMessage(
                        role=msg.get("role", "system"), content=msg.get("content", "")
                    )
                )

        # Add history message placeholder
        if include_messages_placeholder:
            # Directly create ChatPromptTemplate instead of first creating a single type message list
            placeholder = MessagesPlaceholder(variable_name="chat_history")
            all_messages = messages + [placeholder]  # Type compatible
            return ChatPromptTemplate.from_messages(all_messages)

        return ChatPromptTemplate.from_messages(messages)

    def get_langchain_prompt_sync(
        self,
        target_server: str | None = None,
        include_messages_placeholder: bool = True,
    ) -> ChatPromptTemplate:
        """Get LangChain format prompt (synchronous version)

        Convert MCP prompt to LangChain format prompt

        Args:
            target_server: Target server name, valid only in multi-server mode
            include_messages_placeholder: Whether to include message placeholder, for adding history messages

        Returns:
            ChatPromptTemplate: LangChain chat prompt template
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        # Get MCP prompt
        if self._is_multi_client and target_server:
            mcp_prompt = self.client.get_prompt(target_server)
        else:
            mcp_prompt = self.client.get_prompt()

        # Convert to LangChain message
        messages: list[BaseMessage] = []
        for msg in mcp_prompt:
            if msg.get("role", "") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role", "") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
            else:
                messages.append(
                    ChatMessage(
                        role=msg.get("role", "system"), content=msg.get("content", "")
                    )
                )

        # Add history message placeholder
        if include_messages_placeholder:
            # Directly create ChatPromptTemplate instead of first creating a single type message list
            placeholder = MessagesPlaceholder(variable_name="chat_history")
            all_messages = messages + [placeholder]  # Type compatible
            return ChatPromptTemplate.from_messages(all_messages)

        return ChatPromptTemplate.from_messages(messages)

    # Below are methods kept for compatibility with old API
    async def get_prompt_legacy(
        self,
        prompt_name: str,
        arguments: dict[str, Any] | None = None,
        server_name: str = "default",
    ) -> dict[str, Any]:
        """Asynchronously get prompt (compatible with old API)

        This method is deprecated, please use get_prompt method
        """
        return await self.get_prompt(prompt_name, arguments, server_name)

    async def list_resources_internal(
        self, target_server: str | None = None
    ) -> list[dict[str, Any]]:
        """Get resource list

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[dict[str, Any]]: Resource list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(
                list[dict[str, Any]], await self.client.list_resources(target_server)
            )
        return cast(list[dict[str, Any]], await self.client.list_resources())

    async def read_resource_internal(
        self,
        resource_id: str,
        target_server: str | None = None,
    ) -> dict[str, Any]:
        """Read resource content

        Args:
            resource_id: Resource ID
            target_server: Target server name, valid only in multi-server mode

        Returns:
            dict[str, Any]: Resource content
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(
                dict[str, Any],
                await self.client.read_resource(resource_id, target_server),
            )
        return cast(dict[str, Any], await self.client.read_resource(resource_id))

    async def list_prompts_internal(
        self,
        target_server: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get prompt list

        Args:
            target_server: Target server name, valid only in multi-server mode

        Returns:
            list[dict[str, Any]]: Prompt list
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            return cast(
                list[dict[str, Any]], await self.client.list_prompts(target_server)
            )
        return cast(list[dict[str, Any]], await self.client.list_prompts())

    async def add_resource(
        self,
        resource_id: str,
        resource_content: str,
        target_server: str | None = None,
    ) -> None:
        """Add resource

        Args:
            resource_id: Resource ID
            resource_content: Resource content
            target_server: Target server name, valid only in multi-server mode
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            await self.client.add_resource(resource_id, resource_content, target_server)
        else:
            await self.client.add_resource(resource_id, resource_content)

    async def remove_resource(
        self,
        resource_id: str,
        target_server: str | None = None,
    ) -> None:
        """Remove resource

        Args:
            resource_id: Resource ID
            target_server: Target server name, valid only in multi-server mode
        """
        self._check_connection()

        if self.client is None:
            raise ValueError("Client not created")

        if self._is_multi_client and target_server:
            await self.client.remove_resource(resource_id, target_server)
        else:
            await self.client.remove_resource(resource_id)
