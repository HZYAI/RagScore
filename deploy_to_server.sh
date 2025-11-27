#!/bin/bash

# Deployment script for RAGScore project
# Target server: 115.159.95.13
# Target location: ubuntu@VM-0-17-ubuntu:~/projects/RAGScore

set -e  # Exit on error

SERVER_IP="115.159.95.13"
SERVER_USER="ubuntu"
TARGET_DIR="~/projects/RAGScore"
SOURCE_DIR="/home/ubuntu/RAGScore"

echo "=========================================="
echo "RAGScore Deployment Script"
echo "=========================================="
echo "Source: $SOURCE_DIR"
echo "Target: $SERVER_USER@$SERVER_IP:$TARGET_DIR"
echo "=========================================="

# Create target directory on remote server
echo "Creating target directory on remote server..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p ~/projects"

# Copy project files to remote server
echo "Copying project files..."
rsync -avz --progress \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache/' \
  --exclude 'output/' \
  --exclude 'data/' \
  --exclude '.env' \
  $SOURCE_DIR/ $SERVER_USER@$SERVER_IP:$TARGET_DIR/

echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Next steps on the remote server:"
echo "1. SSH into the server: ssh $SERVER_USER@$SERVER_IP"
echo "2. Navigate to project: cd $TARGET_DIR"
echo "3. Create .env file with your API keys"
echo "4. Run setup script: bash setup.sh"
echo "5. Start the web application: bash start_web.sh"
echo ""
echo "=========================================="
