from pathlib import Path

import pandas as pd

from satorl.storage.base import Storage

class LocalStorage(Storage):
    def write(self, df: pd.DataFrame, destination: str) -> str:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return str(path.resolve())
