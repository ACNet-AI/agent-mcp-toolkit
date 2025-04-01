# Contribution Guide

Thank you for considering contributing to agent-mcp-toolkit! This document aims to provide guidance to help you smoothly submit code, report issues, or make suggestions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting New Features](#suggesting-new-features)
  - [Submitting Code](#submitting-code)
- [Development Environment Setup](#development-environment-setup)
- [Development Process](#development-process)
  - [Branch Strategy](#branch-strategy)
  - [Commit Message Conventions](#commit-message-conventions)
  - [Code Style](#code-style)
  - [Testing Requirements](#testing-requirements)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Release Process](#release-process)

## Code of Conduct

This project adopts an open, friendly, and inclusive attitude. We expect all contributors to respect each other and create a positive environment together.

## How to Contribute

### Reporting Bugs

If you find a bug, please submit a report through GitHub Issues, and ensure it includes the following information:

1. A clear and concise description of the problem
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Environment information (operating system, Python version, etc.)
6. If possible, provide a minimal reproducible code example

### Suggesting New Features

If you wish to suggest a new feature for the project, please submit your suggestion through GitHub Issues, including the following information:

1. Feature description
2. Use cases
3. Implementation ideas (if any)
4. Whether you are willing to implement the feature yourself

### Submitting Code

If you want to submit code directly, please follow these steps:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Environment Setup

### Installing Dependencies

```bash
# Clone repository
git clone https://github.com/acnet-ai/agent-mcp-toolkit.git
cd agent-mcp-toolkit

# Install development dependencies using poetry
poetry install --with dev,test

# Or using pip
pip install -e ".[dev,test]"
```

### Recommended Development Tools

- IDE: VS Code or PyCharm
- Code formatting: Black and isort
- Code checking: Ruff
- Testing: pytest and pytest-cov

## Development Process

### Branch Strategy

- `main`: Main branch, contains the latest stable version code
- `develop`: Development branch, contains the latest development version code
- `feature/*`: Feature branches, for developing new features
- `bugfix/*`: Fix branches, for fixing bugs
- `release/*`: Release branches, for preparing new version releases

### Commit Message Conventions

Please follow this commit message format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types include:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation updates
- `style`: Code style changes (not affecting code execution)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test-related changes
- `chore`: Changes to the build process or auxiliary tools

For example:
```
feat(server): Add multi-server connection support

Added functionality for clients to connect to multiple servers simultaneously, including:
- Configuring multi-server connections
- Managing multi-server sessions
- Cross-server tool calling

Fixes #123
```

### Code Style

This project uses the following tools to ensure consistent code style:

- Black: Code formatting
- isort: Import sorting
- Ruff: Code quality checking

Before submitting code, please run the following commands:

```bash
# Format code
black src tests
isort src tests

# Code quality check
ruff check src tests
```

### Testing Requirements

All new code should have corresponding tests. We use pytest for testing, with a coverage target of 95% or higher.

```bash
# Run tests
pytest

# Run tests and check coverage
pytest --cov=langchain_mcp_toolkit

# Generate HTML coverage report
pytest --cov=langchain_mcp_toolkit --cov-report=html
```

## Submitting Pull Requests

Before submitting a PR, please ensure:

1. All tests pass
2. Code adheres to style guidelines
3. Necessary documentation has been added
4. PR title and description clearly explain the changes
5. If the PR resolves an Issue, reference that Issue in the PR description (e.g., `Fixes #123`)

After submitting a PR, maintainers will review your code and provide feedback. If all goes well, your code will be merged into the project.

## Release Process

Project maintainers are responsible for version releases. The release process is as follows:

1. Prepare a release branch `release/vX.Y.Z`
2. Update version number and CHANGELOG.md
3. Perform final testing and checks
4. Merge into the `main` branch
5. Create a version tag
6. Release to PyPI
7. Merge the release branch back to the `develop` branch

---

Thank you again for your contribution! If you have any questions, please feel free to contact the project maintainers. 