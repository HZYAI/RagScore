# RAGScore Deployment Guide

## Server Information
- **IP Address**: 115.159.95.13
- **User**: ubuntu
- **Target Location**: ~/projects/RAGScore

## Dependencies Frozen
✅ All dependencies have been frozen to `requirements.frozen.txt` with exact versions.

## Deployment Steps

### 1. Deploy the Project
Run the deployment script from your local machine:
```bash
cd /home/ubuntu/RAGScore
./deploy_to_server.sh
```

This script will:
- Create the target directory on the remote server
- Copy all project files (excluding venv, cache, and data directories)
- Preserve the frozen dependencies file

### 1.5. Deploy NLTK Data (Required)
The project requires NLTK tokenizers data. Deploy it separately:
```bash
cd /home/ubuntu/RAGScore
./deploy_nltk_data.sh
```

This will copy the `nltk_data/tokenizers` folder (~18MB) to `~/nltk_data/tokenizers` on the remote server, which includes:
- punkt tokenizer
- punkt_tab tokenizer

### 2. Setup on Remote Server
After deployment, SSH into the remote server:
```bash
ssh ubuntu@115.159.95.13
cd ~/projects/RAGScore
```

### 3. Configure Environment
Create a `.env` file with your API keys:
```bash
cp .env.example .env
nano .env  # Edit with your actual API keys
```

### 4. Install Dependencies
**IMPORTANT**: You must run the setup script which installs dependencies AND the ragscore package:
```bash
bash setup.sh
```

Or manually (all steps required):
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install -e .  # This installs the ragscore package - CRITICAL!
```

**Note**: 
- The `pip install -e .` step is essential. Without it, you'll get: `ModuleNotFoundError: No module named 'ragscore'`
- Do NOT use `requirements.frozen.txt` for installation as it contains a local path reference
- Use `requirements.txt` instead, which has the base dependencies

### 5. Start the Application
```bash
bash start_web.sh
```

## Files Included in Deployment
- Source code (`src/`)
- Configuration files (`pyproject.toml`, `requirements.txt`, `requirements.frozen.txt`)
- Setup scripts (`setup.sh`, `start_web.sh`)
- Documentation (`README.md`, `QUICK_START.md`, `SETUP_INSTRUCTIONS.md`)
- Test files (`test_pipeline.py`, `tests/`)

## Files Excluded from Deployment
- Virtual environment (`venv/`)
- Python cache (`__pycache__/`, `*.pyc`)
- Test cache (`.pytest_cache/`)
- Output directory (`output/`)
- Data directory (`data/`)
- Environment file (`.env`) - must be created manually on remote server

## Troubleshooting

### SSH Connection Issues
If you can't connect to the server, ensure:
- You have SSH access configured
- Your SSH key is added to the remote server
- The server firewall allows SSH connections

### Permission Issues
If you encounter permission errors:
```bash
ssh ubuntu@115.159.95.13 "chmod -R u+w ~/projects/RAGScore"
```

### Dependency Installation Issues
If dependencies fail to install, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt  # Use base requirements if frozen fails
```

## Notes
- The frozen dependencies ensure consistent versions across environments
- Make sure to configure your `.env` file with the correct API keys
- The deployment excludes data and output directories to save bandwidth
- You may need to upload your data separately if required
