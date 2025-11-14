#!/bin/bash

# Create output folder
MODEL_DIR="chat_models"

echo "Downloading models into: $MODEL_DIR"
echo

# List of models to download
declare -A MODELS=(
  ["tinyllama-1.1b-chat-v1.0.Q8_0.gguf"]="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q8_0.gguf"
  ["mistral-7b-instruct-v0.1.Q2_K.gguf"]="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q2_K.gguf"
  ["DeepSeek-R1-0528-Qwen3-8B-UD-Q4_K_XL.gguf"]="https://huggingface.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF/resolve/main/DeepSeek-R1-0528-Qwen3-8B-UD-Q4_K_XL.gguf"
)

# Download each model
for NAME in "${!MODELS[@]}"; do
  URL="${MODELS[$NAME]}"
  OUT="$MODEL_DIR/$NAME"

  echo "Downloading: $NAME"
  curl -L "$URL" -o "$OUT"

  if [ $? -eq 0 ]; then
    echo "Saved to $OUT"
  else
    echo "Failed to download $NAME"
  fi

  echo
done

echo "All downloads completed."
