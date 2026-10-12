#!/bin/bash

# Run linters and formatters
echo "Running black..."
black app/ tests/

echo "Running isort..."
isort app/ tests/

echo "Running ruff..."
ruff check app/ tests/

echo "Running mypy..."
mypy app/

