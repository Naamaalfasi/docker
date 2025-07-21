#!/bin/bash

echo "Starting ollama serve in background..."
ollama serve &

echo "Waiting for ollama to be ready..."
sleep 15

echo "Creating academiqa model..."
ollama create academiqa -f /modelfile/Modelfile

echo "Model created successfully, keeping container alive..."
tail -f /dev/null 