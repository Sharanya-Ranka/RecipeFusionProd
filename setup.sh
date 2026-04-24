#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting environment setup..."

# 1. Handle .env file and HF_TOKEN
ENV_FILE=".env"

# If HF_TOKEN is not already set in the shell, prompt the user
if [ -z "$HF_TOKEN" ]; then
    echo "Hugging Face token not found in shell variables."
    read -p "Please paste your HF_TOKEN: " HF_TOKEN
fi

# Create or overwrite the .env file
echo "HF_TOKEN=$HF_TOKEN" > "$ENV_FILE"
echo "✅ Created $ENV_FILE with your token."

# 2. Upgrade pip to ensure smooth installations
echo "Updating pip..."
pip install --upgrade pip

# 3. Install core dependencies
echo "Installing LLM and Data Science stack..."
pip install -U \
    peft \
    trl \
    transformers \
    ipywidgets \
    bitsandbytes \
    datasets \
    pandas \
    numpy \
    huggingface-hub \
    tensorboard \
    hydra-core \
    python-dotenv

# 4. Install vLLM separately (as it often has specific dependency requirements)
echo "Installing vLLM..."
pip install -U vllm

echo "✨ Setup complete! Your environment is ready to go."