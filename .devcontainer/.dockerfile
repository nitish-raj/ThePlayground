FROM mcr.microsoft.com/devcontainers/universal:latest

# Install postgres and other tools
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    pandoc-citeproc \
    curl \
    gdebi-core \
    dirmngr \
    gnupg \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    git \
    python3-pip

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && apt-get install -y google-cloud-sdk

# Create vscode user and set permissions
RUN useradd -ms /bin/bash vscode \
    && mkdir -p /home/vscode/.local/share/code-server /home/vscode/workspace \
    && chown -R vscode:vscode /home/vscode/.local/share/code-server /home/vscode/workspace

# Switch to vscode user
USER vscode

# Set up Git configuration
RUN git config --global core.autocrlf input && \
    git config --global user.email "22993803+nitish-raj@users.noreply.github.com" && \
    git config --global user.name "Nitish"

WORKDIR /workspace/

# Install Jupyter
RUN python3 -m pip install jupyter

# Ensure Git is initialized in the workspace
RUN git init