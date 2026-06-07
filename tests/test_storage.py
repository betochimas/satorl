# Storage backends + factory + URI parsing
import pandas as pd
import pytest

from satorl.storage import open_destination
from satorl.storage.local import LocalStorage
from satorl.storage.s3 import S3Storage


def test_local_write_roundtrip(tmp_path):
    dest = tmp_path / "out.csv"
    LocalStorage().write(pd.DataFrame({"x": [1, 2]}), str(dest))
    assert dest.exists()
    assert pd.read_csv(dest)["x"].tolist() == [1, 2]

def test_open_destination_routing():
    assert isinstance(open_destination("s3://b/k.csv"), S3Storage)
    assert isinstance(open_destination("./out.csv"), LocalStorage)
    with pytest.raises(ValueError):
        open_destination("ftp://x/y")

def test_s3_write_roundtrip(s3_client):
    # Using moto, the s3_client fixture
    df = pd.DataFrame({"a": [1, 2]})
    S3Storage(client=s3_client).write(df, "s3://test-bucket/data/out.csv")
    body = s3_client.get_object(Bucket="test-bucket", Key="data/out.csv")["Body"].read()
    assert pd.read_csv(__import__("io").BytesIO(body))["a"].tolist() == [1, 2]
