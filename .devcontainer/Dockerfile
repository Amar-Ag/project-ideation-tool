FROM mcr.microsoft.com/devcontainers/python:3.11

# Install uv at the system level
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# uv will create .venv inside the mounted workspace via postCreateCommand
