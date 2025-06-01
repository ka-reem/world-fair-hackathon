#!/bin/bash

echo "🦙 Setting up Llama models with Ollama..."

# Install Ollama (if not already installed)
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Pull required models
echo "Pulling Llama models..."
ollama pull llama2:7b
ollama pull llama2:13b
ollama pull codellama

echo "✅ Llama setup complete!"
echo "Available models:"
ollama list 