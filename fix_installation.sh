#!/bin/bash
# Quick fix script for "ModuleNotFoundError: No module named 'ragscore'"

set -e

echo "=========================================="
echo "RAGScore Installation Fix"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found!"
    echo "Please run this script from the RAGScore project directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Virtual environment found"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if ragscore is already installed
if python -c "import ragscore" 2>/dev/null; then
    echo "✅ ragscore package is already installed"
    echo ""
    echo "Testing import..."
    python -c "import ragscore.web.app; print('✅ ragscore.web.app can be imported')"
else
    echo "❌ ragscore package not found"
    echo ""
    echo "Installing ragscore package in editable mode..."
    pip install -e .
    echo ""
    echo "✅ ragscore package installed successfully!"
fi

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
python -c "import ragscore; print('✅ ragscore module: OK')"
python -c "import ragscore.web.app; print('✅ ragscore.web.app module: OK')"
python -c "import ragscore.cli; print('✅ ragscore.cli module: OK')"

echo ""
echo "=========================================="
echo "✅ Installation Fixed!"
echo "=========================================="
echo ""
echo "You can now run:"
echo "  ./start_web.sh"
echo ""
