# RAGScore Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError: No module named 'ragscore'

**Error Message:**
```
/home/ubuntu/RAGScore/venv/bin/python: Error while finding module specification for 'ragscore.web.app' 
(ModuleNotFoundError: No module named 'ragscore')
```

**Cause:**
The `ragscore` package is not installed in the virtual environment. This happens when you skip the package installation step.

**Solution:**
Install the package in editable mode:
```bash
cd ~/projects/RAGScore  # or wherever your project is
source venv/bin/activate
pip install -e .
```

After this, `./start_web.sh` should work correctly.

**Prevention:**
Always run the complete `setup.sh` script which includes the `pip install -e .` step.

---

### Issue 2: Virtual Environment Not Found

**Error Message:**
```
source: venv/bin/activate: No such file or directory
```

**Cause:**
The virtual environment hasn't been created yet.

**Solution:**
```bash
python3 -m venv venv
bash setup.sh
```

---

### Issue 3: DASHSCOPE_API_KEY Not Set

**Error Message:**
```
⚠️  DASHSCOPE_API_KEY is not set!
```

**Cause:**
The `.env` file is missing or doesn't contain the API key.

**Solution:**
```bash
cp .env.example .env
nano .env  # Add your actual API key
```

Edit the file to replace `YOUR_API_KEY_HERE` with your actual DashScope API key.

---

### Issue 4: NLTK Data Not Found

**Error Message:**
```
Resource punkt not found.
```

**Cause:**
NLTK tokenizer data is not installed.

**Solution:**
If you deployed from another server, make sure to run:
```bash
./deploy_nltk_data.sh
```

Or manually download:
```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

---

### Issue 5: Port 8000 Already in Use

**Error Message:**
```
ERROR: [Errno 98] Address already in use
```

**Cause:**
Another process is using port 8000.

**Solution:**
Find and kill the process:
```bash
lsof -ti:8000 | xargs kill -9
```

Or change the port in `start_web.sh` or run manually:
```bash
source venv/bin/activate
python -m ragscore.web.app --port 8001
```

---

## Quick Verification Checklist

Before starting the application, verify:

1. **Virtual environment exists:**
   ```bash
   ls venv/bin/activate
   ```

2. **Package is installed:**
   ```bash
   source venv/bin/activate
   python -c "import ragscore; print('OK')"
   ```

3. **Environment file exists:**
   ```bash
   test -f .env && echo "OK" || echo "Missing"
   ```

4. **NLTK data exists:**
   ```bash
   ls ~/nltk_data/tokenizers/punkt
   ```

If all checks pass, you should be able to run:
```bash
./start_web.sh
```

---

## Complete Fresh Installation

If you're having persistent issues, try a complete fresh installation:

```bash
# Remove old virtual environment
rm -rf venv

# Remove old outputs
rm -rf output/*

# Run setup
bash setup.sh

# Verify installation
source venv/bin/activate
python -c "import ragscore; print('ragscore installed successfully')"

# Start the application
./start_web.sh
```

---

## Getting Help

If you continue to experience issues:

1. Check the error message carefully
2. Verify all prerequisites are installed (Python 3.9-3.11)
3. Ensure you have internet connectivity for downloading dependencies
4. Check disk space: `df -h`
5. Check Python version: `python3 --version`
