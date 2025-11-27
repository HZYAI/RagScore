# RAGScore Deployment Summary

## Issue Identified and Fixed

### Root Cause
The `ModuleNotFoundError: No module named 'ragscore'` error occurs because the RAGScore package needs to be installed in editable mode (`pip install -e .`) after installing dependencies. This was missing from the original workflow.

### Why This Happens
- RAGScore is a Python package with source code in `src/ragscore/`
- The package needs to be installed so Python can find and import the `ragscore` module
- Simply having the files present isn't enough - Python needs the package registered in the virtual environment

## Files Created/Updated

### 1. **setup.py** (NEW)
- Provides setuptools configuration for package installation
- Defines package metadata and dependencies
- Enables `pip install -e .` to work

### 2. **setup.sh** (UPDATED)
- Now includes `pip install -e .` step at the end
- This ensures the ragscore package is properly installed

### 3. **fix_installation.sh** (NEW)
- Quick fix script for users who encounter the module error
- Checks and installs the package if missing
- Verifies installation is working

### 4. **TROUBLESHOOTING.md** (NEW)
- Comprehensive troubleshooting guide
- Documents common issues and solutions
- Includes verification checklist

### 5. **DEPLOYMENT_GUIDE.md** (UPDATED)
- Added clear warnings about the installation requirement
- Explains why `pip install -e .` is critical
- Notes not to use `requirements.frozen.txt` (contains local path)

### 6. **README.md** (UPDATED)
- Enhanced installation instructions
- Added troubleshooting section
- Clarified the importance of package installation

## Deployment Workflow

### For New Server (115.159.95.13)

1. **Deploy Project Files**
   ```bash
   cd /home/ubuntu/RAGScore
   ./deploy_to_server.sh
   ```

2. **Deploy NLTK Data**
   ```bash
   ./deploy_nltk_data.sh
   ```

3. **On New Server - Setup**
   ```bash
   ssh ubuntu@115.159.95.13
   cd ~/projects/RAGScore
   
   # Create .env file
   cp .env.example .env
   nano .env  # Add your DASHSCOPE_API_KEY
   
   # Run setup (includes package installation)
   bash setup.sh
   ```

4. **Start Application**
   ```bash
   ./start_web.sh
   ```

### If You Encounter the Module Error

Simply run:
```bash
./fix_installation.sh
```

Or manually:
```bash
source venv/bin/activate
pip install -e .
```

## Key Points to Remember

1. ✅ **Always run `setup.sh`** - Don't skip steps
2. ✅ **Use `requirements.txt`** - Not `requirements.frozen.txt` 
3. ✅ **Package installation is required** - `pip install -e .`
4. ✅ **NLTK data must be deployed separately** - Use `deploy_nltk_data.sh`
5. ✅ **Environment file is required** - Create `.env` with API key

## Verification Commands

Before starting the application, verify everything is set up:

```bash
# 1. Check virtual environment
ls venv/bin/activate

# 2. Check package installation
source venv/bin/activate
python -c "import ragscore; print('✅ Package installed')"

# 3. Check web module
python -c "import ragscore.web.app; print('✅ Web module OK')"

# 4. Check environment file
test -f .env && echo "✅ .env exists" || echo "❌ .env missing"

# 5. Check NLTK data
ls ~/nltk_data/tokenizers/punkt && echo "✅ NLTK data OK" || echo "❌ NLTK data missing"
```

If all checks pass, you're ready to run:
```bash
./start_web.sh
```

## Files in Deployment

### Included
- Source code (`src/ragscore/`)
- Configuration files (`setup.py`, `pyproject.toml`, `requirements.txt`)
- Scripts (`setup.sh`, `start_web.sh`, `deploy_*.sh`, `fix_installation.sh`)
- Documentation (`README.md`, `DEPLOYMENT_GUIDE.md`, `TROUBLESHOOTING.md`)
- Templates and static files (`src/ragscore/web/templates/`, `src/ragscore/web/static/`)

### Excluded (must be created on target)
- `.env` file (contains API keys - security)
- `venv/` directory (created during setup)
- `output/` directory (created at runtime)
- `data/` directory (upload your own documents)

### Deployed Separately
- `~/nltk_data/tokenizers/` (via `deploy_nltk_data.sh`)

## Architecture Notes

```
RAGScore/
├── src/ragscore/          # Main package (must be installed)
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration
│   ├── pipeline.py        # Main pipeline
│   ├── web/               # Web application
│   │   ├── app.py         # FastAPI application
│   │   ├── templates/     # HTML templates
│   │   └── static/        # Static assets
│   └── ...
├── setup.py               # Package installation config
├── setup.sh               # Setup script (includes pip install -e .)
├── start_web.sh           # Start web server
└── requirements.txt       # Dependencies
```

The key insight: `src/ragscore/` is a Python package that must be installed, not just present in the filesystem.

## Support

- **Quick Fix**: `./fix_installation.sh`
- **Troubleshooting**: See `TROUBLESHOOTING.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`
- **General Usage**: See `README.md`
