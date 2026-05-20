FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends git build-essential \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/panel_exp
