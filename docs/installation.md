# Installation

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation from PyPI

The simplest way to install the MCP Toolkit is via pip:

```bash
pip install agent-mcp-toolkit
```

## Development Installation

For development purposes, you can install the package from source:

```bash
# Clone the repository
git clone https://github.com/ACNet-AI/agent-mcp-toolkit.git
cd agent-mcp-toolkit

# Install in development mode
pip install -e ".[dev,test]"
```

## Dependencies

MCP Toolkit depends on the following packages:

- mcp[cli,rich]>=1.4.1,<1.5.0
- langchain-mcp-adapters>=0.0.5
- langchain>=0.3.20
- langgraph>=0.1.16
- pydantic>=2.8.0,<3.0.0
- anyio>=4.7.0

These dependencies will be automatically installed when you install the package. 