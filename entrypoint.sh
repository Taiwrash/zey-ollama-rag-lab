#!/bin/bash

# Start Ollama in the background
echo "Starting Ollama server..."
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to be available..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
  sleep 2
done

# Pull the model if it's not present
echo "Pulling tinyllama model..."
ollama pull tinyllama

# Start the FastAPI app
echo "Starting FastAPI app..."
exec python app.py
