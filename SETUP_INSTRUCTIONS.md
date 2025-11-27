# RAGScore Setup Instructions

## ✅ Installation Complete!

The dependencies have been installed. Follow these final steps to run the application:

### 1. Create your `.env` file

```bash
cp .env.example .env
```

Then edit `.env` and add your DashScope API key:
```
DASHSCOPE_API_KEY="sk-c2bb48b9dbf547709e60a123c3bef5bd"
```

### 2. Activate the virtual environment

```bash
source venv/bin/activate
```

### 3. Run the web application

```bash
python -m ragscore.web.app
```

Then open your browser to: **http://localhost:8000**

### 4. Or use the CLI

```bash
# Add documents to data/docs/ first, then:
python -m ragscore.cli generate
```

## Features

- **Web Interface**: Beautiful, Apple-style UI with drag-and-drop file upload
- **Real-time Progress**: WebSocket-based progress updates during QA generation
- **Download Results**: Export generated QA pairs as JSON
- **CLI Tool**: Command-line interface for batch processing

## Troubleshooting

If you encounter any issues:

1. Make sure the virtual environment is activated
2. Verify your API key is correct in `.env`
3. Check that documents are in the `data/docs` directory
4. View logs in the terminal for error messages

Enjoy using RAGScore! 🚀
