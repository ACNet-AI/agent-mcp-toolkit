"""
MCP Server Service Module

This module provides functionality for creating and managing MCP servers. The MCPServerService class is the core of server operations,
allowing creation of servers, starting and stopping servers, adding tools, resources and prompts, etc.

Main features:
- Create and manage MCP servers
- Start and stop servers
- Add custom tools, resources and prompts
- Securely compile and execute tool code
- Provide synchronous and asynchronous operation interfaces
"""

import json
import textwrap
from collections.abc import Callable
from typing import Any, cast

import requests  # type: ignore


# Define a basic interface for type hinting
class ServerProtocol:
    """MCP server protocol, used for type hinting"""

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize server"""
        pass

    def start(self, host: str, port: int) -> None:
        """Start server"""
        pass

    def stop(self) -> None:
        """Stop server"""
        pass

    def get_url(self) -> str:
        """Get server URL"""
        return ""

    def add_tool(self, name: str, func: Callable[..., Any], description: str) -> None:
        """Add tool"""
        pass

    def add_resource(self, name: str, content: Any, description: str = "") -> None:
        """Add resource"""
        pass

    def add_prompt(self, name: str, content: str, description: str = "") -> None:
        """Add prompt"""
        pass

# Get appropriate server class based on whether MCP can be imported
def get_mcp_server_class() -> type[Any]:
    """Get MCP server class, returns protocol class if import fails"""
    try:
        from mcp import Server  # type: ignore
        return cast(type[Any], Server)
    except ImportError:
        return ServerProtocol

# Get server class
MCPServerClass = get_mcp_server_class()

# List of safe built-in functions
safe_builtins = [
    "dict", "list", "tuple", "set", "str", "int", "float", "bool",
    "None", "True", "False", "len", "Exception", "TypeError", "ValueError",
    "print", "range", "enumerate", "zip", "map", "filter", "sum", "min", "max"
]

class MCPServerService:
    """
    Service class for managing MCP servers

    This class provides functionality for creating, starting and managing MCP servers, including adding tools, resources and prompts.
    Supports both synchronous and asynchronous operation interfaces, suitable for various environments.

    Attributes:
        _server: MCP server instance
        _is_running: Whether the server is running
        _host: Server host
        _port: Server port

    Example:
        ```python
        # Create server service
        server_service = MCPServerService()

        # Start server
        server_service.start(host="localhost", port=8000)

        # Add tool
        code = '''
        def get_weather(city: str) -> str:
            '''Get weather information'''
            # This is simulated weather information
            return f"The weather in {city} is sunny, temperature 25℃"
        '''
        server_service.add_tool("get_weather", "Get weather information", code)

        # Stop server
        server_service.stop()
        ```
    """

    def __init__(self, server_type: str | None = None):
        """
        Initialize MCP server service

        Create an MCP server service instance, server type can be specified.

        Parameters:
            server_type: Server type, optional. Default is None, using standard MCP server.

        Exceptions:
            RuntimeError: If server creation fails

        Example:
            ```python
            # Create default server
            server_service = MCPServerService()

            # Create custom type server
            server_service = MCPServerService(server_type="custom")
            ```
        """
        self._is_running: bool = False
        self._host: str = "localhost"
        self._port: int = 8000
        self._server: Any = None

        try:
            if server_type:
                # Create custom type server
                self._server = self._create_custom_server(server_type)
            else:
                # Create standard MCP server
                self._server = MCPServerClass()
        except Exception as e:
            raise RuntimeError(f"Failed to create MCP server: {str(e)}") from e

    @property
    def server(self) -> Any:
        """
        Get MCP server instance

        Get the current MCP server instance. If the server has not been created yet, a default server will be created automatically.

        Returns:
            Any: MCP server instance

        Example:
            ```python
            server_service = MCPServerService()
            # Get server instance
            server = server_service.server
            # Use server API directly
            server.add_tool(...)
            ```
        """
        if self._server is None:
            self._server = self._create_default_server()
        return self._server

    @server.setter
    def server(self, value: Any) -> None:
        """Set server instance"""
        self._server = value

    def _create_default_server(self) -> Any:
        """
        Create default MCP server

        Internal method for creating default MCP server instance.

        Returns:
            Any: Default MCP server instance

        Exceptions:
            RuntimeError: If server creation fails
        """
        try:
            return MCPServerClass()
        except Exception as e:
            raise RuntimeError(f"Failed to create default MCP server: {str(e)}") from e

    def _create_custom_server(self, server_type: str) -> Any:
        """
        Create custom type MCP server

        Internal method for creating custom MCP server instance based on specified type.

        Parameters:
            server_type: Server type, such as "fastmcp", etc.

        Returns:
            Any: Custom type MCP server instance

        Exceptions:
            RuntimeError: If server creation fails or type not supported
        """
        try:
            if server_type.lower() == "fastmcp":
                # Try to import and create FastMCP server
                from mcp.server.fastmcp import FastMCP

                return FastMCP()
            else:
                raise ValueError(f"Unsupported server type: {server_type}")
        except ImportError as e:
            raise RuntimeError(f"Failed to import server type '{server_type}': {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to create server type '{server_type}': {str(e)}") from e

    def start(self, host: str = "localhost", port: int = 8000) -> str:
        """
        Start MCP server

        Start the server on specified host and port. If the server is already running, the current URL will be returned.

        Parameters:
            host: Server host address, default is "localhost"
            port: Server port, default is 8000

        Returns:
            str: Server URL or status message

        Exceptions:
            RuntimeError: If starting server fails
        """
        # Check if server is already running
        if self._is_running:
            return f"Server is already running: http://{self._host}:{self._port}"

        try:
            # Set server name and start
            self._host = host
            self._port = port
            self._server.name = "mcp-server"
            self._server.start(host=host, port=port)
            self._is_running = True
            return f"Server started at http://{host}:{port}"
        except Exception as e:
            raise RuntimeError(f"Failed to start server: {str(e)}") from e

    def stop(self) -> str:
        """
        Stop MCP server

        Stop the currently running MCP server. If the server is not running, a corresponding message is returned.

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If stopping server fails

        Example:
            ```python
            server_service = MCPServerService()
            server_service.start()

            # Stop server
            result = server_service.stop()
            print(result)  # Output: Server stopped

            # Try to stop again
            result = server_service.stop()
            print(result)  # Output: Server is not currently running
            ```
        """
        if not self._is_running:
            return "Server is not currently running"

        try:
            self._server.stop()
            self._is_running = False
            return "Server stopped"
        except Exception as e:
            raise RuntimeError(f"Failed to stop server: {str(e)}") from e

    def get_url(self) -> str:
        """
        Get MCP server URL

        Get the URL of the currently running MCP server. If the server is not running, a corresponding message is returned.

        Returns:
            str: Server URL or status message

        Exceptions:
            RuntimeError: If getting URL fails

        Example:
            ```python
            server_service = MCPServerService()

            # Server not running
            url = server_service.get_url()
            print(url)  # Output: Server is not currently running

            # After starting server
            server_service.start()
            url = server_service.get_url()
            print(url)  # Output: http://localhost:8000
            ```
        """
        if not self._is_running:
            return "Server is not currently running"

        try:
            url = self._server.get_url()
            return url if url else f"http://{self._host}:{self._port}"
        except Exception as e:
            raise RuntimeError(f"Failed to get server URL: {str(e)}") from e

    def add_tool(self, name: str, description: str, code: str, code_type: str = "python") -> str:
        """
        Add tool to MCP server

        Compile and add a custom tool to the server. Code will be executed in a secure sandbox environment.

        Parameters:
            name: Tool name
            description: Tool description
            code: Tool code, should contain the implementation function
            code_type: Tool code type, default is "python"

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If adding tool fails

        Example:
            ```python
            server_service = MCPServerService()
            server_service.start()

            # Add a simple tool
            code = '''
            def get_greeting(name: str) -> str:
                '''Return greeting'''
                return f"Hello, {name}!"
            '''
            result = server_service.add_tool("get_greeting", "Return greeting", code)
            print(result)  # Output: Tool 'get_greeting' added to server
            ```
        """
        if not self._is_running:
            return "Error: Server is not currently running, please start the server first"

        try:
            # Dynamically compile tool code
            tool_func = self._compile_tool_code(name, code)
            self._server.add_tool(name, tool_func, description)
            return f"Tool '{name}' added to server"
        except Exception as e:
            raise RuntimeError(f"Failed to add tool: {str(e)}") from e

    def add_resource(self, name: str, content: Any, description: str = "") -> str:
        """
        Add resource to MCP server

        Add a resource to the server, resource can be a string, dictionary or list.

        Parameters:
            name: Resource name
            content: Resource content, can be a string, dictionary or list
            description: Resource description, default is empty string

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If adding resource fails

        Example:
            ```python
            server_service = MCPServerService()
            server_service.start()

            # Add string resource
            result = server_service.add_resource(
                "greeting_template",
                "Hello, {name}! Welcome to {product}.",
                "Greeting template"
            )

            # Add list resource
            cities = ["New York", "Los Angeles", "Chicago", "San Francisco"]
            result = server_service.add_resource("cities", cities, "Major US cities")

            # Add dictionary resource
            weather_data = {
                "New York": {"temperature": 25, "condition": "Sunny"},
                "Los Angeles": {"temperature": 28, "condition": "Cloudy"}
            }
            result = server_service.add_resource("weather_data", weather_data, "City weather data")
            ```
        """
        if not self._is_running:
            return "Error: Server is not currently running, please start the server first"

        try:
            self._server.add_resource(name, content)
            return f"Resource '{name}' added to server"
        except Exception as e:
            raise RuntimeError(f"Failed to add resource: {str(e)}") from e

    def add_prompt(self, name: str, content: str, description: str = "") -> str:
        """
        Add prompt to MCP server

        Add a prompt template to the server, can be used for generating text or building conversations.

        Parameters:
            name: Prompt name
            content: Prompt content, can contain formatting placeholders
            description: Prompt description, default is empty string

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If adding prompt fails

        Example:
            ```python
            server_service = MCPServerService()
            server_service.start()

            # Add simple prompt
            result = server_service.add_prompt(
                "weather_query",
                "Please query the weather for {city}",
                "Weather query template"
            )

            # Add complex conversation prompt
            conversation_prompt = '''
            System: You are a weather assistant, you can answer questions about weather.
            User: {query}
            Assistant:
            '''
            result = server_service.add_prompt(
                "weather_assistant",
                conversation_prompt,
                "Weather assistant conversation template"
            )
            ```
        """
        if not self._is_running:
            return "Error: Server is not currently running, please start the server first"

        try:
            self._server.add_prompt(name, content)
            return f"Prompt '{name}' added to server"
        except Exception as e:
            raise RuntimeError(f"Failed to add prompt: {str(e)}") from e

    def is_running(self) -> bool:
        """
        Check if server is running

        Returns:
            bool: True if server is running, False otherwise

        Example:
            ```python
            server_service = MCPServerService()

            # Check server status
            if not server_service.is_running():
                server_service.start()

            # Use server
            # ...

            # Stop server when done
            if server_service.is_running():
                server_service.stop()
            ```
        """
        return self._is_running

    async def async_start_server(self, host: str = "localhost", port: int = 8000) -> str:
        """
        Asynchronously start MCP server

        Asynchronous version of the start method, for starting server in asynchronous environments.

        Parameters:
            host: Server host, default is localhost
            port: Server port, default is 8000

        Returns:
            str: Server URL or status message

        Exceptions:
            RuntimeError: If starting server fails

        Example:
            ```python
            import asyncio

            async def run_server():
                server_service = MCPServerService()

                # Asynchronously start server
                url = await server_service.async_start_server()
                print(url)

                # Use server
                # ...

                # Stop server when done
                await server_service.async_stop_server()

            asyncio.run(run_server())
            ```
        """
        return self.start(host, port)

    async def async_stop_server(self) -> str:
        """
        Asynchronously stop MCP server

        Asynchronous version of the stop method, for stopping server in asynchronous environments.

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If stopping server fails

        Example:
            ```python
            import asyncio

            async def run_server():
                server_service = MCPServerService()
                await server_service.async_start_server()

                # Use server
                # ...

                # Stop server when done
                result = await server_service.async_stop_server()
                print(result)  # Output: Server stopped

            asyncio.run(run_server())
            ```
        """
        return self.stop()

    def _compile_tool_code(self, name: str, code_str: str) -> Callable[..., Any]:
        """
        Compile tool code

        Compile code string into callable function object for adding to MCP server.

        Parameters:
            name: Tool function name
            code_str: Tool code string

        Returns:
            Callable: Compiled function object

        Exceptions:
            SyntaxError: If code syntax is incorrect
            Exception: Other compilation errors
        """
        # Create a safe namespace
        sandbox = {}
        # Add built-in functions and types
        for k, v in __builtins__.items():  # type: ignore
            if k in safe_builtins:
                sandbox[k] = v

        sandbox["requests"] = requests
        sandbox["json"] = json

        # Construct function code
        full_code = f"def {name}(**kwargs):\n{textwrap.indent(code_str, '    ')}"

        # Execute code
        exec(full_code, sandbox)
        return cast(Callable[..., Any], sandbox[name])

    # Add asynchronous version of get_url method
    async def async_get_url(self) -> str:
        """
        Asynchronously get server URL

        Asynchronous version of the get_url method, for getting server URL in asynchronous environments.

        Returns:
            str: Server URL or status message

        Exceptions:
            RuntimeError: If getting URL fails

        Example:
            ```python
            import asyncio

            async def get_server_info():
                server_service = MCPServerService()
                await server_service.async_start_server()

                # Asynchronously get URL
                url = await server_service.async_get_url()
                print(f"Server running at: {url}")

                await server_service.async_stop_server()

            asyncio.run(get_server_info())
            ```
        """
        return self.get_url()

    # Add asynchronous version of add_tool method
    async def async_add_tool(self, name: str, description: str, code: str, code_type: str = "python") -> str:
        """
        Asynchronously add tool to MCP server

        Asynchronous version of the add_tool method, for adding tools in asynchronous environments.

        Parameters:
            name: Tool name
            description: Tool description
            code: Tool code, should contain the implementation function
            code_type: Tool code type, default is "python"

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If adding tool fails

        Example:
            ```python
            import asyncio

            async def add_server_tool():
                server_service = MCPServerService()
                await server_service.async_start_server()

                # Add a simple tool
                code = '''
                def get_greeting(name: str) -> str:
                    '''Return greeting'''
                    return f"Hello, {name}!"
                '''
                result = await server_service.async_add_tool("get_greeting", "Return greeting", code)
                print(result)  # Output: Tool 'get_greeting' added to server

                await server_service.async_stop_server()

            asyncio.run(add_server_tool())
            ```
        """
        return self.add_tool(name, description, code, code_type)

    # Add asynchronous version of add_resource method
    async def async_add_resource(self, name: str, content: Any, description: str = "") -> str:
        """
        Asynchronously add resource to MCP server

        Asynchronous version of the add_resource method, for adding resources in asynchronous environments.

        Parameters:
            name: Resource name
            content: Resource content, can be a string, dictionary or list
            description: Resource description, default is empty string

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If adding resource fails

        Example:
            ```python
            import asyncio

            async def add_server_resource():
                server_service = MCPServerService()
                await server_service.async_start_server()

                # Add string resource
                result = await server_service.async_add_resource(
                    "greeting_template",
                    "Hello, {name}! Welcome to {product}.",
                    "Greeting template"
                )
                print(result)  # Output: Resource 'greeting_template' added to server

                await server_service.async_stop_server()

            asyncio.run(add_server_resource())
            ```
        """
        return self.add_resource(name, content, description)

    # Add asynchronous version of add_prompt method
    async def async_add_prompt(self, name: str, content: str, description: str = "") -> str:
        """
        Asynchronously add prompt to MCP server

        Asynchronous version of the add_prompt method, for adding prompts in asynchronous environments.

        Parameters:
            name: Prompt name
            content: Prompt content, can contain formatting placeholders
            description: Prompt description, default is empty string

        Returns:
            str: Operation result message

        Exceptions:
            RuntimeError: If adding prompt fails

        Example:
            ```python
            import asyncio

            async def add_server_prompt():
                server_service = MCPServerService()
                await server_service.async_start_server()

                # Add simple prompt
                result = await server_service.async_add_prompt(
                    "weather_query",
                    "Please query the weather for {city}",
                    "Weather query template"
                )
                print(result)  # Output: Prompt 'weather_query' added to server

                await server_service.async_stop_server()

            asyncio.run(add_server_prompt())
            ```
        """
        return self.add_prompt(name, content, description)

    def add_example_resources(self) -> None:
        """Add example resources"""
        # Add city list
        cities = ["New York", "Los Angeles", "Chicago", "San Francisco"]
        result = self.add_resource("cities", cities, "Major US cities")
        if result:
            print(f"Resource added successfully: {result}")

        # Add weather data
        weather_data = {
            "New York": {"temperature": 25, "condition": "Sunny"},
            "Los Angeles": {"temperature": 28, "condition": "Cloudy"}
        }
        self.add_resource("weather_data", weather_data, "City weather data")
