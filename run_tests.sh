#!/bin/bash
set -e  # Exit on error

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Virtual environment is not activated"
    echo "Please activate your virtual environment first"
    exit 1
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest pytest-cov pytest-mock

# Run tests with additional parameters
echo "Starting tests..."
pytest "$@" --cov=src --cov-report=term-missing

echo "Tests completed!" 