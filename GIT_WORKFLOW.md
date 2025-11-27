# Git Workflow Guide for RAGScore

## Repository Information

- **Default Branch**: `main`
- **Repository Location**: `/home/ubuntu/RAGScore`

## Basic Git Commands

### Checking Status
```bash
git status
```

### Viewing Changes
```bash
# View unstaged changes
git diff

# View staged changes
git diff --cached

# View commit history
git log --oneline --graph --all
```

### Making Changes

#### 1. Stage Changes
```bash
# Stage specific files
git add <file1> <file2>

# Stage all changes
git add .

# Stage only modified files (not new files)
git add -u
```

#### 2. Commit Changes
```bash
# Commit with message
git commit -m "Your descriptive commit message"

# Commit with detailed message (opens editor)
git commit
```

#### 3. Amend Last Commit
```bash
# Add forgotten changes to last commit
git add <forgotten-file>
git commit --amend --no-edit

# Change last commit message
git commit --amend -m "New commit message"
```

### Branching

#### Create and Switch Branches
```bash
# Create new branch
git branch feature/new-feature

# Switch to branch
git checkout feature/new-feature

# Create and switch in one command
git checkout -b feature/new-feature
```

#### List Branches
```bash
# List local branches
git branch

# List all branches (including remote)
git branch -a
```

#### Delete Branches
```bash
# Delete merged branch
git branch -d feature/old-feature

# Force delete unmerged branch
git branch -D feature/old-feature
```

### Merging

```bash
# Switch to target branch
git checkout main

# Merge feature branch
git merge feature/new-feature
```

### Undoing Changes

#### Discard Unstaged Changes
```bash
# Discard changes in specific file
git checkout -- <file>

# Discard all unstaged changes
git checkout -- .
```

#### Unstage Files
```bash
# Unstage specific file
git reset HEAD <file>

# Unstage all files
git reset HEAD
```

#### Reset to Previous Commit
```bash
# Soft reset (keeps changes staged)
git reset --soft HEAD~1

# Mixed reset (keeps changes unstaged)
git reset HEAD~1

# Hard reset (discards all changes)
git reset --hard HEAD~1
```

### Stashing Changes

```bash
# Stash current changes
git stash

# Stash with message
git stash save "Work in progress on feature X"

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply and remove most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{0}

# Delete stash
git stash drop stash@{0}
```

## Working with Remote Repositories

### Adding Remote
```bash
# Add remote repository
git remote add origin <repository-url>

# Verify remote
git remote -v
```

### Pushing Changes
```bash
# Push to remote branch
git push origin main

# Push and set upstream
git push -u origin main

# Push all branches
git push --all origin
```

### Pulling Changes
```bash
# Pull from remote
git pull origin main

# Pull with rebase
git pull --rebase origin main
```

### Fetching Changes
```bash
# Fetch all remotes
git fetch --all

# Fetch specific remote
git fetch origin
```

## Recommended Workflow

### Feature Development
1. Create feature branch from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit regularly:
   ```bash
   git add .
   git commit -m "feat: add new functionality"
   ```

3. Keep branch updated with main:
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/your-feature-name
   git merge main
   ```

4. Push feature branch:
   ```bash
   git push -u origin feature/your-feature-name
   ```

5. Merge back to main:
   ```bash
   git checkout main
   git merge feature/your-feature-name
   git push origin main
   ```

### Commit Message Conventions

Use conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add semantic similarity metric
fix: resolve embedding dimension mismatch
docs: update README with installation steps
refactor: optimize vector store search
```

## Useful Aliases

Add these to your `~/.gitconfig`:
```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all --decorate
    amend = commit --amend --no-edit
```

## Tips

1. **Commit Often**: Make small, focused commits
2. **Write Clear Messages**: Describe what and why, not how
3. **Review Before Commit**: Use `git diff` to review changes
4. **Keep Main Clean**: Always test before merging to main
5. **Use Branches**: Create branches for features and experiments
6. **Pull Before Push**: Always pull latest changes before pushing
7. **Don't Commit Secrets**: Never commit `.env` files or API keys

## Ignored Files

The following are automatically ignored (see `.gitignore`):
- `.env` - Environment variables
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.log` - Log files
- `nltk_data/` - NLTK data (can be re-downloaded)
- `data/docs/*` - Document data
- `output/*` - Output files

## Getting Help

```bash
# Get help for any command
git help <command>
git <command> --help

# Quick reference
git help -a
```
