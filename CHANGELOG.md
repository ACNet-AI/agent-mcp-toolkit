# Changelog

This document records all significant changes to the agent-mcp-toolkit project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Complete async API support
- Error handling and automatic reconnection mechanism

## [0.0.1] - 2025-03-30

### Initial Version
- Basic MCP toolkit functionality
- Support for server and client modes
- Support for creating and managing MCP servers
- Support for creating clients and calling server tools
- Support for integration with LangChain and LangGraph
- Multi-server connection support
- Integration with langchain-mcp-adapters MultiServerMCPClient
- LangChain tools and prompt conversion functionality

## Usage

Initialize toolkit:

```python
from langchain_mcp_toolkit import MCPToolkit

# Create toolkit
toolkit = MCPToolkit()

# Get tools
tools = toolkit.get_tools()
```

Server management:

```python
# Server mode
toolkit = MCPToolkit(mode="server")
server_service = toolkit.get_server_service()

# Start server
await server_service.start(name="MyServer", port=8000)
await server_service.add_tool("weather", "Get weather", 
    """def get_weather(city: str) -> str:
        return f"The weather in {city} is sunny, temperature 25℃"
    """)
```

Client calls:

```python
# Client mode
toolkit = MCPToolkit(mode="client")
client_service = toolkit.get_client_service()

# Connect to server
client_service.create("http://localhost:8000", "sse")
await client_service.connect()

# Call tool
result = await client_service.call_tool("default", "get_weather", city="New York")
print(result)  # Output: The weather in New York is sunny, temperature 25℃
``` 

## Multi-server Support

```python
# Create multi-server configuration
server_configs = {
    "weather": {
        "url": "http://localhost:8000",
        "transport": "sse"
    },
    "translation": {
        "url": "http://localhost:8001",
        "transport": "sse"
    }
}

# Create client with multi-server support
client_service = toolkit.get_client_service()
client_service.create(server_configs)
await client_service.connect()

# Call tools on different servers
weather = await client_service.call_tool("weather", "get_weather", city="New York")
translation = await client_service.call_tool("translation", "translate", text="Hello world", target_lang="es")
```

## LangChain Integration

```python
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