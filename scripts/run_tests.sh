#!/bin/bash

# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term -v

