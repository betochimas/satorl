# Imports
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

class Generator(ABC):
    """
    Base class for synthetic data generators.
    """
    name: str = ""
    seed: int | None = None

    @abstractmethod
    def generate(self, rows: int) -> pd.DataFrame:
        """Return `rows` rows of synthetic data."""
        raise NotImplementedError

    def params(self) -> dict[str, Any]:
        """Generation parameters for provenance metadata (excludes seed). Override per generator."""
        return {}