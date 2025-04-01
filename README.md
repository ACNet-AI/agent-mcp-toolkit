# Agent MCP Toolkit

A library of tools for Agent frameworks to interact with MCP (Model Context Protocol) servers and clients. Supports creating and managing MCP servers, registering tools, resources, and prompts, as well as creating client connections and calling server tools.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/agent-mcp-toolkit.svg)](https://badge.fury.io/py/agent-mcp-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🛠️ Convert MCP tools into tools usable by Agents
- 🖥️ Allow Agents to create, start, and manage MCP servers
- 📝 Support dynamic registration of custom tools, resources, and prompts
- 🔌 Provide client connection and tool calling functionality
- 🔄 Support integration with the official langchain-mcp-adapters library
- 🧩 Support LangChain and LangGraph integration
- 🌐 Multi-server support for interacting with multiple MCP servers simultaneously
- 🔄 LangChain tools and prompt conversion for direct LLM agent integration

## Installation

```bash
# Standard installation
pip install agent-mcp-toolkit

# Install from source
git clone https://github.com/acnet-ai/agent-mcp-toolkit.git
cd agent-mcp-toolkit
pip install -e .

# Install test dependencies
pip install agent-mcp-toolkit[test]
```

## Quick Start

### Basic Usage

```python
from langchain.chat_models import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp.server.fastmcp import FastMCP
from langchain_mcp_toolkit import MCPToolkit

# Create MCP server and toolkit
server = FastMCP("WeatherServer")
toolkit = MCPToolkit.from_server_and_api_key(server=server)
tools = toolkit.get_tools()

# Create Agent
model = ChatOpenAI(model="gpt-3.5-turbo")
agent = create_react_agent(model, tools)

# Run Agent
response = agent.invoke({
    "messages": [
        {"role": "user", "content": "Create a weather query tool and check the weather in New York"}
    ]
})
```

## Tool Types

The toolkit provides two types of tools:

### Server Tools
- `mcp_start_server`: Start MCP server
- `mcp_stop_server`: Stop MCP server
- `mcp_get_server_url`: Get server URL
- `mcp_add_tool`: Add tool to server
- `mcp_add_resource`: Add resource to server
- `mcp_add_prompt`: Add prompt to server

### Client Tools
- `mcp_create_client`: Create MCP client
- `mcp_call_tool`: Call MCP tool
- `mcp_list_tools`: List available tools
- `mcp_list_resources`: List available resources
- `mcp_read_resource`: Read resource
- `mcp_list_prompts`: List available prompts
- `mcp_get_prompt`: Get prompt
- `mcp_get_langchain_tools`: Get tools as LangChain tools
- `mcp_get_langchain_prompt`: Get prompt as LangChain messages

## Use Cases

### 1. Create a Tool Server

```python
from langchain_mcp_toolkit import MCPToolkit

# Create server mode toolkit
toolkit = MCPToolkit(mode="server")
server_service = toolkit.get_server_service()

# Start server and add tool
await server_service.start(name="MyToolServer", port=8000)
await server_service.add_tool("weather", "Get weather", 
    """def get_weather(city: str) -> str:
        return f"The weather in {city} is sunny, temperature 25℃"
    """)
```

### 2. Connect to a Server

```python
# Create client mode toolkit
toolkit = MCPToolkit(mode="client")
client_service = toolkit.get_client_service()

# Connect to server
client_service.create("http://localhost:8000", "sse")
await client_service.connect()

# Call tool
result = await client_service.call_tool("default", "weather", city="New York")
print(result)  # Output: The weather in New York is sunny, temperature 25℃
```

### 3. Multi-server Support

```python
# Create client mode toolkit
toolkit = MCPToolkit(mode="client")
client_service = toolkit.get_client_service()

# Configure multiple servers
server_configs = {
    "weather_server": {
        "url": "http://localhost:8000", 
        "transport": "sse"
    },
    "translation_server": {
        "url": "http://localhost:8001", 
        "transport": "sse"
    }
}

# Connect to multiple servers
client_service.create(server_configs)
await client_service.connect()

# Call tools on different servers
weather = await client_service.call_tool("weather_server", "get_weather", city="New York")
translation = await client_service.call_tool("translation_server", "translate", text="Hello", target="es")

# List all available tools from all servers
all_tools = await client_service.list_tools()
```

### 4. LangChain Integration

```python
# Create client mode toolkit and connect to server
toolkit = MCPToolkit(mode="client")
client_service = toolkit.get_client_service()
client_service.create("http://localhost:8000", "sse")
await client_service.connect()

# Get tools as LangChain tools
langchain_tools = await client_service.get_langchain_tools()

# Get prompt as LangChain messages
langchain_prompt = await client_service.get_langchain_prompt(
    "chat_prompt", {"user": "Alice", "question": "What's the weather?"}
)

# Use LangChain tools in agent
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI()
agent = initialize_agent(
    langchain_tools, 
    llm, 
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)

agent.run(langchain_prompt)
```

## FAQ

**Q: Why do I need to install both MCP SDK and agent-mcp-toolkit?**  
A: MCP SDK provides basic functionality, while agent-mcp-toolkit provides Agent-friendly high-level abstractions and tools.

**Q: Compatibility with LangChain/LangGraph?**  
A: Compatible with LangChain 0.3.20+ and LangGraph 0.3.21+.

**Q: Can I connect to multiple MCP servers at once?**  
A: Yes, the toolkit supports multi-server connections through the client service, allowing you to interact with multiple MCP servers simultaneously.

**Q: Compatibility with MCP versions?**  
A: Currently compatible with MCP version 1.4.1 to 1.5.0. Support for newer versions is planned in future releases.

**Q: Can I use MCP tools directly with LangChain agents?**  
A: Yes, the toolkit provides `get_langchain_tools()` and `get_langchain_prompt()` methods that convert MCP tools and prompts to LangChain format.

## Design Philosophy

- **Unified Tool Interface**: All tools use the same base class and interface design
- **Modular Structure**: Functionality is distributed across different modules for easy extension
- **Flexible Tool Selection**: Different tool sets can be selected as needed
- **Async Support**: Provides both synchronous and asynchronous APIs
- **Multi-server Architecture**: Connect to and manage multiple MCP servers simultaneously
- **Framework Agnostic**: Works with various agent frameworks while offering optimized LangChain integration

## Related Links

- [Contribution Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## License

This project is licensed under the MIT License.