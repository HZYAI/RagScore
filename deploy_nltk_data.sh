#!/bin/bash

# Script to deploy nltk_data/tokenizers to the new server
# Target server: 115.159.95.13

set -e  # Exit on error

SERVER_IP="115.159.95.13"
SERVER_USER="ubuntu"
SOURCE_NLTK_DATA="/home/ubuntu/RAGScore/nltk_data/tokenizers"
TARGET_NLTK_DATA="~/nltk_data/tokenizers"

echo "=========================================="
echo "NLTK Data Deployment Script"
echo "=========================================="
echo "Source: $SOURCE_NLTK_DATA"
echo "Target: $SERVER_USER@$SERVER_IP:$TARGET_NLTK_DATA"
echo "=========================================="

# Check if source directory exists
if [ ! -d "$SOURCE_NLTK_DATA" ]; then
    echo "Error: Source directory $SOURCE_NLTK_DATA does not exist!"
    exit 1
fi

# Create target directory on remote server
echo "Creating nltk_data directory on remote server..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p /home/ubuntu/RAGScore/nltk_data"

# Copy tokenizers folder to remote server
echo "Copying tokenizers data..."
rsync -avz --progress \
  $SOURCE_NLTK_DATA/ \
  $SERVER_USER@$SERVER_IP:$TARGET_NLTK_DATA/

echo "=========================================="
echo "NLTK tokenizers deployment completed!"
echo "=========================================="
echo ""
echo "Deployed files:"
ssh $SERVER_USER@$SERVER_IP "ls -lh ~/nltk_data/tokenizers/"
echo ""
echo "=========================================="
