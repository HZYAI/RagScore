# Contributing to RAGScore

Thank you for your interest in contributing to RAGScore! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize what's best for the community

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A DashScope or OpenAI API key (for testing LLM features)

### Types of Contributions

We welcome:

- 🐛 **Bug fixes** - Found a bug? Please report it or submit a fix
- ✨ **New features** - Have an idea? Open an issue to discuss first
- 📚 **Documentation** - Improvements to docs, examples, or comments
- 🧪 **Tests** - More test coverage is always welcome
- 🌐 **Translations** - Help translate documentation

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ragscore.git
cd ragscore
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install in editable mode with all dependencies
pip install -e ".[dev,all]"

# Install pre-commit hooks
pre-commit install
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Verify Setup

```bash
# Run tests
pytest

# Check code style
ruff check src/
black --check src/
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clear, concise code
- Add docstrings to functions and classes
- Update documentation if needed
- Add tests for new functionality

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_your_module.py

# Run with coverage
pytest --cov=ragscore --cov-report=html
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/test_data_processing.py

# Run specific test
pytest tests/test_data_processing.py::TestChunkText::test_chunk_long_text
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures from `conftest.py` when possible
- Mock external services (API calls, file I/O)

Example test:

```python
def test_chunk_text_preserves_content():
    """Test that chunking doesn't lose any content."""
    from ragscore.data_processing import chunk_text
    
    text = "The quick brown fox jumps over the lazy dog."
    chunks = chunk_text(text, chunk_size=5, overlap=1)
    
    # Verify all words are present in chunks
    original_words = set(text.split())
    chunked_words = set()
    for chunk in chunks:
        chunked_words.update(chunk.split())
    
    assert original_words <= chunked_words
```

## Submitting Changes

### 1. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: add support for custom embedding models"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Maintenance tasks

### 2. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what and why
- Reference to related issues (if any)
- Screenshots for UI changes

### 3. Address Review Feedback

- Respond to all comments
- Make requested changes
- Push additional commits as needed

## Style Guide

### Python Style

We use:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type check
mypy src/
```

### Code Style Guidelines

```python
# Good: Clear function with docstring and types
def generate_qa_pairs(
    text: str,
    num_pairs: int = 5,
    difficulty: str = "medium"
) -> List[Dict[str, str]]:
    """
    Generate QA pairs from text.
    
    Args:
        text: Source text to generate questions from
        num_pairs: Number of QA pairs to generate
        difficulty: Question difficulty (easy, medium, hard)
        
    Returns:
        List of dictionaries with 'question' and 'answer' keys
        
    Raises:
        ValueError: If text is empty
        LLMError: If generation fails
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    ...
```

### Documentation Style

- Use Google-style docstrings
- Include type hints
- Document exceptions
- Provide usage examples where helpful

## Project Structure

```
ragscore/
├── src/ragscore/          # Main package
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── data_processing.py # Document processing
│   ├── vector_store.py    # FAISS operations
│   ├── llm.py             # QA generation
│   ├── assessment.py      # RAG evaluation
│   ├── exceptions.py      # Custom exceptions
│   ├── providers/         # LLM providers
│   └── web/               # Web interface
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example scripts
└── ...
```

## Getting Help

- 📖 Check the [documentation](https://ragscore.dev/docs)
- 🐛 Search [existing issues](https://github.com/ragscore/ragscore/issues)
- 💬 Ask in [discussions](https://github.com/ragscore/ragscore/discussions)
- 📧 Email: team@ragscore.dev

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Thanked in documentation

Thank you for helping make RAGScore better! 🎉
