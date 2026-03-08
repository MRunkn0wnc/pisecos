#!/bin/bash
# Download AI model for AEGIS

echo "Downloading AEGIS AI model for Raspberry Pi..."
echo "================================================"

MODEL_DIR="/usr/local/pisecos/core/ai/model"
mkdir -p $MODEL_DIR

cd $MODEL_DIR

echo "Downloading TinyLlama (optimized for armv7l)..."
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -O tinyllama.gguf

if [ -f "tinyllama.gguf" ]; then
    echo " AEGIS AI model downloaded successfully"
    echo "Model size: $(du -h tinyllama.gguf | cut -f1)"
else
    echo " Download failed"
    exit 1
fi

echo ""
echo "AEGIS is now ready with AI capabilities"