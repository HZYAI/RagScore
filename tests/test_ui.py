"""Tests for notebook UI helpers."""

import pytest

from ragscore import ui


@pytest.mark.asyncio
async def test_async_pbar_falls_back_when_notebook_widgets_missing(monkeypatch):
    """Missing ipywidgets should not crash async notebook progress."""
    monkeypatch.setattr(ui, "get_environment", lambda: "jupyter")

    import tqdm.notebook

    class MissingWidgetTqdm:
        def __init__(self, *args, **kwargs):
            raise ImportError("IProgress not found")

    monkeypatch.setattr(tqdm.notebook, "tqdm", MissingWidgetTqdm)

    async def task():
        return "ok"

    async_pbar = ui.get_async_pbar()
    assert await async_pbar.gather(task(), desc="Testing") == ["ok"]
