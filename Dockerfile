FROM python:3.13-bookworm

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nano \
        curl \
        wget \
        zstd \
        git \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI
RUN curl -fsSL https://ollama.com/install.sh | bash

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Set execution perms for entrypoint
RUN chmod +x entrypoint.sh

# Expose FastAPI and Ollama
EXPOSE 8000
EXPOSE 11434

# Ensure app knows to look at localhost for Ollama
ENV OLLAMA_HOST=http://localhost:11434

CMD ["./entrypoint.sh"]
