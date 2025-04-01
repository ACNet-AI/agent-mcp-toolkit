#!/bin/bash

# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

echo "Tests completed!" 