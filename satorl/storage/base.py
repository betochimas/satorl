from abc import ABC, abstractmethod

import pandas as pd

class Storage(ABC):
    @abstractmethod
    def write(self, df: pd.DataFrame, destination: str) -> str:
        """Writes `df` to `destination`; returns a human-readable location."""
        raise NotImplementedError
