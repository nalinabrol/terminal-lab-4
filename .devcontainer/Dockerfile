FROM mcr.microsoft.com/devcontainers/base:1-ubuntu-24.04

RUN sed -i 's|http://|https://|g' /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 openssh-client coreutils diffutils zip unzip tar nano less \
    && rm -rf /var/lib/apt/lists/*
