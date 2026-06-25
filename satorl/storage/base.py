import io
from abc import ABC, abstractmethod

import pandas as pd

class Storage(ABC):
    @abstractmethod
    def write_text(self, content: str, destination: str) -> str:
        """Write raw text to `destination`; return a human-readable location."""
        raise NotImplementedError


    def write(self, df: pd.DataFrame, destination: str) -> str:
        """Writes `df` as CSV to `destination`. Shares one primitive with the sidecar."""
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return self.write_text(buffer.getvalue(), destination)
