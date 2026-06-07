# Generators + registry
import pandas as pd
import pytest

from satorl.generators import available_generators, get_generator
from satorl.generators.gaussian import GaussianGenerator

def test_gaussian_shape_and_columns():
    df = GaussianGenerator(columns=4, seed=0).generate(100)
    assert df.shape == (100, 4)
    assert list(df.columns) == [f"feature_{i}" for i in range(4)]

def test_gaussian_is_reproducible():
    a = GaussianGenerator(seed=10).generate(50)
    b = GaussianGenerator(seed=10).generate(50)
    pd.testing.assert_frame_equal(a, b)

def test_registry_lookup():
    assert get_generator("gaussian") is GaussianGenerator
    assert "gaussian" in available_generators()
    with pytest.raises(KeyError):
        get_generator("not-a-generator")