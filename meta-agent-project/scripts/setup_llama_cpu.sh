#!/bin/bash

echo "🦙 Setting up CPU-optimized Llama models..."

# Install Ollama (if not already installed)
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Pull CPU-friendly quantized models
echo "Pulling CPU-optimized models..."

# Tiny model for low-end systems
echo "📥 Downloading TinyLlama (1.1B params)..."
ollama pull tinyllama

# Small efficient model
echo "📥 Downloading Phi (2.7B params)..."
ollama pull phi

# Quantized Llama2 for better systems
echo "📥 Downloading Llama2 7B (quantized)..."
ollama pull llama2:7b-q4_0

echo "✅ CPU-optimized Llama setup complete!"
echo ""
echo "Available models:"
ollama list
echo ""
echo "💡 The system will auto-select the best model for your CPU!" 