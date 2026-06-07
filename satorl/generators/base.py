# Imports
from abc import abstractmethod

import pandas as pd

class Generator():
    """
    Base class for synthetic data generators.
    """

    @abstractmethod
    def generate(self, rows: int) -> pd.DataFrame:
        """Return `rows` rows of synthetic data."""
        raise NotImplementedError