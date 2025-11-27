#!/bin/bash
# Setup script for RAGScore

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/

echo "Installing dependencies (CPU-only, no GPU required)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

echo "Installing RAGScore package in editable mode..."
pip install -e .

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the CLI:"
echo "  python -m ragscore.cli generate"
echo ""
echo "To start the web server:"
echo "  python -m ragscore.web.app"
