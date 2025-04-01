"""
MCP Toolkit Data Model Definitions

This module defines various data models used in the MCP toolkit, including server configurations, tool definitions, resource definitions, etc.
These models are used to standardize data structures, ensuring consistent data formats and validation throughout the toolkit.

This module mainly includes:
- Generic models: such as NoInput
- Server-related models: such as ServerConfig, ToolDefinition, etc.
- Client-related models: such as ClientConfig, ToolCall, etc.

All models are based on Pydantic's BaseModel, providing data validation and serialization functionality.
"""

from typing import Any

from pydantic import BaseModel, Field


class NoInput(BaseModel):
    """
    Model for operations requiring no input

    Used to represent operations that don't require any input parameters, typically used for tools or operations without parameters.

    Example:
        ```python
        # Used when defining a tool that requires no input
        from langchain.tools import BaseTool

        class NoInputTool(BaseTool):
            name = "no_input_tool"
            description = "A tool that requires no input"
            args_schema = NoInput

            def _run(self, **kwargs):
                return "Executed a tool without input"
        ```
    """

    pass


# Server-related models
class ServerConfig(BaseModel):
    """
    Server Configuration

    Defines configuration parameters for an MCP server, including host address, port, transport type, etc.

    Attributes:
        host: Server host address, default is 'localhost'
        port: Server port, default is 8000
        transport: Transport type, supports 'sse' or 'stdio', default is 'sse'
        command: Start command, only used for stdio mode

    Example:
        ```python
        # Create default server configuration
        config = ServerConfig()
        print(config.host)  # Output: localhost
        print(config.port)  # Output: 8000

        # Custom server configuration
        custom_config = ServerConfig(
            host="0.0.0.0",
            port=9000,
            transport="stdio",
            command="python -m mcp_server"
        )
        ```
    """

    host: str = Field(default="localhost", description="Server host address, default is 'localhost'")
    port: int = Field(default=8000, description="Server port, default is 8000")
    transport: str = Field(default="sse", description="Transport type, supports 'sse' or 'stdio', default is 'sse'")
    command: str | None = Field(None, description="Start command, only used for stdio mode")


class ToolDefinition(BaseModel):
    """
    Tool Definition

    Defines a tool in the MCP server, including name, description, and implementation code.

    Attributes:
        name: Tool name
        description: Tool description
        code: Tool code
        code_type: Tool code type, default is 'python'

    Example:
        ```python
        # Define a simple tool
        tool = ToolDefinition(
            name="hello_world",
            description="Returns Hello World",
            code="def run(inputs=None):\n    return 'Hello World'"
        )

        # Add to server using ServerAddToolTool
        add_tool = ServerAddToolTool(server_service=server_service)
        await add_tool.invoke({"tool": tool})
        ```
    """

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    code: str = Field(..., description="Tool code")
    code_type: str = Field(default="python", description="Tool code type, default is 'python'")


class ResourceDefinition(BaseModel):
    """
    Resource Definition

    Defines a resource in the MCP server, which can be text, a JSON object, or a list.

    Attributes:
        name: Resource name
        content: Resource content, can be a string, dictionary, or list
        description: Resource description, optional

    Example:
        ```python
        # Define a text resource
        text_resource = ResourceDefinition(
            name="greeting",
            content="Hello, world!",
            description="Greeting resource"
        )

        # Define a JSON resource
        json_resource = ResourceDefinition(
            name="config",
            content={"debug": True, "timeout": 30},
            description="Configuration information"
        )

        # Add to server using ServerAddResourceTool
        add_resource = ServerAddResourceTool(server_service=server_service)
        await add_resource.invoke({"resource": text_resource})
        ```
    """

    name: str = Field(..., description="Resource name")
    content: str | dict[str, Any] | list[Any] = Field(..., description="Resource content")
    description: str = Field(default="", description="Resource description, optional")


class PromptDefinition(BaseModel):
    """
    Prompt Definition

    Defines a prompt in the MCP server, used for generating text or guiding AI models.

    Attributes:
        name: Prompt name
        content: Prompt content

    Example:
        ```python
        # Define a simple prompt
        prompt = PromptDefinition(
            name="translation_prompt",
            content="Translate the following text into {{target_language}}:\n{{text}}"
        )

        # Add to server using ServerAddPromptTool
        add_prompt = ServerAddPromptTool(server_service=server_service)
        await add_prompt.invoke({"prompt": prompt})
        ```
    """

    name: str = Field(..., description="Prompt name")
    content: str = Field(..., description="Prompt content")


