#!/bin/bash

# Create initial database migration
alembic revision --autogenerate -m "Initial migration: create all tables"

