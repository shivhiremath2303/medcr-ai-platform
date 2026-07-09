from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """
    Returns the fixtures directory.
    """

    return Path(__file__).parent / "fixtures"
