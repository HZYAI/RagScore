# 🚀 RAGScore Quick Start Guide

## ✅ Setup Complete!

Your RAGScore project is ready to use with:
- ✨ Beautiful Apple-style web interface
- 📊 Real-time progress tracking
- 💾 JSON export functionality
- 🖥️  CPU-only (no GPU required)
- 🇨🇳 Optimized for fast downloads in China

## Start the Web Application

```bash
./start_web.sh
```

Then open your browser to: **http://localhost:8000**

## Using the Web Interface

1. **Upload Documents**: Drag and drop PDF, TXT, MD, or HTML files
2. **Generate QA Pairs**: Click the "Generate QA Pairs" button
3. **Watch Progress**: Real-time updates via WebSocket
4. **View Results**: See generated QA pairs with difficulty levels
5. **Download**: Export all results as JSON

## Alternative: Command Line Interface

```bash
# Activate virtual environment
source venv/bin/activate

# Add documents to data/docs/ directory first
cp your_document.pdf data/docs/

# Generate QA pairs
python -m ragscore.cli generate

# Results will be in: output/generated_qas.jsonl
```

## Project Structure

```
RAGScore/
├── src/ragscore/          # Main source code
│   ├── config.py          # Configuration
│   ├── data_processing.py # Document reading & chunking
│   ├── embedding.py       # Text embeddings
│   ├── vector_store.py    # FAISS index management
│   ├── llm.py            # QA generation with DashScope
│   ├── pipeline.py        # Main pipeline orchestration
│   ├── cli.py            # Command-line interface
│   └── web/              # Web application
│       ├── app.py        # FastAPI backend
│       └── templates/    # HTML frontend
├── data/docs/            # Place your documents here
├── output/               # Generated results
├── requirements.txt      # Python dependencies
├── setup.sh             # Installation script
└── start_web.sh         # Quick start script
```

## Features

### Web Interface
- 📤 Drag-and-drop file upload
- 📊 Real-time progress with WebSocket
- 🎨 Clean, modern Apple-style design
- 📱 Responsive layout
- 💾 One-click JSON download

### QA Generation
- 🤖 Powered by DashScope (Qwen-Turbo)
- 📚 Supports multiple document formats
- 🎯 Three difficulty levels (easy, medium, hard)
- 🔍 FAISS vector search for context
- ✅ Quality rationale and support spans

## API Endpoints

- `GET /` - Web interface
- `POST /api/upload` - Upload documents
- `WS /ws/generate` - Generate QA pairs (WebSocket)
- `GET /api/results` - Get generated results
- `GET /api/download` - Download JSON file
- `DELETE /api/clear` - Clear all data

## Troubleshooting

**Port already in use?**
```bash
# Change port in start_web.sh or run directly:
python -m ragscore.web.app --port 8080
```

**Need to update API key?**
```bash
# Edit .env file
nano .env
```

**Want to clear everything?**
```bash
# Use the web interface "Clear All" button
# Or manually:
rm -rf data/docs/* output/*
```

## Next Steps

1. Upload your documents via the web interface
2. Generate QA pairs and review the results
3. Download the JSON file for your RAG evaluation
4. Iterate and improve your document collection

Enjoy using RAGScore! 🎉
