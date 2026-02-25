#!/bin/bash

CONTAINER_NAME="chromadb"
IMAGE_NAME="chromadb/chroma:latest"
PORT="8000"

echo "🔍 Checking ChromaDB container status..."

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "✓ Container '${CONTAINER_NAME}' exists"
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "✓ Container '${CONTAINER_NAME}' is already running"
        echo "📍 ChromaDB is available at: http://localhost:${PORT}"
        exit 0
    else
        echo "▶️  Starting existing container '${CONTAINER_NAME}'..."
        docker start "${CONTAINER_NAME}"
        echo "✓ Container started successfully"
        echo "📍 ChromaDB is available at: http://localhost:${PORT}"
        exit 0
    fi
else
    echo "📦 Container '${CONTAINER_NAME}' does not exist"
    echo "🔽 Pulling ChromaDB image..."
    docker pull "${IMAGE_NAME}"
    
    echo "🚀 Creating and starting ChromaDB container..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:8000" \
        -v chroma-data:/chroma/chroma \
        "${IMAGE_NAME}"
    
    if [ $? -eq 0 ]; then
        echo "✓ ChromaDB container created and started successfully"
        echo "📍 ChromaDB is available at: http://localhost:${PORT}"
    else
        echo "❌ Failed to create ChromaDB container"
        exit 1
    fi
fi
