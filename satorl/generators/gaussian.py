from typing import Any

import numpy as np
import pandas as pd

from satorl.generators.base import Generator

class GaussianGenerator(Generator):
    """Normally-distributed numeric features."""

    name = "gaussian"

    def __init__(
        self,
        *,
        columns: int = 3,
        mean: float = 0.0,
        std: float = 1.0,
        seed: int | None = None,
    ) -> None:
        self.columns = columns
        self.mean = mean
        self.std = std
        self.seed = seed

    def params(self) -> dict[str, Any]:
        return {"columns": self.columns, "mean": self.mean, "std": self.std}

    def generate(self, rows: int) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        data = rng.normal(self.mean, self.std, size=(rows,self.columns))
        cols = [f"feature_{i}" for i in range(self.columns)]
        return pd.DataFrame(data, columns=cols)
