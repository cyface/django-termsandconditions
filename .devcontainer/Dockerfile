FROM mcr.microsoft.com/devcontainers/python:1-3.13

ENV PYTHONUNBUFFERED=1

# uv manages the project's dependencies; see pyproject.toml and uv.lock.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