# Client-related models
class ClientConfig(BaseModel):
    """
    Client Configuration

    Defines configuration parameters for an MCP client, including server URL and transport type.

    Attributes:
        server_url: MCP server URL, e.g., 'http://localhost:8000'
        transport_type: Transport type, supports 'sse' or 'stdio', default is 'sse'

    Example:
        ```python
        # Create client configuration
        config = ClientConfig(
            server_url="http://localhost:8000",
            transport_type="sse"
        )

        # Use configuration to create client
        client_service = MCPClientService()
        await client_service.create(config.server_url, config.transport_type)
        ```
    """

    server_url: str = Field(..., description="MCP server URL, e.g., 'http://localhost:8000'")
    transport_type: str = Field(
        default="sse", description="Transport type, supports 'sse' or 'stdio', default is 'sse'"
    )


class ToolCall(BaseModel):
    """
    Tool Call

    Defines a client's request to call a server tool.

    Attributes:
        tool_name: Name of the tool to call
        arguments: Tool parameters, provided as a dictionary

    Example:
        ```python
        # Create tool call
        call = ToolCall(
            tool_name="hello_world",
            arguments={"name": "user"}
        )

        # Call tool using ClientCallToolTool
        call_tool = ClientCallToolTool(client_service=client_service)
        result = await call_tool.invoke(call.dict())
        ```
    """

    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Tool parameters, provided as a dictionary")


class ResourceName(BaseModel):
    """
    Resource Name

    Used to specify the name of a resource to read.

    Attributes:
        resource_name: Name of the resource to read

    Example:
        ```python
        # Create resource name request
        resource_req = ResourceName(resource_name="greeting")

        # Read resource using ClientReadResourceTool
        read_resource = ClientReadResourceTool(client_service=client_service)
        content = await read_resource.invoke(resource_req.dict())
        ```
    """

    resource_name: str = Field(..., description="Name of the resource to read")


class PromptName(BaseModel):
    """
    Prompt Name

    Used to specify the name of a prompt to retrieve.

    Attributes:
        prompt_name: Name of the prompt to retrieve

    Example:
        ```python
        # Create prompt name request
        prompt_req = PromptName(prompt_name="translation_prompt")

        # Get prompt using ClientGetPromptTool
        get_prompt = ClientGetPromptTool(client_service=client_service)
        prompt_content = await get_prompt.invoke(prompt_req.dict())
        ```
    """

    prompt_name: str = Field(..., description="Name of the prompt to retrieve")


class LangChainPromptConfig(BaseModel):
    """
    LangChain Prompt Configuration

    Used to retrieve a LangChain-formatted prompt from an MCP server.

    Attributes:
        prompt_name: Prompt name
        arguments: Prompt parameters, optional

    Example:
        ```python
        # Create LangChain prompt configuration
        prompt_config = LangChainPromptConfig(
            prompt_name="translation_prompt",
            arguments={"target_language": "English"}
        )

        # Get LangChain prompt using GetLangChainPromptTool
        get_lc_prompt = GetLangChainPromptTool(client_service=client_service)
        lc_prompt = await get_lc_prompt.invoke(prompt_config.dict())

        # Use LangChain prompt
        llm = ChatOpenAI()
        result = llm.invoke(lc_prompt)
        ```
    """

    prompt_name: str = Field(..., description="Prompt name")
    arguments: dict[str, Any] | None = Field(None, description="Prompt parameters, optional")


class LangChainToolsConfig(BaseModel):
    """
    LangChain Tools Configuration

    Used to retrieve a list of LangChain-formatted tools from an MCP server.

    Attributes:
        include_server_prefix: Whether to add server prefix to tool names

    Example:
        ```python
        # Create LangChain tools configuration
        tools_config = LangChainToolsConfig(include_server_prefix=True)

        # Get LangChain tools using GetLangChainToolsTool
        get_lc_tools = GetLangChainToolsTool(client_service=client_service)
        lc_tools = await get_lc_tools.invoke(tools_config.dict())

        # Use LangChain tools to create Agent
        from langchain.agents import create_openai_functions_agent
        agent = create_openai_functions_agent(llm, lc_tools, prompt)
        ```
    """

    include_server_prefix: bool = Field(default=True, description="Whether to add server prefix to tool names")
