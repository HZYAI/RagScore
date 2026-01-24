"""
RAGScore UI Module - Universal Display Adapter

Auto-detects environment (Colab, Jupyter, Terminal) and provides
the appropriate progress bars and async fixes.

Usage:
    from ragscore.ui import get_pbar, patch_asyncio, get_environment

    # Auto-patch asyncio for notebooks
    patch_asyncio()

    # Get environment-appropriate progress bar
    for item in get_pbar(items, desc="Processing"):
        process(item)
"""

import sys
from collections.abc import Iterable
from typing import Any, Optional


def get_environment() -> str:
    """
    Detect the current execution environment.

    Returns:
        'colab': Google Colab
        'jupyter': Jupyter notebook or VS Code notebook
        'terminal': Standard Python interpreter or IPython terminal
    """
    # Check for Google Colab first
    if "google.colab" in sys.modules:
        return "colab"

    # Check for IPython/Jupyter
    try:
        shell = get_ipython().__class__.__name__  # type: ignore
        if shell == "ZMQInteractiveShell":
            return "jupyter"  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return "terminal"  # IPython terminal
    except NameError:
        pass  # Not in IPython

    return "terminal"


def get_pbar(
    iterable: Optional[Iterable] = None,
    total: Optional[int] = None,
    desc: str = "",
    **kwargs: Any,
):
    """
    Get the appropriate tqdm progress bar for the current environment.

    - Colab/Jupyter: Uses tqdm.notebook with HTML/JS widgets
    - Terminal: Uses standard tqdm with ASCII progress bar

    Args:
        iterable: Iterable to wrap
        total: Total number of items (for manual updates)
        desc: Description text
        **kwargs: Additional tqdm arguments

    Returns:
        tqdm progress bar instance

    Usage:
        for item in get_pbar(items, desc="Processing"):
            process(item)
    """
    env = get_environment()

    if env in ["colab", "jupyter"]:
        try:
            from tqdm.notebook import tqdm

            return tqdm(iterable, total=total, desc=desc, dynamic_ncols=True, **kwargs)
        except ImportError:
            # Fallback to standard tqdm if notebook version unavailable
            pass

    # Terminal or fallback
    from tqdm import tqdm

    return tqdm(iterable, total=total, desc=desc, dynamic_ncols=True, **kwargs)


def get_async_pbar():
    """
    Get the appropriate async tqdm for the current environment.

    Returns a class with a gather() method that shows progress.

    Usage:
        async_pbar = get_async_pbar()
        results = await async_pbar.gather(*tasks, desc="Processing")
    """
    import asyncio

    env = get_environment()

    if env in ["colab", "jupyter"]:
        try:
            from tqdm.notebook import tqdm as tqdm_notebook

            class NotebookAsyncProgress:
                @staticmethod
                async def gather(*tasks, desc: str = ""):
                    """Gather tasks with notebook-friendly progress bar."""
                    pbar = tqdm_notebook(total=len(tasks), desc=desc, dynamic_ncols=True)
                    results = []
                    for coro in asyncio.as_completed(tasks):
                        result = await coro
                        results.append(result)
                        pbar.update(1)
                    pbar.close()
                    return results

            return NotebookAsyncProgress
        except ImportError:
            pass

    # Terminal or fallback - use tqdm.asyncio
    from tqdm.asyncio import tqdm_asyncio

    return tqdm_asyncio


def patch_asyncio() -> bool:
    """
    Patch asyncio for notebook environments.

    Jupyter/Colab run their own event loop, which causes
    'RuntimeError: This event loop is already running' when using asyncio.run().
    This function applies nest_asyncio to allow nested event loops.

    Returns:
        True if patch was applied, False otherwise

    Usage:
        from ragscore.ui import patch_asyncio
        patch_asyncio()  # Call at start of any async pipeline
    """
    env = get_environment()

    if env in ["colab", "jupyter"]:
        try:
            import nest_asyncio

            nest_asyncio.apply()
            return True
        except ImportError:
            # Only warn in interactive environments
            print(
                "⚠️  Warning: 'nest_asyncio' not found. "
                "Install with: pip install nest_asyncio\n"
                "   This may cause errors when running async code in notebooks."
            )
            return False

    return False


def check_jupyter_widgets() -> bool:
    """
    Check if Jupyter widgets are properly installed.

    Returns:
        True if widgets are available, False otherwise
    """
    env = get_environment()

    if env == "jupyter":
        try:
            import ipywidgets  # noqa: F401

            return True
        except ImportError:
            print(
                "💡 Tip: Install 'ipywidgets' for better progress bars:\n   pip install ipywidgets"
            )
            return False

    return True  # Not in Jupyter, so widgets not needed
