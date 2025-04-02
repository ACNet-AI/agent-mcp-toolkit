# Usage Examples

This project contains complete example code located in the `examples` directory:

## Basic Usage

The `examples/basic_usage.py` file demonstrates the basic functionality of Agent MCP Toolkit, including:

- Creating server and client tools
- Initializing MCPToolkit in different modes
- Integrating tools with LangChain and LangGraph
- Creating and using Agents

Example code snippet:

```python
from langchain.chat_models import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_toolkit import MCPToolkit

# Create toolkit
toolkit = MCPToolkit(mode="client_and_server")

# Get all tools
tools = toolkit.get_tools()

# Create Agent
model = ChatOpenAI(model="gpt-3.5-turbo")
agent = create_react_agent(model, tools)

# Execute Agent
messages = [HumanMessage(content=prompt)]
response = await agent.ainvoke({"messages": messages})
```

View the [complete basic usage example](https://github.com/ACNet-AI/agent-mcp-toolkit/blob/main/examples/basic_usage.py) for more details.

## Custom Tools

The `examples/custom_tools.py` file demonstrates how to create custom tools and add them to an MCP server:

- Defining custom tool functions
- Adding tools to the server
- Calling tools from the client
- Creating Agents that use custom tools

Example code snippet:

```python
from langchain_mcp_toolkit import MCPToolkit

# Start server
toolkit = MCPToolkit(mode="server")
server_service = toolkit.get_server_service()
await server_service.async_start_server()

# Add custom tool
calc_code = """
expression = kwargs.get("expression", "")
try:
    allowed_chars = set("0123456789+-*/() .")
    if any(c not in allowed_chars for c in expression):
        return "Error: Expression contains disallowed characters"

    result = eval(expression)
    return f"Calculation result: {result}"
except Exception as e:
    return f"Calculation error: {str(e)}"
"""
await server_service.add_tool("calculator", "Simple calculator", calc_code)

# Client tool call
client_toolkit = MCPToolkit(mode="client")
client_service = client_toolkit.get_client_service()
server_url = await server_service.async_get_url()
await client_service.create("default", {"url": f"{server_url}/sse", "transport": "sse"})
calc_result = await client_service.call_tool("calculator", {"expression": "2 * (3 + 4) - 5"})
```

View the [complete custom tools example](https://github.com/ACNet-AI/agent-mcp-toolkit/blob/main/examples/custom_tools.py) for more details. 